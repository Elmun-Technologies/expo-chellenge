"""Rassilka: maqsad tanlash, xabar yozish, preview, navbat bilan yuborish."""
import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import (TelegramBadRequest, TelegramForbiddenError,
                                TelegramRetryAfter)
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..constants import BCTarget, CANCEL_TEXTS, CB, Role, SubStatus
from ..db import repo
from ..db.models import Expo, Participant, Submission, User
from ..i18n import t
from ..states import BroadcastFlow

log = logging.getLogger(__name__)

router = Router(name="broadcast")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

settings = get_settings()

# bitta vaqtda bitta rassilka (oddiy, single-instance)
_sending_lock = asyncio.Lock()


def kb_targets(lang: str):
    b = InlineKeyboardBuilder()
    for tgt in (BCTarget.ALL, BCTarget.PARTICIPANTS, BCTarget.APPROVED,
                BCTarget.PENDING, BCTarget.TOP10, BCTarget.SINGLE):
        b.button(text=t(lang, f"tgt_{tgt}"), callback_data=f"{CB.BC}:tg:{tgt}")
    b.button(text=t(lang, "btn_cancel"), callback_data=f"{CB.ADMIN}:menu")
    b.adjust(1)
    return b.as_markup()


async def resolve_targets(session: AsyncSession, target_type: str,
                          expo: Expo | None, single_user_id: int | None) -> list[User]:
    if target_type == BCTarget.ALL:
        q = select(User).where(User.is_blocked == False)  # noqa: E712
    elif target_type == BCTarget.SINGLE:
        q = select(User).where(User.id == single_user_id)
    else:
        # faol expo konteksti
        if expo is None:
            return []
        base = (select(User).join(Participant, Participant.user_id == User.id)
                .join(Submission, Submission.participant_id == Participant.id,
                      isouter=True)
                .where(Participant.expo_id == expo.id,
                       User.is_blocked == False))  # noqa: E712
        if target_type == BCTarget.PARTICIPANTS:
            q = base
        elif target_type == BCTarget.APPROVED:
            q = base.where(Submission.status == SubStatus.APPROVED)
        elif target_type == BCTarget.PENDING:
            q = base.where(Submission.status == SubStatus.PENDING)
        elif target_type == BCTarget.TOP10:
            tops = await repo.top_submissions(session, expo.id, limit=10)
            user_ids = [u.id for _, _, u in tops]
            q = select(User).where(User.id.in_(user_ids)) if user_ids else None
            if q is None:
                return []
        else:
            return []
    return list((await session.execute(q)).scalars())


@router.callback_query(F.data == f"{CB.ADMIN}:bc")
async def bc_start(cb: CallbackQuery, state: FSMContext, session, role):
    if role not in Role.ADMIN_PANEL:
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    await state.clear()
    await state.set_state(BroadcastFlow.choose_target)
    await cb.message.edit_text(t("uz", "bc_choose"), reply_markup=kb_targets("uz"))
    await cb.answer()


@router.callback_query(F.data.startswith(f"{CB.BC}:tg:"), BroadcastFlow.choose_target)
async def bc_target(cb: CallbackQuery, state: FSMContext, session):
    target = cb.data.split(":")[-1]
    await state.update_data(target=target)

    if target == BCTarget.SINGLE:
        await state.set_state(BroadcastFlow.single_user)
        await cb.message.edit_text(t("uz", "bc_ask_single"))
    else:
        await state.set_state(BroadcastFlow.message)
        await cb.message.edit_text(t("uz", "bc_ask_msg"))
    await cb.answer()


@router.message(BroadcastFlow.single_user, F.text & ~F.text.in_(CANCEL_TEXTS))
async def bc_single_user(message: Message, state: FSMContext, session):
    raw = message.text.strip()
    user = None
    if raw.lstrip("-").isdigit():
        user = await repo.get_user_by_tg(session, int(raw))
    elif raw.startswith("@"):
        user = await repo.get_user_by_username(session, raw)
    if user is None:
        return await message.answer(t("uz", "user_not_found"))
    await state.update_data(single_user_id=user.id)
    await state.set_state(BroadcastFlow.message)
    await message.answer(f"🎯 {user.full_name} (@{user.username or '—'})\n\n" + t("uz", "bc_ask_msg"))


@router.message(BroadcastFlow.message, F.photo | (F.text & ~F.text.in_(CANCEL_TEXTS)))
async def bc_message(message: Message, state: FSMContext, session):
    payload = {
        "text": (message.caption if message.photo else message.text) or "",
        "photo_file_id": message.photo[-1].file_id if message.photo else None,
    }
    await state.update_data(payload=payload)

    data = await state.get_data()
    expo = await repo.get_active_expo(session)
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    targets = await resolve_targets(session, data["target"], expo,
                                    data.get("single_user_id"))
    await state.update_data(target_count=len(targets), expo_id=expo.id if expo else None)

    # preview: xabarning nusxasi adminning o'ziga
    if payload["photo_file_id"]:
        await message.answer_photo(payload["photo_file_id"], caption=payload["text"])
    else:
        await message.answer(payload["text"] or "—")

    b = InlineKeyboardBuilder()
    b.button(text=t("uz", "btn_bc_send"), callback_data=f"{CB.BC}:send")
    b.button(text=t("uz", "btn_cancel"), callback_data=f"{CB.BC}:cancel")
    b.adjust(2)
    await state.set_state(BroadcastFlow.preview)
    await message.answer(t("uz", "bc_preview", count=len(targets)),
                         reply_markup=b.as_markup())


@router.callback_query(F.data == f"{CB.BC}:cancel", BroadcastFlow.preview)
async def bc_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(t("uz", "bc_cancelled"))
    await cb.answer()


@router.callback_query(F.data == f"{CB.BC}:send", BroadcastFlow.preview)
async def bc_send(cb: CallbackQuery, state: FSMContext, session):
    if _sending_lock.locked():
        return await cb.answer(t("uz", "bc_busy"), show_alert=True)

    data = await state.get_data()
    expo_id = data.get("expo_id")
    expo = await repo.get_expo(session, expo_id) if expo_id else None
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    targets = await resolve_targets(session, data["target"], expo,
                                    data.get("single_user_id"))
    if not targets:
        await state.clear()
        return await cb.answer(t("uz", "user_not_found"), show_alert=True)

    bc_rec = await repo.create_broadcast(
        session, cb.from_user.id, data["target"], data["payload"],
        expo_id=expo.id if expo else None,
        single_user_id=data.get("single_user_id"), total=len(targets))
    await repo.audit(session, cb.from_user.id, "broadcast_started",
                     {"bc_id": bc_rec.id, "target": data["target"],
                      "total": len(targets)})

    await state.clear()
    progress_msg = await cb.message.edit_text(
        t("uz", "bc_started", count=len(targets)))
    await cb.answer()

    bot: Bot = cb.bot
    asyncio.create_task(
        _run_broadcast(bot, bc_rec.id, [u.id for u in targets],
                       data["payload"], progress_msg.chat.id, progress_msg.message_id))


async def _run_broadcast(bot: Bot, broadcast_id: int, user_ids: list[int],
                         payload: dict, prog_chat: int, prog_msg: int):
    """Fon — barcha userlarga yuborish (limitga rioya)."""
    from ..db.session import SessionFactory

    sent = failed = blocked = 0
    total = len(user_ids)
    delay = 1.0 / max(settings.max_msgs_per_sec, 1)

    async with _sending_lock:
        for i, uid in enumerate(user_ids, start=1):
            async with SessionFactory() as session:
                user = await session.get(User, uid)
                if user is None:
                    continue
                try:
                    if payload.get("photo_file_id"):
                        await bot.send_photo(user.tg_id, payload["photo_file_id"],
                                             caption=payload.get("text") or None)
                    else:
                        await bot.send_message(user.tg_id, payload.get("text") or "")
                    sent += 1
                    await repo.add_broadcast_log(session, broadcast_id, uid, "sent")
                except TelegramForbiddenError:
                    blocked += 1
                    failed += 1
                    await repo.mark_blocked(session, uid, True)
                    await repo.add_broadcast_log(session, broadcast_id, uid,
                                                 "failed", "blocked")
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after + 1)
                    try:
                        await bot.send_message(user.tg_id, payload.get("text") or "")
                        sent += 1
                        await repo.add_broadcast_log(session, broadcast_id, uid, "sent")
                    except Exception as e2:
                        failed += 1
                        await repo.add_broadcast_log(session, broadcast_id, uid,
                                                     "failed", str(e2)[:250])
                except Exception as e:
                    failed += 1
                    await repo.add_broadcast_log(session, broadcast_id, uid,
                                                 "failed", str(e)[:250])
                await session.commit()

            await asyncio.sleep(delay)
            if i % 20 == 0 or i == total:
                try:
                    await bot.edit_message_text(
                        chat_id=prog_chat, message_id=prog_msg,
                        text=t("uz", "bc_progress", sent=i, total=total))
                except TelegramBadRequest:
                    pass

    async with SessionFactory() as session:
        await repo.finish_broadcast(session, broadcast_id, sent, failed, blocked)
        await session.commit()

    await bot.edit_message_text(
        chat_id=prog_chat, message_id=prog_msg,
        text=t("uz", "bc_done", sent=sent, failed=failed, blocked=blocked))
