"""Tiny health check server (fly.io healthcheck + preview uchun)."""
from aiohttp import web


async def _health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def make_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", _health)
    app.router.add_get("/health", _health)
    return app
