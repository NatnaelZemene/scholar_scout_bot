from __future__ import annotations

from app.scrapers.base import BaseScholarshipScraper, ScrapedScholarship


class SampleSourceScraper(BaseScholarshipScraper):
    source_name = "sample_source"
    base_url = "https://example.com/scholarships"

    async def fetch(self) -> list[ScrapedScholarship]:
        # Replace with real parsing logic for a chosen source.
        return [
            ScrapedScholarship(
                external_id="sample-001",
                title="Example Global Scholarship",
                url="https://example.com/scholarships/sample-001",
                country="Global",
                level="master",
                field_of_study="computer science",
                funding_type="full",
                language="english",
                description="Sample record used for integration validation.",
            )
        ]
