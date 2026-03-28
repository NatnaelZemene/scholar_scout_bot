from __future__ import annotations


def list_to_csv(values: list[str] | None) -> str | None:
    if not values:
        return None
    cleaned = [v.strip() for v in values if v and v.strip()]
    return ",".join(cleaned) if cleaned else None


def csv_to_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    out = [v.strip() for v in value.split(",") if v.strip()]
    return out or None
