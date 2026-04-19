from __future__ import annotations

from datetime import datetime, date
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SqlEnum,
    Float,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Root base for all SQLAlchemy ORM models in the project.
class Base(DeclarativeBase):
    pass


# Controlled set of study levels used by profiles and scholarships.
class StudyLevel(str, Enum):
    bachelors = "bachelors"
    masters = "masters"
    phd = "phd"
    other = "other"


# Outcome state for a single source scraping run.
class SourceStatus(str, Enum):
    success = "success"
    partial = "partial"
    failed = "failed"


# Delivery channels supported by the notification system.
class NotificationChannel(str, Enum):
    telegram = "telegram"


# One row per Telegram user with onboarding and preference fields.
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    field_of_study: Mapped[str | None] = mapped_column(String(120), nullable=True)
    study_level: Mapped[StudyLevel | None] = mapped_column(SqlEnum(StudyLevel), nullable=True)

    min_budget_usd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_budget_usd: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Canonical scholarship records collected from all supported sources.
class Scholarship(Base):
    __tablename__ = "scholarships"
    __table_args__ = (
        UniqueConstraint("source_name", "source_external_id", name="uq_source_external"),
        Index("ix_scholarships_deadline", "deadline"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(80), nullable=False)
    source_external_id: Mapped[str] = mapped_column(String(140), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(180), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    field_of_study: Mapped[str | None] = mapped_column(String(120), nullable=True)
    study_level: Mapped[StudyLevel | None] = mapped_column(SqlEnum(StudyLevel), nullable=True)

    funding_amount_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Operational log for each scraper execution including counters and errors.
class SourceRun(Base):
    __tablename__ = "source_runs"
    __table_args__ = (
        Index("ix_source_runs_source_started", "source_name", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[SourceStatus] = mapped_column(SqlEnum(SourceStatus), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_inserted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


# Precomputed scholarship match scores for each user.
class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user_id", "scholarship_id", name="uq_user_scholarship_match"),
        Index("ix_matches_user_score", "user_id", "score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    scholarship_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    reasons: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


# Outbound message log used for deduplication and delivery tracking.
class NotificationLog(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("user_id", "scholarship_id", "channel", name="uq_notification_dedupe"),
        Index("ix_notifications_user_sent", "user_id", "sent_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    scholarship_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    channel: Mapped[NotificationChannel] = mapped_column(SqlEnum(NotificationChannel), default=NotificationChannel.telegram, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    message_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)