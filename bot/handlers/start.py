"""/start, ro'yxatdan o'tish FSM, asosiy menyu, challenge'ga qo'shilish."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import get_settings
from ..constants import CANCEL_TEXTS, CB, Role
from ..db import repo
from ..db.models import User
from ..i18n import t
from ..keyboards import (kb_agree, kb_contact, kb_lang, main_menu)
from ..services.context import build_ctx
from ..services.utils import is_valid_phone, normalize_insta
from ..states import Registration

router = Router(name="start")
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

settings = get_settings()


async def show_menu(message: Message, session, db_user: User, role: str | None):
    lang = db_user.language
    ctx = await build_ctx(session, db_user, role)
    await message.answer(
        t(lang, "menu_hint"),
        reply_markup=main_menu(
            lang,
            is_admin=ctx.is_admin,
            can_join=ctx.can_join and db_user.instagram is not None,
            can_send=ctx.can_send,
            can_update=ctx.can_update,
        ),
    )


async def begin_registration(message: Message, state: FSMContext,
                             session, tg_user, existing: User | None):
    # user yozuvini darhol yaratamiz (lang tanlashdan oldin ham)
    if existing is None:
        existing = await repo.create_user(session, tg_user.id, tg_user.username)
    await state.set_state(None)
    await message.answer(t(existing.language, "ask_lang"), reply_markup=kb_lang())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session, db_user, role):
    await state.clear()
    if db_user is None or not db_user.instagram:
        await begin_registration(message, state, session, message.from_user, db_user)
        return

    lang = db_user.language
    ctx = await build_ctx(session, db_user, role)
    if ctx.can_join:
        await start_join_flow(message, state, session, db_user, ctx)
        return
    await show_menu(message, session, db_user, role)


@router.callback_query(F.data.startswith(f"{CB.LANG}:"))
async def cb_set_lang(cb: CallbackQuery, state: FSMContext, session, db_user):
    lang = cb.data.split(":", 1)[1]
    if lang not in ("uz", "ru"):
        lang = "uz"
    user = db_user or await repo.create_user(session, cb.from_user.id, cb.from_user.username)
    user.language = lang
    if user.full_name is None or user.full_name == user.username or str(user.tg_id) == user.full_name:
        user.full_name = None
    await state.update_data(lang=lang)
    await cb.message.edit_text(t(lang, "ask_name"))
    await state.set_state(Registration.name)
    await cb.answer()


@router.message(Registration.name, F.text & ~F.text.in_(CANCEL_TEXTS))
async def reg_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3 or len(name) > 100:
        return await message.answer(t("uz", "err_generic"))
    await state.update_data(full_name=name)
    lang = (await state.get_data()).get("lang", "uz")
    await state.set_state(Registration.phone)
    await message.answer(t(lang, "ask_phone"), reply_markup=kb_contact(lang))


@router.message(Registration.phone, F.contact | F.text)
async def reg_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    phone = None
    if message.contact:
        phone = message.contact.phone_number
    elif message.text and is_valid_phone(message.text):
        phone = message.text.strip()
    if not phone:
        return await message.answer(t(lang, "invalid_phone"))
    await state.update_data(phone=phone)
    await state.set_state(Registration.instagram)
    await message.answer(t(lang, "ask_insta"))


@router.message(Registration.instagram, F.text & ~F.text.in_(CANCEL_TEXTS))
async def reg_insta(message: Message, state: FSMContext, session, db_user, role):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    insta = normalize_insta(message.text)
    if not insta:
        return await message.answer(t(lang, "invalid_insta"))

    user = db_user or await repo.create_user(session, message.from_user.id,
                                             message.from_user.username)
    user.language = lang
    user.full_name = data.get("full_name")
    user.phone = data.get("phone")
    user.instagram = insta

    ctx = await build_ctx(session, user, role)
    if ctx.can_join:
        await start_join_flow(message, state, session, user, ctx)
        return
    await state.clear()
    await message.answer(t(lang, "profile_done_no_expo"))
    await show_menu(message, session, user, role)


async def start_join_flow(message: Message, state: FSMContext, session,
                          db_user: User, ctx):
    """Qoidalarni ko'rsatib, roziligini olamiz."""
    lang = db_user.language
    if not ctx.expo:
        return await message.answer(t(lang, "no_active_expo"))
    if not db_user.instagram:
        return  # profil to'liq emas — avval ro'yxatdan o'tsin
    await state.set_state(Registration.agree)
    await state.update_data(expo_id=ctx.expo.id, lang=lang)
    await message.answer(
        t(lang, "rules_title", rules=ctx.expo.rules_text or "—"),
        reply_markup=kb_agree(lang),
    )


@router.callback_query(F.data == f"{CB.AGREE}:yes", Registration.agree)
async def cb_agree_yes(cb: CallbackQuery, state: FSMContext, session, db_user, role):
    data = await state.get_data()
    expo = await repo.get_expo(session, data.get("expo_id"))
    lang = (db_user.language if db_user else data.get("lang", "uz"))
    await state.clear()
    if expo is None:
        return await cb.message.edit_text(t(lang, "no_active_expo"))
    await repo.ensure_participant(session, db_user.id, expo.id)
    await repo.audit(session, cb.from_user.id, "participant_joined", {"expo_id": expo.id})
    await cb.message.edit_text(t(lang, "reg_done", name=db_user.full_name))
    await cb.answer()
    await show_menu(cb.message, session, db_user, role)


@router.callback_query(F.data == f"{CB.AGREE}:no", Registration.agree)
async def cb_agree_no(cb: CallbackQuery, state: FSMContext, db_user):
    await state.clear()
    lang = db_user.language if db_user else "uz"
    await cb.message.edit_text(t(lang, "declined"))
    await cb.answer()


# Challenge'ga qo'shilish tugmasi (profil to'liq, hali qo'shilmagan)
@router.message(F.text.in_({"🎯 Challenge'ga qo'shilish", "🎯 Участвовать в челлендже"}))
@router.message(Command("join"))
async def cmd_join(message: Message, state: FSMContext, session, db_user, role):
    if db_user is None or not db_user.instagram:
        return await begin_registration(message, state, session, message.from_user, db_user)
    ctx = await build_ctx(session, db_user, role)
    if not ctx.can_join:
        return await message.answer(t(db_user.language, "no_active_expo"))
    await start_join_flow(message, state, session, db_user, ctx)


# Bekor qilish — umumiy
@router.message(F.text.in_(CANCEL_TEXTS), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext, session, db_user, role):
    current = await state.get_state()
    if current:
        await state.clear()
        lang = db_user.language if db_user else "uz"
        await message.answer(t(lang, "cancelled"))
        if db_user:
            await show_menu(message, session, db_user, role)
