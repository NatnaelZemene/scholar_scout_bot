from __future__ import annotations

from app.db.repositories.notification_repository import NotificationRepository
from app.db.repositories.user_filter_repository import UserFilterRepository
from app.db.repositories.user_repository import UserRepository
from app.domain.schemas.notification import NotificationPreviewItem, NotificationPreviewOut
from app.domain.services.exceptions import NotFoundError


class NotificationService:
    def __init__(
        self,
        user_repo: UserRepository,
        filter_repo: UserFilterRepository,
        notification_repo: NotificationRepository,
    ) -> None:
        self.user_repo = user_repo
        self.filter_repo = filter_repo
        self.notification_repo = notification_repo

    async def preview_user_matches(self, telegram_id: int) -> NotificationPreviewOut:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            raise NotFoundError("User not found")

        user_filter = await self.filter_repo.get_by_user_id(user.id)
        if user_filter is None:
            raise NotFoundError("Filter not found")

        matches = await self.notification_repo.preview_matches(user_filter)
        return NotificationPreviewOut(
            telegram_id=telegram_id,
            matches=[
                NotificationPreviewItem(
                    scholarship_id=item.id,
                    title=item.title,
                    url=item.url,
                )
                for item in matches
            ],
        )

    async def log_notification(
        self,
        telegram_id: int,
        scholarship_id: int,
        notification_type: str,
        status: str,
        error_message: str | None,
    ):
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            raise NotFoundError("User not found")

        return await self.notification_repo.create_log(
            user_id=user.id,
            scholarship_id=scholarship_id,
            notification_type=notification_type,
            status=status,
            error_message=error_message,
        )
