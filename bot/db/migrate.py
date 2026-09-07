"""Alembic migratsiyalarni dastur ichidan yuritish (async → sync konvertatsiya bilan)."""
import asyncio
import logging
import os

log = logging.getLogger(__name__)


def _sync_url(url: str) -> str:
    return (url.replace("+aiosqlite", "")
               .replace("+asyncpg", "+psycopg2"))


def run_migrations_sync():
    from alembic import command
    from alembic.config import Config

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = Config(os.path.join(root, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(root, "alembic"))
    cfg.set_main_option("sqlalchemy.url",
                        _sync_url(os.environ.get("DATABASE_URL", "")) or
                        _sync_url_from_settings())
    command.upgrade(cfg, "head")
    log.info("Migratsiyalar OK")


def _sync_url_from_settings() -> str:
    from ..config import get_settings
    return _sync_url(get_settings().database_url)


async def run_migrations():
    await asyncio.to_thread(run_migrations_sync)
