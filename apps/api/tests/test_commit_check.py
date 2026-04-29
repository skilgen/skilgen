from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api import pr_comment
from apps.api.api.routes import repos
from apps.api.api.services import commit_check
from packages.db.database import get_db
from packages.db.models import PRAttribution, PullRequest, Skill


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
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.committed = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    async def commit(self):
        self.committed = True


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", full_name="acme/api", github_installation_id=123)


def _skill() -> Skill:
    skill = Skill(repo_id="repo_1", domain="database", skill_path=".skillayer/database/SKILL.md", content="")
    skill.id = "skill_1"
    skill.anti_patterns = ["never use SELECT *"]
    return skill


def test_commit_check_endpoint_returns_warning_from_diff_without_github() -> None:
    db = Db([Result(_repo()), Result(rows=[_skill()])])
    app = FastAPI()
    app.include_router(repos.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    client = TestClient(app)

    response = client.post(
        "/repos/repo_1/commits/abc123/check",
        json={"diff": "diff --git a/db.py b/db.py\n--- a/db.py\n+++ b/db.py\n@@ -1 +1 @@\n+rows = db.execute('SELECT * FROM users')"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["violations"] == []
    assert len(payload["warnings"]) == 1
    assert payload["skills_checked"] == 1
    assert payload["lines_scanned"] == 1
    assert payload["risk_tier"] == "yellow"


def test_publish_pr_commit_check_updates_attribution_and_posts_deduped_comment(monkeypatch) -> None:
    repo = _repo()
    pr = PullRequest(repo_id="repo_1", github_pr_number=42)
    pr.id = "pr_1"
    attribution = PRAttribution(pr_id="pr_1", primary_agent="codex", confidence=0.8)
    attribution.id = "attr_1"
    db = Db([Result(rows=[_skill()]), Result(attribution)])
    posted: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    risk_calls: list[str] = []
    policy_calls: list[str] = []

    async def fake_fetch(*args, **kwargs):
        return "diff --git a/db.py b/db.py\n--- a/db.py\n+++ b/db.py\n@@ -1 +1 @@\n+rows = db.execute('SELECT * FROM users')"

    async def fake_comment(**kwargs):
        posted.append(kwargs)
        return True

    async def fake_check(**kwargs):
        checks.append(kwargs)
        return True

    async def fake_risk(pr_id, db):
        risk_calls.append(pr_id)
        return {"score": 12, "tier": "green", "breakdown": {}}

    async def fake_policies(org_id, attribution_arg, db):
        policy_calls.append(org_id)
        return []

    monkeypatch.setattr(commit_check, "fetch_commit_diff", fake_fetch)
    monkeypatch.setattr(commit_check, "post_or_update_tracked_violation_comment", fake_comment)
    monkeypatch.setattr(commit_check, "create_skill_review_check_run", fake_check)
    monkeypatch.setattr(commit_check, "compute_risk_score", fake_risk)
    monkeypatch.setattr(commit_check, "evaluate_pr_policies", fake_policies)

    result = __import__("asyncio").run(
        commit_check.publish_pr_commit_check(repo=repo, pr=pr, sha="head_sha", db=db, installation_id=123, base_sha="base_sha")
    )

    assert result.risk_tier == "yellow"
    assert attribution.skills_violated == result.warnings
    assert len(posted) == 1
    assert posted[0]["pr_number"] == 42
    assert posted[0]["pr_id"] == "pr_1"
    assert checks[0]["head_sha"] == "head_sha"
    assert checks[0]["warnings"] == result.warnings
    assert checks[0]["policy_failures"] == []
    assert risk_calls == ["pr_1"]
    assert policy_calls == ["org_1"]
    assert db.committed is True


def test_publish_pr_commit_check_passes_policy_failures_to_check_run(monkeypatch) -> None:
    repo = _repo()
    pr = PullRequest(repo_id="repo_1", github_pr_number=43)
    pr.id = "pr_2"
    attribution = PRAttribution(pr_id="pr_2", primary_agent="codex", confidence=0.8, risk_tier="red")
    attribution.id = "attr_2"
    db = Db([Result(rows=[]), Result(attribution)])
    checks: list[dict[str, Any]] = []

    async def fake_fetch(*args, **kwargs):
        return "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1 +1 @@\n+print('ok')"

    async def fake_check(**kwargs):
        checks.append(kwargs)
        return True

    async def fake_risk(pr_id, db):
        attribution.risk_tier = "red"
        return {"score": 90, "tier": "red", "breakdown": {}}

    async def fake_policies(org_id, attribution_arg, db):
        return [{"policy_id": "p1", "name": "Block red", "rule_type": "block_on_red", "message": "Policy failed"}]

    monkeypatch.setattr(commit_check, "fetch_commit_diff", fake_fetch)
    monkeypatch.setattr(commit_check, "create_skill_review_check_run", fake_check)
    monkeypatch.setattr(commit_check, "compute_risk_score", fake_risk)
    monkeypatch.setattr(commit_check, "evaluate_pr_policies", fake_policies)

    result = __import__("asyncio").run(
        commit_check.publish_pr_commit_check(repo=repo, pr=pr, sha="head_sha", db=db, installation_id=123, base_sha="base_sha")
    )

    assert result.risk_tier == "green"
    assert checks[0]["policy_failures"][0]["rule_type"] == "block_on_red"


def test_violation_comment_dedupe_marker_is_stable() -> None:
    marker = pr_comment.violation_marker("src/auth.py", 42, "auth", "JWT in localStorage")
    body = pr_comment.build_violation_comment(
        marker=marker,
        skill_name="auth",
        severity="critical",
        explanation="JWT stored in localStorage",
        suggested_fix="Use httpOnly cookie",
        dashboard_skill_url="https://app.skillayer.com/dashboard/repos/repo_1/skills/skill_1",
        dashboard_settings_url="https://app.skillayer.com/dashboard/settings",
        dashboard_pr_url="https://app.skillayer.com/dashboard/agent-prs/pr_1",
    )

    assert marker == pr_comment.violation_marker("src/auth.py", 42, "auth", "JWT in localStorage")
    assert marker == pr_comment.violation_marker("src/auth.py", 42, "auth", "same location, updated wording")
    assert f"skillayer-violation:{marker}" in body
    assert "View in PR Inbox" in body
    assert "Powered by Skillayer" in body


def test_check_run_policy_failures_override_conclusion(monkeypatch) -> None:
    payloads: list[dict[str, Any]] = []

    class Response:
        status_code = 201

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, headers, timeout):
            payloads.append(json)
            return Response()

    monkeypatch.setattr(pr_comment, "get_installation_token", lambda installation_id: "token")
    monkeypatch.setattr(pr_comment.httpx, "AsyncClient", Client)

    ok = __import__("asyncio").run(
        pr_comment.create_skill_review_check_run(
            full_name="acme/api",
            installation_id=123,
            head_sha="abc",
            violations=[],
            warnings=[],
            skills_checked=4,
            policy_failures=[{"message": "Policy 'Block red': PR risk tier is RED - merge blocked."}],
        )
    )

    assert ok is True
    assert payloads[0]["conclusion"] == "action_required"
    assert "Policy Violations" in payloads[0]["output"]["summary"]
