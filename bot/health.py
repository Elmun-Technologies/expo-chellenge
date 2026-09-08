"""Tiny health check server (fly.io healthcheck + preview uchun) + web-admin panel."""
from aiogram import Bot
from aiohttp import web


async def _health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def make_app(bot: Bot) -> web.Application:
    app = web.Application()
    app.router.add_get("/", _health)
    app.router.add_get("/health", _health)

    from .webadmin import setup_webadmin
    setup_webadmin(app, bot)

    return app
