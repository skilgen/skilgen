from __future__ import annotations

from contextlib import closing
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sqlite3
from typing import Any


_DEFAULT_PROVIDER = "generic"


def identity_policy_store_path() -> Path:
    explicit = os.getenv("SKILGEN_API_IDENTITY_POLICY_DB", "").strip()
    if explicit:
        return Path(explicit).resolve()
    audit_root = os.getenv("SKILGEN_AUDIT_LOG_ROOT", "").strip()
    if audit_root:
        return Path(audit_root).resolve() / "identity" / "policies.sqlite"
    return Path.cwd().resolve() / ".skilgen" / "api" / "identity-policies.sqlite"


def _connect() -> sqlite3.Connection:
    path = identity_policy_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_policies (
            provider TEXT PRIMARY KEY,
            policy_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return connection


def _normalize_claim_list(raw_value: object, *, field_name: str) -> list[str] | None:
    if raw_value is None or raw_value == "":
        return None
    if not isinstance(raw_value, list):
        raise ValueError(f"`{field_name}` must be a list")
    values = [str(item).strip() for item in raw_value if str(item).strip()]
    return values or []


def _normalize_group_scope_map(raw_value: object) -> dict[str, str] | None:
    if raw_value is None or raw_value == "":
        return None
    if not isinstance(raw_value, dict):
        raise ValueError("`group_scope_map` must be an object")
    return {str(key).strip(): str(value).strip() for key, value in raw_value.items() if str(key).strip() and str(value).strip()}


def _normalize_group_roots_map(raw_value: object) -> dict[str, list[str]] | None:
    if raw_value is None or raw_value == "":
        return None
    if not isinstance(raw_value, dict):
        raise ValueError("`group_roots_map` must be an object")
    normalized: dict[str, list[str]] = {}
    for key, value in raw_value.items():
        group_name = str(key).strip()
        if not group_name:
            continue
        if not isinstance(value, list):
            raise ValueError("`group_roots_map` values must be lists")
        normalized[group_name] = [str(Path(item).resolve()) for item in value if str(item).strip()]
    return normalized


def normalize_identity_policy_update(data: dict[str, object]) -> dict[str, object]:
    provider = str(data.get("provider", _DEFAULT_PROVIDER)).strip().lower() or _DEFAULT_PROVIDER
    normalized: dict[str, object] = {"provider": provider}
    for field_name in ("principal_claims", "scope_claims", "group_claims", "root_claims", "tenant_claims"):
        value = _normalize_claim_list(data.get(field_name), field_name=field_name)
        if value is not None:
            normalized[field_name] = value
    group_scope_map = _normalize_group_scope_map(data.get("group_scope_map"))
    if group_scope_map is not None:
        normalized["group_scope_map"] = group_scope_map
    group_roots_map = _normalize_group_roots_map(data.get("group_roots_map"))
    if group_roots_map is not None:
        normalized["group_roots_map"] = group_roots_map
    return normalized


def upsert_identity_policy(data: dict[str, object]) -> dict[str, object]:
    normalized = normalize_identity_policy_update(data)
    provider = str(normalized["provider"])
    payload = {key: value for key, value in normalized.items() if key != "provider"}
    updated_at = datetime.now(UTC).isoformat()
    with closing(_connect()) as connection, connection:
        connection.execute(
            """
            INSERT INTO identity_policies (provider, policy_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(provider) DO UPDATE SET
                policy_json=excluded.policy_json,
                updated_at=excluded.updated_at
            """,
            (provider, json.dumps(payload, sort_keys=True), updated_at),
        )
    stored = get_identity_policy(provider)
    if stored is None:
        raise RuntimeError("identity policy was not persisted")
    return stored


def get_identity_policy(provider: str) -> dict[str, object] | None:
    with closing(_connect()) as connection:
        row = connection.execute(
            "SELECT provider, policy_json, updated_at FROM identity_policies WHERE provider = ?",
            (provider.strip().lower() or _DEFAULT_PROVIDER,),
        ).fetchone()
    if row is None:
        return None
    payload = json.loads(str(row["policy_json"]))
    payload["provider"] = str(row["provider"])
    payload["updated_at"] = str(row["updated_at"])
    return payload


def list_identity_policies() -> list[dict[str, object]]:
    with closing(_connect()) as connection:
        rows = connection.execute(
            "SELECT provider, policy_json, updated_at FROM identity_policies ORDER BY provider ASC"
        ).fetchall()
    policies: list[dict[str, object]] = []
    for row in rows:
        payload = json.loads(str(row["policy_json"]))
        payload["provider"] = str(row["provider"])
        payload["updated_at"] = str(row["updated_at"])
        policies.append(payload)
    return policies


def resolve_identity_policy(provider: str) -> dict[str, object]:
    normalized_provider = provider.strip().lower() or _DEFAULT_PROVIDER
    generic = get_identity_policy(_DEFAULT_PROVIDER)
    specific = None if normalized_provider == _DEFAULT_PROVIDER else get_identity_policy(normalized_provider)
    merged: dict[str, object] = {}
    sources: list[str] = []
    for source_name, payload in (("generic", generic), (normalized_provider, specific)):
        if payload is None:
            continue
        sources.append(source_name)
        for key, value in payload.items():
            if key in {"provider", "updated_at"}:
                continue
            merged[key] = value
    merged["provider"] = normalized_provider
    merged["sources"] = sources
    return merged
