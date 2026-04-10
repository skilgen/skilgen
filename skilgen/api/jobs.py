from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from itertools import count
from pathlib import Path
from threading import Lock
from typing import Callable
from datetime import datetime, timezone


@dataclass
class JobRecord:
    job_id: str
    job_type: str
    status: str
    payload: dict[str, object]
    result: dict[str, object] | None = None
    error: str | None = None
    progress: int = 0
    message: str = "queued"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    finished_at: str | None = None
    cancel_requested: bool = False
    events: list[dict[str, object]] = field(default_factory=list)


class JobCancelledError(RuntimeError):
    pass


_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="skilgen-job")
_job_counter = count(1)
_job_lock = Lock()
_jobs: dict[str, JobRecord] = {}


def _job_storage_dir(payload: dict[str, object]) -> Path | None:
    project_root = payload.get("project_root")
    if not isinstance(project_root, str):
        return None
    return Path(project_root).resolve() / ".skilgen" / "jobs"


def _persist_job(job: JobRecord) -> None:
    storage_dir = _job_storage_dir(job.payload)
    if storage_dir is None:
        return
    storage_dir.mkdir(parents=True, exist_ok=True)
    job_path = storage_dir / f"{job.job_id}.json"
    job_path.write_text(json.dumps(job_payload(job), indent=2), encoding="utf-8")


def _load_job_from_disk(job_id: str, project_root: str | Path) -> JobRecord | None:
    job_path = Path(project_root).resolve() / ".skilgen" / "jobs" / f"{job_id}.json"
    if not job_path.exists():
        return None
    try:
        payload = json.loads(job_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return JobRecord(
        job_id=payload["job_id"],
        job_type=payload["job_type"],
        status=payload["status"],
        payload=payload["payload"],
        result=payload.get("result"),
        error=payload.get("error"),
        progress=int(payload.get("progress", 0)),
        message=str(payload.get("message", "")),
        created_at=payload.get("created_at"),
        started_at=payload.get("started_at"),
        finished_at=payload.get("finished_at"),
        cancel_requested=bool(payload.get("cancel_requested", False)),
        events=list(payload.get("events", [])),
    )


def _next_job_id() -> str:
    return f"job-{next(_job_counter)}"


def update_job(job: JobRecord, *, status: str | None = None, progress: int | None = None, message: str | None = None) -> None:
    with _job_lock:
        if status is not None:
            job.status = status
            if status == "running" and job.started_at is None:
                job.started_at = datetime.now(timezone.utc).isoformat()
            if status in {"completed", "failed", "cancelled"}:
                job.finished_at = datetime.now(timezone.utc).isoformat()
        if progress is not None:
            job.progress = max(0, min(100, progress))
        if message is not None:
            job.message = message
        _persist_job(job)


def append_job_event(job: JobRecord, message: str, progress: int | None = None) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
    }
    if progress is not None:
        event["progress"] = max(0, min(100, progress))
    with _job_lock:
        job.events.append(event)
        _persist_job(job)


def request_cancel(job_id: str, project_root: str | Path | None = None) -> JobRecord | None:
    job = get_job(job_id, project_root)
    if job is None:
        return None
    with _job_lock:
        if job.status in {"completed", "failed", "cancelled"}:
            return job
        job.cancel_requested = True
        if job.status == "queued":
            job.status = "cancelled"
            job.progress = 100
            job.message = "cancelled"
            job.finished_at = datetime.now(timezone.utc).isoformat()
        else:
            job.message = "cancel requested"
        _persist_job(job)
    return job


def submit_job(
    job_type: str,
    payload: dict[str, object],
    fn: Callable[[Callable[[int, str], None]], dict[str, object]],
) -> JobRecord:
    job = JobRecord(job_id=_next_job_id(), job_type=job_type, status="queued", payload=payload)
    with _job_lock:
        _jobs[job.job_id] = job
        _persist_job(job)

    def runner() -> dict[str, object]:
        if job.cancel_requested:
            update_job(job, status="cancelled", progress=100, message="cancelled")
            raise JobCancelledError("job cancelled before start")
        update_job(job, status="running", progress=10, message="running")
        try:
            def report(progress: int, message: str) -> None:
                if job.cancel_requested:
                    update_job(job, status="cancelled", progress=100, message="cancelled")
                    raise JobCancelledError("job cancelled")
                update_job(job, progress=progress, message=message)
                append_job_event(job, message, progress)

            result = fn(report)
            job.result = result
            update_job(job, status="completed", progress=100, message="completed")
            append_job_event(job, "Finished delivery.", 100)
            _persist_job(job)
            return result
        except JobCancelledError:
            job.error = "job cancelled"
            update_job(job, status="cancelled", progress=100, message="cancelled")
            append_job_event(job, "Job cancelled.", 100)
            _persist_job(job)
            raise
        except Exception as exc:  # noqa: BLE001
            job.error = str(exc)
            update_job(job, status="failed", progress=100, message="failed")
            append_job_event(job, f"Job failed: {exc}", 100)
            _persist_job(job)
            raise

    _executor.submit(runner)
    return job


def get_job(job_id: str, project_root: str | Path | None = None) -> JobRecord | None:
    with _job_lock:
        job = _jobs.get(job_id)
    if job is not None:
        return job
    if project_root is None:
        return None
    return _load_job_from_disk(job_id, project_root)


def list_jobs(project_root: str | Path | None = None) -> list[JobRecord]:
    with _job_lock:
        jobs = list(_jobs.values())
    if project_root is None:
        return jobs
    root = Path(project_root).resolve()
    filtered = [job for job in jobs if Path(str(job.payload.get("project_root", ""))).resolve() == root]
    jobs_dir = root / ".skilgen" / "jobs"
    if jobs_dir.exists():
        seen = {job.job_id for job in filtered}
        for path in sorted(jobs_dir.glob("job-*.json")):
            record = _load_job_from_disk(path.stem, root)
            if record is not None and record.job_id not in seen:
                filtered.append(record)
    return sorted(filtered, key=lambda record: record.job_id)


def job_payload(job: JobRecord) -> dict[str, object]:
    return {
        "job_id": job.job_id,
        "job_type": job.job_type,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "cancel_requested": job.cancel_requested,
        "events": job.events,
        "payload": job.payload,
        "result": job.result,
        "error": job.error,
    }
