"""Review huquqi: hay'at (review) guruhining HAR BIR a'zosi moderator hisoblanadi.

Bot guruhda admin bo'lgani uchun foydalanuvchining a'zoligini Telegram API
(`getChatMember`) orqali tekshiramiz — har bir hay'at a'zosini alohida
`/addadmin ... moderator` qilish shart emas. Guruhdan chiqib ketgan yoki
chiqarib yuborilgan odam avtomatik ravishda huquqdan mahrum bo'ladi.
"""
import time

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from ..config import get_settings
from ..constants import Role

# Anonim guruh admini nomidan keladigan update'lar shu rasmiy Telegram boti
# id'si bilan keladi (GroupAnonymousBot). Anonim yozish faqat adminlarga
# mumkin, shuning uchun uni shartsiz qabul qilamiz.
GROUP_ANONYMOUS_BOT_ID = 1087968824

# Faol a'zolik statuslari ("left"/"kicked" — a'zo emas)
_MEMBER_STATUSES = {"creator", "administrator", "member"}

# (chat_id, user_id) -> (ruxsat bormi, tekshirilgan vaqt monotonic)
_cache: dict[tuple[int, int], tuple[bool, float]] = {}
_TTL_SECONDS = 60.0


def is_member_status(status: str, is_member: bool | None = None) -> bool:
    """getChatMember statusi bo'yicha foydalanuvchi guruh a'zosimi?"""
    if status in _MEMBER_STATUSES:
        return True
    if status == "restricted":
        # restricted foydalanuvchi guruhda qolgan yoki chiqarib yuborilgan bo'lishi mumkin
        return bool(is_member)
    return False  # "left" / "kicked"


async def is_chat_member(bot: Bot, chat_id: int | None, user_id: int | None, *,
                         use_cache: bool = True) -> bool:
    """Foydalanuvchi hozir chat a'zosi ekanini tekshiradi (qisqa kesh bilan)."""
    if not chat_id or not user_id:
        return False
    if user_id == GROUP_ANONYMOUS_BOT_ID:
        return True

    key = (chat_id, user_id)
    now = time.monotonic()
    if use_cache:
        cached = _cache.get(key)
        if cached is not None and now - cached[1] < _TTL_SECONDS:
            return cached[0]

    try:
        member = await bot.get_chat_member(chat_id, user_id)
        allowed = is_member_status(member.status, getattr(member, "is_member", None))
    except TelegramBadRequest:
        # Foydalanuvchi bu guruhda hech qachon bo'lmagan → Telegram xato qaytaradi
        allowed = False
    except Exception:
        # API vaqtincha ishlamasa — eski kesh natijasini qaytaramiz, aks holda rad
        cached = _cache.get(key)
        if cached is not None:
            return cached[0]
        return False

    if use_cache:
        _cache[key] = (allowed, now)
    return allowed


async def can_review(bot: Bot, role: str | None, chat_id: int | None,
                     user_id: int | None) -> bool:
    """Arizani tasdiqlash/rad etish huquqi bormi?

    1) bazadagi moderator/admin/superadmin rollari (avvalgidek ishlaydi);
    2) bo'lmasa — foydalanuvchi review (hay'at) guruhining a'zosi bo'lsa,
       huquq beriladi.
    """
    if role in Role.REVIEWERS:
        return True
    settings = get_settings()
    if not settings.review_group_id or chat_id != settings.review_group_id:
        return False
    return await is_chat_member(bot, settings.review_group_id, user_id)
