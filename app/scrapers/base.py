from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class ScrapedScholarship:
    external_id: str
    title: str
    url: str
    country: str | None = None
    level: str | None = None
    field_of_study: str | None = None
    funding_type: str | None = None
    language: str | None = None
    deadline_date: date | None = None
    amount_text: str | None = None
    description: str | None = None


class BaseScholarshipScraper(ABC):
    source_name: str
    base_url: str

    @abstractmethod
    async def fetch(self) -> list[ScrapedScholarship]:
        raise NotImplementedError
