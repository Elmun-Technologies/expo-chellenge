"""Batafsil CSV eksport — Telegram `/export` va web-admin panel uchun umumiy.

Har bir fayl to'liq ma'lumot beradi: qaysi foydalanuvchi, qaysi akkaunt,
skrinshot qachon yuborilgan, kiritilgan son, OCR'dan o'qilgan son, kim va
qachon tasdiqlagan/rad etgan — hammasi alohida ustunlarda. Vaqtlar Toshkent
(UTC+5) bo'yicha.
"""
import csv
import io
import zipfile

from sqlalchemy import select

from ..db.models import (Admin, Expo, Participant, Submission, User,
                         ViewReport)
from .utils import utc_to_tash


def _tash(dt) -> str:
    """Naive UTC datetime → Toshkent vaqtidagi 'YYYY-MM-DD HH:MM' satri."""
    if dt is None:
        return ""
    t = utc_to_tash(dt)
    return t.strftime("%Y-%m-%d %H:%M")


def _csv_bytes(headers: list[str], rows: list[tuple]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)
    # BOM bilan — Excel'da o'zbek/rus harflari to'g'ri ochiladi
    return buf.getvalue().encode("utf-8-sig")


def _ocr_match(r: ViewReport) -> str:
    if r.ocr_views is None:
        return "n/a"
    return "yes" if r.ocr_views == r.views_count else "no"


async def _reviewer_names(session) -> dict[int, str]:
    """tg_id -> ko'rsatiladigan ism (username yoki full_name)."""
    names: dict[int, str] = {}
    users = (await session.execute(select(User))).scalars().all()
    for u in users:
        names[u.tg_id] = u.username or u.full_name or str(u.tg_id)
    admins = (await session.execute(select(Admin))).scalars().all()
    for a in admins:
        names.setdefault(a.tg_id, f"{a.role}:{a.tg_id}")
    return names


def _rev(names: dict[int, str], tg_id: int | None) -> str:
    if not tg_id:
        return ""
    return names.get(tg_id, str(tg_id))


async def build_exports(session, expo: Expo) -> list[tuple[str, bytes]]:
    """(filename, csv_bytes) juftliklari: users / submissions / screenshots /
    leaderboard."""
    names = await _reviewer_names(session)
    slug = str(expo.id)

    # --- foydalanuvchilar (ishtirokchilar) ---
    users_rows = (await session.execute(
        select(User, Participant)
        .join(Participant, Participant.user_id == User.id)
        .where(Participant.expo_id == expo.id)
        .order_by(User.id))).all()

    # --- topshiriqlar (submissions) ---
    subs_rows = (await session.execute(
        select(Submission, Participant, User)
        .join(Participant, Submission.participant_id == Participant.id)
        .join(User, Participant.user_id == User.id)
        .where(Submission.expo_id == expo.id)
        .order_by(Submission.id))).all()

    # --- skrinshotlar (view_reports) ---
    rep_rows = (await session.execute(
        select(ViewReport, Submission, Participant, User)
        .join(Submission, ViewReport.submission_id == Submission.id)
        .join(Participant, Submission.participant_id == Participant.id)
        .join(User, Participant.user_id == User.id)
        .where(Submission.expo_id == expo.id)
        .order_by(ViewReport.id))).all()

    out: list[tuple[str, bytes]] = []

    # 1) users.csv — har bir ishtirokchi bo'yicha
    sub_by_participant: dict[int, list[Submission]] = {}
    for sub, _p, _u in subs_rows:
        sub_by_participant.setdefault(sub.participant_id, []).append(sub)
    user_rows = []
    for u, p in users_rows:
        subs = sub_by_participant.get(p.id, [])
        latest = subs[-1] if subs else None
        user_rows.append((
            u.tg_id, u.username or "", u.full_name or "", u.phone or "",
            u.instagram or "", u.language,
            _tash(u.created_at), _tash(p.joined_at),
            len(subs),
            latest.current_views if latest else 0,
            latest.status if latest else "",
        ))
    out.append((f"expo{slug}_users.csv", _csv_bytes(
        ["tg_id", "username", "full_name", "phone", "instagram", "language",
         "registered_at_tashkent", "joined_at_tashkent", "submissions_count",
         "current_views", "submission_status"], user_rows)))

    # 2) submissions.csv — har bir topshiriq bo'yicha
    sub_rows = []
    for sub, p, u in subs_rows:
        sub_rows.append((
            sub.id, expo.title, u.tg_id, u.username or "", u.full_name or "",
            u.phone or "", u.instagram or "", sub.status, sub.video_url,
            sub.current_views, _tash(sub.submitted_at), _tash(sub.reviewed_at),
            _rev(names, sub.reviewed_by), sub.reject_reason or "",
        ))
    out.append((f"expo{slug}_submissions.csv", _csv_bytes(
        ["sub_id", "expo", "tg_id", "username", "full_name", "phone",
         "instagram", "status", "video_url", "current_views",
         "submitted_at_tashkent", "reviewed_at_tashkent", "reviewed_by",
         "reject_reason"], sub_rows)))

    # 3) screenshots.csv — HAR BIR skrinshot bo'yicha (batafsil analitika)
    shot_rows = []
    for r, sub, p, u in rep_rows:
        shot_rows.append((
            r.id, sub.id, u.tg_id, u.username or "", u.full_name or "",
            u.instagram or "", r.views_count, r.ocr_views or "",
            r.ocr_handle or "", _ocr_match(r),
            r.status, "yes" if r.is_final else "no",
            ", ".join(r.flags or []),
            _tash(r.created_at), _tash(r.reviewed_at),
            _rev(names, r.reviewed_by),
        ))
    out.append((f"expo{slug}_screenshots.csv", _csv_bytes(
        ["report_id", "sub_id", "tg_id", "username", "full_name", "instagram",
         "typed_views", "ocr_views", "ocr_handle", "ocr_match", "status",
         "is_final", "flags", "submitted_at_tashkent", "reviewed_at_tashkent",
         "reviewed_by"], shot_rows)))

    # 4) leaderboard.csv — tasdiqlanganlar reyting bo'yicha
    approved = [s for s in subs_rows if s[0].status == "approved"]
    approved.sort(key=lambda x: (-x[0].current_views, x[0].submitted_at))
    lb_rows = []
    for i, (sub, p, u) in enumerate(approved, start=1):
        lb_rows.append((
            i, u.tg_id, u.username or "", u.full_name or "",
            u.instagram or "", u.phone or "", sub.video_url,
            sub.current_views, _tash(sub.submitted_at),
        ))
    out.append((f"expo{slug}_leaderboard.csv", _csv_bytes(
        ["rank", "tg_id", "username", "full_name", "instagram", "phone",
         "video_url", "views", "submitted_at_tashkent"], lb_rows)))

    return out


def zip_files(files: list[tuple[str, bytes]]) -> bytes:
    """Barcha CSV'larni bitta ZIP arxivga joylaydi (web panel uchun)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files:
            z.writestr(name, data)
    return buf.getvalue()
