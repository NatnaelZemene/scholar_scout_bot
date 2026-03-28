from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete

from app.db.models.notification_log import NotificationLog
from app.db.models.scholarship import Scholarship
from app.db.session import SessionLocal


async def run_cleanup_job(notification_retention_days: int = 90) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=notification_retention_days)

    async with SessionLocal() as session:
        await session.execute(
            delete(NotificationLog).where(NotificationLog.sent_at < cutoff)
        )
        await session.execute(
            delete(Scholarship).where(Scholarship.deadline_date.is_not(None), Scholarship.deadline_date < date.today())
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(run_cleanup_job())
