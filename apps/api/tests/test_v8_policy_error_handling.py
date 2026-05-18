from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

import apps.api.api.v8.policy.routes as policy_routes
from apps.api.api.auth import get_current_org_id
from apps.api.api.v8.policy.routes import _load_policy_rows, router as policy_router
from packages.db.database import get_db


class _FailingDb:
    """Async DB stub whose execute() always raises SQLAlchemyError."""

    def __init__(self) -> None:
        self.rollback_called = False

    async def execute(self, *_args: Any, **_kwargs: Any) -> Any:
        raise SQLAlchemyError("boom")

    async def rollback(self) -> None:
        self.rollback_called = True


def test_load_policy_rows_handles_sqlalchemy_error() -> None:
    db = _FailingDb()

    rows = asyncio.run(
        _load_policy_rows("org_1", db, enabled_only=False, newest_first=True)  # type: ignore[arg-type]
    )

    assert rows == []
    assert db.rollback_called is True


def test_list_quarantine_returns_empty_on_db_error(monkeypatch) -> None:
    # Bypass the v8 enablement gate (it would call is_v8 on the DB).
    async def _no_assert(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(policy_routes, "_ensure_v8", _no_assert)

    db = _FailingDb()

    app = FastAPI()
    app.include_router(policy_router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"

    client = TestClient(app)
    response = client.get("/v8/orgs/org_1/policy/quarantine")

    assert response.status_code == 200
    assert response.json() == []
    assert db.rollback_called is True
