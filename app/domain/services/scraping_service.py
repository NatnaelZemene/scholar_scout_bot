from __future__ import annotations

from app.db.repositories.scholarship_repository import ScholarshipRepository
from app.db.repositories.scholarship_source_repository import ScholarshipSourceRepository
from app.scrapers.base import ScrapedScholarship


class ScrapingService:
    def __init__(
        self,
        source_repo: ScholarshipSourceRepository,
        scholarship_repo: ScholarshipRepository,
    ) -> None:
        self.source_repo = source_repo
        self.scholarship_repo = scholarship_repo

    async def upsert_batch(self, source_name: str, source_url: str, rows: list[ScrapedScholarship]) -> int:
        source = await self.source_repo.get_by_name(source_name)
        if source is None:
            source = await self.source_repo.create(name=source_name, base_url=source_url)

        count = 0
        for row in rows:
            await self.scholarship_repo.upsert(
                source_id=source.id,
                external_id=row.external_id,
                payload={
                    "title": row.title,
                    "url": row.url,
                    "country": row.country,
                    "level": row.level,
                    "field_of_study": row.field_of_study,
                    "funding_type": row.funding_type,
                    "language": row.language,
                    "deadline_date": row.deadline_date,
                    "amount_text": row.amount_text,
                    "description": row.description,
                    "is_active": True,
                },
            )
            count += 1

        return count
