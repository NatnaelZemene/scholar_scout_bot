from __future__ import annotations

from app.db.repositories.user_repository import UserRepository
from app.domain.schemas.user import UserCreate, UserUpdate
from app.domain.services.exceptions import ConflictError, NotFoundError


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, payload: UserCreate):
        existing = await self.user_repo.get_by_telegram_id(payload.telegram_id)
        if existing is not None:
            raise ConflictError("User already exists")
        return await self.user_repo.create(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )

    async def get(self, telegram_id: int):
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def update(self, telegram_id: int, payload: UserUpdate):
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            raise NotFoundError("User not found")

        return await self.user_repo.update(
            user=user,
            username=payload.username if payload.username is not None else user.username,
            first_name=payload.first_name if payload.first_name is not None else user.first_name,
            last_name=payload.last_name if payload.last_name is not None else user.last_name,
        )
