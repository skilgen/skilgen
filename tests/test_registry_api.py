from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes import registry
from packages.db.database import get_db


class FakeResult:
    def __init__(
        self,
        *,
        scalar_one: object | None = None,
        scalar_one_or_none: object | None = None,
        first: object | None = None,
        all_rows: list[object] | None = None,
    ) -> None:
        self._scalar_one = scalar_one
        self._scalar_one_or_none = scalar_one_or_none
        self._first = first
        self._all = all_rows or []

    def scalar_one(self) -> object | None:
        return self._scalar_one

    def scalar_one_or_none(self) -> object | None:
        return self._scalar_one_or_none

    def first(self) -> object | None:
        return self._first

    def all(self) -> list[object]:
        return self._all


class FakeDb:
    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.flushed = False
        self.rolled_back = False

    async def execute(self, _query: object) -> FakeResult:
        return self.results.pop(0)

    async def flush(self) -> None:
        self.flushed = True

    async def rollback(self) -> None:
        self.rolled_back = True


def _objects() -> tuple[object, object, object]:
    listing = SimpleNamespace(
        id="reg_1",
        org_id="org_1",
        repo_id="repo_1",
        skill_id="skill_1",
        domain="backend/api",
        name="API skill",
        description="Reusable API guidance.",
        is_public=True,
        is_official=False,
        import_count=3,
        tags=["api", "fastapi"],
        created_at=datetime(2026, 4, 23, 12, 0, 0),
    )
    skill = SimpleNamespace(
        id="skill_1",
        repo_id="repo_1",
        domain="backend/api",
        skill_path="skills/backend/api/SKILL.md",
        content="# API\n\nUse FastAPI routes.",
        content_hash="abc123",
        score_total=84,
    )
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="skillayer/api")
    return listing, skill, repo


def _client(db: FakeDb, *, auth: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(registry.router)

    async def override_db() -> Any:
        yield db

    async def override_org_id() -> str:
        return "org_1"

    async def override_user() -> dict[str, object]:
        return {"email": "owner@example.com"}

    app.dependency_overrides[get_db] = override_db
    if auth:
        app.dependency_overrides[get_current_org_id] = override_org_id
        app.dependency_overrides[get_current_user] = override_user
    return TestClient(app)


def test_list_registry_returns_public_paginated_skills() -> None:
    listing, skill, _repo = _objects()
    db = FakeDb([FakeResult(scalar_one=1), FakeResult(all_rows=[(listing, skill)])])

    response = _client(db).get("/registry?search=api&tag=fastapi&sort=score")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["skills"][0]["id"] == "reg_1"
    assert body["skills"][0]["score_total"] == 84
    assert body["skills"][0]["tags"] == ["api", "fastapi"]


def test_get_registry_skill_returns_full_content() -> None:
    listing, skill, repo = _objects()
    db = FakeDb([FakeResult(first=(listing, skill, repo))])

    response = _client(db).get("/registry/reg_1")

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "# API\n\nUse FastAPI routes."
    assert body["repo_full_name"] == "skillayer/api"
    assert body["skill_path"] == "skills/backend/api/SKILL.md"


def test_publish_registry_skill_validates_org_scope_and_returns_listing() -> None:
    listing, skill, repo = _objects()
    db = FakeDb([FakeResult(first=(skill, repo)), FakeResult(scalar_one_or_none=listing)])

    response = _client(db).post(
        "/registry/publish",
        json={
            "skill_id": "skill_1",
            "name": "API skill",
            "description": "Reusable API guidance.",
            "tags": ["API", "fastapi", "api"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "API skill"
    assert body["tags"] == ["api", "fastapi"]
    assert db.flushed is True


def test_publish_registry_skill_rejects_other_org_skill() -> None:
    _listing, skill, repo = _objects()
    repo.org_id = "org_2"
    db = FakeDb([FakeResult(first=(skill, repo))])

    response = _client(db).post(
        "/registry/publish",
        json={"skill_id": "skill_1", "name": "API", "description": "Description"},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "SKILL_FORBIDDEN"


def test_import_registry_skill_requires_auth() -> None:
    db = FakeDb([])

    response = _client(db, auth=False).post("/registry/reg_1/import")

    assert response.status_code in {401, 403}


def test_import_registry_skill_increments_count_and_returns_content() -> None:
    listing, skill, repo = _objects()
    db = FakeDb([FakeResult(first=(listing, skill, repo)), FakeResult()])

    response = _client(db).post("/registry/reg_1/import")

    assert response.status_code == 200
    body = response.json()
    assert body["import_count"] == 4
    assert body["content_hash"] == "abc123"
    assert db.flushed is True
