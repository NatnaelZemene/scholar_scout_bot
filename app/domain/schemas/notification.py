from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationLogCreate(BaseModel):
    user_telegram_id: int
    scholarship_id: int
    notification_type: str = Field(default="new_scholarship", min_length=2, max_length=50)
    status: str = Field(default="sent", min_length=2, max_length=30)
    error_message: str | None = None


class NotificationLogOut(BaseModel):
    id: int
    user_id: int
    scholarship_id: int
    notification_type: str
    status: str
    error_message: str | None
    sent_at: datetime

    model_config = {"from_attributes": True}


class NotificationPreviewItem(BaseModel):
    scholarship_id: int
    title: str
    url: str


class NotificationPreviewOut(BaseModel):
    telegram_id: int
    matches: list[NotificationPreviewItem]
