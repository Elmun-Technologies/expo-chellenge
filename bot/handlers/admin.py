"""Admin panel: Expo yaratish/boshqarish, yakunlash, g'oliblar, adminlar."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..config import get_settings
from ..constants import CANCEL_TEXTS, CB, ExpoStatus, Role
from ..db import repo
from ..db.models import Expo
from ..i18n import t
from ..keyboards import (kb_activate, kb_admin_panel, kb_cancel,
                         kb_finish_confirm, kb_winners_confirm)
from ..services.ranking import medal
from ..services.utils import fmt_dt, fmt_int, parse_date
from ..states import ExpoCreate

router = Router(name="admin")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

settings = get_settings()


def admin_only(data_role):
    return data_role in Role.ADMIN_PANEL


async def _open_panel(target: Message | CallbackQuery, session, lang, user_id):
    active = await repo.get_active_expo(session)
    expos = await repo.list_expos(session)
    has_draft = any(e.status == ExpoStatus.DRAFT for e in expos)
    has_finished = any(e.status == ExpoStatus.FINISHED for e in expos)
    kb = kb_admin_panel(lang, has_active=active is not None,
                        has_draft=has_draft,
                        has_finished=has_finished)
    text = t(lang, "admin_menu")
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


# ---------------- panel ----------------

@router.message(Command("admin"))
@router.message(F.text.in_({"⚙️ Admin panel", "⚙️ Админ панель"}))
async def cmd_admin(message: Message, session, db_user, role):
    if not admin_only(role):
        return await message.answer(t(db_user.language if db_user else "uz", "admin_denied"))
    lang = db_user.language if db_user else "uz"
    await _open_panel(message, session, lang, message.from_user.id)


@router.callback_query(F.data == f"{CB.ADMIN}:menu")
async def cb_admin_menu(cb: CallbackQuery, session, db_user, role, state: FSMContext):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    await state.clear()
    await _open_panel(cb, session, "uz", cb.from_user.id)
    await cb.answer()


# ---------------- Expo yaratish ----------------

@router.callback_query(F.data == f"{CB.ADMIN}:new")
async def cb_expo_new(cb: CallbackQuery, state: FSMContext, role):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    await state.set_state(ExpoCreate.title)
    await cb.message.answer(t("uz", "expo_ask_title"), reply_markup=kb_cancel("uz"))
    await cb.answer()


@router.message(ExpoCreate.title, F.text & ~F.text.in_(CANCEL_TEXTS))
async def expo_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip()[:200])
    await state.set_state(ExpoCreate.desc)
    await message.answer(t("uz", "expo_ask_desc"), reply_markup=kb_cancel("uz"))


@router.message(ExpoCreate.desc, F.text & ~F.text.in_(CANCEL_TEXTS))
async def expo_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(ExpoCreate.rules)
    await message.answer(t("uz", "expo_ask_rules"), reply_markup=kb_cancel("uz"))


@router.message(ExpoCreate.rules, F.text & ~F.text.in_(CANCEL_TEXTS))
async def expo_rules(message: Message, state: FSMContext):
    await state.update_data(rules=message.text.strip(), prizes=[])
    await state.set_state(ExpoCreate.prizes)
    b = InlineKeyboardBuilder()
    b.button(text=t("uz", "expo_prizes_done"), callback_data=CB.PRIZES_DONE)
    await message.answer(t("uz", "expo_ask_prizes"), reply_markup=b.as_markup())


@router.message(ExpoCreate.prizes, F.text & ~F.text.in_(CANCEL_TEXTS))
async def expo_prizes(message: Message, state: FSMContext):
    data = await state.get_data()
    prizes: list = data.get("prizes") or []
    raw = message.text.strip()
    for sep in ("—", "-", ":", "="):
        if sep in raw:
            left, right = raw.split(sep, 1)
            if left.strip().isdigit():
                prizes.append({"place": int(left.strip()), "prize": right.strip()})
                break
    else:
        prizes.append({"place": len(prizes) + 1, "prize": raw})
    await state.update_data(prizes=prizes)
    b = InlineKeyboardBuilder()
    b.button(text=t("uz", "expo_prizes_done"), callback_data=CB.PRIZES_DONE)
    await message.answer(f"➕ Qo'shildi: {raw}\n\nYana yozing yoki tugmani bosing:",
                         reply_markup=b.as_markup())


@router.callback_query(F.data == CB.PRIZES_DONE, ExpoCreate.prizes)
async def expo_prizes_done(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("prizes"):
        return await cb.answer("Kamida bitta sovg'a kerak!", show_alert=True)
    await state.set_state(ExpoCreate.start)
    await cb.message.answer(t("uz", "expo_ask_start"), reply_markup=kb_cancel("uz"))
    await cb.answer()


@router.message(ExpoCreate.start, F.text & ~F.text.in_(CANCEL_TEXTS))
async def expo_start(message: Message, state: FSMContext):
    dt = parse_date(message.text)
    if dt is None:
        return await message.answer(t("uz", "bad_date"))
    await state.update_data(start_at=dt.isoformat())
    await state.set_state(ExpoCreate.end)
    await message.answer(t("uz", "expo_ask_end"), reply_markup=kb_cancel("uz"))


@router.message(ExpoCreate.end, F.text & ~F.text.in_(CANCEL_TEXTS))
async def expo_end(message: Message, state: FSMContext):
    dt = parse_date(message.text)
    if dt is None:
        return await message.answer(t("uz", "bad_date"))
    data = await state.get_data()
    await state.update_data(end_at=dt.isoformat())
    prizes = "\n".join(f"{medal(p['place'])} {p['prize']}" for p in data["prizes"])
    b = InlineKeyboardBuilder()
    b.button(text=t("uz", "btn_save"), callback_data=f"{CB.ADMIN}:newsave")
    b.button(text=t("uz", "btn_cancel"), callback_data=f"{CB.ADMIN}:menu")
    b.adjust(1)
    await state.set_state(ExpoCreate.confirm)
    await message.answer(
        t("uz", "expo_summary", title=data["title"], desc=data["desc"],
          rules=data["rules"], prizes=prizes,
          start=data["start_at"][:16].replace("T", " "),
          end=data["end_at"][:16].replace("T", " ")),
        reply_markup=b.as_markup())


@router.callback_query(F.data == f"{CB.ADMIN}:newsave", ExpoCreate.confirm)
async def expo_save(cb: CallbackQuery, state: FSMContext, session):
    data = await state.get_data()
    from datetime import datetime
    expo = await repo.create_expo(
        session,
        title=data["title"], description=data["desc"], rules_text=data["rules"],
        prizes=data["prizes"],
        start_at=datetime.fromisoformat(data["start_at"]),
        end_at=datetime.fromisoformat(data["end_at"]),
        created_by=cb.from_user.id,
    )
    await repo.audit(session, cb.from_user.id, "expo_created", {"expo_id": expo.id})
    await state.clear()
    await cb.message.edit_text(t("uz", "expo_saved"),
                               reply_markup=kb_activate(expo.id, "uz"))
    await cb.answer()


# ---------------- faollashtirish ----------------

@router.callback_query(F.data.startswith(f"{CB.ADMIN}:act:"))
async def expo_activate(cb: CallbackQuery, session, role):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    expo_id = int(cb.data.split(":")[-1])
    blocker = await repo.activate_expo(session, expo_id)
    if blocker is not None:
        return await cb.answer(t("uz", "expo_other_active", title=blocker.title),
                               show_alert=True)
    expo = await repo.get_expo(session, expo_id)
    await repo.audit(session, cb.from_user.id, "expo_activated", {"expo_id": expo_id})
    await cb.message.edit_text(t("uz", "expo_activated", title=expo.title))
    await cb.answer()


# ---------------- ro'yxat ----------------

@router.callback_query(F.data == f"{CB.ADMIN}:list")
async def expo_list(cb: CallbackQuery, session, role):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    expos = await repo.list_expos(session)
    if not expos:
        return await cb.answer(t("uz", "list_empty"), show_alert=True)
    text = "📋 <b>Expo'lar:</b>\n\n"
    b = InlineKeyboardBuilder()
    for e in expos:
        text += t("uz", "expo_line", id=e.id, title=e.title, status=e.status,
                  start=fmt_dt(e.start_at), end=fmt_dt(e.end_at)) + "\n"
        if e.status == ExpoStatus.DRAFT:
            b.button(text=f"▶️ #{e.id} faollashtirish",
                     callback_data=f"{CB.ADMIN}:act:{e.id}")
        if e.status == ExpoStatus.ACTIVE:
            b.button(text=f"⏹ #{e.id} yakunlash",
                     callback_data=f"{CB.ADMIN}:finish:{e.id}")
        if e.status == ExpoStatus.FINISHED:
            b.button(text=f"🏆 #{e.id} g'oliblar",
                     callback_data=f"{CB.ADMIN}:winners:{e.id}")
    b.adjust(1)
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


# ---------------- yakunlash ----------------

@router.callback_query(F.data == f"{CB.ADMIN}:finish")
async def cb_finish_active(cb: CallbackQuery, session, role):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    expo = await repo.get_active_expo(session)
    if expo is None:
        return await cb.answer(t("uz", "no_finished"), show_alert=True)
    await cb.message.edit_text(t("uz", "finish_confirm", title=expo.title),
                               reply_markup=kb_finish_confirm(expo.id, "uz"))
    await cb.answer()


@router.callback_query(F.data.startswith(f"{CB.ADMIN}:finish:"))
async def cb_finish_id(cb: CallbackQuery, session, role):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    expo_id = int(cb.data.split(":")[-1])
    expo = await repo.get_expo(session, expo_id)
    await cb.message.edit_text(t("uz", "finish_confirm", title=expo.title),
                               reply_markup=kb_finish_confirm(expo_id, "uz"))
    await cb.answer()


@router.callback_query(F.data.startswith(f"{CB.ADMIN}:finishyes:"))
async def cb_finish_yes(cb: CallbackQuery, session, role):
    if not admin_only(role):
        return await cb.answer(t("uz", "admin_denied"), show_alert=True)
    expo_id = int(cb.data.split(":")[-1])
    expo = await repo.finish_expo(session, expo_id)
    await repo.audit(session, cb.from_user.id, "expo_finished", {"expo_id": expo_id})

    # TOP-10 ga final tekshiruv so'rovi
    from ..keyboards import kb_final_check
    top = await repo.top_submissions(session, expo_id, limit=10)
    n = 0
    for sub, p, u in top:
        lang = u.language or "uz"
        try:
            await cb.bot.send_message(
                u.tg_id,
                t(lang, "final_check_req", hours=settings.final_check_hours),
                reply_markup=kb_final_check(lang, expo_id))
            n += 1
        except Exception:
            pass
    await cb.message.edit_text(t("uz", "finished") + f"\n📨 Yuborildi: {n} ta")
    await cb.answer()


# ---------------- g'oliblar ----------------

@router.callback_query(F.data == f"{CB.ADMIN}:winners")
async def cb_winners_menu(cb: CallbackQuery, session, role):
    if role != Role.SUPERADMIN:
        return await cb.answer(t("uz", "need_super"), show_alert=True)
    expos = await repo.list_expos(session)
    finished = next((e for e in expos if e.status == ExpoStatus.FINISHED), None)
    if finished is None:
        return await cb.answer(t("uz", "no_finished"), show_alert=True)
    await _winners_preview(cb, session, finished)


@router.callback_query(F.data.startswith(f"{CB.ADMIN}:winners:"))
async def cb_winners_id(cb: CallbackQuery, session, role):
    if role != Role.SUPERADMIN:
        return await cb.answer(t("uz", "need_super"), show_alert=True)
    expo = await repo.get_expo(session, int(cb.data.split(":")[-1]))
    await _winners_preview(cb, session, expo)


async def _winners_preview(cb: CallbackQuery, session, expo: Expo):
    top = await repo.top_submissions(session, expo.id)
    if not top:
        return await cb.answer(t("uz", "winners_none"), show_alert=True)

    prizes = {p["place"]: p["prize"] for p in (expo.prizes or [])}
    places = sorted(prizes) or [1]
    lines = []
    for i, (sub, p, u) in enumerate(top[: max(places)], start=1):
        prize = prizes.get(i, "—")
        lines.append(t("uz", "winner_line", medal=medal(i),
                       name=u.full_name or "—",
                       insta=f"@{u.instagram}" if u.instagram else "—",
                       views=fmt_int(sub.current_views), prize=prize))
    await cb.message.edit_text(
        t("uz", "winners_preview", winners="".join(lines)),
        reply_markup=kb_winners_confirm(expo.id, "uz"))
    await cb.answer()


@router.callback_query(F.data.startswith(f"{CB.ADMIN}:winx:"))
async def cb_winners_announce(cb: CallbackQuery, session, role):
    if role != Role.SUPERADMIN:
        return await cb.answer(t("uz", "need_super"), show_alert=True)
    expo = await repo.get_expo(session, int(cb.data.split(":")[-1]))
    if expo.status != ExpoStatus.FINISHED:
        return await cb.answer("Allaqachon e'lon qilingan yoki yakunlanmagan.",
                               show_alert=True)

    top = await repo.top_submissions(session, expo.id)
    prizes = {p["place"]: p["prize"] for p in (expo.prizes or [])}
    places = sorted(prizes) or [1]

    lines = []
    winners = []
    for i, (sub, p, u) in enumerate(top[: max(places)], start=1):
        prize = prizes.get(i, "—")
        winners.append((i, prize, sub, p, u))
        lines.append(t("uz", "winner_line", medal=medal(i),
                       name=u.full_name or "—",
                       insta=f"@{u.instagram}" if u.instagram else "—",
                       views=fmt_int(sub.current_views), prize=prize))

    await repo.close_expo(session, expo.id)
    await repo.audit(session, cb.from_user.id, "winners_announced",
                     {"expo_id": expo.id,
                      "winners": [[w[0], w[4].id, w[1]] for w in winners]})

    # g'oliblarga yakkaxon tabrik
    for place, prize, sub, p, u in winners:
        lang = u.language or "uz"
        try:
            await cb.bot.send_message(
                u.tg_id, t(lang, "winner_pm", place=place, prize=prize))
        except Exception:
            pass

    # umumiy e'lon
    announce_text = t("uz", "winner_announce", expo=expo.title, winners="".join(lines))
    if settings.announce_chat_id:
        try:
            await cb.bot.send_message(settings.announce_chat_id, announce_text)
        except Exception:
            pass
    elif settings.review_group_id:
        await cb.bot.send_message(settings.review_group_id, announce_text)

    await cb.message.edit_text(t("uz", "winners_done"))
    await cb.answer()


# ---------------- adminlarni boshqarish ----------------

@router.message(Command("addadmin"))
async def add_admin_cmd(message: Message, session, role):
    if role != Role.SUPERADMIN:
        return
    parts = message.text.split()
    if len(parts) != 3 or parts[2] not in (Role.MODERATOR, Role.ADMIN, Role.SUPERADMIN):
        return await message.answer(
            "Format: /addadmin <tg_id> <moderator|admin|superadmin>")
    await repo.add_admin(session, int(parts[1]), parts[2])
    await repo.audit(session, message.from_user.id, "admin_added",
                     {"tg_id": int(parts[1]), "role": parts[2]})
    await message.answer(f"✅ {parts[1]} → {parts[2]}")


@router.message(Command("deladmin"))
async def del_admin_cmd(message: Message, session, role):
    if role != Role.SUPERADMIN:
        return
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("Format: /deladmin <tg_id>")
    await repo.remove_admin(session, int(parts[1]))
    await message.answer("✅ O'chirildi")


@router.callback_query(F.data == f"{CB.ADMIN}:users")
async def list_admins_cb(cb: CallbackQuery, session, role):
    if role != Role.SUPERADMIN:
        return await cb.answer(t("uz", "need_super"), show_alert=True)
    admins = await repo.list_admins(session)
    text = "👥 <b>Adminlar:</b>\n\n" + "\n".join(
        f"• {a.tg_id} — {a.role}" for a in admins) or "Bo'sh"
    text += "\n\n/addadmin <tg_id> <moderator|admin|superadmin>\n/deladmin <tg_id>"
    await cb.message.edit_text(text, reply_markup=None)
    await cb.answer()
