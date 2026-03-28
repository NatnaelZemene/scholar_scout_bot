from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScholarshipScraper, ScrapedScholarship


class ScholarshipsComScraper(BaseScholarshipScraper):
    source_name = "scholarships_com"
    base_url = "https://www.scholarships.com/financial-aid/college-scholarships/scholarship-directory"

    async def fetch(self) -> list[ScrapedScholarship]:
        results: list[ScrapedScholarship] = []
        # Update headers strictly to impersonate a standard browser without bot signals
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
        
        test_url = f"{self.base_url}/academic-major/computer-science"
        
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                response = await client.get(test_url, timeout=15.0)
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise RuntimeError(f"Error fetching from Scholarships.com: {e}") from e

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Scholarships.com typically stores their data in a table with row classes or standard tds
        rows = soup.select("table tbody tr")
        
        for row in rows[:10]:  # Limit to 10 for initial testing
            title_tag = row.select_one("td.entry-info h3 a, td.title a, a")
            amount_tag = row.select_one("td.amount, td.award")
            
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            full_url = f"https://www.scholarships.com{link}" if link.startswith("/") else link
            amount = amount_tag.get_text(strip=True) if amount_tag else None
            
            results.append(ScrapedScholarship(
                external_id=f"scholcom-{hash(full_url)}",
                title=title,
                url=full_url,
                amount_text=amount,
                field_of_study="Computer Science", # based on the directory category
                country="USA", # Scholarships.com is heavily US-focused
            ))

        return results
