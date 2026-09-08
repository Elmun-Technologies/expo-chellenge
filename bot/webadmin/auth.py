"""Web-admin panel uchun oddiy parol + imzolangan cookie autentifikatsiyasi.

Uchinchi tomon session kutubxonasi shart emas: cookie qiymati
"<amal_qilish_muddati>.<hmac_imzo>" ko'rinishida, imzo kaliti
ADMIN_PASSWORD + BOT_TOKEN'dan olinadi (ikkalasi ham faqat serverga ma'lum).
"""
import hashlib
import hmac
import time

from aiohttp import web

from ..config import get_settings

COOKIE_NAME = "expo_admin_session"
SESSION_TTL = 7 * 24 * 3600  # 7 kun

settings = get_settings()


def _signing_key() -> bytes:
    return hashlib.sha256(
        f"{settings.admin_password}:{settings.bot_token}".encode()).digest()


def make_session_cookie() -> str:
    expires_at = int(time.time()) + SESSION_TTL
    payload = str(expires_at)
    sig = hmac.new(_signing_key(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def is_valid_session_cookie(value: str | None) -> bool:
    if not value or "." not in value:
        return False
    payload, _, sig = value.partition(".")
    expected = hmac.new(_signing_key(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return False
    try:
        return int(payload) > time.time()
    except ValueError:
        return False


def check_password(candidate: str) -> bool:
    if not settings.admin_password:
        return False
    return hmac.compare_digest(candidate, settings.admin_password)


@web.middleware
async def auth_middleware(request: web.Request, handler):
    path = request.path
    if not path.startswith("/admin"):
        return await handler(request)
    if not settings.admin_password:
        return web.Response(
            status=503,
            text="Web-admin panel o'chirilgan: ADMIN_PASSWORD sozlanmagan.")
    if path in ("/admin/login", "/admin/login/"):
        return await handler(request)
    cookie = request.cookies.get(COOKIE_NAME)
    if not is_valid_session_cookie(cookie):
        raise web.HTTPFound("/admin/login")
    return await handler(request)
