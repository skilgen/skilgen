from __future__ import annotations

import asyncio
import importlib
from types import SimpleNamespace

import sqlalchemy as sa
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext

from apps.api.api.index import app
from apps.api.api.v8.settings.rbac import has_permission, matches_scope_expression, permission_matches


rbac_migration = importlib.import_module("apps.api.alembic.versions.20260505_0002_settings_rbac")


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


def test_v8_settings_router_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/settings/rbac" in paths
    assert "/v8/orgs/{org_id}/settings/notifications/digest" in paths
    assert "/v8/orgs/{org_id}/settings/admin-audit" in paths


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
