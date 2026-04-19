from __future__ import annotations

from app.scrapers.base import BaseSourceAdapter, RawScholarshipItem


class DemoSourceAdapter(BaseSourceAdapter):
    """Small deterministic adapter used for local smoke tests."""

    source_name = "demo_source"

    def fetch(self) -> list[RawScholarshipItem]:
        return [
            RawScholarshipItem(
                source_external_id="demo-1",
                title="Demo Scholarship One",
                url="https://example.com/demo-1",
                payload={"country": "Global"},
            ),
            RawScholarshipItem(
                source_external_id="demo-2",
                title="Demo Scholarship Two",
                url="https://example.com/demo-2",
                payload={"country": "Global"},
            ),
        ]
