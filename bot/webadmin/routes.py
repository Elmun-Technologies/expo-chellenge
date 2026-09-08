"""Web-admin panel: dashboard, expo'lar, topshiriqlar, reyting, rassilka."""
import asyncio
import csv
import io
import logging
import math
import os

from aiogram import Bot
from aiohttp import ClientSession, web
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import func, select

from ..config import get_settings
from ..constants import BCTarget, SubStatus
from ..db import repo
from ..db.models import Participant, Submission, User, ViewReport
from ..db.session import SessionFactory
from ..handlers.broadcast import resolve_targets, _run_broadcast
from ..handlers.review import _notify_user, _user_of
from ..services.utils import tash_to_utc
from . import auth

log = logging.getLogger(__name__)
settings = get_settings()

_templates_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(_templates_dir),
    autoescape=select_autoescape(["html"]),
)


def render(template: str, **ctx) -> web.Response:
    html = jinja_env.get_template(template).render(**ctx)
    return web.Response(text=html, content_type="text/html")


async def _current_or_latest_expo(session):
    expo = await repo.get_active_expo(session)
    if expo is None:
        expos = await repo.list_expos(session, limit=1)
        expo = expos[0] if expos else None
    return expo


# ---------------- login/logout ----------------

async def login_form(request: web.Request) -> web.Response:
    return render("login.html", error=None)


async def login_submit(request: web.Request) -> web.Response:
    data = await request.post()
    if auth.check_password(str(data.get("password", ""))):
        resp = web.HTTPFound("/admin/dashboard")
        resp.set_cookie(auth.COOKIE_NAME, auth.make_session_cookie(),
                        max_age=auth.SESSION_TTL, httponly=True, samesite="Lax")
        return resp
    return render("login.html", error="Parol noto'g'ri")


async def logout(request: web.Request) -> web.Response:
    resp = web.HTTPFound("/admin/login")
    resp.del_cookie(auth.COOKIE_NAME)
    return resp


async def index(request: web.Request) -> web.Response:
    return web.HTTPFound("/admin/dashboard")


# ---------------- dashboard ----------------

async def dashboard(request: web.Request) -> web.Response:
    async with SessionFactory() as session:
        expo = await _current_or_latest_expo(session)
        if expo is None:
            return render("dashboard.html", active="dashboard", expo=None, stats=None, top5=[])
        users_count = await session.scalar(select(func.count(User.id)))
        participants_count = await session.scalar(
            select(func.count(Participant.id)).where(Participant.expo_id == expo.id))
        stats = {
            "users": users_count,
            "participants": participants_count,
            "pending": await repo.count_submissions(session, expo.id, SubStatus.PENDING),
            "approved": await repo.count_submissions(session, expo.id, SubStatus.APPROVED),
            "rejected": await repo.count_submissions(session, expo.id, SubStatus.REJECTED),
            "views": await repo.total_views(session, expo.id),
        }
        top5 = await repo.top_submissions(session, expo.id, limit=5)
        return render("dashboard.html", active="dashboard", expo=expo, stats=stats, top5=top5)


# ---------------- expos ----------------

async def expos_list(request: web.Request) -> web.Response:
    async with SessionFactory() as session:
        expos = await repo.list_expos(session, limit=50)
        return render("expos.html", active="expos", expos=expos, flash=None, flash_type=None)


async def expos_new(request: web.Request) -> web.Response:
    data = await request.post()
    prizes = []
    for i, line in enumerate((data.get("prizes_raw") or "").splitlines(), start=1):
        line = line.strip()
        if line:
            prizes.append({"place": i, "prize": line})
    try:
        start_at = tash_to_utc(_parse_local(data["start_at"]))
        end_at = tash_to_utc(_parse_local(data["end_at"]))
    except Exception:
        async with SessionFactory() as session:
            expos = await repo.list_expos(session, limit=50)
            return render("expos.html", active="expos", expos=expos,
                         flash="Sana formati noto'g'ri", flash_type="err")

    async with SessionFactory() as session:
        await repo.create_expo(
            session, title=data["title"], description=data.get("description", ""),
            rules_text=data.get("rules_text", ""), prizes=prizes,
            start_at=start_at, end_at=end_at, created_by=0)
        await repo.audit(session, 0, "expo_created_web", {"title": data["title"]})
        await session.commit()
    return web.HTTPFound("/admin/expos")


def _parse_local(value: str):
    from datetime import datetime
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")


async def expos_activate(request: web.Request) -> web.Response:
    expo_id = int(request.match_info["expo_id"])
    async with SessionFactory() as session:
        blocker = await repo.activate_expo(session, expo_id)
        if blocker is not None:
            expos = await repo.list_expos(session, limit=50)
            await session.commit()
            return render("expos.html", active="expos", expos=expos,
                         flash=f"Avval faol: {blocker.title}ni yakunlang", flash_type="err")
        await repo.audit(session, 0, "expo_activated_web", {"expo_id": expo_id})
        await session.commit()
    return web.HTTPFound("/admin/expos")


async def expos_finish(request: web.Request) -> web.Response:
    expo_id = int(request.match_info["expo_id"])
    async with SessionFactory() as session:
        await repo.finish_expo(session, expo_id)
        await repo.audit(session, 0, "expo_finished_web", {"expo_id": expo_id})
        await session.commit()
    return web.HTTPFound("/admin/expos")


# ---------------- submissions ----------------

PAGE_SIZE = 30


async def submissions_list(request: web.Request) -> web.Response:
    status = request.query.get("status") or None
    q = request.query.get("q") or None
    page = max(1, int(request.query.get("page", 1) or 1))
    async with SessionFactory() as session:
        expo = await _current_or_latest_expo(session)
        if expo is None:
            return render("submissions_list.html", active="submissions", expo=None,
                         rows=[], status=status, q=q, page=1, pages=1)
        total = await repo.count_search_submissions(session, expo.id, status, q)
        pages = max(1, math.ceil(total / PAGE_SIZE))
        rows = await repo.search_submissions(session, expo.id, status, q,
                                             limit=PAGE_SIZE, offset=(page - 1) * PAGE_SIZE)
        return render("submissions_list.html", active="submissions", expo=expo,
                     rows=rows, status=status, q=q, page=page, pages=pages)


async def submission_detail(request: web.Request, flash=None, flash_type=None) -> web.Response:
    sub_id = int(request.match_info["sub_id"])
    async with SessionFactory() as session:
        sub = await repo.get_submission(session, sub_id)
        if sub is None:
            raise web.HTTPNotFound(text="Topshiriq topilmadi")
        user = await _user_of(session, sub)
        report = await repo.pending_report_for(session, sub.id)
        history = await repo.user_reports(session, sub.id, limit=15)
        return render("submission_detail.html", active="submissions", sub=sub, user=user,
                     report=report, history=history, flash=flash, flash_type=flash_type)


async def submission_approve(request: web.Request) -> web.Response:
    sub_id = int(request.match_info["sub_id"])
    bot: Bot = request.app["bot"]
    async with SessionFactory() as session:
        sub = await repo.get_submission(session, sub_id)
        if sub is None:
            raise web.HTTPNotFound()
        report = await repo.pending_report_for(session, sub.id)
        if report is None:
            await session.commit()
            return await submission_detail(request, "Ko'rib chiqiladigan hisobot yo'q", "err")
        is_initial = sub.status == SubStatus.PENDING
        await repo.approve_submission_report(session, sub, report, 0)
        await repo.audit(session, 0, "review_approve_web",
                         {"sub_id": sub.id, "views": report.views_count})
        user = await _user_of(session, sub)
        await session.commit()
        if user:
            await _notify_user(bot, user,
                               "ntf_approved" if is_initial else "ntf_update_approved",
                               views=report.views_count)
    return web.HTTPFound(f"/admin/submissions/{sub_id}")


async def submission_reject(request: web.Request) -> web.Response:
    sub_id = int(request.match_info["sub_id"])
    data = await request.post()
    reason = str(data.get("reason", "")).strip() or "Sabab ko'rsatilmagan"
    bot: Bot = request.app["bot"]
    from ..handlers.review import apply_decision
    async with SessionFactory() as session:
        sub = await repo.get_submission(session, sub_id)
        if sub is None:
            raise web.HTTPNotFound()
        await apply_decision(bot=bot, session=session, sub=sub, mode="rej",
                             reason=reason, actor_id=0)
        await session.commit()
    return web.HTTPFound(f"/admin/submissions/{sub_id}")


# ---------------- leaderboard ----------------

async def leaderboard(request: web.Request) -> web.Response:
    async with SessionFactory() as session:
        expo = await _current_or_latest_expo(session)
        rows = await repo.top_submissions(session, expo.id) if expo else []
        return render("leaderboard.html", active="leaderboard", expo=expo, rows=rows)


# ---------------- broadcast ----------------

async def broadcast_form(request: web.Request, flash=None, flash_type=None) -> web.Response:
    async with SessionFactory() as session:
        expo = await _current_or_latest_expo(session)
        counts = {}
        for target in (BCTarget.ALL, BCTarget.PARTICIPANTS, BCTarget.APPROVED,
                      BCTarget.PENDING, BCTarget.TOP10):
            targets = await resolve_targets(session, target, expo, None)
            counts[target] = len(targets)
        return render("broadcast.html", active="broadcast", counts=counts,
                     flash=flash, flash_type=flash_type)


async def broadcast_send(request: web.Request) -> web.Response:
    data = await request.post()
    target = str(data.get("target", "all"))
    text = str(data.get("text", "")).strip()
    bot: Bot = request.app["bot"]
    if not text:
        return await broadcast_form(request, "Xabar matni bo'sh bo'lishi mumkin emas", "err")

    async with SessionFactory() as session:
        expo = await _current_or_latest_expo(session)
        targets = await resolve_targets(session, target, expo, None)
        if not targets:
            return await broadcast_form(request, "Bu auditoriyada hech kim yo'q", "err")
        payload = {"text": text}
        bc = await repo.create_broadcast(
            session, 0, target, payload,
            expo_id=expo.id if expo else None, total=len(targets))
        await repo.audit(session, 0, "broadcast_started_web",
                         {"bc_id": bc.id, "target": target, "total": len(targets)})
        bc_id = bc.id
        user_ids = [u.id for u in targets]
        await session.commit()

    asyncio.create_task(_run_broadcast(bot, bc_id, user_ids, payload))
    return await broadcast_form(request, f"🚀 Yuborilmoqda: {len(user_ids)} kishiga", "ok")


# ---------------- export ----------------

def _csv_response(headers, rows, filename) -> web.Response:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)
    return web.Response(
        body=buf.getvalue().encode("utf-8-sig"), content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})


async def export_csv(request: web.Request) -> web.Response:
    kind = request.match_info["kind"]
    async with SessionFactory() as session:
        expo = await _current_or_latest_expo(session)
        if expo is None:
            raise web.HTTPNotFound(text="Faol expo yo'q")
        if kind == "users":
            users = (await session.execute(
                select(User).join(Participant, Participant.user_id == User.id)
                .where(Participant.expo_id == expo.id))).scalars().all()
            return _csv_response(
                ["tg_id", "username", "full_name", "phone", "instagram", "language", "joined"],
                [(u.tg_id, u.username, u.full_name, u.phone, u.instagram, u.language,
                  u.created_at.strftime("%Y-%m-%d %H:%M")) for u in users],
                "users.csv")
        if kind == "leaderboard":
            subs = await repo.top_submissions(session, expo.id)
            return _csv_response(
                ["rank", "full_name", "instagram", "url", "views", "submitted_at"],
                [(i, u.full_name, u.instagram, s.video_url, s.current_views,
                  s.submitted_at.strftime("%Y-%m-%d %H:%M"))
                 for i, (s, p, u) in enumerate(subs, start=1)],
                "leaderboard.csv")
        if kind == "views":
            reports = (await session.execute(
                select(ViewReport).join(Submission, ViewReport.submission_id == Submission.id)
                .where(Submission.expo_id == expo.id)
                .order_by(ViewReport.id))).scalars().all()
            return _csv_response(
                ["sub_id", "views", "status", "is_final", "flags", "created_at"],
                [(r.submission_id, r.views_count, r.status, r.is_final,
                  ",".join(r.flags or []), r.created_at.strftime("%Y-%m-%d %H:%M"))
                 for r in reports],
                "view_history.csv")
    raise web.HTTPNotFound()


# ---------------- telegram file proxy (skrinshotlarni ko'rsatish) ----------------

async def file_proxy(request: web.Request) -> web.Response:
    file_id = request.match_info["file_id"]
    bot: Bot = request.app["bot"]
    try:
        tg_file = await bot.get_file(file_id)
        url = f"https://api.telegram.org/file/bot{settings.bot_token}/{tg_file.file_path}"
    except Exception:
        raise web.HTTPNotFound()
    async with ClientSession() as http:
        async with http.get(url) as resp:
            body = await resp.read()
            return web.Response(body=body, content_type=resp.content_type)


def setup(app: web.Application, bot: Bot):
    app["bot"] = bot
    app.middlewares.append(auth.auth_middleware)
    app.router.add_get("/admin", index)
    app.router.add_get("/admin/login", login_form)
    app.router.add_post("/admin/login", login_submit)
    app.router.add_post("/admin/logout", logout)
    app.router.add_get("/admin/dashboard", dashboard)
    app.router.add_get("/admin/expos", expos_list)
    app.router.add_post("/admin/expos/new", expos_new)
    app.router.add_post("/admin/expos/{expo_id}/activate", expos_activate)
    app.router.add_post("/admin/expos/{expo_id}/finish", expos_finish)
    app.router.add_get("/admin/submissions", submissions_list)
    app.router.add_get("/admin/submissions/{sub_id}", submission_detail)
    app.router.add_post("/admin/submissions/{sub_id}/approve", submission_approve)
    app.router.add_post("/admin/submissions/{sub_id}/reject", submission_reject)
    app.router.add_get("/admin/leaderboard", leaderboard)
    app.router.add_get("/admin/broadcast", broadcast_form)
    app.router.add_post("/admin/broadcast/send", broadcast_send)
    app.router.add_get("/admin/export/{kind}", export_csv)
    app.router.add_get("/admin/file/{file_id}", file_proxy)
