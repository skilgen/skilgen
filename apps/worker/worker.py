from __future__ import annotations

import asyncio

from celery import Celery

from apps.api.api.analysis import run_analysis
from packages.db.config import settings
from packages.db.database import AsyncSessionLocal


celery_app = Celery("skillayer", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_max_retries=3,
    task_default_retry_delay=60,
)


@celery_app.task(bind=True, name="run_analysis", max_retries=3)
def run_analysis_task(
    self,
    run_id: str,
    repo_id: str,
    installation_id: int,
    full_name: str,
) -> None:
    async def _run() -> None:
        async with AsyncSessionLocal() as db:
            await run_analysis(run_id, repo_id, installation_id, full_name, db)

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc
