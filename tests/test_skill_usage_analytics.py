from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from apps.api.api.routes import admin, orgs, skills
from apps.api.api.routes.skills import UsagePayload
from packages.db.config import settings
from packages.db.database import get_db


ROOT = Path(__file__).resolve().parents[1]


class FakeResult:
    """Configurable async SQLAlchemy result double."""

    def __init__(
        self,
        *,
        first_value: object | None = None,
        scalar_one_value: object | None = None,
        one_value: object | None = None,
        rows: list[object] | None = None,
        rowcount: int = 0,
    ) -> None:
        self._first_value = first_value
        self._scalar_one_value = scalar_one_value
        self._one_value = one_value
        self._rows = rows or []
        self.rowcount = rowcount

    def first(self) -> object | None:
        """Return the configured first row."""
        return self._first_value

    def scalar_one(self) -> object:
        """Return the configured scalar value."""
        return self._scalar_one_value

    def one(self) -> object:
        """Return the configured row value."""
        return self._one_value

    def all(self) -> list[object]:
        """Return configured rows."""
        return self._rows


class FakeDb:
    """Async DB double that captures executed statements."""

    def __init__(self, results: list[FakeResult], get_value: object | None = None) -> None:
        self.results = results
        self.get_value = get_value
        self.statements: list[object] = []
        self.added: list[object] = []
        self.flush_count = 0
        self.rollback_count = 0

    async def execute(self, statement: object) -> FakeResult:
        """Record and return the next fake result."""
        self.statements.append(statement)
        return self.results.pop(0)

    async def get(self, model: object, key: str) -> object | None:
        """Return the configured lookup value."""
        return self.get_value

    def add(self, value: object) -> None:
        """Capture added ORM objects."""
        self.added.append(value)

    async def flush(self) -> None:
        """Record flush calls."""
        self.flush_count += 1

    async def rollback(self) -> None:
        """Record rollback calls."""
        self.rollback_count += 1


def test_record_skill_usage_uses_atomic_update_and_event() -> None:
    """Skill usage should update counters atomically and store event metadata."""
    db = FakeDb([FakeResult(first_value=SimpleNamespace(repo_id="repo_1")), FakeResult()])

    result = asyncio.run(
        skills.record_skill_usage(
            "skill_1",
            UsagePayload(agent_runtime="codex", session_id="session_1"),
            db=db,  # type: ignore[arg-type]
            current_org_id="org_1",
            _current_user={"email": "dev@example.com"},
        )
    )

    update_sql = str(db.statements[1].compile(compile_kwargs={"literal_binds": True}))
    assert result.recorded is True
    assert "load_count_30d=(skills.load_count_30d + 1)" in update_sql
    assert db.added[0].agent_runtime == "codex"
    assert db.added[0].session_id == "session_1"
    assert db.added[0].repo_id == "repo_1"
    assert db.flush_count == 1


def test_record_skill_usage_rejects_out_of_scope_skill() -> None:
    """Skill usage should reject skills outside the authenticated org."""
    db = FakeDb([FakeResult(first_value=None)], get_value=SimpleNamespace(id="skill_1"))

    try:
        asyncio.run(
            skills.record_skill_usage(
                "skill_1",
                UsagePayload(agent_runtime="codex", session_id="session_1"),
                db=db,  # type: ignore[arg-type]
                current_org_id="org_1",
                _current_user={"email": "dev@example.com"},
            )
        )
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == "Forbidden"
    else:
        raise AssertionError("Expected out-of-scope skill usage to be rejected")


def test_org_analytics_returns_expected_payload() -> None:
    """Org analytics should include loads, top skills, agent breakdown, and 30 days."""
    now = datetime.now(UTC).replace(tzinfo=None)
    top_skill = SimpleNamespace(
        id="skill_1",
        domain="backend/api",
        skill_path="skills/backend/api/SKILL.md",
        repo_id="repo_1",
        load_count_30d=12,
        last_loaded_at=now,
    )
    never_skill = SimpleNamespace(
        id="skill_2",
        domain="frontend",
        skill_path="skills/frontend/SKILL.md",
        repo_id="repo_1",
    )
    db = FakeDb(
        [
            FakeResult(scalar_one_value=2),
            FakeResult(one_value=SimpleNamespace(total_loads=12, unique_loaded=1)),
            FakeResult(rows=[(top_skill, "AnomalyDetector", "acme/AnomalyDetector")]),
            FakeResult(rows=[(never_skill, "AnomalyDetector", "acme/AnomalyDetector")]),
            FakeResult(rows=[("codex", 3)]),
            FakeResult(rows=[(now.date().isoformat(), 3)]),
            FakeResult(first_value=SimpleNamespace(id="repo_1", name="AnomalyDetector", full_name="acme/AnomalyDetector", loads=12)),
        ]
    )

    payload = asyncio.run(orgs.get_org_analytics("org_1", db=db, current_org_id="org_1"))  # type: ignore[arg-type]

    assert payload["total_loads_30d"] == 12
    assert payload["unique_skills_loaded"] == 1
    assert payload["total_skills"] == 2
    assert payload["top_skills"][0]["domain"] == "backend/api"  # type: ignore[index]
    assert payload["never_loaded"][0]["skill_path"] == "skills/frontend/SKILL.md"  # type: ignore[index]
    assert payload["agent_breakdown"] == {"codex": 3}
    assert len(payload["daily_loads"]) == 30
    assert payload["daily_loads"][-1]["loads"] == 3  # type: ignore[index]
    assert payload["most_active_repo"]["name"] == "AnomalyDetector"  # type: ignore[index]


def test_org_analytics_enforces_org_scope() -> None:
    """Org analytics should not leak data across organizations."""
    try:
        asyncio.run(orgs.get_org_analytics("org_requested", db=FakeDb([]), current_org_id="org_other"))  # type: ignore[arg-type]
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == "Forbidden"
    else:
        raise AssertionError("Expected org scope enforcement")


def _admin_client(db: FakeDb) -> TestClient:
    """Build a test client for the admin router."""
    app = FastAPI()
    app.include_router(admin.router)

    async def override_db() -> Any:
        yield db

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_admin_rollup_requires_secret(monkeypatch) -> None:
    """Admin usage rollup must reject invalid secrets."""
    monkeypatch.setattr(settings, "ADMIN_SECRET", "expected")

    response = _admin_client(FakeDb([])).post("/admin/rollup-usage", headers={"x-admin-secret": "wrong"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid admin secret", "code": "ADMIN_SECRET_INVALID"}


def test_admin_rollup_resets_stale_usage(monkeypatch) -> None:
    """Admin usage rollup should reset counters for stale skill loads."""
    monkeypatch.setattr(settings, "ADMIN_SECRET", "expected")
    db = FakeDb([FakeResult(rowcount=4)])

    response = _admin_client(db).post("/admin/rollup-usage", headers={"x-admin-secret": "expected"})

    assert response.status_code == 200
    assert response.json() == {"rolled_up": True, "reset_count": 4}
    update_sql = str(db.statements[0].compile(compile_kwargs={"literal_binds": True}))
    assert "load_count_30d=0" in update_sql
    assert "last_loaded_at" in update_sql


def test_dashboard_analytics_page_and_nav_are_wired() -> None:
    """Dashboard should expose the analytics route, nav item, and graceful error copy."""
    page = (ROOT / "apps/dashboard/app/dashboard/analytics/page.tsx").read_text(encoding="utf-8")
    data = (ROOT / "apps/dashboard/lib/data.ts").read_text(encoding="utf-8")
    nav = (ROOT / "apps/dashboard/src/lib/mock-data.ts").read_text(encoding="utf-8")
    layout = (ROOT / "apps/dashboard/app/dashboard/layout.tsx").read_text(encoding="utf-8")

    assert "Unable to load {section}. Refresh the page or contact support." in page
    assert "TopSkillsChart" in page
    assert "NeverLoadedList" in page
    assert "30-day skill usage sparkline" in page
    assert "getOrgAnalytics" in data
    assert 'href: "/dashboard/analytics"' in nav
    assert "BarChart3" in layout
