"""Barcha handler routerlarini yig'uvchi."""
from aiogram import Router

from . import admin, broadcast, leaderboard, review, start, submission, stats

root_router = Router()
# Tartib muhim: guruh review → admin → oqimlar → start (eng oxirida)
root_router.include_router(review.router)
root_router.include_router(admin.router)
root_router.include_router(broadcast.router)
root_router.include_router(submission.router)
root_router.include_router(leaderboard.router)
root_router.include_router(stats.router)
root_router.include_router(start.router)
