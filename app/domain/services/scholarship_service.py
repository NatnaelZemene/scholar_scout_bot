from __future__ import annotations

from datetime import date

from app.db.repositories.scholarship_repository import ScholarshipRepository
from app.domain.services.exceptions import NotFoundError


class ScholarshipService:
    def __init__(self, scholarship_repo: ScholarshipRepository) -> None:
        self.scholarship_repo = scholarship_repo

    async def list_scholarships(self, skip: int, limit: int):
        return await self.scholarship_repo.list(skip=skip, limit=limit)

    async def search_scholarships(
        self,
        country: str | None,
        level: str | None,
        field_of_study: str | None,
        deadline_before: date | None,
        skip: int,
        limit: int,
    ):
        return await self.scholarship_repo.search(
            country=country,
            level=level,
            field_of_study=field_of_study,
            deadline_before=deadline_before,
            skip=skip,
            limit=limit,
        )

    async def get_detail(self, scholarship_id: int):
        row = await self.scholarship_repo.get_by_id(scholarship_id)
        if row is None:
            raise NotFoundError("Scholarship not found")
        return row
