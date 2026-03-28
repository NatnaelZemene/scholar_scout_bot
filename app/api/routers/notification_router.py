from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.db.repositories.notification_repository import NotificationRepository
from app.db.repositories.user_filter_repository import UserFilterRepository
from app.db.repositories.user_repository import UserRepository
from app.domain.schemas.notification import NotificationLogCreate, NotificationLogOut, NotificationPreviewOut
from app.domain.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/preview/{telegram_id}", response_model=NotificationPreviewOut)
async def preview_user_matches(
    telegram_id: int,
    db: AsyncSession = Depends(db_session_dependency),
) -> NotificationPreviewOut:
    service = NotificationService(UserRepository(db), UserFilterRepository(db), NotificationRepository(db))
    return await service.preview_user_matches(telegram_id)


@router.post("/log", response_model=NotificationLogOut, status_code=status.HTTP_201_CREATED)
async def create_notification_log(
    payload: NotificationLogCreate,
    db: AsyncSession = Depends(db_session_dependency),
) -> NotificationLogOut:
    service = NotificationService(UserRepository(db), UserFilterRepository(db), NotificationRepository(db))
    row = await service.log_notification(
        telegram_id=payload.user_telegram_id,
        scholarship_id=payload.scholarship_id,
        notification_type=payload.notification_type,
        status=payload.status,
        error_message=payload.error_message,
    )
    await db.commit()
    return NotificationLogOut.model_validate(row)
