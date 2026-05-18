from __future__ import annotations

import asyncio
import importlib
from datetime import datetime, timedelta
from typing import Any

import pytest
from sqlalchemy.exc import SQLAlchemyError

audit_router = importlib.import_module("apps.api.api.v8.audit.router")
EvidencePackageRequest = audit_router.EvidencePackageRequest
EvidencePackageResponse = audit_router.EvidencePackageResponse
_ensure_chain = audit_router._ensure_chain
create_evidence_package = audit_router.create_evidence_package


class _FailingDb:
    """A minimal async DB stub whose execute() always raises SQLAlchemyError."""

    def __init__(self) -> None:
        self.rollback_called = False
        self.commit_called = False
        self.added: list[Any] = []

    async def execute(self, *_args: Any, **_kwargs: Any) -> Any:
        raise SQLAlchemyError("boom")

    async def rollback(self) -> None:
        self.rollback_called = True

    async def commit(self) -> None:
        self.commit_called = True

    def add(self, obj: Any) -> None:
        self.added.append(obj)


class _CommitFailingDb:
    """A DB stub that fails on commit but not on execute."""

    def __init__(self) -> None:
        self.rollback_called = False
        self.added: list[Any] = []

    async def commit(self) -> None:
        raise SQLAlchemyError("commit boom")

    async def rollback(self) -> None:
        self.rollback_called = True

    def add(self, obj: Any) -> None:
        self.added.append(obj)


def test_ensure_chain_returns_empty_on_db_error() -> None:
    db = _FailingDb()

    result = asyncio.run(_ensure_chain(db, "org_1"))

    assert result == []
    assert db.rollback_called is True


def test_create_evidence_package_returns_preview_on_commit_error(monkeypatch) -> None:
    db = _CommitFailingDb()

    # _assert_enabled performs an org_id check + an is_v8 db call we want to skip.
    async def _no_assert(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(audit_router, "_assert_enabled", _no_assert)

    payload = EvidencePackageRequest(
        control="SOC2",
        period_start=datetime(2026, 5, 1, 0, 0, 0),
        period_end=datetime(2026, 5, 1, 0, 0, 0) + timedelta(days=7),
    )

    response = asyncio.run(
        create_evidence_package(
            org_id="org_1",
            payload=payload,
            db=db,  # type: ignore[arg-type]
            current_org_id="org_1",
        )
    )

    assert isinstance(response, EvidencePackageResponse)
    assert response.status == "preview"
    assert response.queued is False
    # The preview status under agent_compliance should be flipped to "preview"
    assert response.result["agent_compliance"]["status"] == "preview"
    assert db.rollback_called is True
