"""DB ulanishi: engine + session factory (async)."""
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings

_settings = get_settings()

# sqlite uchun katalog yaratamiz
if _settings.database_url.startswith("sqlite"):
    import re
    m = re.search(r"sqlite[^:]*:///(.*)", _settings.database_url)
    if m and m.group(1) != ":memory:":
        os.makedirs(os.path.dirname(m.group(1)) or ".", exist_ok=True)

engine = create_async_engine(_settings.database_url, pool_pre_ping=True)
SessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
