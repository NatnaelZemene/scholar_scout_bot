from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models.scholarship_source import ScholarshipSource
from app.db.repositories.base import BaseRepository


class ScholarshipSourceRepository(BaseRepository):
    async def get_by_name(self, name: str) -> ScholarshipSource | None:
        result = await self.session.execute(select(ScholarshipSource).where(ScholarshipSource.name == name))
        return result.scalar_one_or_none()

    async def create(self, name: str, base_url: str, is_active: bool = True) -> ScholarshipSource:
        source = ScholarshipSource(name=name, base_url=base_url, is_active=is_active)
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def update_last_scraped(self, source: ScholarshipSource) -> ScholarshipSource:
        source.last_scraped_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(source)
        return source
