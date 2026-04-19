from __future__ import annotations

from app.db.init_db import init_db
from app.scrapers.demo_adapter import DemoSourceAdapter
from app.scrapers.runner import run_source_adapter


if __name__ == "__main__":
    init_db()
    summary = run_source_adapter(DemoSourceAdapter(), attempts=3)
    print(
        {
            "run_id": summary.run_id,
            "source_name": summary.source_name,
            "status": summary.status.value,
            "items_seen": summary.items_seen,
            "items_valid": summary.items_valid,
            "items_inserted": summary.items_inserted,
            "items_updated": summary.items_updated,
            "error_message": summary.error_message,
        }
    )
