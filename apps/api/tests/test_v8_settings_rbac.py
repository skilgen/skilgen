from __future__ import annotations

import asyncio
import base64
import importlib
import json
from datetime import datetime
from types import SimpleNamespace

import sqlalchemy as sa
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from starlette.requests import Request

from apps.api.api.index import app
from apps.api.api.auth import get_current_org_id
from apps.api.api.v8.flags import request_flag_cache
from apps.api.api.v8.settings.rbac import PERMISSIONS, has_permission, matches_scope_expression, permission_matches
from packages.db.database import get_db
from packages.db.models import AuditEvent, Job, Org


rbac_migration = importlib.import_module("apps.api.alembic.versions.20260505_0002_settings_rbac")
settings_router = importlib.import_module("apps.api.api.v8.settings.router")


class Result:
    def __init__(self, rows: list[tuple[object, object]]) -> None:
        self._rows = rows

    def all(self) -> list[tuple[object, object]]:
        return self._rows

    def scalar_one_or_none(self) -> object | None:
        return self._rows[0][0] if self._rows else None

    def scalars(self):
        return self


class Db:
    def __init__(self, rows: list[tuple[object, object]]) -> None:
        self.rows = rows

    async def execute(self, _stmt: object) -> Result:
        return Result(self.rows)


class EventDb:
    def __init__(self, events: list[AuditEvent]) -> None:
        self.events = events
        self.statements: list[str] = []
        self.limits: list[int | None] = []

    async def execute(self, stmt: object) -> Result:
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        limit_clause = getattr(stmt, "_limit_clause", None)
        limit = getattr(limit_clause, "value", None)
        rows = self.events
        if "audit_events.severity = 'warning'" in compiled:
            rows = [event for event in rows if event.severity == "warning"]
        if "audit_events.actor_login" in compiled and "ravi" in compiled:
            rows = [event for event in rows if event.actor_login and "ravi" in event.actor_login]
        self.statements.append(compiled)
        self.limits.append(limit)
        return Result(rows[:limit] if limit is not None else rows)


class OrgDb:
    def __init__(self, org: Org) -> None:
        self.org = org
        self.committed = False
        self.added: list[object] = []

    async def get(self, model: object, row_id: str) -> Org | None:
        assert model is Org
        assert row_id == self.org.id
        return self.org

    def add(self, item: object) -> None:
        self.added.append(item)

    async def execute(self, _stmt: object) -> Result:
        return Result([])

    async def commit(self) -> None:
        self.committed = True


def test_v8_settings_router_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/settings/rbac" in paths
    assert "/v8/orgs/{org_id}/settings/notifications/digest" in paths
    assert "/v8/orgs/{org_id}/settings/admin-audit" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/agent-compliance" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/{connector_id}/sync" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-events" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-jobs" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-jobs/{job_id}" in paths
    assert "settings.admin_audit.read" in PERMISSIONS


def test_agent_compliance_connector_endpoint_returns_metadata_state(monkeypatch) -> None:
    org = Org(id="org-1", github_org_id=1, login="acme", name="Acme", settings={
        "v8_agent_compliance_connectors": {
            "codex-cli": {
                "enabled": True,
                "source_types": ["agent sessions", "model tier"],
                "scopes": ["audit.read"],
                "last_sync_status": "pending",
                "content_retention": "metadata-only",
                "updated_at": "2026-05-10T19:10:00",
            }
        }
    })

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def db_override():
        yield OrgDb(org)

    app.dependency_overrides[get_current_org_id] = lambda: "org-1"
    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[request_flag_cache] = lambda: None
    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    try:
        response = TestClient(app).get("/v8/orgs/org-1/settings/connectors/agent-compliance")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    codex = next(item for item in payload["connectors"] if item["id"] == "codex-cli")
    assert payload["content_retention_default"] == "metadata-only"
    assert payload["configured_count"] == 1
    assert codex["enabled"] is True
    assert codex["content_retention"] == "metadata-only"


def test_admin_audit_returns_operator_rollups(monkeypatch) -> None:
    events = [
        AuditEvent(
            id="evt-1",
            org_id="org-1",
            event_type="settings.rbac_role_created",
            action="created",
            actor_login="ravi",
            resource_type="role",
            resource_id="role-1",
            summary="Created RBAC role Admin",
            severity="info",
            created_at=datetime(2026, 5, 11, 10, 0, 0),
        ),
        AuditEvent(
            id="evt-2",
            org_id="org-1",
            event_type="settings.agent_compliance_connector_configured",
            action="updated",
            actor_login="maya",
            resource_type="connector",
            resource_id="codex-cli",
            summary="Configured connector",
            severity="warning",
            created_at=datetime(2026, 5, 11, 9, 0, 0),
        ),
        AuditEvent(
            id="evt-3",
            org_id="org-1",
            event_type="member.invited",
            action="invited",
            actor_login="maya",
            resource_type="member",
            resource_id="member-1",
            summary="Invited member",
            severity="warning",
            created_at=datetime(2026, 5, 11, 8, 0, 0),
        ),
    ]

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)

    db = EventDb(events)
    response = asyncio.run(
        settings_router.get_admin_audit(
            "org-1",
            severity="warning",
            limit=1,
            db=db,
            current_org_id="org-1",
        )
    )

    assert response["summary"] == {"events": 2, "actors": 1, "critical": 0, "warnings": 2, "resource_types": 2}
    assert response["filters"]["severity"] == "warning"
    assert response["filters"]["limit"] == 1
    assert response["rollup"] == {"source_events": 2, "limit": 5000, "truncated": False}
    assert response["severity_counts"] == {"info": 0, "warning": 2, "critical": 0}
    assert {"key": "connector", "label": "connector", "count": 1} in response["resource_types"]
    assert len(response["events"]) == 1
    assert response["events"][0]["event_type"] == "settings.agent_compliance_connector_configured"
    assert db.limits == [5001, 1]
    assert all("audit_events.severity = 'warning'" in statement for statement in db.statements)


def test_admin_audit_exposes_truncated_rollup_metadata() -> None:
    events = [
        AuditEvent(
            id=f"evt-{index}",
            org_id="org-1",
            event_type="settings.rbac_role_created",
            action="created",
            actor_login="ravi",
            resource_type="role",
            resource_id=f"role-{index}",
            summary="Created RBAC role",
            severity="warning",
            created_at=datetime(2026, 5, 11, 10, 0, 0),
        )
        for index in range(5000)
    ]
    payload = settings_router._admin_audit_payload(
        events=events,
        page_events=events[:1],
        rollup_truncated=True,
        window_days=30,
        actor=None,
        event_type=None,
        resource_type=None,
        severity="warning",
        limit=1,
    )

    assert payload["summary"]["events"] == 5000
    assert payload["rollup"] == {"source_events": 5000, "limit": 5000, "truncated": True}


def test_configure_agent_compliance_connector_persists_metadata_only_state(monkeypatch) -> None:
    org = Org(id="org-1", github_org_id=1, login="acme", name="Acme", settings={})
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def emit(*args, **kwargs):
        return None

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    monkeypatch.setattr(settings_router.audit, "emit", emit)

    request = Request({"type": "http", "headers": []})
    response = asyncio.run(
        settings_router.configure_agent_compliance_connector(
            "org-1",
            settings_router.AgentComplianceConnectorPayload(
                connector_id="codex-cli",
                enabled=True,
                source_types=["agent sessions", "model tier"],
                scopes=["audit.read", "policy.evaluate"],
            ),
            request,
            db=db,
            current_org_id="org-1",
        )
    )

    stored = org.settings["v8_agent_compliance_connectors"]["codex-cli"]
    assert response["configured_count"] == 1
    assert stored["enabled"] is True
    assert stored["content_retention"] == "metadata-only"
    assert "secret" not in stored
    assert db.committed is True


def test_request_agent_compliance_connector_sync_updates_cursor_state(monkeypatch) -> None:
    org = Org(
        id="org-1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "codex-cli": {
                    "enabled": True,
                    "source_types": ["agent sessions"],
                    "scopes": ["audit.read"],
                    "cursor": "old-cursor",
                    "last_sync_status": "success",
                    "content_retention": "metadata-only",
                }
            }
        },
    )
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def emit(*args, **kwargs):
        return None

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    monkeypatch.setattr(settings_router.audit, "emit", emit)

    response = asyncio.run(
        settings_router.request_agent_compliance_connector_sync(
            "org-1",
            "codex-cli",
            settings_router.AgentComplianceSyncPayload(cursor="next-cursor", dry_run=True),
            Request({"type": "http", "headers": []}),
            db=db,
            current_org_id="org-1",
        )
    )

    stored = org.settings["v8_agent_compliance_connectors"]["codex-cli"]
    assert stored["cursor"] == "next-cursor"
    assert stored["last_sync_status"] == "pending"
    assert stored["last_sync_mode"] == "dry-run"
    assert stored["last_sync_plan"]["pagination_strategy"] == "cursor-resume"
    assert stored["last_sync_plan"]["provider_adapter_required"] is True
    assert stored["last_sync_plan"]["source_record_type"] == "operational-telemetry"
    assert response.connector_id == "codex-cli"
    assert response.cursor == "next-cursor"
    assert response.next_cursor_required is True
    assert response.ready_for_provider_pull is True
    assert response.content_retention == "metadata-only"
    assert db.committed is True


def test_request_agent_compliance_connector_sync_marks_formal_compliance_retention(monkeypatch) -> None:
    org = Org(
        id="org-1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "openai-compliance": {
                    "enabled": True,
                    "source_types": ["audit logs"],
                    "scopes": ["audit.read"],
                    "content_retention": "metadata-only",
                }
            }
        },
    )
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def emit(*args, **kwargs):
        return None

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    monkeypatch.setattr(settings_router.audit, "emit", emit)

    response = asyncio.run(
        settings_router.request_agent_compliance_connector_sync(
            "org-1",
            "openai-compliance",
            settings_router.AgentComplianceSyncPayload(dry_run=True),
            Request({"type": "http", "headers": []}),
            db=db,
            current_org_id="org-1",
        )
    )

    stored = org.settings["v8_agent_compliance_connectors"]["openai-compliance"]
    assert response.source_record_type == "formal-compliance"
    assert response.retention_window_days == 30
    assert response.pagination_strategy == "cursor-resume"
    assert "30-day compliance-log retention window" in " ".join(response.next_actions)
    assert stored["last_sync_plan"]["content_retention"] == "metadata-only"


def test_agent_compliance_catalog_covers_required_coding_agent_sources() -> None:
    connectors = {str(item["id"]): item for item in settings_router._agent_compliance_registry()}

    for connector_id in {"cursor", "windsurf", "github-copilot", "gitlab-duo", "codex-cli", "claude-code", "aider"}:
        connector = connectors[connector_id]
        assert connector["category"] == "coding-agent"
        assert connector["source_type"]
        assert connector["description"]
        assert {"agent sessions", "model usage"} & set(connector["capabilities"])

    internal_mcp = connectors["internal-mcp"]
    assert internal_mcp["category"] == "runtime"
    assert "mcp calls" in internal_mcp["capabilities"]
    assert "approval decisions" in internal_mcp["capabilities"]

    for connector_id in {"github-actions", "gitlab-ci", "circleci"}:
        connector = connectors[connector_id]
        assert connector["category"] == "ci-cd"
        assert connector["source_type"]
        assert connector["description"]
        assert "jobs" in connector["capabilities"]
        assert "test outcomes" in connector["capabilities"]


def test_connector_catalog_covers_required_git_provider_sources() -> None:
    connectors = {str(item["id"]): item for item in settings_router.connector_registry()}

    for connector_id in {"github", "gitlab", "bitbucket"}:
        connector = connectors[connector_id]
        assert connector["category"] == "source-control"
        assert connector["source_type"]
        assert connector["description"]
        assert "webhooks" in connector["capabilities"]
        assert "commit signatures" in connector["capabilities"]
        assert "AI attribution headers" in connector["capabilities"]

    assert "merge requests" in connectors["gitlab"]["capabilities"]
    assert "pull requests" in connectors["bitbucket"]["capabilities"]


def test_request_agent_compliance_connector_sync_requires_enabled_connector(monkeypatch) -> None:
    org = Org(id="org-1", github_org_id=1, login="acme", name="Acme", settings={})
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)

    try:
        asyncio.run(
            settings_router.request_agent_compliance_connector_sync(
                "org-1",
                "codex-cli",
                settings_router.AgentComplianceSyncPayload(),
                Request({"type": "http", "headers": []}),
                db=db,
                current_org_id="org-1",
            )
        )
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 409
    else:
        raise AssertionError("Expected sync request to require enabled connector")


def test_request_agent_compliance_connector_sync_rejects_ingestion_mode(monkeypatch) -> None:
    org = Org(
        id="org-1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "codex-cli": {
                    "enabled": True,
                    "source_types": ["agent sessions"],
                    "scopes": ["audit.read"],
                    "cursor": "old-cursor",
                    "last_sync_status": "success",
                    "content_retention": "metadata-only",
                }
            }
        },
    )
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)

    try:
        asyncio.run(
            settings_router.request_agent_compliance_connector_sync(
                "org-1",
                "codex-cli",
                settings_router.AgentComplianceSyncPayload(dry_run=False),
                Request({"type": "http", "headers": []}),
                db=db,
                current_org_id="org-1",
            )
        )
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400
    else:
        raise AssertionError("Expected sync readiness to reject ingestion mode")


def test_ingest_agent_compliance_events_normalizes_every_metric_metadata_only(monkeypatch) -> None:
    org = Org(
        id="org-1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "codex-cli": {
                    "enabled": True,
                    "source_types": ["agent sessions"],
                    "scopes": ["audit.read"],
                    "cursor": "old-cursor",
                    "last_sync_status": "success",
                    "content_retention": "metadata-only",
                    "total_ingested_count": 2,
                }
            }
        },
    )
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def emit(*args, **kwargs):
        return None

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    monkeypatch.setattr(settings_router.audit, "emit", emit)

    response = asyncio.run(
        settings_router.ingest_agent_compliance_events(
            "org-1",
            "codex-cli",
            settings_router.AgentComplianceIngestPayload(
                cursor="old-cursor",
                next_cursor="new-cursor",
                events=[
                    settings_router.AgentComplianceEventPayload(
                        provider_event_id="evt-1",
                        actor_login="ravi",
                        provider="OpenAI Compliance Platform",
                        model="gpt-5.2",
                        intelligence_tier="very-high",
                        access_scope="full-access",
                        full_access=True,
                        autonomous_access=True,
                        tool_permissions=["shell", "apply_patch"],
                        tool_calls=3,
                        mcp_tools=["github"],
                        repo_id="repo-1",
                        repo_name="skillayer/api",
                        file_targets=["apps/api/api/v8/settings/router.py"],
                        policy_decision="require_approval",
                        approval_status="approved",
                        violations=["raw-content-retention-disabled"],
                        warnings=2,
                        tokens_input=1200,
                        tokens_output=450,
                        cost_usd=0.042,
                        latency_ms=881,
                        error_count=1,
                        session_id="session-1",
                        metadata={"prompt": "do not store", "safe_metric": "kept"},
                    )
                ],
            ),
            Request({"type": "http", "headers": []}),
            db=db,
            current_org_id="org-1",
        )
    )

    event = next(item for item in db.added if isinstance(item, AuditEvent))
    stored = org.settings["v8_agent_compliance_connectors"]["codex-cli"]
    assert response.ingested_count == 1
    assert response.next_cursor == "new-cursor"
    assert response.metrics["tokens_input"] == 1200
    assert response.metrics["tokens_output"] == 450
    assert response.metrics["cost_usd"] == 0.042
    assert response.metrics["full_access_events"] == 1
    assert response.metrics["autonomous_access_events"] == 1
    assert response.metrics["tool_permission_events"] == 6
    assert stored["last_ingested_count"] == 1
    assert stored["total_ingested_count"] == 3
    assert stored["last_provider_event_id"] == "evt-1"
    assert event.event_type == "agent.compliance"
    assert event.severity == "critical"
    assert event.metadata_json["content_retention"] == "metadata-only"
    assert event.metadata_json["redaction_state"] == "raw-content-dropped"
    assert event.metadata_json["safe_metric"] == "kept"
    assert "prompt" not in event.metadata_json
    assert "source_envelope_hash" in event.metadata_json


def test_ingest_agent_compliance_events_falls_back_to_request_actor(monkeypatch) -> None:
    org = Org(
        id="org-1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "codex-cli": {
                    "enabled": True,
                    "source_types": ["agent sessions"],
                    "scopes": ["audit.read"],
                    "cursor": None,
                    "content_retention": "metadata-only",
                    "total_ingested_count": 0,
                }
            }
        },
    )
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def emit(*args, **kwargs):
        return None

    def token_for(actor: str) -> str:
        header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
        payload = base64.urlsafe_b64encode(json.dumps({"preferred_username": actor}).encode()).decode().rstrip("=")
        return f"{header}.{payload}.x"

    actor_login = "ravi@example.com"
    request = Request(
        {
            "type": "http",
            "headers": [(b"authorization", f"Bearer {token_for(actor_login)}".encode())],
        }
    )

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    monkeypatch.setattr(settings_router.audit, "emit", emit)

    response = asyncio.run(
        settings_router.ingest_agent_compliance_events(
            "org-1",
            "codex-cli",
            settings_router.AgentComplianceIngestPayload(
                cursor=None,
                next_cursor=None,
                events=[
                    settings_router.AgentComplianceEventPayload(
                        provider_event_id="evt-actor-fallback",
                        provider="Codex CLI",
                        actor_login=None,
                        access_scope="full-access",
                    )
                ],
            ),
            request,
            db=db,
            current_org_id="org-1",
        )
    )

    event = next(item for item in db.added if isinstance(item, AuditEvent))
    assert response.ingested_count == 1
    assert event.actor_login == actor_login
    assert event.metadata_json["actor_login"] == actor_login


def test_queue_agent_compliance_ingest_job_tracks_cursor_page_state(monkeypatch) -> None:
    org = Org(
        id="org-1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "openai-compliance": {
                    "enabled": True,
                    "source_types": ["audit logs"],
                    "scopes": ["audit.read"],
                    "cursor": "cursor-1",
                    "content_retention": "metadata-only",
                }
            }
        },
    )
    db = OrgDb(org)

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def emit(*args, **kwargs):
        return None

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)
    monkeypatch.setattr(settings_router.audit, "emit", emit)

    response = asyncio.run(
        settings_router.queue_agent_compliance_ingest_job(
            "org-1",
            "openai-compliance",
            settings_router.AgentComplianceIngestPayload(
                cursor="cursor-1",
                next_cursor="cursor-2",
                events=[
                    settings_router.AgentComplianceEventPayload(
                        provider_event_id="evt-job-1",
                        provider="OpenAI Compliance Platform",
                    )
                ],
            ),
            Request({"type": "http", "headers": []}),
            BackgroundTasks(),
            db=db,
            current_org_id="org-1",
        )
    )

    job = next(item for item in db.added if isinstance(item, Job))
    stored = org.settings["v8_agent_compliance_connectors"]["openai-compliance"]
    assert response.queued is True
    assert response.event_count == 1
    assert response.cursor == "cursor-1"
    assert response.next_cursor == "cursor-2"
    assert job.type == "agent_compliance.ingest"
    assert job.status == "queued"
    assert job.result_json["pagination_strategy"] == "cursor-resume"
    assert job.result_json["content_retention"] == "metadata-only"
    assert stored["last_sync_status"] == "queued"
    assert stored["last_sync_mode"] == "ingest-job"
    assert stored["last_ingest_job"]["job_id"] == job.id
    assert stored["last_ingest_job"]["event_count"] == 1


def test_agent_compliance_ingest_job_status_is_connector_scoped(monkeypatch) -> None:
    job = Job(
        id="job-1",
        org_id="org-1",
        type="agent_compliance.ingest",
        status="completed",
        result_json={
            "connector_id": "openai-compliance",
            "ingested_count": 3,
            "content_retention": "metadata-only",
        },
        created_at=datetime(2026, 5, 11, 8, 30, 0),
    )

    class JobDb:
        async def get(self, model: object, row_id: str) -> object | None:
            assert model is Job
            assert row_id == "job-1"
            return job

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    monkeypatch.setattr(settings_router, "_assert_v8_org", ensure_v8)

    response = asyncio.run(
        settings_router.get_agent_compliance_ingest_job(
            "org-1",
            "openai-compliance",
            "job-1",
            db=JobDb(),
            current_org_id="org-1",
        )
    )

    assert response.job_id == "job-1"
    assert response.status == "completed"
    assert response.result["ingested_count"] == 3


def test_scope_expression_positive_for_payments_repo() -> None:
    expression = {"all": [{"surface": "policy"}, {"repo": "payments/*"}]}
    context = {"surface": "policy", "repo": "payments/api"}

    assert matches_scope_expression(expression, context) is True


def test_scope_expression_negative_for_wrong_repo() -> None:
    expression = "surface:policy && repo:payments/*"
    context = {"surface": "policy", "repo": "growth/site"}

    assert matches_scope_expression(expression, context) is False


def test_scope_expression_supports_any_and_not() -> None:
    expression = {"all": [{"any": [{"team": "security"}, {"team": "platform"}]}, {"not": {"repo": "sandbox/*"}}]}

    assert matches_scope_expression(expression, {"team": "platform", "repo": "payments/api"}) is True
    assert matches_scope_expression(expression, {"team": "platform", "repo": "sandbox/demo"}) is False


def test_permission_wildcards_match_nested_permissions() -> None:
    assert permission_matches("settings.*", "settings.rbac.manage") is True
    assert permission_matches("settings.read", "settings.rbac.manage") is False


def test_has_permission_allows_matching_permission_and_scope() -> None:
    role = SimpleNamespace(permissions=["policy.approvals.approve"])
    binding = SimpleNamespace(scope_expression={"repo": "payments/*"})

    allowed = asyncio.run(
        has_permission(
            Db([(role, binding)]),
            org_id="org_1",
            principal_id="reviewer@example.com",
            permission="policy.approvals.approve",
            scope={"repo": "payments/api"},
        )
    )

    assert allowed is True


def test_has_permission_denies_out_of_scope_binding() -> None:
    role = SimpleNamespace(permissions=["policy.approvals.approve"])
    binding = SimpleNamespace(scope_expression={"repo": "payments/*"})

    allowed = asyncio.run(
        has_permission(
            Db([(role, binding)]),
            org_id="org_1",
            principal_id="reviewer@example.com",
            permission="policy.approvals.approve",
            scope={"repo": "growth/site"},
        )
    )

    assert allowed is False


def test_rbac_migration_up_and_down() -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("create table orgs (id varchar primary key)"))
        context = MigrationContext.configure(connection)
        ops = Operations(context)
        original_op = rbac_migration.op
        rbac_migration.op = ops
        try:
            rbac_migration.upgrade()
            inspector = sa.inspect(connection)
            assert "roles" in inspector.get_table_names()
            assert "role_bindings" in inspector.get_table_names()

            rbac_migration.downgrade()
            inspector = sa.inspect(connection)
            assert "roles" not in inspector.get_table_names()
            assert "role_bindings" not in inspector.get_table_names()
        finally:
            rbac_migration.op = original_op
