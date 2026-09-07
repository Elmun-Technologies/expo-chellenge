"""Entry point: `python -m bot.main`."""
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from .config import get_settings
from .db import repo
from .db.session import SessionFactory
from .handlers import root_router
from .health import make_app
from .middlewares import DbSessionMiddleware, UserContextMiddleware

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("bot.main")

settings = get_settings()


async def on_startup(bot: Bot):
    # superadminlarni bazada ro'yxatga yozamiz (har startupda, idempotent)
    if settings.superadmin_ids:
        async with SessionFactory() as session:
            await repo.seed_superadmins(session, settings.superadmin_ids)
            await session.commit()
    me = await bot.get_me()
    log.info("Bot ishga tushdi: @%s", me.username)


async def run_health_server():
    app = make_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.web_port)
    await site.start()
    log.info("Health server: 0.0.0.0:%d", settings.web_port)


async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN env o'zgaruvchisi topilmadi!")

    if settings.auto_migrate:
        try:
            from .db.migrate import run_migrations
            await run_migrations()
        except Exception as e:
            log.warning("Alembic migratsiya ishlamadi (%s) — create_all bilan davom", e)
            from .db.models import Base
            from .db.session import engine
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            log.info("create_all OK")

    bot = Bot(token=settings.bot_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(DbSessionMiddleware())
    dp.message.middleware(UserContextMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(UserContextMiddleware())

    dp.include_router(root_router)

    await run_health_server()
    await on_startup(bot)

    # jadvaldagi rassilkalar yonish-fon jarayoni
    from .handlers.broadcast import broadcast_scheduler
    asyncio.create_task(broadcast_scheduler(bot))

    log.info("Polling boshlanyapti...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("To'xtatildi")
