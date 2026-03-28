from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import and_, or_, select

from app.db.models.notification_log import NotificationLog
from app.db.models.scholarship import Scholarship
from app.db.models.user_filter import UserFilter
from app.db.repositories.base import BaseRepository


class NotificationRepository(BaseRepository):
    async def create_log(
        self,
        user_id: int,
        scholarship_id: int,
        notification_type: str,
        status: str,
        error_message: str | None,
    ) -> NotificationLog:
        row = NotificationLog(
            user_id=user_id,
            scholarship_id=scholarship_id,
            notification_type=notification_type,
            status=status,
            error_message=error_message,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def preview_matches(self, user_filter: UserFilter) -> list[Scholarship]:
        stmt = select(Scholarship).where(Scholarship.is_active.is_(True))

        if user_filter.funding_type:
            stmt = stmt.where(Scholarship.funding_type.ilike(f"%{user_filter.funding_type}%"))
        if user_filter.language:
            stmt = stmt.where(Scholarship.language.ilike(f"%{user_filter.language}%"))
        if user_filter.deadline_within_days:
            deadline = date.today() + timedelta(days=user_filter.deadline_within_days)
            stmt = stmt.where(Scholarship.deadline_date.is_not(None), Scholarship.deadline_date <= deadline)

        group_clauses = []
        if user_filter.preferred_levels:
            levels = [x.strip() for x in user_filter.preferred_levels.split(",") if x.strip()]
            group_clauses.append(or_(*[Scholarship.level.ilike(f"%{lvl}%") for lvl in levels]))
        if user_filter.preferred_fields:
            fields = [x.strip() for x in user_filter.preferred_fields.split(",") if x.strip()]
            group_clauses.append(or_(*[Scholarship.field_of_study.ilike(f"%{field}%") for field in fields]))
        if user_filter.preferred_countries:
            countries = [x.strip() for x in user_filter.preferred_countries.split(",") if x.strip()]
            group_clauses.append(or_(*[Scholarship.country.ilike(f"%{country}%") for country in countries]))

        if group_clauses:
            stmt = stmt.where(and_(*group_clauses))

        result = await self.session.execute(stmt.limit(50))
        return list(result.scalars().all())
