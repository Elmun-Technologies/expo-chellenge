"""Barcha handler routerlarini yig'uvchi."""
from aiogram import Router

from . import (admin, broadcast, group_stats, leaderboard, random_draw,
               review, start, stats, submission)

root_router = Router()
# Tartib muhim: guruh handlerlari → admin → oqimlar → start (eng oxirida)
root_router.include_router(review.router)
root_router.include_router(group_stats.router)
root_router.include_router(admin.router)
root_router.include_router(broadcast.router)
root_router.include_router(random_draw.router)
root_router.include_router(submission.router)
root_router.include_router(leaderboard.router)
root_router.include_router(stats.router)
root_router.include_router(start.router)
