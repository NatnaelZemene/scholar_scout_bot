from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScholarshipScraper, ScrapedScholarship


class ScholarshipsComScraper(BaseScholarshipScraper):
    source_name = "scholarships_com"
    base_url = "https://www.scholarships.com/financial-aid/college-scholarships/scholarship-directory"

    async def fetch(self) -> list[ScrapedScholarship]:
        # TODO: Implement actual HTTP request and HTML parsing
        results: list[ScrapedScholarship] = []
        return results
