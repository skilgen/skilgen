#!/usr/bin/env python3
"""Capture an anonymized Cursor state.vscdb fixture for importer regression tests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any


SENSITIVE_KEY_RE = re.compile(r"(content|prompt|text|body|diff|secret|token|password|api[_-]?key)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{12,}|[A-Za-z0-9+/]{32,}={0,2})")
HOME_RE = re.compile(r"/Users/[^/]+|/home/[^/]+|C:\\Users\\[^\\]+", re.IGNORECASE)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _scrub_string(value: str, *, key: str = "") -> str:
    if SENSITIVE_KEY_RE.search(key):
        return f"<redacted:{_hash(value)}>"
    scrubbed = HOME_RE.sub("<home>", value)
    scrubbed = SECRET_VALUE_RE.sub("<secret>", scrubbed)
    if len(scrubbed) > 240:
        return f"{scrubbed[:120]}...<truncated:{len(scrubbed)}>"
    return scrubbed


def _scrub(value: Any, *, key: str = "") -> Any:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return _scrub_string(value, key=key)
        return _scrub(parsed, key=key)
    if isinstance(value, list):
        return [_scrub(item, key=key) for item in value[:20]]
    if isinstance(value, dict):
        scrubbed: dict[str, Any] = {}
        for raw_key, raw_value in list(value.items())[:100]:
            item_key = str(raw_key)
            scrubbed[item_key] = _scrub(raw_value, key=item_key)
        return scrubbed
    return value


def _sqlite_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def capture_cursor_fixture(db_path: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        table_names = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for table_name in table_names:
            table_identifier = _sqlite_identifier(str(table_name))
            columns = [row[1] for row in connection.execute(f"PRAGMA table_info({table_identifier})").fetchall()]
            key_column = next((column for column in columns if column.lower() in {"key", "id"}), None)
            value_column = next((column for column in columns if column.lower() in {"value", "contents"}), None)
            if not key_column or not value_column:
                continue
            key_identifier = _sqlite_identifier(key_column)
            value_identifier = _sqlite_identifier(value_column)
            for key, value in connection.execute(f"SELECT {key_identifier}, {value_identifier} FROM {table_identifier} LIMIT 200"):
                rows.append({"table": table_name, "key": _scrub_string(str(key), key="key"), "value": _scrub(value, key=str(key))})
    finally:
        connection.close()

    return {
        "schema_version": 1,
        "source": "cursor_state_vscdb_anonymized",
        "source_file": db_path.name,
        "row_count": len(rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Anonymize a Cursor state.vscdb into a shareable JSON fixture.")
    parser.add_argument("state_vscdb", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fixture = capture_cursor_fixture(args.state_vscdb.expanduser().resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "row_count": fixture["row_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
