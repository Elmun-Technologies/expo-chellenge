"""SQLAlchemy modellari. Barcha vaqtlar naive UTC."""
from datetime import datetime, timezone

from sqlalchemy import (BigInteger, Boolean, DateTime, ForeignKey, Integer,
                        String, Text, UniqueConstraint, func)
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Telegram file_id uzunligi 200 yetadi; matnlar Text'da


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="uz")
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20))  # moderator/admin/superadmin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Expo(Base):
    __tablename__ = "expos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    rules_text: Mapped[str] = mapped_column(Text, default="")
    prizes: Mapped[list] = mapped_column(SQLiteJSON, default=list)  # [{place:1, prize:"iPhone"}]
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    created_by: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (UniqueConstraint("user_id", "expo_id", name="uq_part_user_expo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    expo_id: Mapped[int] = mapped_column(ForeignKey("expos.id"), index=True)
    agreed_rules: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user: Mapped[User] = relationship(lazy="joined")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("expo_id", "video_url", name="uq_sub_expo_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"), index=True)
    expo_id: Mapped[int] = mapped_column(ForeignKey("expos.id"), index=True)
    video_url: Mapped[str] = mapped_column(String(500))
    platform: Mapped[str] = mapped_column(String(30), default="instagram")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    current_views: Mapped[int] = mapped_column(Integer, default=0)
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    participant: Mapped[Participant] = relationship(lazy="joined")


class ViewReport(Base):
    """Prosmottar TARIXI: har bir skrinshot alohida qator."""
    __tablename__ = "view_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), index=True)
    screenshot_file_id: Mapped[str] = mapped_column(String(200))
    views_count: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    flags: Mapped[list] = mapped_column(SQLiteJSON, default=list)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_tg_id: Mapped[int] = mapped_column(BigInteger)
    target_type: Mapped[str] = mapped_column(String(20))
    expo_id: Mapped[int | None] = mapped_column(ForeignKey("expos.id"), nullable=True)
    single_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    payload: Mapped[dict] = mapped_column(SQLiteJSON, default=dict)  # {text, photo_file_id}
    status: Mapped[str] = mapped_column(String(20), default="sending")  # sending/scheduled/done/cancelled
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    broadcast_id: Mapped[int] = mapped_column(ForeignKey("broadcasts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(20))  # sent/failed
    error: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class RandomDraw(Base):
    """🎲 Random sovg'a o'yinlari — to'liq shaffoflik bilan saqlanadi."""
    __tablename__ = "random_draws"

    id: Mapped[int] = mapped_column(primary_key=True)
    expo_id: Mapped[int] = mapped_column(ForeignKey("expos.id"), index=True)
    prize: Mapped[str] = mapped_column(String(300))
    winners_count: Mapped[int] = mapped_column(Integer)
    candidates_hash: Mapped[str] = mapped_column(String(20))  # sha256 qisqa — ro'yxat o'zgarmaganining isboti
    winner_user_ids: Mapped[list] = mapped_column(SQLiteJSON, default=list)
    created_by: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    payload: Mapped[dict] = mapped_column(SQLiteJSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
