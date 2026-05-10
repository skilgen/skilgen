from __future__ import annotations

import asyncio
from datetime import datetime
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

from apps.api.api.v8.audit.router import (
    EvidencePackageRequest,
    ExportRequest,
    PublishRootRequest,
    _event_payload,
    _event_response,
    _filters,
    _write_raw_ndjson,
    create_evidence_package,
    create_export,
    export_report,
    get_agent_compliance_audit,
    get_event_log,
    get_report,
    get_worm_targets,
    list_reports,
    publish_root,
)
from packages.db.models import AuditEvent
import pytest


audit_router = importlib.import_module("apps.api.api.v8.audit.router")


def _event(event_id: str = "evt_1") -> AuditEvent:
    return AuditEvent(
        id=event_id,
        org_id="org_1",
        event_type="policy.violation_detected",
        action="blocked",
        actor_login="ravi",
        actor_ip="127.0.0.1",
        repo_id="repo_1",
        repo_name="payments",
        skill_id="skill_1",
        skill_domain="security",
        resource_type="repo",
        resource_id="repo_1",
        summary="Blocked privileged action",
        severity="critical",
        metadata_json={"sensitivity_tier": "regulated"},
        created_at=datetime(2026, 5, 1, 12, 0, 0),
    )


def _agent_event(event_id: str = "evt_agent_1") -> AuditEvent:
    return AuditEvent(
        id=event_id,
        org_id="org_1",
        event_type="agent.compliance",
        action="observed",
        actor_login="ravi",
        actor_ip=None,
        repo_id="repo_1",
        repo_name="acme/payments",
        skill_id=None,
        skill_domain=None,
        resource_type="codex_cli",
        resource_id="session_1",
        summary="Codex CLI full-access session observed",
        severity="warning",
        metadata_json={
            "provider": "Codex CLI",
            "model": "gpt-5.2",
            "intelligence_tier": "very-high",
            "access_scope": "full-access",
            "policy_decision": "allow-with-review",
            "source_envelope_hash": "abc123",
            "raw_prompt": "must not be returned",
        },
        created_at=datetime(2026, 5, 1, 12, 0, 0),
    )


class Db:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    def add(self, item) -> None:
        self.added = item


class Result:
    def __init__(self, *, scalar_value=None, rows=None) -> None:
        self._scalar_value = scalar_value
        self._rows = rows or []

    def scalar(self):
        return self._scalar_value

    def scalars(self):
        return self

    def all(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None

    def __iter__(self):
        return iter(self._rows)


class ExecuteDb(Db):
    def __init__(self, results) -> None:
        super().__init__()
        self.results = list(results)

    async def execute(self, _statement, _params=None):
        return self.results.pop(0)


def test_event_payload_and_response_include_chain() -> None:
    event = _event()
    payload = _event_payload(event)
    assert payload["metadata"] == {"sensitivity_tier": "regulated"}
    response = _event_response(
        event,
        SimpleNamespace(event_id=event.id, sequence=0, event_hash="a" * 64, previous_hash="0" * 64, root_hash="b" * 64, merkle_proof=[]),
    )
    assert response.chain is not None
    assert response.chain.root_hash == "b" * 64


def test_filters_build_expected_sqlalchemy_clauses() -> None:
    filters = _filters(
        "org_1",
        event_type="policy.violation_detected",
        actor="ravi",
        repo_id="repo_1",
        severity="critical",
        date_from=datetime(2026, 5, 1),
        date_to=datetime(2026, 5, 2),
    )
    rendered = " ".join(str(item) for item in filters)
    assert "audit_events.org_id" in rendered
    assert "audit_events.event_type" in rendered
    assert "lower(audit_events.actor_login)" in rendered
    assert len(filters) == 7


def test_raw_ndjson_export_rejects_invalid_destination() -> None:
    with pytest.raises(Exception) as exc:
        _write_raw_ndjson("https://example.com/audit.ndjson", [_event()])
    assert "raw NDJSON destination" in str(exc.value)


def test_create_export_logs_audit_event_for_each_format(monkeypatch, tmp_path: Path) -> None:
    async def allow(*_args, **_kwargs) -> None:
        return None

    async def rows(*_args, **_kwargs):
        return [_event()]

    calls: list[dict[str, object]] = []

    async def emit(_db, _org_id, event_type, action, summary, **kwargs):
        calls.append({"event_type": event_type, "action": action, "summary": summary, **kwargs})

    monkeypatch.setattr(audit_router, "_assert_enabled", allow)
    monkeypatch.setattr(audit_router, "_export_rows", rows)
    monkeypatch.setattr(audit_router.audit, "emit", emit)
    request = SimpleNamespace(headers={})

    for format_name in ["csv", "json", "splunk_hec", "datadog_cloud_siem", "sumo_logic", "microsoft_sentinel"]:
        db = Db()
        response = asyncio.run(create_export("org_1", ExportRequest(format=format_name), request, db, "org_1"))
        assert response.event_count == 1
        assert response.audit_event_logged is True
        assert db.committed is True

    raw_path = tmp_path / "audit.ndjson"
    raw_db = Db()
    raw = asyncio.run(create_export("org_1", ExportRequest(format="raw_ndjson_s3", destination=f"file://{raw_path}"), request, raw_db, "org_1"))
    assert raw.content_type == "application/x-ndjson"
    assert "policy.violation_detected" in raw_path.read_text(encoding="utf-8")

    assert len(calls) == 7
    assert {call["event_type"] for call in calls} == {"audit.export.created"}


def test_event_log_and_report_endpoints_with_fake_db(monkeypatch) -> None:
    event = _event()
    chain_row = SimpleNamespace(event_id=event.id, sequence=0, event_hash="a" * 64, previous_hash="0" * 64, root_hash="b" * 64, merkle_proof=[])

    async def allow(*_args, **_kwargs) -> None:
        return None

    async def ensure(*_args, **_kwargs):
        return [chain_row]

    monkeypatch.setattr(audit_router, "_assert_enabled", allow)
    monkeypatch.setattr(audit_router, "_ensure_chain", ensure)
    db = ExecuteDb([Result(scalar_value=1), Result(rows=[event])])
    response = asyncio.run(get_event_log("org_1", limit=10, db=db, current_org_id="org_1"))
    assert response.total == 1
    assert response.events[0].chain.root_hash == "b" * 64

    row = SimpleNamespace(
        _mapping={
            "id": "evt_1",
            "event_type": "analysis.completed",
            "action": "completed",
            "actor_login": "ravi",
            "repo_name": "payments",
            "skill_domain": None,
            "severity": "info",
            "summary": "AI change",
            "created_at": datetime(2026, 5, 1, 12, 0, 0),
            "commit_sha": "abc",
            "policy_id": None,
            "policy_decision": "allow",
            "control_mapping": "SOC2 CC8.1",
            "agent_runtime": "codex",
            "sensitivity_tier": "regulated",
        }
    )
    report_db = ExecuteDb([Result(rows=[row])])
    report = asyncio.run(get_report("org_1", "ai-assisted-change-log", db=report_db, current_org_id="org_1"))
    assert report.rows[0].commit_sha == "abc"
    assert asyncio.run(list_reports("org_1", db=ExecuteDb([]), current_org_id="org_1"))[0].id == "ai-assisted-change-log"


def test_agent_compliance_audit_returns_metadata_only_events(monkeypatch) -> None:
    async def allow(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(audit_router, "_assert_enabled", allow)
    response = asyncio.run(get_agent_compliance_audit("org_1", window_days=30, limit=100, db=ExecuteDb([Result(rows=[_agent_event()])]), current_org_id="org_1"))

    assert response.content_retention == "metadata-only"
    assert response.events[0].provider == "Codex CLI"
    assert response.events[0].intelligence_tier == "very-high"
    assert response.events[0].source_envelope_hash == "abc123"
    assert not hasattr(response.events[0], "raw_prompt")


def test_agent_compliance_audit_filters_provider_after_metadata_projection(monkeypatch) -> None:
    async def allow(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(audit_router, "_assert_enabled", allow)
    response = asyncio.run(
        get_agent_compliance_audit(
            "org_1",
            provider="Cursor",
            window_days=30,
            limit=100,
            db=ExecuteDb([Result(rows=[_agent_event()])]),
            current_org_id="org_1",
        )
    )

    assert response.total == 0


def test_report_export_publish_root_and_evidence_queue(monkeypatch) -> None:
    async def allow(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(audit_router, "_assert_enabled", allow)
    row = SimpleNamespace(
        _mapping={
            "id": "evt_1",
            "event_type": "analysis.completed",
            "action": "completed",
            "actor_login": "ravi",
            "repo_name": "payments",
            "skill_domain": None,
            "severity": "info",
            "summary": "AI change",
            "created_at": datetime(2026, 5, 1, 12, 0, 0),
            "commit_sha": "abc",
            "policy_id": None,
            "policy_decision": "allow",
            "control_mapping": "SOC2 CC8.1",
            "agent_runtime": "codex",
            "sensitivity_tier": "regulated",
        }
    )
    exported = asyncio.run(export_report("org_1", "ai-assisted-change-log", format="csv", db=ExecuteDb([Result(rows=[row])]), current_org_id="org_1"))
    assert exported.media_type == "text/csv"

    chain_rows = [
        SimpleNamespace(sequence=0, root_hash="a" * 64, merkle_proof=[]),
        SimpleNamespace(sequence=1, root_hash="b" * 64, merkle_proof=[{"side": "left", "hash": "a" * 64}]),
    ]

    async def ensure(*_args, **_kwargs):
        return chain_rows

    def publish(document, provider=None):
        assert "payload" not in document
        assert document["storage_provider"] == "gcs_bucket_lock"
        assert provider == "gcs_bucket_lock"
        return "gs://locked/audit-roots/org_1/root.json", "pending"

    monkeypatch.setattr(audit_router, "_ensure_chain", ensure)
    monkeypatch.setattr(audit_router, "publish_worm_root", publish)
    root_db = ExecuteDb([])
    root = asyncio.run(publish_root("org_1", PublishRootRequest(cadence="hourly", storage_provider="gcs_bucket_lock"), db=root_db, current_org_id="org_1"))
    assert root.status == "pending"
    assert root.storage_provider == "gcs_bucket_lock"
    assert root_db.committed is True

    fake_task = SimpleNamespace(apply_async=lambda **_kwargs: None)
    monkeypatch.setitem(sys.modules, "apps.worker.worker", SimpleNamespace(build_evidence_package_task=fake_task))
    evidence_db = Db()
    evidence = asyncio.run(
        create_evidence_package(
            "org_1",
            EvidencePackageRequest(control="SOC2 CC8.1", period_start=datetime(2026, 1, 1), period_end=datetime(2026, 3, 31)),
            db=evidence_db,
            current_org_id="org_1",
        )
    )
    assert evidence.queued is True
    assert evidence_db.committed is True


def test_worm_target_endpoint_lists_three_root_only_targets(monkeypatch) -> None:
    async def allow(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(audit_router, "_assert_enabled", allow)
    response = asyncio.run(get_worm_targets("org_1", db=ExecuteDb([]), current_org_id="org_1"))

    assert [target.provider for target in response] == ["s3_object_lock", "gcs_bucket_lock", "azure_immutable_blob"]
    assert all(target.content_retention == "root-and-proof-only" for target in response)
