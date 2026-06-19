from __future__ import annotations

from datetime import datetime
from typing import Any

from apps.api.api.services.pr_risk import coverage_signal, compute_risk_score, incident_signal, ownership_signal, violation_signal
from packages.db.models import AgentSession, Commit, PRAttribution, PullRequest


class Result:
    def __init__(self, scalar=None, rows=None) -> None:
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, pr: PullRequest, results: list[Result]) -> None:
        self.pr = pr
        self.results = results
        self.added: list[Any] = []
        self.committed = False

    async def get(self, model, id_):
        return self.pr if model is PullRequest and id_ == self.pr.id else None

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        self.committed = True


def _pr(raw: dict | None = None) -> PullRequest:
    pr = PullRequest(repo_id="repo_1", github_pr_number=42)
    pr.id = "pr_1"
    pr.additions = 20
    pr.deletions = 4
    pr.raw = raw or {"files": [{"filename": "src/auth.py"}]}
    return pr


def _commit(path: str = "src/auth.py") -> Commit:
    commit = Commit(repo_id="repo_1", sha="sha_1")
    commit.id = "commit_1"
    commit.pr_id = "pr_1"
    commit.raw = {"files": [{"filename": path}]}
    return commit


def _incident(path: str = "src/auth.py") -> AgentSession:
    return AgentSession(
        id="session_1",
        repo_id="repo_1",
        org_id="org_1",
        session_id="session_1",
        agent_runtime="codex",
        files_touched=[path],
        outcome="incident",
        session_start=datetime(2026, 4, 28, 10, 0, 0),
        created_at=datetime(2026, 4, 28, 10, 0, 0),
    )


def test_violation_signal_counts_error_and_warning_points() -> None:
    signal = violation_signal([
        {"severity": "critical"},
        {"severity": "error"},
        {"severity": "warning"},
    ])

    assert signal["points"] == 24
    assert signal["error_count"] == 2
    assert signal["warning_count"] == 1


def test_incident_signal_scores_file_overlap() -> None:
    signal = incident_signal({"src/auth.py"}, [_incident("src/auth.py")])

    assert signal["points"] == 12
    assert signal["incident_count"] == 1
    assert signal["files"] == ["src/auth.py"]


def test_coverage_signal_flags_added_code_without_tests() -> None:
    signal = coverage_signal(_pr(), {"src/auth.py"})

    assert signal["points"] == 15
    assert signal["test_files_changed"] is False


def test_ownership_signal_skips_when_codeowners_missing() -> None:
    signal = ownership_signal(_pr(), {"src/auth.py"})

    assert signal["points"] == 0
    assert "No CODEOWNERS" in signal["explanation"]


def test_red_pr_from_errors_incidents_and_coverage_drop() -> None:
    pr = _pr(raw={"files": [{"filename": "src/auth.py"}], "check_runs": [{"coverage_delta": -5}]})
    attribution = PRAttribution(
        pr_id="pr_1",
        primary_agent="codex",
        confidence=0.9,
        skills_violated=[
            {"severity": "critical"},
            {"severity": "error"},
            {"severity": "error"},
            {"severity": "critical"},
        ],
    )
    db = Db(pr, [Result(attribution), Result(rows=[_commit()]), Result(rows=[_incident(), _incident()])])

    result = __import__("asyncio").run(compute_risk_score("pr_1", db))

    assert result["score"] >= 70
    assert result["tier"] == "red"
    assert attribution.risk_score == result["score"]
    assert db.committed is True


def test_clean_pr_scores_green() -> None:
    pr = _pr(raw={"files": [{"filename": "tests/test_auth.py"}]})
    attribution = PRAttribution(pr_id="pr_1", primary_agent="human", confidence=1.0, skills_violated=[])
    db = Db(pr, [Result(attribution), Result(rows=[_commit("tests/test_auth.py")]), Result(rows=[])])

    result = __import__("asyncio").run(compute_risk_score("pr_1", db))

    assert result["score"] <= 29
    assert result["tier"] == "green"
