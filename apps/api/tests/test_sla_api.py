from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.api.routes import sla
from packages.db.models.sla_policy import SLAPolicy


class Result:
    def __init__(self, rows=None, scalar=0) -> None:
        self.rows = rows or []
        self.scalar = scalar

    def scalar_one(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, *, policy=None, repo=None, results=None) -> None:
        self.policy = policy
        self.repo = repo
        self.results = list(results or [])
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def get(self, model, item_id):
        if model.__name__ == "SLAPolicy":
            return self.policy
        if model.__name__ == "Repo":
            return self.repo
        return None

    def add(self, item):
        if not item.id:
            item.id = "sla_1"
        self.added.append(item)
        self.policy = item

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True

    async def refresh(self, item):
        if not item.id:
            item.id = "sla_1"


def _policy() -> SLAPolicy:
    return SLAPolicy(id="sla_1", org_id="org_1", repo_id="repo_1", name="Coverage", coverage_target_pct=80, alert_email=None, created_at=datetime.utcnow(), last_status="unknown")


def test_create_sla_policy_commits_and_returns_response() -> None:
    db = Db(repo=SimpleNamespace(name="api"))
    payload = sla.SLAPolicyPayload(name="Coverage", repo_id="repo_1", coverage_target_pct=80)

    response = asyncio.run(sla.create_sla("org_1", payload, db, "org_1"))

    assert response.id == "sla_1"
    assert response.name == "Coverage"
    assert db.committed is True
    assert isinstance(db.added[0], SLAPolicy)


def test_check_sla_marks_breaching_when_coverage_below_target() -> None:
    policy = _policy()
    db = Db(policy=policy, results=[Result(scalar=10), Result(scalar=6)])

    response = asyncio.run(sla.check_sla("org_1", "sla_1", db, "org_1"))

    assert response["status"] == "breaching"
    assert response["current_coverage"] == 60
    assert response["gap"] == 20
    assert policy.last_checked_at is not None
    assert db.committed is True


def test_delete_sla_policy_deactivates_policy() -> None:
    policy = _policy()
    db = Db(policy=policy)

    response = asyncio.run(sla.delete_sla("org_1", "sla_1", db, "org_1"))

    assert response == {"deactivated": True}
    assert policy.is_active is False
    assert db.committed is True


def test_sla_scope_mismatch_raises_403() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(sla.list_sla("org_1", Db(), "org_other"))

    assert exc.value.status_code == 403
