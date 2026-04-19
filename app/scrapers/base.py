from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class RawScholarshipItem:
    """Normalized raw scholarship payload emitted by any source adapter."""

    source_external_id: str
    title: str
    url: str
    payload: dict[str, Any]


class BaseSourceAdapter(ABC):
    """Common contract all source adapters must implement."""

    source_name: str = "unknown"

    @abstractmethod
    def fetch(self) -> list[RawScholarshipItem]:
        """Pull records from one source and return normalized raw items."""
        raise NotImplementedError

    def validate(self, item: RawScholarshipItem) -> bool:
        """Shared minimum validation so broken rows are filtered early."""
        return bool(item.source_external_id and item.title and item.url)
