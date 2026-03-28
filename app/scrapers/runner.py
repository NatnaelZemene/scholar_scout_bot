import asyncio

from app.db.repositories.scholarship_repository import ScholarshipRepository
from app.db.repositories.scholarship_source_repository import ScholarshipSourceRepository
from app.db.session import SessionLocal
from app.domain.services.scraping_service import ScrapingService
from app.scrapers.sources.scholarships_com import ScholarshipsComScraper


async def main() -> None:
    # List of all active scrapers you want to run
    scrapers = [ScholarshipsComScraper()]
    
    for scraper in scrapers:
        try:
            records = await scraper.fetch()
            if not records:
                print(f"Source: {scraper.source_name}")
                print("Fetched records: 0")
                print("Skipped DB upsert because no rows were returned.")
                print("-" * 30)
                continue

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
            print("-" * 30)
        except Exception as exc:  # noqa: BLE001
            print(f"Scraper failed for {scraper.source_name}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
