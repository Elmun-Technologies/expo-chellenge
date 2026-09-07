"""Statistika va CSV eksport."""
import csv
import io
from datetime import timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy import func, select

from ..constants import Role, SubStatus
from ..db import repo
from ..db.models import Participant, Submission, User, ViewReport, utcnow
from ..i18n import t
from ..services.utils import fmt_int

router = Router(name="stats")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


async def _build_stats_text(session, expo, lang: str) -> str:
    users = (await session.execute(select(func.count(User.id)))).scalar_one()
    blocked = (await session.execute(
        select(func.count(User.id)).where(User.is_blocked == True))).scalar_one()  # noqa

    if expo is None:
        return t(lang, "stats_no_expo") + f"\n\n👥 {t(lang, 'tgt_all')}: {users}"

    participants = (await session.execute(
        select(func.count(Participant.id)).where(Participant.expo_id == expo.id))).scalar_one()
    submitted = await repo.count_submissions(session, expo.id)
    pending = await repo.count_submissions(session, expo.id, SubStatus.PENDING)
    approved = await repo.count_submissions(session, expo.id, SubStatus.APPROVED)
    rejected = await repo.count_submissions(session, expo.id, SubStatus.REJECTED)
    views = await repo.total_views(session, expo.id)
    avg = round(views / approved) if approved else 0

    text = t(lang, "stats_report", expo=expo.title, users=fmt_int(users),
             participants=fmt_int(participants), submitted=fmt_int(submitted),
             pending=fmt_int(pending), approved=fmt_int(approved),
             rejected=fmt_int(rejected), views=fmt_int(views),
             avg=fmt_int(avg), blocked=fmt_int(blocked))

    # kunlik ro'yxatdan o'tish (oxirgi 14 kun) — python'da guruhlaymiz
    since = utcnow() - timedelta(days=14)
    rows = (await session.execute(
        select(User.created_at).where(User.created_at >= since))).scalars().all()
    daily: dict[str, int] = {}
    for dt in rows:
        daily[dt.strftime("%d.%m")] = daily.get(dt.strftime("%d.%m"), 0) + 1
    if daily:
        maxc = max(daily.values())
        lines = "".join(
            f"{d}: {'█' * max(1, round(c / maxc * 10))} {c}\n"
            for d, c in sorted(daily.items(), key=lambda x: x[0][-2:] + x[0][:2])
        )
        text += t(lang, "stats_daily", daily=lines)
    return text


@router.message(Command("stats"))
@router.callback_query(F.data == "adm:stats")
async def show_stats(event, session, role, db_user):
    if role not in Role.ADMIN_PANEL:
        if isinstance(event, Message):
            await event.answer(t("uz", "admin_denied"))
        else:
            await event.answer(t("uz", "admin_denied"), show_alert=True)
        return
    lang = db_user.language if db_user else "uz"
    expo = await repo.get_active_expo(session)
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    text = await _build_stats_text(session, expo, lang)
    if isinstance(event, Message):
        await event.answer(text)
    else:
        await event.message.edit_text(text)
        await event.answer()


# ---------------- CSV eksport ----------------

def _to_csv(headers: list[str], rows: list[tuple]) -> BufferedInputFile:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)
    return BufferedInputFile(buf.getvalue().encode("utf-8-sig"),
                             filename="export.csv")


@router.message(Command("export"))
@router.callback_query(F.data == "adm:export")
async def export_csv(event, session, role, db_user):
    if role not in Role.ADMIN_PANEL:
        if isinstance(event, CallbackQuery):
            return await event.answer(t("uz", "admin_denied"), show_alert=True)
        return
    message = event.message if isinstance(event, CallbackQuery) else event
    lang = "uz"

    expo = await repo.get_active_expo(session)
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    if expo is None:
        return await message.answer(t(lang, "stats_no_expo"))

    users = (await session.execute(
        select(User).join(Participant, Participant.user_id == User.id)
        .where(Participant.expo_id == expo.id))).scalars().all()
    await message.answer_document(
        _to_csv(["tg_id", "username", "full_name", "phone", "instagram", "language",
                 "joined"],
                [(u.tg_id, u.username, u.full_name, u.phone, u.instagram, u.language,
                  u.created_at.strftime("%Y-%m-%d %H:%M")) for u in users]),
        caption=f"users.csv — {expo.title}")

    subs = await repo.top_submissions(session, expo.id)
    await message.answer_document(
        _to_csv(["rank", "full_name", "instagram", "url", "views", "submitted_at"],
                [(i, u.full_name, u.instagram, s.video_url, s.current_views,
                  s.submitted_at.strftime("%Y-%m-%d %H:%M"))
                 for i, (s, p, u) in enumerate(subs, start=1)]),
        caption="leaderboard.csv")

    reports = (await session.execute(
        select(ViewReport).join(Submission, ViewReport.submission_id == Submission.id)
        .where(Submission.expo_id == expo.id)
        .order_by(ViewReport.id))).scalars().all()
    await message.answer_document(
        _to_csv(["sub_id", "views", "status", "is_final", "flags", "created_at"],
                [(r.submission_id, r.views_count, r.status, r.is_final,
                  ",".join(r.flags or []), r.created_at.strftime("%Y-%m-%d %H:%M"))
                 for r in reports]),
        caption="view_history.csv")

    if isinstance(event, CallbackQuery):
        await event.answer(t(lang, "export_done"))
