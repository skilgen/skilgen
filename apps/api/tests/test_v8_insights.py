from __future__ import annotations

import importlib
from datetime import datetime, timedelta
from types import SimpleNamespace

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from apps.api.api.auth import get_current_org_id
from apps.api.api.v8.insights import router as insights_router
from packages.db.database import get_db
from packages.db.models import PRAttribution, PullRequest


insights = importlib.import_module("apps.api.api.v8.insights.router")
migration = importlib.import_module("apps.api.alembic.versions.20260505_0006_v8_insights_risk_views")

NOW = datetime(2026, 5, 4, 12, 0, 0)


class Result:
    def __init__(self, rows=None, scalar=0) -> None:
        self.rows = rows or []
        self._scalar = scalar

    def scalar(self):
        return self._scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows

    def mappings(self):
        return self


class Db:
    def __init__(self, results=None, *, fail_first=False) -> None:
        self.results = list(results or [])
        self.fail_first = fail_first
        self.rolled_back = False

    async def execute(self, statement, params=None):
        if self.fail_first:
            self.fail_first = False
            raise SQLAlchemyError("view missing")
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def rollback(self):
        self.rolled_back = True


def _repo(repo_id: str, name: str, tier: str = "internal"):
    return SimpleNamespace(id=repo_id, org_id="org_1", name=name, full_name=f"acme/{name}", is_active=True, sensitivity_tier=tier)


def _pr(pr_id: str, repo_id: str, days_old: int = 1) -> PullRequest:
    pr = PullRequest(repo_id=repo_id, github_pr_number=int(pr_id.split("_")[-1]))
    pr.id = pr_id
    pr.opened_at = NOW - timedelta(days=days_old)
    return pr


def _attr(pr_id: str, agent: str, violated: bool = False) -> PRAttribution:
    attr = PRAttribution(pr_id=pr_id, primary_agent=agent, confidence=0.9)
    attr.skills_violated = [{"severity": "critical", "skill_name": "security"}] if violated else []
    return attr


def _client(db: Db, monkeypatch, *, enabled: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(insights_router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"

    async def fake_is_v8(org_id, db=None):
        return enabled

    monkeypatch.setattr(insights, "is_v8", fake_is_v8)
    monkeypatch.setattr(insights, "_utc_now", lambda: NOW)
    return TestClient(app)


def test_insights_router_paths_are_registered() -> None:
    app = FastAPI()
    app.include_router(insights_router)
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/insights/fleet-kpis" in paths
    assert "/v8/orgs/{org_id}/insights/risky-agents" in paths
    assert "/v8/orgs/{org_id}/insights/risky-repos" in paths
    assert "/v8/orgs/{org_id}/insights/coverage-sla" in paths


def test_insights_routes_404_when_ia_v8_disabled(monkeypatch) -> None:
    response = _client(Db(), monkeypatch, enabled=False).get("/v8/orgs/org_1/insights/risky-agents")

    assert response.status_code == 404


def test_fleet_kpis_contract_includes_prior_period_comparison(monkeypatch) -> None:
    approved = SimpleNamespace(status="approved", created_at=NOW - timedelta(hours=2), reviewed_at=NOW - timedelta(hours=1))
    rejected = SimpleNamespace(status="rejected", created_at=NOW - timedelta(hours=3), reviewed_at=NOW - timedelta(hours=1))
    current_pr = _pr("pr_1", "repo_1")
    previous_pr = _pr("pr_2", "repo_1", days_old=31)
    db = Db(
        [
            Result([approved, rejected]),
            Result([]),
            Result(scalar=10),
            Result(scalar=5),
            Result(["repo_1"]),
            Result([current_pr]),
            Result([_attr("pr_1", "codex", violated=True)]),
            Result(["repo_1"]),
            Result([previous_pr]),
            Result([_attr("pr_2", "codex", violated=False)]),
            Result(scalar=1),
            Result(scalar=0),
            Result(["repo_1"]),
            Result([current_pr]),
            Result([_attr("pr_1", "codex", violated=True)]),
            Result(["repo_1"]),
            Result([previous_pr]),
            Result([]),
            Result(["ravi"]),
            Result(["ravi", "sam"]),
        ]
    )
    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/fleet-kpis")

    assert response.status_code == 200
    payload = response.json()
    metrics = {metric["key"]: metric for metric in payload["metrics"]}
    assert metrics["total_agent_actions"]["current"] == 10
    assert metrics["total_agent_actions"]["previous"] == 5
    assert metrics["deny_rate"]["current"] == 1.0
    assert metrics["approval_rate"]["current"] == 0.5
    assert metrics["median_time_to_approve"]["current"] == 60
    assert metrics["quarantined_skills"]["status"] == "unavailable"
    assert metrics["attributed_agent_commits"]["previous"] == 0.0


def test_risky_agent_fallback_sorts_by_prd_formula(monkeypatch) -> None:
    db = Db(
        [
            Result([_repo("repo_1", "payments", "regulated"), _repo("repo_2", "docs", "internal")]),
            Result([_pr("pr_1", "repo_1"), _pr("pr_2", "repo_1"), _pr("pr_3", "repo_2")]),
            Result([_attr("pr_1", "codex", True), _attr("pr_2", "codex", True), _attr("pr_3", "cursor", True)]),
        ],
        fail_first=True,
    )
    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/risky-agents")

    assert response.status_code == 200
    rows = response.json()["rows"]
    assert rows[0]["name"] == "codex"
    assert rows[0]["composite_risk"] == 6.0
    assert rows[1]["name"] == "cursor"
    assert db.rolled_back is True


def test_risky_view_sql_snapshot_contains_required_formula() -> None:
    sql = migration.risky_agents_view_sql("postgresql", has_sensitivity_tier=True)

    assert "CREATE VIEW v8_insights_risky_agents AS" in sql
    assert "SUM(denied) * 1.0 / COUNT(*)" in sql
    assert "AVG(scope_weight) * COUNT(*) AS composite_risk" in sql
    assert "CURRENT_TIMESTAMP - interval '30 days'" in sql


def test_risky_views_migration_upgrade_and_downgrade(monkeypatch) -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE repos (id TEXT PRIMARY KEY, org_id TEXT, full_name TEXT, sensitivity_tier TEXT, is_active BOOLEAN)"))
        connection.execute(sa.text("CREATE TABLE pull_requests (id TEXT PRIMARY KEY, repo_id TEXT, opened_at DATETIME)"))
        connection.execute(sa.text("CREATE TABLE pr_attributions (id TEXT PRIMARY KEY, pr_id TEXT, primary_agent TEXT, skills_violated TEXT)"))
        context = MigrationContext.configure(connection)
        monkeypatch.setattr(migration, "op", Operations(context))

        migration.upgrade()
        views = {row[0] for row in connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='view'")).all()}
        assert "v8_insights_risky_agents" in views
        assert "v8_insights_risky_repos" in views

        migration.downgrade()
        views = {row[0] for row in connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='view'")).all()}
        assert "v8_insights_risky_agents" not in views
        assert "v8_insights_risky_repos" not in views


def test_one_million_event_fixture_limitation_is_documented() -> None:
    path = "docs/v8-refactor/insights-pr6-fixture-limitations.md"
    assert "1M-event" in open(path, encoding="utf-8").read()
