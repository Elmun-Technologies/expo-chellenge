"""Middleware: har bir update uchun DB sessiya + user + lang + role."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from .config import get_settings
from .db import repo
from .db.session import SessionFactory
from .db.models import utcnow

settings = get_settings()


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]):
        async with SessionFactory() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise


class UserContextMiddleware(BaseMiddleware):
    """data ga db_user / lang / role qo'shadi (private va group uchun bir xil)."""

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]):
        from_user = data.get("event_from_user")
        session = data.get("session")
        data["db_user"] = None
        data["role"] = None
        data["lang"] = settings.default_lang

        if from_user is not None and session is not None:
            user = await repo.get_user_by_tg(session, from_user.id)
            if user is not None:
                if isinstance(event, Message):  # faqat real harakatda touch
                    user.last_active_at = utcnow()
                    if user.username != from_user.username:
                        user.username = from_user.username
                data["db_user"] = user
                data["lang"] = user.language or settings.default_lang

            role = await repo.get_role(session, from_user.id)
            if from_user.id in settings.superadmin_ids:
                role = "superadmin"
            data["role"] = role

        return await handler(event, data)
