from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from skilgen.core.config import load_config
from skilgen.core.repo_state import classify_repo_change, git_repo_state
from skilgen.delivery import run_delivery


def _state_dir(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "state"


def _state_path(project_root: str | Path) -> Path:
    return _state_dir(project_root) / "autoupdate.json"


def _requirements_record_path(project_root: str | Path) -> Path:
    return _state_dir(project_root) / "autoupdate-requirements.txt"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_state(project_root: str | Path, payload: dict[str, object]) -> None:
    path = _state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def auto_update_status(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    default = {
        "enabled": config.update_trigger in {"auto", "watch"},
        "update_trigger": config.update_trigger,
        "running": False,
        "pid": None,
        "interval_seconds": 2.0,
        "started_at": None,
        "last_run_at": None,
        "last_event": None,
        "project_root": str(root),
    }
    path = _state_path(root)
    if not path.exists():
        return default
    payload = json.loads(path.read_text(encoding="utf-8"))
    pid = payload.get("pid")
    running = False
    if isinstance(pid, int):
        try:
            os.kill(pid, 0)
            running = True
        except OSError:
            running = False
    payload["running"] = running
    payload.setdefault("enabled", default["enabled"])
    payload.setdefault("update_trigger", config.update_trigger)
    payload.setdefault("project_root", str(root))
    return payload


def _requirements_path_for_worker(project_root: Path) -> Path | None:
    path = _requirements_record_path(project_root)
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    return Path(raw) if raw else None


def _record_requirements_path(project_root: Path, requirements_path: str | Path | None) -> None:
    path = _requirements_record_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("" if requirements_path is None else str(Path(requirements_path).resolve()), encoding="utf-8")


def _file_snapshot(project_root: Path) -> dict[str, int]:
    tracked: dict[str, int] = {}
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root).as_posix()
        if relative.startswith((".git/", ".skilgen/", "skills/", "__pycache__/")):
            continue
        if path.name in {"AGENTS.md", "ANALYSIS.md", "FEATURES.md", "REPORT.md", "TRACEABILITY.md"}:
            continue
        tracked[relative] = path.stat().st_mtime_ns
    return tracked


def _snapshot(project_root: Path) -> dict[str, object]:
    return {
        "files": _file_snapshot(project_root),
        "git": git_repo_state(project_root),
    }


def ensure_auto_update_worker(
    project_root: str | Path,
    *,
    requirements_path: str | Path | None = None,
    interval_seconds: float = 2.0,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    enabled = config.update_trigger in {"auto", "watch"}
    if not enabled:
        state = auto_update_status(root)
        state["enabled"] = False
        state["reason"] = "update_trigger_disabled"
        return state
    if requirements_path is not None:
        _record_requirements_path(root, requirements_path)
    status = auto_update_status(root)
    if status.get("running"):
        return status
    cmd = [
        sys.executable,
        "-m",
        "skilgen.cli.main",
        "autoupdate",
        "worker",
        "--project-root",
        str(root),
        "--interval",
        str(interval_seconds),
    ]
    process = subprocess.Popen(  # noqa: S603
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    pid = process.pid
    process.returncode = 0
    payload = {
        "enabled": True,
        "update_trigger": config.update_trigger,
        "running": True,
        "pid": pid,
        "interval_seconds": interval_seconds,
        "started_at": _timestamp(),
        "last_run_at": None,
        "last_event": "worker_started",
        "project_root": str(root),
    }
    _write_state(root, payload)
    return payload


def stop_auto_update_worker(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    status = auto_update_status(root)
    pid = status.get("pid")
    if isinstance(pid, int) and status.get("running"):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    payload = {
        **status,
        "running": False,
        "last_event": "worker_stopped",
    }
    _write_state(root, payload)
    return payload


def run_auto_update_worker(project_root: str | Path, *, interval_seconds: float = 2.0) -> None:
    root = Path(project_root).resolve()
    config = load_config(root)
    payload = {
        "enabled": config.update_trigger in {"auto", "watch"},
        "update_trigger": config.update_trigger,
        "running": True,
        "pid": os.getpid(),
        "interval_seconds": interval_seconds,
        "started_at": _timestamp(),
        "last_run_at": None,
        "last_event": "worker_running",
        "project_root": str(root),
    }
    _write_state(root, payload)
    previous = _snapshot(root)
    while True:
        time.sleep(interval_seconds)
        current = _snapshot(root)
        if current == previous:
            continue
        change = classify_repo_change(previous, current)
        requirements = _requirements_path_for_worker(root)
        run_delivery(requirements, root)
        payload = {
            **payload,
            "last_run_at": _timestamp(),
            "last_event": change["event_type"],
            "last_change_summary": change,
        }
        _write_state(root, payload)
        previous = current
