from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api import auth
from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from packages.db.database import get_db


class FakeResult:
    """Small async SQLAlchemy result double."""

    def __init__(self, value: object | None = None) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object | None:
        return self.value

    def first(self) -> object | None:
        return self.value


class FakeDb:
    """Queued DB double for API-key route and auth tests."""

    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.orgs = [result.value for result in results if hasattr(result.value, "api_key")]
        self.flush_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.added: list[object] = []

    async def execute(self, statement: object) -> FakeResult:
        compiled = str(statement.compile(compile_kwargs={"literal_binds": True}))
        if compiled.startswith("UPDATE orgs") and "api_key=" in compiled.replace(" ", ""):
            value = compiled.split("api_key='", 1)[-1].split("'", 1)[0]
            org_id = compiled.split("orgs.id = '", 1)[-1].split("'", 1)[0]
            for org in self.orgs:
                if getattr(org, "id", None) == org_id:
                    org.api_key = value
            return FakeResult(None)
        if not self.results:
            return FakeResult(None)
        return self.results.pop(0)

    async def flush(self) -> None:
        self.flush_count += 1

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1

    def add(self, item: object) -> None:
        self.added.append(item)


def _org(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "id": "org_123",
        "login": "acme",
        "name": "Acme",
        "api_key": "sk-existing",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)

    async def override_org_id() -> str:
        return "org_123"

    async def override_db() -> Any:
        yield db

    app.dependency_overrides[get_current_org_id] = override_org_id
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def _credentials(token: str) -> SimpleNamespace:
    return SimpleNamespace(credentials=token)


def test_get_api_key_generates_missing_key_and_saves(monkeypatch) -> None:
    org = _org(api_key=None)
    db = FakeDb([FakeResult(org)])
    monkeypatch.setattr(orgs, "_generate_org_api_key", lambda: "sk-generated")

    response = _client(db).get("/orgs/org_123/api-key")

    assert response.status_code == 200
    assert response.json() == {"api_key": "sk-generated"}
    assert org.api_key == "sk-generated"
    assert db.commit_count == 1


def test_get_api_key_is_idempotent() -> None:
    org = _org(api_key="sk-stable")
    db = FakeDb([FakeResult(org), FakeResult(org)])
    client = _client(db)

    first = client.get("/orgs/org_123/api-key")
    second = client.get("/orgs/org_123/api-key")

    assert first.json() == {"api_key": "sk-stable"}
    assert second.json() == {"api_key": "sk-stable"}
    assert db.commit_count == 0


def test_rotate_api_key_replaces_existing_key(monkeypatch) -> None:
    org = _org(api_key="sk-old")
    db = FakeDb([FakeResult(org)])
    monkeypatch.setattr(orgs, "_generate_org_api_key", lambda: "sk-new")

    response = _client(db).post("/orgs/org_123/api-key/rotate")

    assert response.status_code == 200
    assert response.json() == {"api_key": "sk-new"}
    assert org.api_key == "sk-new"
    assert db.flush_count == 1
    assert db.commit_count == 1


def test_rotated_old_key_no_longer_authenticates(monkeypatch) -> None:
    monkeypatch.setattr(auth, "_deployment_mode", lambda: "bootstrap")
    fallback_org = _org(id="org_fallback", api_key="sk-new")
    db = FakeDb([FakeResult(fallback_org)])

    resolved = asyncio.run(get_current_org_id(_credentials("sk-old"), db))

    assert resolved == "org_fallback"
    assert resolved != "org_123"


def test_valid_bearer_api_key_resolves_org_id() -> None:
    db = FakeDb([FakeResult(_org(id="org_api", api_key="sk-valid"))])

    resolved = asyncio.run(get_current_org_id(_credentials("sk-valid"), db))

    assert resolved == "org_api"


def test_valid_device_api_key_resolves_org_id() -> None:
    authorization = SimpleNamespace(org_id="org_device", status="approved", revoked_at=None)
    db = FakeDb([FakeResult(None), FakeResult(authorization)])

    resolved = asyncio.run(get_current_org_id(_credentials("sk-device-valid"), db))

    assert resolved == "org_device"


def test_invalid_bearer_api_key_falls_through_to_bootstrap(monkeypatch) -> None:
    monkeypatch.setattr(auth, "_deployment_mode", lambda: "bootstrap")
    db = FakeDb([FakeResult(_org(id="org_bootstrap", api_key="sk-other"))])

    resolved = asyncio.run(get_current_org_id(_credentials("sk-invalid"), db))

    assert resolved == "org_bootstrap"
