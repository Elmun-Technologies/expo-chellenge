"""Barcha klaviaturalar (reply + inline)."""
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from .constants import CB
from .i18n import t


# ---------- reply ----------

def kb_cancel(lang: str):
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text=t(lang, "btn_cancel")))
    return b.as_markup(resize_keyboard=True)


def kb_contact(lang: str):
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text=t(lang, "btn_share_contact"), request_contact=True))
    b.row(KeyboardButton(text=t(lang, "btn_cancel")))
    return b.as_markup(resize_keyboard=True)


def kb_keep_link(lang: str, sub_id: int):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_keep_link"), callback_data=f"{CB.KEEPLINK}:{sub_id}")
    return b.as_markup()


def main_menu(lang: str, *, is_admin: bool, can_join: bool,
              can_send: bool, can_update: bool):
    b = ReplyKeyboardBuilder()
    if can_join:
        b.row(KeyboardButton(text=t(lang, "btn_join")))
    if can_send:
        b.row(KeyboardButton(text=t(lang, "btn_send_video")))
    if can_update:
        b.row(KeyboardButton(text=t(lang, "btn_update_views")))
    b.row(KeyboardButton(text=t(lang, "btn_my_rank")),
          KeyboardButton(text=t(lang, "btn_top")))
    b.row(KeyboardButton(text=t(lang, "btn_my_stats")),
          KeyboardButton(text=t(lang, "btn_rules")))
    if is_admin:
        b.row(KeyboardButton(text=t(lang, "btn_admin")))
    return b.as_markup(resize_keyboard=True)


# ---------- inline ----------

def kb_lang():
    b = InlineKeyboardBuilder()
    b.button(text="🇺🇿 O'zbek", callback_data=f"{CB.LANG}:uz")
    b.button(text="🇷🇺 Русский", callback_data=f"{CB.LANG}:ru")
    return b.as_markup()


def kb_agree(lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_agree"), callback_data=f"{CB.AGREE}:yes")
    b.button(text=t(lang, "btn_decline"), callback_data=f"{CB.AGREE}:no")
    return b.as_markup()


def kb_confirm(lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_confirm"), callback_data="confirm:yes")
    b.button(text=t(lang, "btn_cancel"), callback_data="confirm:no")
    return b.as_markup()


def kb_review(sub_id: int, lang: str = "uz"):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_approve"), callback_data=f"{CB.REVIEW}:{sub_id}:ok")
    b.button(text=t(lang, "btn_reject"), callback_data=f"{CB.REVIEW}:{sub_id}:rej")
    b.button(text=t(lang, "btn_changes"), callback_data=f"{CB.REVIEW}:{sub_id}:ch")
    b.adjust(3)
    return b.as_markup()


def kb_reasons(sub_id: int, mode: str, lang: str = "uz"):
    """mode: rej (rad) | ch (qayta ishlash)"""
    b = InlineKeyboardBuilder()
    for code in ("wrong_screen", "bad_link", "not_own", "edited", "other"):
        b.button(text=t(lang, f"rsn_{code}"),
                 callback_data=f"{CB.REASON}:{sub_id}:{mode}:{code}")
    b.adjust(2, 2, 1)
    return b.as_markup()


def kb_resubmit(lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_resubmit"), callback_data=f"{CB.RESUB}:go")
    return b.as_markup()


def kb_final_check(lang: str, expo_id: int):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_final_send"), callback_data=f"{CB.FINALCHK}:{expo_id}")
    return b.as_markup()


# ---------- admin ----------

def kb_admin_panel(lang: str, *, has_active: bool, has_draft: bool,
                   has_finished: bool, has_random: bool = False,
                   scheduled_count: int = 0):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "abtn_new_expo"), callback_data=f"{CB.ADMIN}:new")
    b.button(text=t(lang, "abtn_list"), callback_data=f"{CB.ADMIN}:list")
    if has_active:
        b.button(text=t(lang, "abtn_finish"), callback_data=f"{CB.ADMIN}:finish")
    if has_finished:
        b.button(text=t(lang, "abtn_winners"), callback_data=f"{CB.ADMIN}:winners")
    if has_random:
        b.button(text=t(lang, "abtn_random"), callback_data="rnd:start")
    b.button(text=t(lang, "abtn_broadcast"), callback_data=f"{CB.ADMIN}:bc")
    b.button(text=t(lang, "abtn_stats"), callback_data=f"{CB.ADMIN}:stats")
    b.button(text=t(lang, "abtn_export"), callback_data=f"{CB.ADMIN}:export")
    b.button(text=t(lang, "abtn_users"), callback_data=f"{CB.ADMIN}:users")
    if scheduled_count:
        b.button(text=t(lang, "abtn_scheduled", n=scheduled_count),
                 callback_data="bc:sched_list")
    b.adjust(2)
    return b.as_markup()


def kb_activate(expo_id: int, lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_activate"), callback_data=f"{CB.ADMIN}:act:{expo_id}")
    return b.as_markup()


def kb_finish_confirm(expo_id: int, lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_finish_yes"), callback_data=f"{CB.ADMIN}:finishyes:{expo_id}")
    b.button(text=t(lang, "btn_cancel"), callback_data=f"{CB.ADMIN}:menu")
    b.adjust(1)
    return b.as_markup()


def kb_winners_confirm(expo_id: int, lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_announce"), callback_data=f"{CB.ADMIN}:winx:{expo_id}")
    b.button(text=t(lang, "btn_cancel"), callback_data=f"{CB.ADMIN}:menu")
    b.adjust(1)
    return b.as_markup()


# ---------- random sovg'a ----------

def kb_random_count(lang: str):
    b = InlineKeyboardBuilder()
    for n in (1, 2, 3, 4, 5):
        b.button(text=str(n), callback_data=f"rnd:n:{n}")
    b.button(text=t(lang, "btn_cancel"), callback_data=f"{CB.ADMIN}:menu")
    b.adjust(5, 1)
    return b.as_markup()


def kb_rnd_preview(lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "rnd_btn_go"), callback_data="rnd:go")
    b.button(text=t(lang, "btn_cancel"), callback_data=f"{CB.ADMIN}:menu")
    b.adjust(2)
    return b.as_markup()


# ---------- rassilka preview + jadval ----------

def kb_bc_preview(lang: str):
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "bc_btn_now"), callback_data=f"{CB.BC}:now")
    b.button(text=t(lang, "bc_btn_sched"), callback_data=f"{CB.BC}:sched")
    b.button(text=t(lang, "btn_cancel"), callback_data=f"{CB.BC}:cancel")
    b.adjust(2, 1)
    return b.as_markup()


def kb_unsched(items, lang: str):
    b = InlineKeyboardBuilder()
    for bc in items:
        b.button(text=f"❌ #{bc.id}", callback_data=f"{CB.BC}:un:{bc.id}")
    b.button(text="⬅️ Orqaga" if lang == "uz" else "⬅️ Назад",
             callback_data=f"{CB.ADMIN}:menu")
    b.adjust(1)
    return b.as_markup()
