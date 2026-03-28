from __future__ import annotations

from app.db.repositories.user_filter_repository import UserFilterRepository
from app.db.repositories.user_repository import UserRepository
from app.domain.schemas.filter import UserFilterOut, UserFilterUpsert
from app.domain.services.exceptions import NotFoundError
from app.domain.services.helpers import csv_to_list, list_to_csv


class FilterService:
    def __init__(self, user_repo: UserRepository, filter_repo: UserFilterRepository) -> None:
        self.user_repo = user_repo
        self.filter_repo = filter_repo

    async def get_user_filter(self, telegram_id: int) -> UserFilterOut:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            raise NotFoundError("User not found")

        row = await self.filter_repo.get_by_user_id(user.id)
        if row is None:
            raise NotFoundError("Filter not found")

        return UserFilterOut(
            preferred_levels=csv_to_list(row.preferred_levels),
            preferred_fields=csv_to_list(row.preferred_fields),
            preferred_countries=csv_to_list(row.preferred_countries),
            funding_type=row.funding_type,
            language=row.language,
            deadline_within_days=row.deadline_within_days,
            is_active=row.is_active,
        )

    async def upsert_user_filter(self, telegram_id: int, payload: UserFilterUpsert) -> UserFilterOut:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            raise NotFoundError("User not found")

        row = await self.filter_repo.upsert(
            user_id=user.id,
            preferred_levels=list_to_csv(payload.preferred_levels),
            preferred_fields=list_to_csv(payload.preferred_fields),
            preferred_countries=list_to_csv(payload.preferred_countries),
            funding_type=payload.funding_type,
            language=payload.language,
            deadline_within_days=payload.deadline_within_days,
            is_active=payload.is_active,
        )

        return UserFilterOut(
            preferred_levels=csv_to_list(row.preferred_levels),
            preferred_fields=csv_to_list(row.preferred_fields),
            preferred_countries=csv_to_list(row.preferred_countries),
            funding_type=row.funding_type,
            language=row.language,
            deadline_within_days=row.deadline_within_days,
            is_active=row.is_active,
        )
