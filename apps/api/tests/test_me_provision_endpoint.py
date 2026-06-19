from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_user
from apps.api.api.index import app
from packages.db.database import get_db
from packages.db.models import Org, Role, RoleBinding, User
from packages.db.models.base import new_uuid


class Result:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def scalar_one_or_none(self) -> object | None:
        if not self._rows:
            return None
        return self._rows[0]


class ProvisionDb:
    def __init__(self) -> None:
        self.orgs: list[Org] = []
        self.users: list[User] = []
        self.roles: list[Role] = []
        self.bindings: list[RoleBinding] = []
        self.added: list[object] = []

    def add(self, item: object) -> None:
        self.added.append(item)

    async def flush(self) -> None:
        for item in list(self.added):
            if hasattr(item, "id") and (getattr(item, "id", None) is None):
                setattr(item, "id", new_uuid())
            if isinstance(item, Org):
                self.orgs.append(item)
            elif isinstance(item, User):
                self.users.append(item)
            elif isinstance(item, Role):
                self.roles.append(item)
            elif isinstance(item, RoleBinding):
                self.bindings.append(item)
        self.added.clear()

    async def get(self, model: object, row_id: str) -> object | None:
        if model is Org:
            return next((org for org in self.orgs if str(org.id) == str(row_id)), None)
        return None

    async def execute(self, stmt):  # type: ignore[no-untyped-def]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        if "FROM users" in compiled:
            if "users.email" in compiled:
                email = compiled.split("users.email = '", 1)[-1].split("'", 1)[0]
                return Result([user.id for user in self.users if user.email == email])
            return Result([user.id for user in self.users])
        if "FROM orgs" in compiled and "orgs.login" in compiled:
            login = compiled.split("orgs.login = '", 1)[-1].split("'", 1)[0]
            return Result([org for org in self.orgs if org.login == login])
        if "FROM roles" in compiled:
            org_id = compiled.split("roles.org_id = '", 1)[-1].split("'", 1)[0]
            name = compiled.split("roles.name = '", 1)[-1].split("'", 1)[0]
            return Result([role for role in self.roles if str(role.org_id) == org_id and role.name == name])
        if "FROM role_bindings" in compiled:
            return Result([binding.id for binding in self.bindings])
        return Result([])

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("IA_V8_DEFAULT", "true")

    db = ProvisionDb()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: {"email": "dev@acme.test", "org_id": None}

    yield TestClient(app), db

    app.dependency_overrides.clear()
    os.environ.pop("IA_V8_DEFAULT", None)


def test_me_provision_creates_org_and_user(client):  # type: ignore[no-untyped-def]
    http, db = client
    response = http.post("/me/provision", json={"source": "magic_link", "email": "dev@acme.test", "name": "Dev"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["created"]["org"] is True
    assert payload["user"]["email"] == "dev@acme.test"
    assert payload["org"]["login"] == "acme.test"
    assert len(db.orgs) == 1
    assert len(db.users) == 1


def test_me_provision_rejects_email_mismatch(client):  # type: ignore[no-untyped-def]
    http, _db = client
    response = http.post("/me/provision", json={"source": "magic_link", "email": "other@acme.test", "name": "Dev"})
    assert response.status_code == 403
