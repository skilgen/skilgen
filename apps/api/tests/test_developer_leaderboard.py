from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from packages.db.database import get_db
from packages.db.models import PRAttribution


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
    return SimpleNamespace(id=repo_id, org_id="org_1", name="api", is_active=True)


def _session(
    login: str,
    *,
    days_old: int = 1,
    files: list[str] | None = None,
    skills: list[str] | None = None,
    runtime: str = "codex",
    session_id: str = "session_1",
):
    return SimpleNamespace(
        id=session_id,
        repo_id="repo_1",
        org_id="org_1",
        engineer_login=login,
        session_start=NOW - timedelta(days=days_old),
        files_touched=files or [],
        skills_loaded=skills or [],
        agent_runtime=runtime,
        outcome=None,
    )


def _pr(
    login: str,
    *,
    pr_id: str = "pr_1",
    days_old: int = 1,
    state: str = "open",
    additions: int = 10,
    deletions: int = 5,
):
    return SimpleNamespace(
        id=pr_id,
        repo_id="repo_1",
        author_login=login,
        opened_at=NOW - timedelta(days=days_old),
        merged_at=NOW - timedelta(days=days_old - 1) if state == "merged" else None,
        closed_at=NOW - timedelta(days=days_old - 1) if state == "closed" else None,
        state=state,
        additions=additions,
        deletions=deletions,
    )


def _attr(
    pr_id: str,
    *,
    risk_score: int = 0,
    risk_tier: str = "green",
    skills_loaded: list[str] | None = None,
    findings: list[dict[str, object]] | None = None,
) -> PRAttribution:
    attr = PRAttribution(pr_id=pr_id, primary_agent="codex", confidence=0.9)
    attr.risk_score = risk_score
    attr.risk_tier = risk_tier
    attr.skills_loaded = skills_loaded or []
    attr.skills_violated = findings or []
    return attr


def _client(db: Db, monkeypatch) -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    monkeypatch.setattr(orgs, "_utc_now_naive", lambda: NOW)
    return TestClient(app)


def test_developer_leaderboard_empty_org(monkeypatch) -> None:
    client = _client(Db([Result([])]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard")

    assert response.status_code == 200
    assert response.json()["developers"] == []


def test_developer_leaderboard_sessions_only(monkeypatch) -> None:
    sessions = [_session("ravi", files=["a.py", "b.py"], skills=["auth", "api"], runtime="claude_code")]
    client = _client(Db([Result([_repo()]), Result(sessions), Result([])]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard")

    assert response.status_code == 200
    ravi = response.json()["developers"][0]
    assert ravi["login"] == "ravi"
    assert ravi["sessions_count"] == 1
    assert ravi["files_touched"] == 2
    assert ravi["prs_opened"] == 0
    assert ravi["compliance_pct"] == 100.0
    assert ravi["agent_runtimes"] == ["claude_code"]
    assert ravi["skills_loaded"] == ["api", "auth"]


def test_developer_leaderboard_prs_only(monkeypatch) -> None:
    prs = [_pr("ravi", pr_id="pr_1", state="merged", additions=40, deletions=7)]
    attrs = [_attr("pr_1", skills_loaded=["auth"], risk_score=20, risk_tier="green")]
    client = _client(Db([Result([_repo()]), Result([]), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard")

    ravi = response.json()["developers"][0]
    assert ravi["sessions_count"] == 0
    assert ravi["prs_opened"] == 1
    assert ravi["prs_merged"] == 1
    assert ravi["lines_changed"] == 47
    assert ravi["skills_loaded"] == ["auth"]


def test_developer_leaderboard_merges_sessions_and_prs_same_login(monkeypatch) -> None:
    sessions = [_session("ravi", files=["a.py"], skills=["agents"], runtime="codex")]
    prs = [_pr("ravi", pr_id="pr_1", state="open", additions=3, deletions=2)]
    attrs = [_attr("pr_1", skills_loaded=["agents", "cli"], findings=[{"severity": "warning", "skill_name": "cli"}], risk_score=35, risk_tier="yellow")]
    client = _client(Db([Result([_repo()]), Result(sessions), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard")

    ravi = response.json()["developers"][0]
    assert ravi["sessions_count"] == 1
    assert ravi["prs_opened"] == 1
    assert ravi["warnings_total"] == 1
    assert ravi["violations_total"] == 0
    assert ravi["risk_distribution"] == {"green": 0, "yellow": 1, "red": 0}
    assert ravi["skills_loaded"][:2] == ["agents", "cli"]


def test_developer_leaderboard_ranks_by_compliance(monkeypatch) -> None:
    prs = [_pr("clean", pr_id="pr_1"), _pr("risky", pr_id="pr_2")]
    attrs = [
        _attr("pr_1", findings=[]),
        _attr("pr_2", findings=[{"severity": "critical", "skill_name": "security"}], risk_score=80, risk_tier="red"),
    ]
    client = _client(Db([Result([_repo()]), Result([]), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard?sort_by=compliance")

    developers = response.json()["developers"]
    assert [item["login"] for item in developers] == ["clean", "risky"]
    assert developers[0]["rank"] == 1
    assert developers[1]["compliance_pct"] == 0.0


def test_developer_leaderboard_sort_by_violations(monkeypatch) -> None:
    prs = [_pr("risky", pr_id="pr_1"), _pr("clean", pr_id="pr_2")]
    attrs = [
        _attr("pr_1", findings=[{"severity": "error", "skill_name": "auth"}, {"severity": "fatal", "skill_name": "secrets"}]),
        _attr("pr_2", findings=[]),
    ]
    client = _client(Db([Result([_repo()]), Result([]), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard?sort_by=violations")

    assert [item["login"] for item in response.json()["developers"]] == ["risky", "clean"]


def test_developer_leaderboard_days_filter_excludes_old_session(monkeypatch) -> None:
    sessions = [_session("recent", days_old=2), _session("old", days_old=20)]
    client = _client(Db([Result([_repo()]), Result(sessions), Result([])]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard?days=7")

    assert [item["login"] for item in response.json()["developers"]] == ["recent"]


def test_developer_leaderboard_lines_changed_and_file_dedupe(monkeypatch) -> None:
    sessions = [
        _session("ravi", files=["a.py", "b.py"], session_id="session_1"),
        _session("ravi", files=["a.py", "c.py"], session_id="session_2"),
    ]
    prs = [_pr("ravi", pr_id="pr_1", additions=100, deletions=25), _pr("ravi", pr_id="pr_2", additions=10, deletions=5)]
    attrs = [_attr("pr_1"), _attr("pr_2")]
    client = _client(Db([Result([_repo()]), Result(sessions), Result(prs), Result(attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard")

    ravi = response.json()["developers"][0]
    assert ravi["files_touched"] == 3
    assert ravi["lines_changed"] == 140


def test_developer_leaderboard_trend_up_and_sparkline(monkeypatch) -> None:
    current_prs = [_pr("ravi", pr_id="pr_1", days_old=1), _pr("ravi", pr_id="pr_2", days_old=2)]
    current_attrs = [_attr("pr_1", findings=[]), _attr("pr_2", findings=[])]
    previous_prs = [_pr("ravi", pr_id="pr_old", days_old=10)]
    previous_attrs = [_attr("pr_old", findings=[{"severity": "critical", "skill_name": "security"}])]
    client = _client(Db([Result([_repo()]), Result([]), Result(current_prs), Result(current_attrs), Result(previous_prs), Result(previous_attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard?days=7&include_trend=true")

    ravi = response.json()["developers"][0]
    assert ravi["trend"] == {"compliance_delta": 100.0, "violations_delta": -1, "direction": "up"}
    assert len(ravi["sparkline"]) == 7
    assert ravi["sparkline"].count(100.0) == 2


def test_developer_leaderboard_trend_down_flat_and_null(monkeypatch) -> None:
    current_prs = [
        _pr("down", pr_id="pr_1", days_old=1),
        _pr("flat", pr_id="pr_2", days_old=1),
        _pr("new", pr_id="pr_3", days_old=1),
    ]
    current_attrs = [
        _attr("pr_1", findings=[{"severity": "critical", "skill_name": "auth"}]),
        _attr("pr_2", findings=[]),
        _attr("pr_3", findings=[]),
    ]
    previous_prs = [_pr("down", pr_id="old_1", days_old=10), _pr("flat", pr_id="old_2", days_old=10)]
    previous_attrs = [_attr("old_1", findings=[]), _attr("old_2", findings=[])]
    client = _client(Db([Result([_repo()]), Result([]), Result(current_prs), Result(current_attrs), Result(previous_prs), Result(previous_attrs)]), monkeypatch)

    response = client.get("/orgs/org_1/developer-leaderboard?days=7&include_trend=true&sort_by=violations")

    rows = {item["login"]: item for item in response.json()["developers"]}
    assert rows["down"]["trend"]["direction"] == "down"
    assert rows["flat"]["trend"]["direction"] == "flat"
    assert rows["new"]["trend"] is None
