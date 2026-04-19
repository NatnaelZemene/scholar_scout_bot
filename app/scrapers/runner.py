from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.db.models import SourceRun, SourceStatus
from app.db.session import SessionLocal
from app.scrapers.base import BaseSourceAdapter
from app.scrapers.retry import with_retry


@dataclass
class RunSummary:
    run_id: int
    source_name: str
    status: SourceStatus
    items_seen: int
    items_valid: int
    error_message: str | None


def run_source_adapter(adapter: BaseSourceAdapter, attempts: int = 3) -> RunSummary:
    """Execute one adapter run and persist metrics into source_runs."""
    db = SessionLocal()
    run = SourceRun(source_name=adapter.source_name, status=SourceStatus.failed)
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        items = with_retry(adapter.fetch, attempts=attempts)
        valid_count = sum(1 for item in items if adapter.validate(item))

        run.items_seen = len(items)
        run.items_inserted = valid_count
        run.items_updated = 0
        run.status = SourceStatus.success if valid_count == len(items) else SourceStatus.partial
        run.error_message = None
    except Exception as exc:  # pragma: no cover - exercised in smoke script
        run.status = SourceStatus.failed
        run.error_message = str(exc)
        run.items_seen = 0
        run.items_inserted = 0
        run.items_updated = 0
        valid_count = 0
    finally:
        run.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(run)
        summary = RunSummary(
            run_id=run.id,
            source_name=run.source_name,
            status=run.status,
            items_seen=run.items_seen,
            items_valid=valid_count,
            error_message=run.error_message,
        )
        db.close()

    return summary
