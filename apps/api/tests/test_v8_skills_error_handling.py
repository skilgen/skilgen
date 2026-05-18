from __future__ import annotations

import asyncio
import importlib
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

skills_router_module = importlib.import_module("apps.api.api.v8.skills.router")
V8DriftResponse = skills_router_module.V8DriftResponse
_skill_half_life_available = skills_router_module._skill_half_life_available
drift = skills_router_module.drift
repos = skills_router_module.repos


class _Result:
    def __init__(self, rows: list[Any] | None = None) -> None:
        self._rows = rows or []

    def all(self) -> list[Any]:
        return self._rows

    def scalars(self) -> "_Result":
        return self


class _ErrorOnExecuteDb:
    """A DB stub whose execute() always raises SQLAlchemyError."""

    def __init__(self) -> None:
        self.rollback_called = False

    async def execute(self, *_args: Any, **_kwargs: Any) -> Any:
        raise SQLAlchemyError("boom")

    async def rollback(self) -> None:
        self.rollback_called = True


class _ScriptedDb:
    """A DB stub whose execute() returns or raises based on a scripted sequence."""

    def __init__(self, script: list[Any]) -> None:
        self.script = list(script)
        self.calls = 0

    async def execute(self, *_args: Any, **_kwargs: Any) -> Any:
        self.calls += 1
        if not self.script:
            raise AssertionError(f"Unexpected execute call #{self.calls}")
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def test_skill_half_life_available_returns_false_on_error() -> None:
    db = _ErrorOnExecuteDb()

    available = asyncio.run(_skill_half_life_available(db))  # type: ignore[arg-type]

    assert available is False
    assert db.rollback_called is True


def test_drift_returns_empty_response_on_error(monkeypatch) -> None:
    async def _no_require(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(skills_router_module, "_require_v8", _no_require)

    db = _ErrorOnExecuteDb()

    response = asyncio.run(
        drift(org_id="org_1", db=db, current_org_id="org_1")  # type: ignore[arg-type]
    )

    assert isinstance(response, V8DriftResponse)
    assert response.events == []
    assert response.total == 0


def test_repos_falls_back_to_skill_count_only_on_half_life_error(monkeypatch) -> None:
    async def _no_require(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(skills_router_module, "_require_v8", _no_require)

    # Build a fake repo and skill_count row for the fallback query path.
    repo = SimpleNamespace(
        id="repo_1",
        name="api",
        full_name="acme/api",
        language="Python",
        sensitivity_tier="internal",
        is_active=True,
        last_analysed_at=datetime(2026, 5, 1, 12, 0, 0),
    )

    # Scripted execute sequence:
    # 1) primary join with SkillHalfLife => SQLAlchemyError (triggers fallback)
    # 2) fallback query returning [(repo, skill_count)]
    # 3) _org_policies query (returns empty result)
    fallback_result = _Result(rows=[(repo, 5)])
    policies_result = _Result(rows=[])
    db = _ScriptedDb(
        script=[
            SQLAlchemyError("half-life table missing"),
            fallback_result,
            policies_result,
        ]
    )

    response = asyncio.run(
        repos(org_id="org_1", db=db, current_org_id="org_1")  # type: ignore[arg-type]
    )

    # Both the failing first query and the fallback execute path should have run,
    # plus the trailing _org_policies query.
    assert db.calls == 3
    assert response.total == 1
    assert response.repos[0].id == "repo_1"
    assert response.repos[0].generated_skill_count == 5
    # Drift count defaults to 0 in fallback path.
    assert response.repos[0].drift_count == 0
