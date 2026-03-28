from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class ScholarshipCreate(BaseModel):
    source_id: int
    external_id: str | None = None
    title: str = Field(min_length=3, max_length=500)
    url: str
    country: str | None = None
    level: str | None = None
    field_of_study: str | None = None
    funding_type: str | None = None
    language: str | None = None
    deadline_date: date | None = None
    amount_text: str | None = None
    description: str | None = None
    is_active: bool = True


class ScholarshipOut(BaseModel):
    id: int
    source_id: int
    external_id: str | None = None
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
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScholarshipSearchParams(BaseModel):
    country: str | None = None
    level: str | None = None
    field_of_study: str | None = None
    deadline_before: date | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
