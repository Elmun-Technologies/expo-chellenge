"""DB ulanishi: engine + session factory (async)."""
import os

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings

_settings = get_settings()

# sqlite uchun katalog yaratamiz
if _settings.database_url.startswith("sqlite"):
    import re
    m = re.search(r"sqlite[^:]*:///(.*)", _settings.database_url)
    if m and m.group(1) != ":memory:":
        os.makedirs(os.path.dirname(m.group(1)) or ".", exist_ok=True)

# asyncpg `sslmode` query-parametrini libpq kabi tushunmaydi (ssl handshake
# reset bo'ladi) — Fly.io ichki (flycast) Postgres ulanishida SSL kerak
# emas, shuning uchun `sslmode=disable`ni asyncpg tushunadigan `ssl=False`
# connect_args'ga aylantiramiz.
_url = make_url(_settings.database_url)
_connect_args: dict = {}
if _url.get_backend_name() == "postgresql" and _url.query.get("sslmode") == "disable":
    _url = _url.difference_update_query(["sslmode"])
    _connect_args["ssl"] = False

engine = create_async_engine(_url, pool_pre_ping=True, connect_args=_connect_args)
SessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
