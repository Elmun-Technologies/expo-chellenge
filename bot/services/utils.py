"""Formatlash va parslash utilitalari (aiogram'dan mustaqil — test uchun)."""
import re
from datetime import datetime

REELS_LINK = re.compile(
    r"^https?://(www\.)?instagram\.com/(reel|reels|p)/[A-Za-z0-9_-]{5,20}/?(\?.*)?$",
    re.IGNORECASE,
)
INSTA_HANDLE = re.compile(r"^[A-Za-z0-9._]{1,30}$")
PHONE = re.compile(r"^\+?\d{9,15}$")

DATE_FORMATS = ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d")


def is_reels_link(text: str) -> bool:
    return bool(REELS_LINK.match(text.strip()))


def normalize_insta(text: str) -> str | None:
    """'@User_Name' -> 'user_name' (validatsiya bilan)."""
    h = text.strip().lstrip("@").lower()
    return h if INSTA_HANDLE.match(h) else None


def is_valid_phone(text: str) -> bool:
    return bool(PHONE.match(text.strip()))


def parse_views(text: str) -> int | None:
    """'12 500' / '12,500' / '12500' -> 12500"""
    digits = re.sub(r"[^\d]", "", text)
    if not digits or len(digits) > 12:
        return None
    return int(digits)


def parse_date(text: str) -> datetime | None:
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%d.%m.%Y %H:%M") if dt else "—"


def mask_handle(handle: str | None) -> str:
    """Maxfiylik: '@alisher_nur' -> '@alis***'"""
    if not handle:
        return "—"
    h = handle.lstrip("@")
    visible = h[:4] if len(h) > 4 else h
    return f"@{visible}***"
