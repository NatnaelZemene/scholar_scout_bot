from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Scholarship, SourceRun, SourceStatus, StudyLevel
from app.db.session import SessionLocal
from app.scrapers.base import BaseSourceAdapter, RawScholarshipItem
from app.scrapers.retry import with_retry


@dataclass
class RunSummary:
    run_id: int
    source_name: str
    status: SourceStatus
    items_seen: int
    items_valid: int
    items_inserted: int
    items_updated: int
    error_message: str | None


def _coerce_study_level(value: object) -> StudyLevel | None:
    if value is None:
        return None
    if isinstance(value, StudyLevel):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        try:
            return StudyLevel(normalized)
        except ValueError:
            return None
    return None


def _coerce_deadline(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _upsert_scholarship(
    db: Session,
    source_name: str,
    item: RawScholarshipItem,
) -> str:
    existing = db.execute(
        select(Scholarship).where(
            Scholarship.source_name == source_name,
            Scholarship.source_external_id == item.source_external_id,
        )
    ).scalar_one_or_none()

    payload = item.payload or {}

    if existing is None:
        db.add(
            Scholarship(
                source_name=source_name,
                source_external_id=item.source_external_id,
                title=item.title,
                url=item.url,
                organization=payload.get("organization"),
                summary=payload.get("summary"),
                country=payload.get("country"),
                field_of_study=payload.get("field_of_study"),
                study_level=_coerce_study_level(payload.get("study_level")),
                funding_amount_usd=payload.get("funding_amount_usd"),
                deadline=_coerce_deadline(payload.get("deadline")),
                extra_data=payload,
            )
        )
        return "inserted"

    existing.title = item.title
    existing.url = item.url
    existing.organization = payload.get("organization")
    existing.summary = payload.get("summary")
    existing.country = payload.get("country")
    existing.field_of_study = payload.get("field_of_study")
    existing.study_level = _coerce_study_level(payload.get("study_level"))
    existing.funding_amount_usd = payload.get("funding_amount_usd")
    existing.deadline = _coerce_deadline(payload.get("deadline"))
    existing.extra_data = payload
    existing.scraped_at = datetime.utcnow()
    return "updated"


def run_source_adapter(adapter: BaseSourceAdapter, attempts: int = 3) -> RunSummary:
    """Execute one adapter run and persist metrics into source_runs."""
    db = SessionLocal()
    run = SourceRun(source_name=adapter.source_name, status=SourceStatus.failed)
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        items = with_retry(adapter.fetch, attempts=attempts)
        valid_count = 0
        inserted_count = 0
        updated_count = 0

        for item in items:
            if not adapter.validate(item):
                continue
            valid_count += 1
            result = _upsert_scholarship(db, adapter.source_name, item)
            if result == "inserted":
                inserted_count += 1
            else:
                updated_count += 1

        run.items_seen = len(items)
        run.items_inserted = inserted_count
        run.items_updated = updated_count
        run.status = SourceStatus.success if valid_count == len(items) else SourceStatus.partial
        run.error_message = None
    except Exception as exc:  # pragma: no cover - exercised in smoke script
        db.rollback()
        run.status = SourceStatus.failed
        run.error_message = str(exc)
        run.items_seen = 0
        run.items_inserted = 0
        run.items_updated = 0
        valid_count = 0
        inserted_count = 0
        updated_count = 0
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
            items_inserted=inserted_count,
            items_updated=updated_count,
            error_message=run.error_message,
        )
        db.close()

    return summary
