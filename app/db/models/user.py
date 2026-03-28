
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
	from app.db.models.notification_log import NotificationLog
	from app.db.models.user_filter import UserFilter


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
	username: Mapped[str | None] = mapped_column(String(255), nullable=True)
	first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
	last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
	)

	user_filter: Mapped["UserFilter | None"] = relationship(back_populates="user", uselist=False)
	notifications: Mapped[list["NotificationLog"]] = relationship(back_populates="user")

