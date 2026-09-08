"""Brauzer orqali ishlaydigan admin panel (Fly Dashboard emas — botning o'z sahifasi).

`ADMIN_PASSWORD` env/secret bo'sh bo'lsa, /admin/* butunlay 503 qaytaradi.
"""
from aiohttp import web
from aiogram import Bot

from .routes import setup as _setup


def setup_webadmin(app: web.Application, bot: Bot):
    _setup(app, bot)
