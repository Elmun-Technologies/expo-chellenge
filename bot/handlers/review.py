"""Moderatsiya: guruh ichidagi tasdiqlash / rad etish / qayta ishlash."""
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import CB, ReportStatus, Role, SubStatus
from ..db import repo
from ..db.models import Participant, Submission, User, utcnow
from ..i18n import t
from ..keyboards import kb_reasons, kb_resubmit
from ..services.utils import fmt_int

log = logging.getLogger(__name__)

router = Router(name="review")
router.callback_query.filter(F.message.chat.type.in_({"group", "supergroup"}))
router.message.filter(F.chat.type.in_({"group", "supergroup"}))

# reply asosida yoziladigan "boshqa sabab" kutilmalari:
# {(chat_id, prompt_message_id): (submission_id, mode)}
pending_custom_reason: dict[tuple[int, int], tuple[int, str]] = {}


async def _user_of(session: AsyncSession, sub: Submission) -> User | None:
    return (await session.execute(
        select(User).join(Participant, User.id == Participant.user_id)
        .where(Participant.id == sub.participant_id)
    )).scalar_one_or_none()


async def _notify_user(bot: Bot, user: User, key: str,
                       views: int | None = None, reason: str | None = None):
    lang = user.language or "uz"
    kw: dict = {}
    if views is not None:
        kw["views"] = fmt_int(views)
    if reason is not None:
        kw["reason"] = reason
    markup = kb_resubmit(lang) if key in ("ntf_rejected", "ntf_changes") else None
    try:
        await bot.send_message(user.tg_id, t(lang, key, **kw), reply_markup=markup)
    except Exception as e:
        log.warning("Foydalanuvchiga xabar yuborilmadi (%s): %s", user.tg_id, e)


def _mod_name(user) -> str:
    return f"@{user.username}" if user.username else user.full_name


def _edit_mark(message: Message, key: str, mod: str, reason: str | None = None):
    caption = (message.caption or "")
    if key == "rev_approved_mark":
        caption += t("uz", key, mod=mod)
    else:
        caption += t("uz", key, mod=mod, reason=reason or "")
    return message.edit_caption(caption=caption[:1020], reply_markup=None)


# ---------------- tugmalar: ok / rej / ch ----------------

@router.callback_query(F.data.startswith(f"{CB.REVIEW}:"))
async def review_action(cb: CallbackQuery, session, role):
    if role not in Role.REVIEWERS:
        return await cb.answer(t("uz", "no_rights"), show_alert=True)

    _, sub_id_s, action = cb.data.split(":")
    sub = await repo.get_submission(session, int(sub_id_s))
    if sub is None:
        return await cb.answer("Topilmadi", show_alert=True)

    report = await repo.pending_report_for(session, sub.id)
    if report is None:
        return await cb.answer(t("uz", "rev_already"), show_alert=True)

    if action == "ok":
        is_initial = sub.status == SubStatus.PENDING
        await repo.approve_submission_report(session, sub, report, cb.from_user.id)
        await repo.audit(session, cb.from_user.id, "review_approve",
                         {"sub_id": sub.id, "views": report.views_count,
                          "is_final": report.is_final})
        try:
            await _edit_mark(cb.message, "rev_approved_mark", _mod_name(cb.from_user))
        except TelegramBadRequest:
            pass
        user = await _user_of(session, sub)
        if user:
            await _notify_user(cb.bot, user,
                               "ntf_approved" if is_initial else "ntf_update_approved",
                               views=report.views_count)
        await cb.answer("✅ Tasdiqlandi")
        return

    # rej / ch — avval sabab tanlanadi
    mode = "rej" if action == "rej" else "ch"
    await cb.message.edit_reply_markup(reply_markup=kb_reasons(sub.id, mode))
    await cb.answer()


@router.callback_query(F.data.startswith(f"{CB.REASON}:"))
async def review_reason(cb: CallbackQuery, session, role):
    if role not in Role.REVIEWERS:
        return await cb.answer(t("uz", "no_rights"), show_alert=True)

    parts = cb.data.split(":")
    sub_id, mode, code = int(parts[1]), parts[2], parts[3]
    sub = await repo.get_submission(session, sub_id)
    if sub is None:
        return await cb.answer("Topilmadi", show_alert=True)

    if code == "other":
        await cb.message.edit_reply_markup(reply_markup=None)
        msg = await cb.message.answer(t("uz", "custom_reason_prompt"))
        pending_custom_reason[(cb.message.chat.id, msg.message_id)] = (sub_id, mode)
        return await cb.answer()

    reason = t("uz", f"rsn_{code}")
    await apply_decision(bot=cb.bot, session=session, sub=sub, mode=mode,
                         reason=reason, actor_id=cb.from_user.id)
    mark = "rev_rejected_mark" if mode == "rej" else "rev_changes_mark"
    try:
        await _edit_mark(cb.message, mark, _mod_name(cb.from_user), reason)
    except TelegramBadRequest:
        pass
    await cb.answer()


# ---------------- "boshqa sabab" reply ----------------

@router.message(F.reply_to_message)
async def custom_reason_reply(message: Message, session, role):
    if role not in Role.REVIEWERS or not message.text:
        return
    key = (message.chat.id, message.reply_to_message.message_id)
    item = pending_custom_reason.pop(key, None)
    if item is None:
        return
    sub_id, mode = item
    sub = await repo.get_submission(session, sub_id)
    if sub is None:
        return await message.answer("Ariza topilmadi.")
    reason = message.text.strip()
    await apply_decision(bot=message.bot, session=session, sub=sub,
                         mode=mode, reason=reason, actor_id=message.from_user.id)
    await message.answer(f"✅ Ko'rib chiqildi. Sabab: {reason}")


# ---------------- umumiy ro'sxat ----------------

async def apply_decision(*, bot: Bot, session: AsyncSession, sub: Submission,
                         mode: str, reason: str, actor_id: int):
    """Rad etish (rej) yoki qayta ishlashga (ch) — DB + foydalanuvchiga xabar."""
    report = await repo.pending_report_for(session, sub.id)
    if report:
        report.status = ReportStatus.REJECTED
        report.reviewed_by = actor_id
        report.reviewed_at = utcnow()

    is_initial = sub.status == SubStatus.PENDING
    if is_initial:
        sub.status = SubStatus.REJECTED if mode == "rej" else SubStatus.CHANGES
        sub.reject_reason = reason
        sub.reviewed_by = actor_id
        sub.reviewed_at = utcnow()

    await repo.audit(session, actor_id, f"review_{mode}",
                     {"sub_id": sub.id, "reason": reason})

    user = await _user_of(session, sub)
    if not user:
        return
    if is_initial:
        key = "ntf_rejected" if mode == "rej" else "ntf_changes"
    else:
        key = "ntf_update_rejected"
    await _notify_user(bot, user, key, reason=reason)
