from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

ALLOWED_LEVELS = {"bachelor", "master", "phd", "postdoc", "diploma", "certificate"}
ALLOWED_FUNDING_TYPES = {"full", "partial", "tuition", "stipend", "mixed"}


class UserFilterUpsert(BaseModel):
    preferred_levels: list[str] | None = None
    preferred_fields: list[str] | None = None
    preferred_countries: list[str] | None = None
    funding_type: str | None = None
    language: str | None = None
    deadline_within_days: int | None = Field(default=None, ge=1, le=365)
    is_active: bool = True

    @field_validator("preferred_levels")
    @classmethod
    def validate_levels(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        normalized = [v.strip().lower() for v in value if v and v.strip()]
        invalid = [v for v in normalized if v not in ALLOWED_LEVELS]
        if invalid:
            raise ValueError(f"Invalid levels: {', '.join(invalid)}")
        return normalized

    @field_validator("funding_type")
    @classmethod
    def validate_funding(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in ALLOWED_FUNDING_TYPES:
            raise ValueError(f"Invalid funding_type: {value}")
        return normalized


class UserFilterOut(BaseModel):
    preferred_levels: list[str] | None = None
    preferred_fields: list[str] | None = None
    preferred_countries: list[str] | None = None
    funding_type: str | None = None
    language: str | None = None
    deadline_within_days: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}
