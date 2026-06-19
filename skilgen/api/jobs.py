from __future__ import annotations

import json
import sqlite3
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Callable

from skilgen.core.audit import append_audit_event


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
_job_lock = Lock()
_runtime_jobs: dict[str, JobRecord] = {}
_runtime_futures: dict[str, Future[dict[str, object]]] = {}
_recovered_roots: set[Path] = set()
_STATUS_POLL_FLUSH_SECONDS = 0.5


def _job_root(payload: dict[str, object]) -> Path | None:
    project_root = payload.get("project_root")
    if not isinstance(project_root, str):
        return None
    return Path(project_root).resolve()


def _db_path(project_root: str | Path) -> Path:
    root = Path(project_root).resolve()
    return root / ".skilgen" / "jobs" / "jobs.sqlite"


def _connect(project_root: str | Path) -> sqlite3.Connection:
    path = _db_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            project_root TEXT NOT NULL,
            job_type TEXT NOT NULL,
            status TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            result_json TEXT,
            error TEXT,
            progress INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            started_at TEXT,
            finished_at TEXT,
            cancel_requested INTEGER NOT NULL,
            events_json TEXT NOT NULL
        )
        """
    )
    return connection


def _row_to_job(row: sqlite3.Row) -> JobRecord:
    return JobRecord(
        job_id=str(row["job_id"]),
        job_type=str(row["job_type"]),
        status=str(row["status"]),
        payload=json.loads(row["payload_json"]),
        result=json.loads(row["result_json"]) if row["result_json"] else None,
        error=str(row["error"]) if row["error"] is not None else None,
        progress=int(row["progress"]),
        message=str(row["message"]),
        created_at=str(row["created_at"]),
        started_at=str(row["started_at"]) if row["started_at"] is not None else None,
        finished_at=str(row["finished_at"]) if row["finished_at"] is not None else None,
        cancel_requested=bool(row["cancel_requested"]),
        events=json.loads(row["events_json"]) if row["events_json"] else [],
    )


def _persist_job(job: JobRecord) -> None:
    root = _job_root(job.payload)
    if root is None:
        return
    with closing(_connect(root)) as connection, connection:
        connection.execute(
            """
            INSERT INTO jobs (
                job_id, project_root, job_type, status, payload_json, result_json, error,
                progress, message, created_at, started_at, finished_at, cancel_requested, events_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                project_root=excluded.project_root,
                job_type=excluded.job_type,
                status=excluded.status,
                payload_json=excluded.payload_json,
                result_json=excluded.result_json,
                error=excluded.error,
                progress=excluded.progress,
                message=excluded.message,
                created_at=excluded.created_at,
                started_at=excluded.started_at,
                finished_at=excluded.finished_at,
                cancel_requested=excluded.cancel_requested,
                events_json=excluded.events_json
            """,
            (
                job.job_id,
                str(root),
                job.job_type,
                job.status,
                json.dumps(job.payload, sort_keys=True),
                json.dumps(job.result, sort_keys=True) if job.result is not None else None,
                job.error,
                job.progress,
                job.message,
                job.created_at,
                job.started_at,
                job.finished_at,
                int(job.cancel_requested),
                json.dumps(job.events, sort_keys=True),
            ),
        )


def _recover_persisted_jobs(project_root: str | Path) -> None:
    root = Path(project_root).resolve()
    with _job_lock:
        if root in _recovered_roots:
            return
        active_runtime_jobs = [
            job
            for job in _runtime_jobs.values()
            if _job_root(job.payload) == root and job.status in {"queued", "running"}
        ]
        if active_runtime_jobs:
            _recovered_roots.add(root)
            return
        interrupted_at = datetime.now(timezone.utc).isoformat()
        with closing(_connect(root)) as connection, connection:
            rows = connection.execute(
                "SELECT job_id, events_json FROM jobs WHERE status = 'running'"
            ).fetchall()
            for row in rows:
                events = json.loads(row["events_json"]) if row["events_json"] else []
                events.append(
                    {
                        "timestamp": interrupted_at,
                        "message": "Job interrupted after server restart.",
                        "progress": 100,
                    }
                )
                connection.execute(
                    """
                    UPDATE jobs
                    SET status = ?, message = ?, finished_at = ?, error = ?, events_json = ?
                    WHERE job_id = ?
                    """,
                    (
                        "interrupted",
                        "interrupted",
                        interrupted_at,
                        "job interrupted after restart",
                        json.dumps(events, sort_keys=True),
                        row["job_id"],
                    ),
                )
        _recovered_roots.add(root)


def _load_job_from_disk(job_id: str, project_root: str | Path) -> JobRecord | None:
    _recover_persisted_jobs(project_root)
    with closing(_connect(project_root)) as connection:
        row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    return _row_to_job(row)


def _next_job_id() -> str:
    return f"job-{uuid.uuid4().hex[:12]}"


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
        _runtime_jobs[job.job_id] = job
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
        _runtime_jobs[job.job_id] = job
        _persist_job(job)


def request_cancel(job_id: str, project_root: str | Path | None = None) -> JobRecord | None:
    job = get_job(job_id, project_root, flush_future=False)
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
        _runtime_jobs[job.job_id] = job
        _persist_job(job)
    root = _job_root(job.payload)
    if root is not None:
        append_audit_event(root, action="job_cancel", outcome="success", source="jobs", job_id=job.job_id)
    return job


def submit_job(
    job_type: str,
    payload: dict[str, object],
    fn: Callable[[Callable[[int, str], None]], dict[str, object]],
) -> JobRecord:
    job = JobRecord(job_id=_next_job_id(), job_type=job_type, status="queued", payload=payload)
    root = _job_root(payload)
    with _job_lock:
        if root is not None:
            _recovered_roots.add(root)
        _runtime_jobs[job.job_id] = job
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
            append_job_event(job, "Finished delivery.", 100)
            root = _job_root(job.payload)
            if root is not None:
                append_audit_event(root, action="job_complete", outcome="success", source="jobs", job_id=job.job_id)
            update_job(job, status="completed", progress=100, message="completed")
            return result
        except JobCancelledError:
            job.error = "job cancelled"
            append_job_event(job, "Job cancelled.", 100)
            update_job(job, status="cancelled", progress=100, message="cancelled")
            raise
        except Exception as exc:  # noqa: BLE001
            job.error = str(exc)
            append_job_event(job, f"Job failed: {exc}", 100)
            root = _job_root(job.payload)
            if root is not None:
                append_audit_event(root, action="job_complete", outcome="failed", source="jobs", job_id=job.job_id)
            update_job(job, status="failed", progress=100, message="failed")
            raise

    future = _executor.submit(runner)
    with _job_lock:
        _runtime_futures[job.job_id] = future

    def _forget_future(_future: Future[dict[str, object]]) -> None:
        with _job_lock:
            _runtime_futures.pop(job.job_id, None)

    future.add_done_callback(_forget_future)
    return job


def get_job(job_id: str, project_root: str | Path | None = None, *, flush_future: bool = True) -> JobRecord | None:
    if flush_future:
        with _job_lock:
            future = _runtime_futures.get(job_id)
        if future is not None:
            try:
                future.result(timeout=_STATUS_POLL_FLUSH_SECONDS)
            except TimeoutError:
                pass
            except Exception:
                pass
    with _job_lock:
        future = _runtime_futures.get(job_id)
    if future is not None:
        try:
            future.result(timeout=0.05)
        except TimeoutError:
            pass
        except Exception:
            pass
    with _job_lock:
        job = _runtime_jobs.get(job_id)
    if job is not None:
        return job
    if project_root is None:
        return None
    return _load_job_from_disk(job_id, project_root)


def list_jobs(project_root: str | Path | None = None) -> list[JobRecord]:
    if project_root is None:
        with _job_lock:
            return sorted(_runtime_jobs.values(), key=lambda record: record.created_at)
    _recover_persisted_jobs(project_root)
    with closing(_connect(project_root)) as connection:
        rows = connection.execute("SELECT * FROM jobs ORDER BY created_at").fetchall()
    return [_row_to_job(row) for row in rows]


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
