from __future__ import annotations

import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler

from app.jobs.cleanup_job import run_cleanup_job
from app.jobs.notification_job import run_notification_job


def main() -> None:
    scheduler = BlockingScheduler()

    def notification_runner() -> None:
        asyncio.run(run_notification_job(dry_run=False))

    def cleanup_runner() -> None:
        asyncio.run(run_cleanup_job())

    scheduler.add_job(
        notification_runner,
        trigger="interval",
        minutes=30,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        cleanup_runner,
        trigger="cron",
        hour=2,
        minute=0,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()


if __name__ == "__main__":
    main()
