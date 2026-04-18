from __future__ import annotations

import math
import os
from pathlib import Path
import sqlite3


def rate_limit_store_path() -> Path:
    configured = os.getenv("SKILGEN_API_RATE_LIMIT_DB", "").strip()
    if configured:
        return Path(configured).resolve()
    audit_root = os.getenv("SKILGEN_AUDIT_LOG_ROOT", "").strip()
    if audit_root:
        return Path(audit_root).resolve() / "api" / "rate-limit.sqlite"
    return Path.cwd().resolve() / ".skilgen" / "api" / "rate-limit.sqlite"


def _connect(path: Path | None = None) -> sqlite3.Connection:
    target = (path or rate_limit_store_path()).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target, timeout=30.0, isolation_level=None)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rate_limit_events (
            bucket_key TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_rate_limit_events_bucket_time "
        "ON rate_limit_events(bucket_key, created_at)"
    )
    return connection


def consume_rate_limit(
    bucket_key: str,
    *,
    max_count: int,
    window_seconds: float,
    now: float,
    db_path: Path | None = None,
) -> tuple[bool, int]:
    if max_count <= 0:
        return True, 0
    cutoff = now - window_seconds
    connection = _connect(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM rate_limit_events WHERE created_at < ?", (cutoff,))
        current_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM rate_limit_events WHERE bucket_key = ? AND created_at >= ?",
                (bucket_key, cutoff),
            ).fetchone()[0]
        )
        if current_count >= max_count:
            oldest = connection.execute(
                "SELECT MIN(created_at) FROM rate_limit_events WHERE bucket_key = ? AND created_at >= ?",
                (bucket_key, cutoff),
            ).fetchone()[0]
            connection.execute("COMMIT")
            retry_after = max(1, math.ceil(window_seconds - (now - float(oldest)))) if oldest is not None else 1
            return False, retry_after
        connection.execute(
            "INSERT INTO rate_limit_events(bucket_key, created_at) VALUES(?, ?)",
            (bucket_key, now),
        )
        connection.execute("COMMIT")
        return True, 0
    except Exception:
        connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def clear_rate_limit_store(db_path: Path | None = None) -> None:
    target = (db_path or rate_limit_store_path()).resolve()
    if not target.exists():
        return
    connection = _connect(target)
    try:
        connection.execute("DELETE FROM rate_limit_events")
    finally:
        connection.close()
