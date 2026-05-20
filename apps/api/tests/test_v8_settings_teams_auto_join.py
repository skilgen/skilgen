from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.index import app
from apps.api.api.v8.flags import request_flag_cache
from packages.db.database import get_db
from packages.db.models import Org, Role, RoleBinding


class Result:
    def __init__(self, rows: list[tuple[object, object]]) -> None:
        self._rows = rows

    def all(self) -> list[tuple[object, object]]:
        return self._rows


class TeamsDb:
    def __init__(self, org: Org, role: Role, binding: RoleBinding) -> None:
        self.org = org
        self.role = role
        self.binding = binding
        self.committed = False

    async def get(self, model: object, row_id: str) -> object | None:
        if model is Org and str(row_id) == str(self.org.id):
            return self.org
        return None

    async def execute(self, stmt: Any) -> Result:
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        if "FROM roles" in compiled and "role_bindings" in compiled:
            return Result([(self.role, self.binding)])
        return Result([])

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None

    def add(self, _item: object) -> None:
        return None


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("IA_V8_DEFAULT", "true")

    org = Org(
        id="org_acme",
        github_org_id=-1,
        login="acme.test",
        name="Acme",
        plan="free",
        seat_count=0,
        auto_join_domain=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    role = Role(
        id="role_owner",
        org_id=org.id,
        name="owner",
        description="",
        permissions=["*"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    binding = RoleBinding(
        id="binding_owner",
        org_id=org.id,
        role_id=role.id,
        principal_type="user",
        principal_id="owner@acme.test",
        scope_expression={},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db = TeamsDb(org, role, binding)

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: org.id
    app.dependency_overrides[get_current_user] = lambda: {"email": "owner@acme.test"}
    app.dependency_overrides[request_flag_cache] = lambda: None

    yield TestClient(app), db

    app.dependency_overrides.clear()
    os.environ.pop("IA_V8_DEFAULT", None)


def test_put_auto_join_domain_updates_org(client):  # type: ignore[no-untyped-def]
    http, db = client
    response = http.put(f"/v8/orgs/{db.org.id}/settings/teams/auto-join-domain", json={"enabled": False})
    assert response.status_code == 200
    assert response.json()["auto_join_domain"] is False
    assert db.org.auto_join_domain is False
    assert db.committed is True
