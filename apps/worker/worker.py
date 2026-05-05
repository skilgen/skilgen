from __future__ import annotations

import asyncio

from celery import Celery

from apps.api.api.analysis import run_analysis
from apps.api.api.v8.audit.router import build_evidence_package_for_job
from packages.db.config import settings
from packages.db.database import AsyncSessionLocal
from packages.db.models import Job


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
    pr_number: int | None = None,
    base_score: dict[str, int] | None = None,
    head_sha: str | None = None,
) -> None:
    async def _run() -> None:
        async with AsyncSessionLocal() as db:
            await run_analysis(
                run_id,
                repo_id,
                installation_id,
                full_name,
                db,
                pr_number=pr_number,
                base_score=base_score,
                head_sha=head_sha,
            )

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc


@celery_app.task(bind=True, name="build_evidence_package", max_retries=3)
def build_evidence_package_task(self, job_id: str, org_id: str, control: str, period_start: str, period_end: str) -> None:
    async def _run() -> None:
        async with AsyncSessionLocal() as db:
            job = await db.get(Job, job_id)
            if job is None:
                return
            job.status = "running"
            await db.commit()
            try:
                result = await build_evidence_package_for_job(db, job_id, org_id, control, period_start, period_end)
                job.status = "completed"
                job.result_json = {**(job.result_json or {}), **result}
                await db.commit()
            except Exception as exc:
                job.status = "failed"
                job.result_json = {**(job.result_json or {}), "error": str(exc)}
                await db.commit()
                raise

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc
