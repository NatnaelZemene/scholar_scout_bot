from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from sqlalchemy import select

from app.db.models.user import User
from app.db.repositories.notification_repository import NotificationRepository
from app.db.repositories.user_filter_repository import UserFilterRepository
from app.db.session import SessionLocal


async def with_retry(
    action: Callable[[], Awaitable[object]],
    attempts: int = 3,
    delay_seconds: float = 0.5,
) -> None:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            await action()
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            await asyncio.sleep(delay_seconds)
    if last_error is not None:
        raise last_error


async def run_notification_job(dry_run: bool = True) -> None:
    async with SessionLocal() as session:
        users = (await session.execute(select(User))).scalars().all()
        filter_repo = UserFilterRepository(session)
        notification_repo = NotificationRepository(session)

        for user in users:
            user_filter = await filter_repo.get_by_user_id(user.id)
            if user_filter is None or not user_filter.is_active:
                continue

            matches = await notification_repo.preview_matches(user_filter)
            print(f"User {user.telegram_id} matches: {len(matches)}")

            if dry_run:
                continue

            for scholarship in matches:
                await with_retry(
                    lambda: notification_repo.create_log(
                        user_id=user.id,
                        scholarship_id=scholarship.id,
                        notification_type="new_scholarship",
                        status="sent",
                        error_message=None,
                    )
                )

        if not dry_run:
            await session.commit()


if __name__ == "__main__":
    asyncio.run(run_notification_job(dry_run=True))
