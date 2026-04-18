from __future__ import annotations

import contextlib
import fcntl
import json
from datetime import UTC, datetime
import os
from pathlib import Path
from threading import Lock
from typing import Any


_AUDIT_LOCK = Lock()


def audit_log_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "audit" / "events.jsonl"


def central_audit_log_path() -> Path | None:
    raw_root = os.getenv("SKILGEN_AUDIT_LOG_ROOT", "").strip()
    if not raw_root:
        return None
    return Path(raw_root).resolve() / "audit" / "events.jsonl"


def _write_audit_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        with contextlib.suppress(OSError):
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
        handle.flush()
        with contextlib.suppress(OSError):
            os.fsync(handle.fileno())
        with contextlib.suppress(OSError):
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_central_audit_event(
    *,
    action: str,
    outcome: str,
    source: str,
    actor: str = "system",
    project_root: str | Path | None = None,
    principal: str | None = None,
    scope: str | None = None,
    tenant: str | None = None,
    request_id: str | None = None,
    job_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> Path | None:
    path = central_audit_log_path()
    if path is None:
        return None
    payload: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "outcome": outcome,
        "source": source,
        "actor": actor,
    }
    if project_root is not None:
        payload["project_root"] = str(Path(project_root).resolve())
    if principal:
        payload["principal"] = principal
    if scope:
        payload["scope"] = scope
    if tenant:
        payload["tenant"] = tenant
    if request_id:
        payload["request_id"] = request_id
    if job_id:
        payload["job_id"] = job_id
    if details:
        payload["details"] = details
    with _AUDIT_LOCK:
        _write_audit_payload(path, payload)
    return path


def append_audit_event(
    project_root: str | Path,
    *,
    action: str,
    outcome: str,
    source: str,
    actor: str = "system",
    principal: str | None = None,
    scope: str | None = None,
    tenant: str | None = None,
    request_id: str | None = None,
    job_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> Path:
    path = audit_log_path(project_root)
    resolved_project_root = Path(project_root).resolve()
    payload: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "outcome": outcome,
        "source": source,
        "actor": actor,
        "project_root": str(resolved_project_root),
    }
    if principal:
        payload["principal"] = principal
    if scope:
        payload["scope"] = scope
    if tenant:
        payload["tenant"] = tenant
    if request_id:
        payload["request_id"] = request_id
    if job_id:
        payload["job_id"] = job_id
    if details:
        payload["details"] = details
    with _AUDIT_LOCK:
        _write_audit_payload(path, payload)
        central_path = central_audit_log_path()
        if central_path is not None and central_path.resolve() != path.resolve():
            _write_audit_payload(central_path, payload)
    return path
