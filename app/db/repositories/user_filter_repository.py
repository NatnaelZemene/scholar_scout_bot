from __future__ import annotations

from sqlalchemy import select

from app.db.models.user_filter import UserFilter
from app.db.repositories.base import BaseRepository


class UserFilterRepository(BaseRepository):
    async def get_by_user_id(self, user_id: int) -> UserFilter | None:
        result = await self.session.execute(select(UserFilter).where(UserFilter.user_id == user_id))
        return result.scalar_one_or_none()

    async def upsert(
        self,
        user_id: int,
        preferred_levels: str | None,
        preferred_fields: str | None,
        preferred_countries: str | None,
        funding_type: str | None,
        language: str | None,
        deadline_within_days: int | None,
        is_active: bool,
    ) -> UserFilter:
        db_filter = await self.get_by_user_id(user_id)
        if db_filter is None:
            db_filter = UserFilter(user_id=user_id)
            self.session.add(db_filter)

        db_filter.preferred_levels = preferred_levels
        db_filter.preferred_fields = preferred_fields
        db_filter.preferred_countries = preferred_countries
        db_filter.funding_type = funding_type
        db_filter.language = language
        db_filter.deadline_within_days = deadline_within_days
        db_filter.is_active = is_active

        await self.session.flush()
        await self.session.refresh(db_filter)
        return db_filter
