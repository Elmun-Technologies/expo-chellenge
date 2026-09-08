"""Barcha DB so'rovlar — bitta joyda (handlar faqat shularni chaqiradi)."""
from datetime import datetime
from typing import Iterable

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import ExpoStatus, Role, SubStatus, ReportStatus
from .models import (Admin, AuditLog, Broadcast, BroadcastLog, Expo,
                     Participant, RandomDraw, Submission, User, ViewReport,
                     utcnow)


# ---------------- users ----------------

async def get_user_by_tg(session: AsyncSession, tg_id: int) -> User | None:
    return (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    return (await session.execute(
        select(User).where(func.lower(User.username) == username.lower().lstrip("@"))
    )).scalar_one_or_none()


async def create_user(session: AsyncSession, tg_id: int, username: str | None) -> User:
    user = User(tg_id=tg_id, username=username,
                full_name=username or str(tg_id))
    session.add(user)
    await session.flush()
    return user


async def mark_blocked(session: AsyncSession, user_id: int, blocked: bool = True):
    await session.execute(update(User).where(User.id == user_id).values(is_blocked=blocked))


# ---------------- admins ----------------

async def get_role(session: AsyncSession, tg_id: int) -> str | None:
    role = (await session.execute(
        select(Admin.role).where(Admin.tg_id == tg_id))).scalar_one_or_none()
    return role


async def add_admin(session: AsyncSession, tg_id: int, role: str) -> Admin:
    existing = (await session.execute(select(Admin).where(Admin.tg_id == tg_id))).scalar_one_or_none()
    if existing:
        existing.role = role
        return existing
    a = Admin(tg_id=tg_id, role=role)
    session.add(a)
    await session.flush()
    return a


async def remove_admin(session: AsyncSession, tg_id: int):
    await session.execute(delete(Admin).where(Admin.tg_id == tg_id))


async def list_admins(session: AsyncSession) -> list[Admin]:
    return list((await session.execute(select(Admin).order_by(Admin.role))).scalars())


async def seed_superadmins(session: AsyncSession, tg_ids: Iterable[int]):
    for tg in tg_ids:
        await add_admin(session, tg, Role.SUPERADMIN)


# ---------------- expo ----------------

async def create_expo(session: AsyncSession, *, title, description, rules_text,
                      prizes, start_at, end_at, created_by) -> Expo:
    expo = Expo(title=title, description=description, rules_text=rules_text,
                prizes=prizes, start_at=start_at, end_at=end_at,
                status=ExpoStatus.DRAFT, created_by=created_by)
    session.add(expo)
    await session.flush()
    return expo


async def get_active_expo(session: AsyncSession) -> Expo | None:
    return (await session.execute(
        select(Expo).where(Expo.status == ExpoStatus.ACTIVE)
        .order_by(Expo.id.desc()))).scalar_one_or_none()


async def get_expo(session: AsyncSession, expo_id: int) -> Expo | None:
    return await session.get(Expo, expo_id)


async def list_expos(session: AsyncSession, limit: int = 15) -> list[Expo]:
    return list((await session.execute(
        select(Expo).order_by(Expo.id.desc()).limit(limit))).scalars())


async def activate_expo(session: AsyncSession, expo_id: int) -> Expo | None:
    """Ketma-ketlik qoidasi: boshqa faol expo bo'lsa — uni qaytarib beramiz (xato)."""
    other = await get_active_expo(session)
    if other and other.id != expo_id:
        return other  # chaqiruvchi xabarni ko'rsatadi
    expo = await session.get(Expo, expo_id)
    expo.status = ExpoStatus.ACTIVE
    await session.flush()
    return None


async def finish_expo(session: AsyncSession, expo_id: int) -> Expo | None:
    expo = await session.get(Expo, expo_id)
    expo.status = ExpoStatus.FINISHED
    expo.finished_at = utcnow()
    await session.flush()
    return expo


async def close_expo(session: AsyncSession, expo_id: int) -> Expo | None:
    expo = await session.get(Expo, expo_id)
    expo.status = ExpoStatus.CLOSED
    await session.flush()
    return expo


# ---------------- participants ----------------

async def ensure_participant(session: AsyncSession, user_id: int, expo_id: int) -> Participant:
    p = (await session.execute(select(Participant).where(
        Participant.user_id == user_id, Participant.expo_id == expo_id))).scalar_one_or_none()
    if p is None:
        p = Participant(user_id=user_id, expo_id=expo_id)
        session.add(p)
        await session.flush()
    return p


async def get_participant(session: AsyncSession, user_id: int, expo_id: int) -> Participant | None:
    return (await session.execute(select(Participant).where(
        Participant.user_id == user_id, Participant.expo_id == expo_id))).scalar_one_or_none()


# ---------------- submissions ----------------

async def get_submission(session: AsyncSession, sub_id: int) -> Submission | None:
    return (await session.execute(
        select(Submission).where(Submission.id == sub_id))).scalar_one_or_none()


async def get_submission_for_participant(session: AsyncSession, participant_id: int) -> Submission | None:
    return (await session.execute(
        select(Submission).where(Submission.participant_id == participant_id)
        .order_by(Submission.id.desc()))).scalars().first()


async def url_taken(session: AsyncSession, expo_id: int, video_url: str,
                    exclude_submission_id: int | None = None) -> bool:
    q = select(func.count(Submission.id)).where(
        Submission.expo_id == expo_id, Submission.video_url == video_url)
    if exclude_submission_id:
        q = q.where(Submission.id != exclude_submission_id)
    return (await session.execute(q)).scalar_one() > 0


async def save_submission(session: AsyncSession, participant: Participant,
                          expo_id: int, video_url: str) -> Submission:
    """Yangi yoki mavjud (rejected/changes) submission ni pending holatga qaytaradi."""
    sub = await get_submission_for_participant(session, participant.id)
    if sub is None:
        sub = Submission(participant_id=participant.id, expo_id=expo_id,
                         video_url=video_url, status=SubStatus.PENDING)
        session.add(sub)
    else:
        sub.video_url = video_url
        sub.status = SubStatus.PENDING
        sub.reject_reason = None
        sub.submitted_at = utcnow()
    await session.flush()
    return sub


async def approve_submission_report(session: AsyncSession, sub: Submission,
                                    report: ViewReport, mod_tg_id: int):
    sub.status = SubStatus.APPROVED
    sub.current_views = report.views_count
    sub.reviewed_by = mod_tg_id
    sub.reviewed_at = utcnow()
    sub.last_approved_at = utcnow()
    report.status = ReportStatus.APPROVED
    report.reviewed_by = mod_tg_id
    report.reviewed_at = utcnow()
    await session.flush()


async def pending_report_for(session: AsyncSession, submission_id: int) -> ViewReport | None:
    return (await session.execute(
        select(ViewReport).where(ViewReport.submission_id == submission_id,
                                 ViewReport.status == ReportStatus.PENDING)
        .order_by(ViewReport.id.desc()))).scalars().first()


async def last_approved_report(session: AsyncSession, submission_id: int) -> ViewReport | None:
    return (await session.execute(
        select(ViewReport).where(ViewReport.submission_id == submission_id,
                                 ViewReport.status == ReportStatus.APPROVED)
        .order_by(ViewReport.id.desc()))).scalars().first()


async def user_reports(session: AsyncSession, submission_id: int, limit: int = 10) -> list[ViewReport]:
    return list((await session.execute(
        select(ViewReport).where(ViewReport.submission_id == submission_id,
                                 ViewReport.status == ReportStatus.APPROVED)
        .order_by(ViewReport.id.desc()).limit(limit))).scalars())


async def top_submissions(session: AsyncSession, expo_id: int,
                          limit: int | None = None) -> list[tuple[Submission, Participant, User]]:
    """Tasdiqlangan submissionlar prosmotr bo'yicha: (sub, participant, user)."""
    q = (select(Submission, Participant, User)
         .join(Participant, Submission.participant_id == Participant.id)
         .join(User, Participant.user_id == User.id)
         .where(Submission.expo_id == expo_id,
                Submission.status == SubStatus.APPROVED)
         .order_by(Submission.current_views.desc(), Submission.submitted_at.asc()))
    if limit:
        q = q.limit(limit)
    return list((await session.execute(q)).all())


async def count_submissions(session: AsyncSession, expo_id: int, status: str | None = None) -> int:
    q = select(func.count(Submission.id)).where(Submission.expo_id == expo_id)
    if status:
        q = q.where(Submission.status == status)
    return (await session.execute(q)).scalar_one()


def _submissions_search_query(expo_id: int, status: str | None, q: str | None):
    query = (select(Submission, Participant, User)
             .join(Participant, Submission.participant_id == Participant.id)
             .join(User, Participant.user_id == User.id)
             .where(Submission.expo_id == expo_id))
    if status:
        query = query.where(Submission.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.where(
            User.full_name.ilike(like) | User.instagram.ilike(like) |
            User.phone.ilike(like) | Submission.video_url.ilike(like))
    return query


async def search_submissions(session: AsyncSession, expo_id: int, status: str | None = None,
                              q: str | None = None, limit: int = 50,
                              offset: int = 0) -> list[tuple[Submission, Participant, User]]:
    query = (_submissions_search_query(expo_id, status, q)
             .order_by(Submission.submitted_at.desc()).limit(limit).offset(offset))
    return list((await session.execute(query)).all())


async def count_search_submissions(session: AsyncSession, expo_id: int, status: str | None = None,
                                    q: str | None = None) -> int:
    query = _submissions_search_query(expo_id, status, q).with_only_columns(
        func.count(Submission.id))
    return (await session.execute(query)).scalar_one()


async def total_views(session: AsyncSession, expo_id: int) -> int:
    return (await session.execute(
        select(func.coalesce(func.sum(Submission.current_views), 0))
        .where(Submission.expo_id == expo_id,
               Submission.status == SubStatus.APPROVED))).scalar_one()


# ---------------- broadcast ----------------

async def create_broadcast(session: AsyncSession, admin_tg_id: int, target_type: str,
                           payload: dict, expo_id=None, single_user_id=None, total=0,
                           scheduled_at=None) -> Broadcast:
    bc = Broadcast(admin_tg_id=admin_tg_id, target_type=target_type, payload=payload,
                   expo_id=expo_id, single_user_id=single_user_id, total=total,
                   scheduled_at=scheduled_at,
                   status="scheduled" if scheduled_at else "sending")
    session.add(bc)
    await session.flush()
    return bc


async def due_scheduled_broadcasts(session: AsyncSession, now: datetime) -> list[Broadcast]:
    return list((await session.execute(
        select(Broadcast).where(Broadcast.status == "scheduled",
                                Broadcast.scheduled_at <= now)
        .order_by(Broadcast.id))).scalars())


async def list_scheduled_broadcasts(session: AsyncSession) -> list[Broadcast]:
    return list((await session.execute(
        select(Broadcast).where(Broadcast.status == "scheduled")
        .order_by(Broadcast.scheduled_at))).scalars())


async def count_scheduled_broadcasts(session: AsyncSession) -> int:
    return (await session.execute(
        select(func.count(Broadcast.id))
        .where(Broadcast.status == "scheduled"))).scalar_one()


async def cancel_broadcast(session: AsyncSession, broadcast_id: int) -> bool:
    bc = await session.get(Broadcast, broadcast_id)
    if bc is None or bc.status != "scheduled":
        return False
    bc.status = "cancelled"
    await session.flush()
    return True


async def claim_broadcast(session: AsyncSession, broadcast_id: int) -> Broadcast | None:
    """Scheduler uchun: juft yuborilishni oldini olish."""
    bc = await session.get(Broadcast, broadcast_id)
    if bc is None or bc.status != "scheduled":
        return None
    bc.status = "sending"
    await session.flush()
    return bc


async def add_broadcast_log(session: AsyncSession, broadcast_id: int, user_id: int,
                            status: str, error: str | None = None):
    session.add(BroadcastLog(broadcast_id=broadcast_id, user_id=user_id,
                             status=status, error=error))


async def finish_broadcast(session: AsyncSession, broadcast_id: int,
                           sent: int, failed: int, blocked: int):
    bc = await session.get(Broadcast, broadcast_id)
    bc.status = "done"
    bc.sent_count = sent
    bc.failed_count = failed
    bc.blocked_count = blocked
    bc.finished_at = utcnow()
    await session.flush()


# ---------------- random draw ----------------

async def eligible_random_candidates(session: AsyncSession, expo: Expo):
    """Tasdiqlangan ishtirokchilar. Yakunlangan expo'da asosiy g'oliblar chiqarib tashlanadi."""
    rows = await top_submissions(session, expo.id)
    if expo.status in (ExpoStatus.FINISHED, ExpoStatus.CLOSED):
        skip = max((p["place"] for p in (expo.prizes or [])), default=0)
        rows = rows[skip:]
    return rows


async def save_draw(session: AsyncSession, expo_id: int, prize: str,
                    winners_count: int, candidates_hash: str,
                    winner_user_ids: list[int], created_by: int) -> RandomDraw:
    d = RandomDraw(expo_id=expo_id, prize=prize, winners_count=winners_count,
                   candidates_hash=candidates_hash, winner_user_ids=winner_user_ids,
                   created_by=created_by)
    session.add(d)
    await session.flush()
    return d


# ---------------- audit ----------------

async def audit(session: AsyncSession, actor_tg_id: int, action: str, payload: dict | None = None):
    session.add(AuditLog(actor_tg_id=actor_tg_id, action=action, payload=payload or {}))
