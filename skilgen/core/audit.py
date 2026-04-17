from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any


_AUDIT_LOCK = Lock()


def audit_log_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "audit" / "events.jsonl"


def append_audit_event(
    project_root: str | Path,
    *,
    action: str,
    outcome: str,
    source: str,
    actor: str = "system",
    request_id: str | None = None,
    job_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> Path:
    path = audit_log_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "outcome": outcome,
        "source": source,
        "actor": actor,
    }
    if request_id:
        payload["request_id"] = request_id
    if job_id:
        payload["job_id"] = job_id
    if details:
        payload["details"] = details
    with _AUDIT_LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return path
