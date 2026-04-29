from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.api.auth import get_admin_secret
from apps.api.api.index import app
from apps.api.api.routes import admin, orgs
from packages.db.models import LoginEvent


class Result:
    def __init__(self, *, rows=None, scalar=None) -> None:
        self.rows = rows or []
        self.scalar = scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows

    def scalar_one(self):
        return self.scalar

    def scalar_one_or_none(self):
        return self.scalar


class Db:
    def __init__(self, *, org=None, results=None) -> None:
        self.org = org
        self.results = list(results or [])
        self.added = []
        self.deleted = []
        self.committed = False
        self.rolled_back = False

    async def get(self, model, key):
        if model.__name__ == "Org":
            return self.org
        return None

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    def add(self, item) -> None:
        self.added.append(item)

    async def delete(self, item) -> None:
        self.deleted.append(item)

    async def refresh(self, item) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


def test_admin_and_metrics_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/admin/overview" in paths
    assert "/admin/orgs" in paths
    assert "/admin/users" in paths
    assert "/admin/logins" in paths
    assert "/metrics" in paths


def test_admin_secret_rejects_missing_or_wrong_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_SECRET", "server-secret")

    with pytest.raises(HTTPException) as missing:
        get_admin_secret("")
    assert missing.value.status_code == 403

    with pytest.raises(HTTPException) as wrong:
        get_admin_secret("wrong")
    assert wrong.value.status_code == 403


def test_admin_secret_accepts_matching_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_SECRET", "server-secret")

    assert get_admin_secret("server-secret") == "server-secret"


def test_login_event_endpoint_records_ip_and_user_agent() -> None:
    db = Db()
    request = SimpleNamespace(
        headers={"x-forwarded-for": "203.0.113.10, 10.0.0.1", "user-agent": "pytest-agent"},
        client=SimpleNamespace(host="127.0.0.1"),
    )

    response = asyncio.run(
        orgs.create_login_event(
            "org_1",
            orgs.LoginEventRequest(user_login="ravi", user_email="ravi@example.com"),
            request,
            db,
            "org_1",
        )
    )

    assert response == {"ok": True}
    assert db.committed is True
    assert isinstance(db.added[0], LoginEvent)
    assert db.added[0].ip_address == "203.0.113.10"
    assert db.added[0].user_agent == "pytest-agent"


def test_admin_overview_returns_core_totals() -> None:
    now = datetime.utcnow()
    org = SimpleNamespace(id="org_1", plan="team", is_suspended=False)
    session = SimpleNamespace(org_id="org_1", session_start=now - timedelta(days=1))
    run = SimpleNamespace(repo_id="repo_1", created_at=now - timedelta(days=2))
    pr = SimpleNamespace(opened_at=now - timedelta(days=3))
    login = SimpleNamespace(user_login="ravi", created_at=now - timedelta(days=1))
    db = Db(
        results=[
            Result(rows=[org]),
            Result(rows=[session]),
            Result(rows=[run]),
            Result(rows=[pr]),
            Result(rows=[login]),
            Result(scalar=7),
            Result(scalar=2),
            Result(rows=[("repo_1", "org_1")]),
        ]
    )

    response = asyncio.run(admin.admin_overview("server-secret", db))

    assert response["orgs"]["total"] == 1
    assert response["orgs"]["active_30d"] == 1
    assert response["orgs"]["by_plan"]["team"] == 1
    assert response["users"]["total_unique"] == 1
    assert response["data"]["total_skills"] == 7
    assert response["data"]["total_repos"] == 2


def test_suspend_org_sets_state_and_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    org = SimpleNamespace(id="org_1", is_suspended=False, suspended_at=None, suspended_reason=None)
    db = Db(org=org)

    async def summary(_db, item):
        return {"id": item.id, "is_suspended": item.is_suspended, "suspended_reason": item.suspended_reason}

    monkeypatch.setattr(admin, "_org_summary", summary)

    response = asyncio.run(admin.suspend_org("org_1", admin.SuspendOrgRequest(reason="billing issue"), "server-secret", db))

    assert response["is_suspended"] is True
    assert response["suspended_reason"] == "billing issue"
    assert org.suspended_at is not None
    assert db.committed is True


def test_unsuspend_org_clears_state(monkeypatch: pytest.MonkeyPatch) -> None:
    org = SimpleNamespace(id="org_1", is_suspended=True, suspended_at=datetime.utcnow(), suspended_reason="billing issue")
    db = Db(org=org)

    async def summary(_db, item):
        return {"id": item.id, "is_suspended": item.is_suspended, "suspended_reason": item.suspended_reason}

    monkeypatch.setattr(admin, "_org_summary", summary)

    response = asyncio.run(admin.unsuspend_org("org_1", "server-secret", db))

    assert response["is_suspended"] is False
    assert response["suspended_reason"] is None
    assert org.suspended_at is None
    assert db.committed is True


def test_delete_org_removes_org() -> None:
    org = SimpleNamespace(id="org_1")
    db = Db(org=org)

    response = asyncio.run(admin.delete_org("org_1", "server-secret", db))

    assert response == {"ok": True, "deleted_org_id": "org_1"}
    assert db.deleted == [org]
    assert db.committed is True
