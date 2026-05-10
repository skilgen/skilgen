from __future__ import annotations

import asyncio
import importlib
from types import SimpleNamespace

import sqlalchemy as sa
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from fastapi.testclient import TestClient
from starlette.requests import Request

from apps.api.api.index import app
from apps.api.api.auth import get_current_org_id
from apps.api.api.v8.flags import request_flag_cache
from apps.api.api.v8.settings.rbac import has_permission, matches_scope_expression, permission_matches
from packages.db.database import get_db
from packages.db.models import Org


rbac_migration = importlib.import_module("apps.api.alembic.versions.20260505_0002_settings_rbac")
settings_router = importlib.import_module("apps.api.api.v8.settings.router")


class Result:
    def __init__(self, rows: list[tuple[object, object]]) -> None:
        self._rows = rows

    def all(self) -> list[tuple[object, object]]:
        return self._rows


class Db:
    def __init__(self, rows: list[tuple[object, object]]) -> None:
        self.rows = rows

    async def execute(self, _stmt: object) -> Result:
        return Result(self.rows)


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

    async def commit(self) -> None:
        self.committed = True


def test_v8_settings_router_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/settings/rbac" in paths
    assert "/v8/orgs/{org_id}/settings/notifications/digest" in paths
    assert "/v8/orgs/{org_id}/settings/admin-audit" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/agent-compliance" in paths
    assert "/v8/orgs/{org_id}/settings/connectors/{connector_id}/sync" in paths


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
    codex = next(item for item in response["connectors"] if item["id"] == "codex-cli")
    assert stored["cursor"] == "next-cursor"
    assert stored["last_sync_status"] == "pending"
    assert stored["last_sync_mode"] == "dry-run"
    assert codex["connected"] is False
    assert db.committed is True


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
