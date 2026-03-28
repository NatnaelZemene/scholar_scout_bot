from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.db.repositories.user_filter_repository import UserFilterRepository
from app.db.repositories.user_repository import UserRepository
from app.domain.schemas.filter import UserFilterOut, UserFilterUpsert
from app.domain.services.filter_service import FilterService

router = APIRouter(prefix="/users", tags=["filters"])


@router.put("/{telegram_id}/filters", response_model=UserFilterOut)
async def upsert_filter(
    telegram_id: int,
    payload: UserFilterUpsert,
    db: AsyncSession = Depends(db_session_dependency),
) -> UserFilterOut:
    service = FilterService(UserRepository(db), UserFilterRepository(db))
    row = await service.upsert_user_filter(telegram_id, payload)
    await db.commit()
    return row


@router.get("/{telegram_id}/filters", response_model=UserFilterOut)
async def get_filter(telegram_id: int, db: AsyncSession = Depends(db_session_dependency)) -> UserFilterOut:
    service = FilterService(UserRepository(db), UserFilterRepository(db))
    return await service.get_user_filter(telegram_id)
