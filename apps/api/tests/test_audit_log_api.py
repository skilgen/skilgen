from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from apps.api.api.routes import orgs
from packages.db.models import AuditEvent


class Result:
    def __init__(self, scalar: int | None = None, rows: list[Any] | None = None) -> None:
        self._scalar = scalar
        self._rows = rows or []

    def scalar(self) -> int | None:
        return self._scalar

    def scalars(self) -> "Result":
        return self

    def all(self) -> list[Any]:
        return self._rows


class Db:
    def __init__(self, rows: list[Any]) -> None:
        self.rows = rows
        self.calls = 0

    async def execute(self, _statement: object) -> Result:
        self.calls += 1
        if "count" in str(_statement).lower() and self.rows and isinstance(self.rows[0], AuditEvent):
            return Result(scalar=len(self.rows))
        return Result(rows=self.rows)


def _event(
    event_id: str,
    *,
    actor: str | None = "ravi",
    event_type: str = "policy.updated",
    severity: str = "info",
    repo_id: str | None = "repo_1",
    created_at: datetime | None = None,
) -> AuditEvent:
    return AuditEvent(
        id=event_id,
        org_id="org_1",
        event_type=event_type,
        action="updated",
        actor_login=actor,
        repo_id=repo_id,
        repo_name="api" if repo_id else None,
        summary=f"{event_type} by {actor or 'system'}",
        severity=severity,
        metadata_json={"event_id": event_id},
        created_at=created_at or datetime(2026, 4, 28, 12, 0, 0),
    )


def test_audit_log_actor_filter_maps_query_param(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    original = orgs._audit_log_filters

    def wrapper(org_id: str, **kwargs):
        captured.update(kwargs)
        return original(org_id, **kwargs)

    monkeypatch.setattr(orgs, "_audit_log_filters", wrapper)
    response = asyncio.run(orgs.get_audit_log("org_1", actor="ravi", limit=50, offset=0, db=Db([_event("evt_1")]), current_org_id="org_1"))

    assert captured["actor"] == "ravi"
    assert response.events[0].actor_login == "ravi"


def test_audit_log_severity_filter_maps_query_param(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    original = orgs._audit_log_filters

    def wrapper(org_id: str, **kwargs):
        captured.update(kwargs)
        return original(org_id, **kwargs)

    monkeypatch.setattr(orgs, "_audit_log_filters", wrapper)
    response = asyncio.run(orgs.get_audit_log("org_1", severity="critical", limit=50, offset=0, db=Db([_event("evt_1", severity="critical")]), current_org_id="org_1"))

    assert captured["severity"] == "critical"
    assert response.events[0].severity == "critical"


def test_audit_log_date_from_excludes_older_rows(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    original = orgs._audit_log_filters

    def wrapper(org_id: str, **kwargs):
        captured.update(kwargs)
        return original(org_id, **kwargs)

    monkeypatch.setattr(orgs, "_audit_log_filters", wrapper)
    date_from = datetime(2026, 4, 28, 0, 0, 0)
    rows = [_event("new", created_at=datetime(2026, 4, 28, 12, 0, 0))]
    response = asyncio.run(orgs.get_audit_log("org_1", date_from=date_from, limit=50, offset=0, db=Db(rows), current_org_id="org_1"))

    assert captured["date_from"] == date_from
    assert [event.id for event in response.events] == ["new"]


def test_audit_log_export_csv_content_type_and_all_rows() -> None:
    rows = [
        _event("evt_1", actor="ravi", event_type="policy.updated"),
        _event("evt_2", actor=None, event_type="settings.changed", severity="warning"),
    ]
    response = asyncio.run(orgs.export_audit_log("org_1", db=Db(rows), current_org_id="org_1"))

    async def read_body() -> str:
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            chunks.append(chunk.encode("utf-8") if isinstance(chunk, str) else chunk)
        return b"".join(chunks).decode("utf-8")

    body = asyncio.run(read_body())
    assert response.media_type == "text/csv"
    assert response.headers["content-disposition"] == "attachment; filename=audit-log.csv"
    assert "timestamp,actor,event_type,severity,repo,description,metadata" in body
    assert "policy.updated" in body
    assert "settings.changed" in body


def test_audit_log_event_types_are_deduped() -> None:
    db = Db(["policy.updated", "policy.updated", "settings.changed"])

    result = asyncio.run(orgs.get_audit_log_event_types("org_1", db=db, current_org_id="org_1"))

    assert result == ["policy.updated", "settings.changed"]
