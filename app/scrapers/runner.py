import asyncio

from app.db.repositories.scholarship_repository import ScholarshipRepository
from app.db.repositories.scholarship_source_repository import ScholarshipSourceRepository
from app.db.session import SessionLocal
from app.domain.services.scraping_service import ScrapingService
from app.scrapers.sources.sample_source import SampleSourceScraper


async def main() -> None:
    scraper = SampleSourceScraper()
    try:
        records = await scraper.fetch()
        async with SessionLocal() as session:
            source_repo = ScholarshipSourceRepository(session)
            scholarship_repo = ScholarshipRepository(session)
            service = ScrapingService(source_repo, scholarship_repo)
            count = await service.upsert_batch(
                source_name=scraper.source_name,
                source_url=scraper.base_url,
                rows=records,
            )
            source = await source_repo.get_by_name(scraper.source_name)
            if source is not None:
                await source_repo.update_last_scraped(source)
            await session.commit()

        print(f"Source: {scraper.source_name}")
        print(f"Fetched records: {len(records)}")
        print(f"Upserted records: {count}")
    except Exception as exc:  # noqa: BLE001
        print(f"Scraper failed for {scraper.source_name}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
