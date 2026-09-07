"""🎲 Random sovg'a o'yinlari — shaffof (xesh bilan) tanlov."""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import get_settings
from ..constants import CANCEL_TEXTS, CB, ExpoStatus, Role, SubStatus
from ..db import repo
from ..i18n import t
from ..keyboards import kb_random_count, kb_rnd_preview
from ..services.random_draw import candidates_hash, pick_winners
from ..states import RandomFlow

log = logging.getLogger(__name__)

router = Router(name="random_draw")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

settings = get_settings()


async def _expo_for_draw(session):
    """Yakunlangan (oxirgi) yoki faol expo."""
    expos = await repo.list_expos(session)
    for e in expos:
        if e.status == ExpoStatus.FINISHED:
            return e
    for e in expos:
        if e.status == ExpoStatus.CLOSED:
            return e
    return next((e for e in expos if e.status == ExpoStatus.ACTIVE), None)


@router.callback_query(F.data == "rnd:start")
async def rnd_start(cb: CallbackQuery, state: FSMContext, session, role):
    if role not in Role.ADMIN_PANEL:
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    expo = await _expo_for_draw(session)
    if expo is None or not await repo.count_submissions(session, expo.id, SubStatus.APPROVED):
        return await cb.answer(t("uz", "rnd_none"), show_alert=True)
    await state.clear()
    await state.update_data(expo_id=expo.id)
    await state.set_state(RandomFlow.count)
    await cb.message.edit_text(t("uz", "rnd_choose_count"),
                               reply_markup=kb_random_count("uz"))
    await cb.answer()


@router.callback_query(F.data.startswith("rnd:n:"), RandomFlow.count)
async def rnd_count(cb: CallbackQuery, state: FSMContext):
    n = int(cb.data.split(":")[-1])
    await state.update_data(count=n)
    await state.set_state(RandomFlow.prize)
    await cb.message.edit_text(t("uz", "rnd_ask_prize"))
    await cb.answer()


@router.message(RandomFlow.prize, F.text & ~F.text.in_(CANCEL_TEXTS))
async def rnd_prize(message: Message, state: FSMContext, session):
    prize = message.text.strip()[:300]
    await state.update_data(prize=prize)

    data = await state.get_data()
    expo = await repo.get_expo(session, data["expo_id"])
    rows = await repo.eligible_random_candidates(session, expo)
    if not rows:
        await state.clear()
        return await message.answer(t("uz", "rnd_none"))
    ids = sorted(u.id for _, _, u in rows)
    await state.set_state(RandomFlow.preview)
    await message.answer(
        t("uz", "rnd_preview", expo=expo.title, prize=prize,
          count=data["count"], total=len(ids), hash=candidates_hash(ids)),
        reply_markup=kb_rnd_preview("uz"))


@router.callback_query(F.data == "rnd:go", RandomFlow.preview)
async def rnd_go(cb: CallbackQuery, state: FSMContext, session):
    data = await state.get_data()
    expo = await repo.get_expo(session, data["expo_id"])
    rows = await repo.eligible_random_candidates(session, expo)
    ids = sorted(u.id for _, _, u in rows)
    if not ids:
        await state.clear()
        return await cb.answer(t("uz", "rnd_none"), show_alert=True)

    h = candidates_hash(ids)
    winners = pick_winners(ids, data["count"])
    await repo.save_draw(session, expo.id, data["prize"], data["count"],
                         h, winners, cb.from_user.id)
    await repo.audit(session, cb.from_user.id, "random_draw",
                     {"expo_id": expo.id, "prize": data["prize"],
                      "candidates_hash": h, "candidates": ids,
                      "winners": winners})
    await state.clear()

    uid_map = {u.id: u for _, _, u in rows}
    winner_users = [uid_map[i] for i in winners]

    # g'oliblarga yakkaxon
    for u in winner_users:
        try:
            await cb.bot.send_message(
                u.tg_id, t(u.language or "uz", "rnd_winner_pm",
                           expo=expo.title, prize=data["prize"]))
        except Exception as e:
            log.warning("random pm xatosi: %s", e)

    # umumiy e'lon
    lines = "".join(
        t("uz", "rnd_line", i=i,
          name=u.full_name or "—",
          insta=f"@{u.instagram}" if u.instagram else "—")
        for i, u in enumerate(winner_users, start=1))
    announce = t("uz", "rnd_announce", expo=expo.title, prize=data["prize"],
                 lines=lines, hash=h)
    for chat in (settings.announce_chat_id, settings.review_group_id):
        if chat:
            try:
                await cb.bot.send_message(chat, announce)
            except Exception as e:
                log.warning("random announce xatosi %s: %s", chat, e)

    await cb.message.edit_text(t("uz", "rnd_done"))
    await cb.answer()
