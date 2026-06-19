from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from packages.db.database import get_db
from packages.db.models import PRAttribution, PullRequest


NOW = datetime(2026, 4, 28, 12, 0, 0)


class Result:
    def __init__(self, rows=None) -> None:
        self.rows = rows or []

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, results: list[Result]) -> None:
        self.results = results

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)


def _repo(repo_id: str = "repo_1"):
    return SimpleNamespace(id=repo_id, org_id="org_1", name="api", full_name="acme/api")


def _pr(index: int, days_old: int, state: str = "open", merged: bool = False, closed: bool = False) -> PullRequest:
    pr = PullRequest(repo_id="repo_1", github_pr_number=index)
    pr.id = f"pr_{index}"
    pr.state = state
    pr.opened_at = NOW - timedelta(days=days_old)
    pr.merged_at = NOW - timedelta(days=days_old - 1) if merged else None
    pr.closed_at = NOW - timedelta(days=days_old - 1) if closed else None
    return pr


def _attr(
    pr_id: str,
    agent: str,
    risk_score: int,
    risk_tier: str,
    confidence: float = 0.9,
    skills_loaded: list[str] | None = None,
    skills_violated: list[dict[str, object]] | None = None,
) -> PRAttribution:
    attr = PRAttribution(pr_id=pr_id, primary_agent=agent, confidence=confidence)
    attr.risk_score = risk_score
    attr.risk_tier = risk_tier
    attr.skills_loaded = skills_loaded or []
    attr.skills_violated = skills_violated or []
    return attr


def _client(db: Db, monkeypatch) -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    monkeypatch.setattr(orgs, "_utc_now_naive", lambda: NOW)
    return TestClient(app)


def test_agent_scorecard_aggregates_per_agent(monkeypatch) -> None:
    prs = [
        _pr(1, 1, state="merged", merged=True),
        _pr(2, 2, state="closed", closed=True),
        _pr(3, 3),
        _pr(4, 4, state="merged", merged=True),
    ]
    attrs = [
        _attr("pr_1", "codex", 80, "red", 0.8, ["auth", "testing"], [{"severity": "critical", "skill_name": "auth"}]),
        _attr("pr_2", "codex", 30, "green", 0.9, ["auth"], [{"severity": "warning", "skill_name": "testing"}]),
        _attr("pr_3", "codex", 10, "green", 1.0, ["cli"], []),
        _attr("pr_4", "claude_code", 50, "yellow", 0.7, ["agents"], []),
    ]
    client = _client(Db([Result([_repo()]), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/agent-scorecard?days=30")

    assert response.status_code == 200
    payload = response.json()
    assert payload["window_days"] == 30
    codex = next(agent for agent in payload["agents"] if agent["agent"] == "codex")
    assert codex["display_name"] == "Codex CLI"
    assert codex["prs_total"] == 3
    assert codex["prs_merged"] == 1
    assert codex["prs_reverted"] == 1
    assert codex["violations_total"] == 1
    assert codex["warnings_total"] == 1
    assert codex["violation_rate"] == 0.3333
    assert codex["compliance_pct"] == 66.7
    assert codex["avg_risk_score"] == 40.0
    assert codex["confidence_avg"] == 0.9
    assert codex["skills_loaded"][0] == "auth"
    assert codex["top_skills"][0] == "auth"
    assert codex["violation_skill_names"] == ["auth"]
    assert codex["top_violations"] == ["auth"]


def test_agent_scorecard_empty_state(monkeypatch) -> None:
    client = _client(Db([Result([])]), monkeypatch)

    response = client.get("/orgs/org_1/agent-scorecard?days=7")

    assert response.status_code == 200
    assert response.json()["agents"] == []


def test_agent_scorecard_filters_by_days(monkeypatch) -> None:
    recent = _pr(1, 2)
    old = _pr(2, 20)
    attrs = [
        _attr("pr_1", "codex", 20, "green", skills_loaded=["recent"]),
        _attr("pr_2", "codex", 90, "red", skills_loaded=["old"]),
    ]
    client = _client(Db([Result([_repo()]), Result([recent, old]), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/agent-scorecard?days=7")

    assert response.status_code == 200
    agents = response.json()["agents"]
    assert len(agents) == 1
    assert agents[0]["prs_total"] == 1
    assert agents[0]["avg_risk_score"] == 20.0
    assert agents[0]["skills_loaded"] == ["recent"]


def test_agent_scorecard_counts_violations_and_risk_distribution(monkeypatch) -> None:
    prs = [_pr(1, 1), _pr(2, 1), _pr(3, 1)]
    attrs = [
        _attr("pr_1", "cursor", 85, "red", skills_violated=[{"severity": "error", "skill_name": "security"}]),
        _attr("pr_2", "cursor", 45, "yellow", skills_violated=[{"severity": "warning", "skill_name": "tests"}]),
        _attr("pr_3", "cursor", 5, "green", skills_violated=[{"severity": "fatal", "title": "deploy"}]),
    ]
    client = _client(Db([Result([_repo()]), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/agent-scorecard?days=30")

    assert response.status_code == 200
    cursor = response.json()["agents"][0]
    assert cursor["violations_total"] == 2
    assert cursor["warnings_total"] == 1
    assert cursor["risk_distribution"] == {"green": 1, "yellow": 1, "red": 1}
    assert cursor["violation_skill_names"] == ["deploy", "security"]
