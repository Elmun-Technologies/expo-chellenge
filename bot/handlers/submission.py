"""Video yuborish, prosmotr yangilash, qayta yuborish, final tekshiruv."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import get_settings
from ..constants import CANCEL_TEXTS, CB, ExpoStatus, SubStatus
from ..db import repo
from ..db.models import Submission, User, utcnow
from ..i18n import t
from ..keyboards import kb_cancel, kb_confirm, kb_keep_link
from ..services.context import build_ctx
from ..services.flags import compute_flags
from ..services.utils import fmt_dt, fmt_int, is_reels_link, parse_views
from ..states import SubmitVideo, UpdateViews

router = Router(name="submission")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

settings = get_settings()

SEND_BTN = {"🎥 Video yuborish", "🎥 Отправить видео"}
UPDATE_BTN = {"🔄 Prosmotrni yangilash", "🔄 Обновить просмотры"}


# ---------------- guruhga yuborish ----------------

async def send_to_review(bot, lang, sub: Submission, report, user: User,
                         kind: str, old_views: int | None = None):
    """Arizani moderatsiya guruhiga yuboradi."""
    if kind == "update":
        delta_pct = 0
        if old_views:
            delta_pct = round((report.views_count - old_views) / max(old_views, 1) * 100)
        sign = "+" if delta_pct >= 0 else ""
        head = t(lang, "rev_update", sub_id=sub.id, old=fmt_int(old_views or 0),
                 new=fmt_int(report.views_count), sign=sign, pct=delta_pct)
    elif kind == "final":
        head = t(lang, "rev_final", sub_id=sub.id)
    else:
        head = t(lang, "rev_new", sub_id=sub.id)

    caption = head + t(
        lang, "rev_body",
        name=user.full_name or "—",
        insta=f"@{user.instagram}" if user.instagram else "—",
        phone=user.phone or "—",
        url=sub.video_url,
        views=fmt_int(report.views_count),
    )
    if report.flags:
        caption += t(lang, "rev_flags", flags=", ".join(report.flags))

    from ..keyboards import kb_review
    if settings.review_group_id:
        try:
            await bot.send_photo(
                chat_id=settings.review_group_id,
                photo=report.screenshot_file_id,
                caption=caption[:1020],
                reply_markup=kb_review(sub.id, lang),
            )
        except Exception:
            # fallback: rasmlarsiz
            await bot.send_message(chat_id=settings.review_group_id,
                                   text=(caption + f"\n📸 file_id: {report.screenshot_file_id}")[:4000],
                                   reply_markup=kb_review(sub.id, lang))
    else:
        import logging
        logging.getLogger(__name__).warning("REVIEW_GROUP_ID sozlanmagan!")
        for sa in settings.superadmin_ids:
            try:
                await bot.send_message(sa, "⚠️ REVIEW_GROUP_ID sozlanmagan — ariza guruhga kelmadi! " + caption)
            except Exception:
                pass


# ---------------- yangi video ----------------

@router.message(F.text.in_(SEND_BTN))
async def start_submit(message: Message, state: FSMContext, session, db_user, role):
    if db_user is None:
        return
    lang = db_user.language
    ctx = await build_ctx(session, db_user, role)
    if ctx.participant is None or ctx.expo is None:
        return await message.answer(t(lang, "not_participant"))
    if ctx.expo.status != ExpoStatus.ACTIVE:
        return await message.answer(t(lang, "expo_window",
                                      start=fmt_dt(ctx.expo.start_at),
                                      end=fmt_dt(ctx.expo.end_at)))
    if not ctx.expo_open:
        return await message.answer(t(lang, "expo_window",
                                      start=fmt_dt(ctx.expo.start_at),
                                      end=fmt_dt(ctx.expo.end_at)))
    sub = ctx.submission
    if sub and sub.status == SubStatus.PENDING:
        return await message.answer(t(lang, "already_pending", sub_id=sub.id))
    if sub and sub.status == SubStatus.APPROVED:
        return await message.answer(t(lang, "have_video", sub_id=sub.id))

    # resubmission yoki yangi
    await state.set_state(SubmitVideo.link)
    keep = bool(sub and sub.video_url)
    await state.update_data(lang=lang, keep_link=None, sub_id=sub.id if sub else None)
    if keep:
        await message.answer(t(lang, "resub_notice"))
        await message.answer(t(lang, "ask_link"), reply_markup=kb_keep_link(lang, sub.id))
    else:
        await message.answer(t(lang, "ask_link"), reply_markup=kb_cancel(lang))


@router.callback_query(F.data.startswith(f"{CB.KEEPLINK}:"), SubmitVideo.link)
async def cb_keep_link(cb: CallbackQuery, state: FSMContext, session, db_user):
    lang = (db_user.language if db_user else "uz")
    await state.update_data(keep_link=True)
    await cb.message.edit_text(t(lang, "ask_views"))
    await state.set_state(SubmitVideo.views)
    await cb.answer()


@router.message(SubmitVideo.link, F.text & ~F.text.in_(CANCEL_TEXTS))
async def sub_link(message: Message, state: FSMContext, session, db_user):
    lang = (db_user.language if db_user else "uz")
    url = message.text.strip()
    if not is_reels_link(url):
        return await message.answer(t(lang, "invalid_link"))
    ctx = await build_ctx(session, db_user, None)
    taken = await repo.url_taken(session, ctx.expo.id, url,
                                 exclude_submission_id=ctx.submission.id if ctx.submission else None)
    if taken:
        return await message.answer(t(lang, "link_taken"))
    await state.update_data(video_url=url, keep_link=False)
    await state.set_state(SubmitVideo.views)
    await message.answer(t(lang, "ask_views"))


@router.message(SubmitVideo.views, F.text & ~F.text.in_(CANCEL_TEXTS))
async def sub_views(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    views = parse_views(message.text)
    if views is None:
        return await message.answer(t(lang, "invalid_views"))
    await state.update_data(views=views)
    await state.set_state(SubmitVideo.screenshot)
    await message.answer(t(lang, "ask_screen"), reply_markup=kb_cancel(lang))


@router.message(SubmitVideo.screenshot, F.photo)
async def sub_screenshot(message: Message, state: FSMContext, session, db_user):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(screenshot_file_id=message.photo[-1].file_id)

    # tasdiqlash ekraini
    url = data.get("video_url")
    ctx = await build_ctx(session, db_user, None)
    if data.get("keep_link") and ctx.submission:
        url = ctx.submission.video_url
        await state.update_data(video_url=url)
    if not url:
        await state.clear()
        return await message.answer(t(lang, "err_generic"))
    await state.set_state(SubmitVideo.confirm)
    await message.answer(
        t(lang, "confirm_block", url=url, views=fmt_int(data["views"])),
        reply_markup=kb_confirm(lang),
    )


@router.message(SubmitVideo.screenshot)
async def sub_screenshot_wrong(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(t(data.get("lang", "uz"), "need_photo"))


@router.callback_query(F.data == "confirm:yes", SubmitVideo.confirm)
async def sub_confirm_yes(cb: CallbackQuery, state: FSMContext, session, db_user, role):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    ctx = await build_ctx(session, db_user, role)
    if ctx.participant is None or ctx.expo is None:
        await state.clear()
        return await cb.message.edit_text(t(lang, "not_participant"))

    taken = await repo.url_taken(session, ctx.expo.id, data["video_url"],
                                 exclude_submission_id=ctx.submission.id if ctx.submission else None)
    if taken:
        await state.clear()
        return await cb.message.edit_text(t(lang, "link_taken"))

    sub = await repo.save_submission(session, ctx.participant, ctx.expo.id,
                                     data["video_url"])
    from ..db.models import ViewReport
    report = ViewReport(
        submission_id=sub.id,
        screenshot_file_id=data["screenshot_file_id"],
        views_count=data["views"],
        flags=compute_flags(None, data["views"], None, utcnow(),
                            settings.suspect_jump_pct, settings.suspect_jump_abs),
    )
    session.add(report)
    await session.flush()
    await repo.audit(session, cb.from_user.id, "submission_created",
                     {"sub_id": sub.id, "views": data["views"]})
    await state.clear()

    await send_to_review(cb.bot, lang, sub, report, db_user, kind="new")
    await cb.message.edit_text(t(lang, "submitted", sub_id=sub.id))
    await cb.answer()


@router.callback_query(F.data == "confirm:no", SubmitVideo.confirm)
async def sub_confirm_no(cb: CallbackQuery, state: FSMContext, db_user):
    await state.clear()
    lang = db_user.language if db_user else "uz"
    await cb.message.edit_text(t(lang, "cancelled"))
    await cb.answer()


# ---------------- qayta yuborish (inline tugma) ----------------

@router.callback_query(F.data == f"{CB.RESUB}:go")
async def cb_resubmit(cb: CallbackQuery, state: FSMContext, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    if ctx.submission is None or ctx.submission.status not in (SubStatus.REJECTED, SubStatus.CHANGES):
        return await cb.answer(t(lang, "already_pending",
                                 sub_id=ctx.submission.id if ctx.submission else 0),
                               show_alert=True)
    await state.set_state(SubmitVideo.link)
    await state.update_data(lang=lang, sub_id=ctx.submission.id, keep_link=None)
    await cb.message.answer(t(lang, "ask_link"),
                            reply_markup=kb_keep_link(lang, ctx.submission.id))
    await cb.answer()


# ---------------- prosmotr yangilash ----------------

@router.message(F.text.in_(UPDATE_BTN))
async def start_update(message: Message, state: FSMContext, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    if ctx.submission is None or ctx.submission.status != SubStatus.APPROVED:
        return await message.answer(t(lang, "no_submission"))

    if await repo.pending_report_for(session, ctx.submission.id):
        return await message.answer(t(lang, "report_pending_exists"))

    is_final = ctx.expo.status == ExpoStatus.FINISHED if ctx.expo else False
    if is_final:
        from datetime import timedelta
        deadline = (ctx.expo.finished_at or utcnow()) + timedelta(hours=settings.final_check_hours)
        if utcnow() > deadline:
            return await message.answer(t(lang, "final_late"))

    await state.set_state(UpdateViews.views)
    await state.update_data(lang=lang, is_final=is_final)
    await message.answer(t(lang, "update_ask_views",
                           current=fmt_int(ctx.submission.current_views)),
                         reply_markup=kb_cancel(lang))


@router.message(UpdateViews.views, F.text & ~F.text.in_(CANCEL_TEXTS))
async def upd_views(message: Message, state: FSMContext, session, db_user, role):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    views = parse_views(message.text)
    if views is None:
        return await message.answer(t(lang, "invalid_views"))
    ctx = await build_ctx(session, db_user, role)
    current = ctx.submission.current_views if ctx.submission else 0
    if views < current:
        return await message.answer(t(lang, "views_too_low",
                                      new=fmt_int(views), current=fmt_int(current)))
    await state.update_data(views=views)
    await state.set_state(UpdateViews.screenshot)
    await message.answer(t(lang, "ask_screen"), reply_markup=kb_cancel(lang))


@router.message(UpdateViews.screenshot, F.photo)
async def upd_screenshot(message: Message, state: FSMContext, session, db_user, role):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    ctx = await build_ctx(session, db_user, role)
    sub = ctx.submission
    if sub is None:
        await state.clear()
        return await message.answer(t(lang, "no_submission"))
    if await repo.pending_report_for(session, sub.id):
        await state.clear()
        return await message.answer(t(lang, "report_pending_exists"))

    last = await repo.last_approved_report(session, sub.id)
    flags = compute_flags(
        sub.current_views, data["views"],
        sub.last_approved_at or (last.created_at if last else None),
        utcnow(), settings.suspect_jump_pct, settings.suspect_jump_abs,
    )
    from ..db.models import ViewReport
    report = ViewReport(
        submission_id=sub.id,
        screenshot_file_id=message.photo[-1].file_id,
        views_count=data["views"],
        flags=flags,
        is_final=bool(data.get("is_final")),
    )
    session.add(report)
    await session.flush()
    await repo.audit(session, message.from_user.id, "views_update_request",
                     {"sub_id": sub.id, "views": data["views"], "flags": flags})
    await state.clear()

    await send_to_review(message.bot, lang, sub, report, db_user,
                         kind="final" if data.get("is_final") else "update",
                         old_views=sub.current_views)
    await message.answer(t(lang, "update_submitted"))


@router.message(UpdateViews.screenshot)
async def upd_screenshot_wrong(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(t(data.get("lang", "uz"), "need_photo"))


# ---------------- final tekshiruv tugmasi (yakundan keyin) ----------------

@router.callback_query(F.data.startswith(f"{CB.FINALCHK}:"))
async def cb_final_check(cb: CallbackQuery, state: FSMContext, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    if ctx.submission is None or ctx.submission.status != SubStatus.APPROVED:
        return await cb.answer(t(lang, "no_submission"), show_alert=True)
    if await repo.pending_report_for(session, ctx.submission.id):
        return await cb.answer(t(lang, "report_pending_exists"), show_alert=True)

    await state.set_state(UpdateViews.views)
    await state.update_data(lang=lang, is_final=True)
    await cb.message.answer(t(lang, "update_ask_views",
                              current=fmt_int(ctx.submission.current_views)),
                            reply_markup=kb_cancel(lang))
    await cb.answer()
