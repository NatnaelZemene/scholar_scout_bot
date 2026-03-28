from __future__ import annotations

from datetime import date

from sqlalchemy import Select, select

from app.db.models.scholarship import Scholarship
from app.db.repositories.base import BaseRepository


class ScholarshipRepository(BaseRepository):
    async def get_by_id(self, scholarship_id: int) -> Scholarship | None:
        result = await self.session.execute(select(Scholarship).where(Scholarship.id == scholarship_id))
        return result.scalar_one_or_none()

    async def get_by_source_external(self, source_id: int, external_id: str) -> Scholarship | None:
        result = await self.session.execute(
            select(Scholarship).where(
                Scholarship.source_id == source_id,
                Scholarship.external_id == external_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, source_id: int, external_id: str, payload: dict) -> Scholarship:
        row = await self.get_by_source_external(source_id=source_id, external_id=external_id)
        if row is None:
            row = Scholarship(source_id=source_id, external_id=external_id, **payload)
            self.session.add(row)
        else:
            for key, value in payload.items():
                setattr(row, key, value)

        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def list(self, skip: int, limit: int) -> list[Scholarship]:
        stmt = select(Scholarship).where(Scholarship.is_active.is_(True)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self,
        country: str | None,
        level: str | None,
        field_of_study: str | None,
        deadline_before: date | None,
        skip: int,
        limit: int,
    ) -> list[Scholarship]:
        stmt: Select[tuple[Scholarship]] = select(Scholarship).where(Scholarship.is_active.is_(True))

        if country:
            stmt = stmt.where(Scholarship.country.ilike(f"%{country.strip()}%"))
        if level:
            stmt = stmt.where(Scholarship.level.ilike(f"%{level.strip()}%"))
        if field_of_study:
            stmt = stmt.where(Scholarship.field_of_study.ilike(f"%{field_of_study.strip()}%"))
        if deadline_before:
            stmt = stmt.where(Scholarship.deadline_date <= deadline_before)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
