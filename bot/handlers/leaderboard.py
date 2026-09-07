"""Reyting, mening o'rningim, mening statistikam, qoidalar."""
from aiogram import F, Router
from aiogram.types import Message

from ..constants import ExpoStatus
from ..db import repo
from ..i18n import t
from ..services.context import build_ctx
from ..services.ranking import find_rank, medal
from ..services.utils import fmt_int, mask_handle

router = Router(name="leaderboard")
router.message.filter(F.chat.type == "private")

BTN_TOP = {"🏆 Top-10"}
BTN_RANK = {"📊 Mening o'rning", "📊 Моё место"}
BTN_STATS = {"📈 Mening statistikam", "📈 Моя статистика"}
BTN_RULES = {"ℹ️ Qoidalar", "ℹ️ Правила"}


@router.message(F.text.in_(BTN_TOP))
async def show_top(message: Message, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    if ctx.expo is None:
        return await message.answer(t(lang, "no_active_expo"))

    rows = await repo.top_submissions(session, ctx.expo.id, limit=10)
    if not rows:
        return await message.answer(t(lang, "top_empty"))

    text = t(lang, "top_title", expo=ctx.expo.title) + "\n\n"
    for i, (sub, p, u) in enumerate(rows, start=1):
        text += t(lang, "top_line", medal=medal(i), name=u.full_name or "—",
                  insta=f"@{u.instagram}" if u.instagram else "—",
                  views=fmt_int(sub.current_views))
    if ctx.expo.status in (ExpoStatus.FINISHED, ExpoStatus.CLOSED):
        text += t(lang, "top_frozen")
    await message.answer(text)


@router.message(F.text.in_(BTN_RANK))
async def show_rank(message: Message, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    sub = ctx.submission
    if ctx.expo is None:
        return await message.answer(t(lang, "no_active_expo"))
    if sub is None or sub.status != "approved":
        return await message.answer(t(lang, "no_rank"))

    rows = await repo.top_submissions(session, ctx.expo.id)
    rank_info = find_rank(rows, sub.id, views_key=lambda r: r[0].current_views,
                          id_key=lambda r: r[0].id)
    if rank_info is None:
        return await message.answer(t(lang, "no_rank"))
    rank, total, idx = rank_info

    neighbors_txt = ""
    if idx > 0:
        _, _, above_u = rows[idx - 1]
        above_v = rows[idx - 1][0].current_views
        neighbors_txt += t(lang, "rank_above", r=rank - 1,
                           name=mask_handle(above_u.instagram),
                           views=fmt_int(above_v),
                           diff=fmt_int(above_v - sub.current_views))
    neighbors_txt += t(lang, "rank_you", r=rank, views=fmt_int(sub.current_views))
    if idx + 1 < len(rows):
        _, _, below_u = rows[idx + 1]
        below_v = rows[idx + 1][0].current_views
        neighbors_txt += t(lang, "rank_below", r=rank + 1,
                           name=mask_handle(below_u.instagram),
                           views=fmt_int(below_v),
                           diff=fmt_int(sub.current_views - below_v))
    else:
        neighbors_txt += t(lang, "rank_last")

    await message.answer(t(lang, "rank_block", rank=rank, total=total,
                           views=fmt_int(sub.current_views),
                           neighbors=neighbors_txt))


@router.message(F.text.in_(BTN_STATS))
async def show_my_stats(message: Message, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    sub = ctx.submission
    if sub is None:
        return await message.answer(t(lang, "my_stats_empty"))
    reports = await repo.user_reports(session, sub.id)
    if not reports:
        return await message.answer(t(lang, "my_stats_empty"))
    lines = "".join(
        t(lang, "my_stats_line", date=fmt_dt(r.created_at), views=fmt_int(r.views_count))
        for r in reversed(reports)
    )
    await message.answer(t(lang, "my_stats", lines=lines))


@router.message(F.text.in_(BTN_RULES))
async def show_rules(message: Message, session, db_user, role):
    lang = db_user.language if db_user else "uz"
    ctx = await build_ctx(session, db_user, role)
    if ctx.expo is None:
        return await message.answer(t(lang, "no_active_expo"))
    await message.answer(f"📜 <b>{ctx.expo.title}</b>\n\n{ctx.expo.rules_text}")
