from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.db.repositories.user_repository import UserRepository
from app.domain.schemas.user import UserCreate, UserOut, UserUpdate
from app.domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(db_session_dependency)) -> UserOut:
    service = UserService(UserRepository(db))
    user = await service.register(payload)
    await db.commit()
    return UserOut.model_validate(user)


@router.get("/{telegram_id}", response_model=UserOut)
async def get_user(telegram_id: int, db: AsyncSession = Depends(db_session_dependency)) -> UserOut:
    service = UserService(UserRepository(db))
    user = await service.get(telegram_id)
    return UserOut.model_validate(user)


@router.patch("/{telegram_id}", response_model=UserOut)
async def update_user(
    telegram_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(db_session_dependency),
) -> UserOut:
    service = UserService(UserRepository(db))
    user = await service.update(telegram_id, payload)
    await db.commit()
    return UserOut.model_validate(user)
