"""Guruh ichida adminlar uchun tezkor buyruqlar: /stats, /top."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from ..db import repo
from ..i18n import t
from ..services.access import can_review
from ..services.utils import fmt_int
from .stats import _build_stats_text

router = Router(name="group_stats")
router.message.filter(F.chat.type.in_({"group", "supergroup"}))


@router.message(Command("stats"))
async def group_stats(message: Message, session, role):
    if not await can_review(message.bot, role, message.chat.id, message.from_user.id):
        return
    expo = await repo.get_active_expo(session)
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    await message.reply(await _build_stats_text(session, expo, "uz"))


@router.message(Command("top"))
async def group_top(message: Message, session, role):
    if not await can_review(message.bot, role, message.chat.id, message.from_user.id):
        return
    expo = await repo.get_active_expo(session)
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    if expo is None:
        return await message.reply(t("uz", "stats_no_expo"))

    rows = await repo.top_submissions(session, expo.id, limit=10)
    if not rows:
        return await message.reply(t("uz", "top_empty"))
    text = t("uz", "group_top_title", expo=expo.title) + "\n\n"
    for i, (sub, p, u) in enumerate(rows, start=1):
        text += f"{i}. <b>{u.full_name}</b> (@{u.instagram or '—'}) — 👁 {fmt_int(sub.current_views)}\n"
    await message.reply(text)
