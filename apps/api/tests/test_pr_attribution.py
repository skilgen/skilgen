from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import repos
from apps.api.api.services.pr_attribution import _tier1_session_hash_match, attribute_pr
from packages.db.database import get_db
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
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.added: list[Any] = []
        self.committed = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        for index, item in enumerate(self.added, start=1):
            if getattr(item, "id", None) is None:
                item.id = f"attr_{index}"

    async def commit(self):
        self.committed = True


def _pr() -> PullRequest:
    pr = PullRequest(repo_id="repo_1", github_pr_number=42)
    pr.id = "pr_1"
    pr.author_login = "octocat"
    pr.author_type = "User"
    pr.additions = 10
    pr.deletions = 2
    pr.raw = {"github": {"head": {"ref": "feature/auth"}}}
    return pr


def _commit(message: str = "change", raw: dict | None = None, additions: int = 10, deletions: int = 2) -> Commit:
    commit = Commit(repo_id="repo_1", sha="commit_1", message=message, additions=additions, deletions=deletions)
    commit.id = "commit_row_1"
    commit.pr_id = "pr_1"
    commit.raw = raw or {}
    return commit


def _session(agent: str, session_id: str, hashes: dict[str, str], skills: list[str]) -> AgentSession:
    session = AgentSession(
        id=session_id,
        repo_id="repo_1",
        org_id="org_1",
        session_id=session_id,
        agent_runtime=agent,
        produced_file_hashes=hashes,
        skills_loaded=skills,
        skill_paths_loaded=skills,
        session_start=datetime(2026, 4, 28, 10, 0, 0),
        created_at=datetime(2026, 4, 28, 10, 0, 0),
    )
    return session


def test_tier2_commit_trailer_attributes_claude() -> None:
    db = Db([
        Result(_pr()),
        Result(rows=[_commit("Fix auth\n\nCo-Authored-By: Claude <noreply@anthropic.com>")]),
        Result(rows=[]),
        Result(None),
    ])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "claude_code"
    assert attribution.confidence == 0.85
    assert attribution.skills_loaded == []
    assert db.committed is True


def test_tier1_file_content_hash_match_beats_commit_trailer_and_flattens_skills() -> None:
    pr = _pr()
    commit = _commit(
        "Fix auth\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
        raw={"file_hashes": {"src/auth.py": "sha256_after"}},
        additions=7,
        deletions=3,
    )
    session = _session("codex", "session_1", {"src/auth.py": "sha256_after"}, ["auth", "security", "auth"])
    db = Db([Result(pr), Result(rows=[commit]), Result(rows=[session]), Result(None)])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "codex"
    assert attribution.confidence == 0.90
    assert attribution.lines_by_agent == {"codex": 10}
    assert attribution.sessions == ["session_1"]
    assert attribution.skills_loaded == ["auth", "security"]


def test_tier1_mixed_when_hashes_match_multiple_agents() -> None:
    pr = _pr()
    commits = [
        _commit(raw={"file_hashes": {"src/a.py": "hash_a"}}, additions=3, deletions=1),
        _commit(raw={"file_hashes": {"src/b.py": "hash_b"}}, additions=4, deletions=1),
    ]
    commits[1].sha = "commit_2"
    sessions = [
        _session("claude_code", "session_a", {"src/a.py": "hash_a"}, ["agents"]),
        _session("codex", "session_b", {"src/b.py": "hash_b"}, ["cli"]),
    ]
    db = Db([Result(pr), Result(rows=commits), Result(rows=sessions), Result(None)])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "mixed"
    assert attribution.confidence == 0.70
    assert attribution.lines_by_agent == {"claude_code": 4, "codex": 5}
    assert attribution.sessions == ["session_a", "session_b"]
    assert attribution.skills_loaded == ["agents", "cli"]


def test_tier1_matches_produced_artifact_after_hash() -> None:
    pr = _pr()
    commit = _commit(raw={"file_hashes": {"src/generated.py": "artifact_hash"}}, additions=2, deletions=1)
    session = _session("claude_code", "session_artifact", {}, ["backend"])
    session.produced_artifacts = [{"file_path": "src/generated.py", "after_hash": "artifact_hash", "tool": "Write"}]
    db = Db([Result(pr), Result(rows=[commit]), Result(rows=[session]), Result(None)])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "claude_code"
    assert attribution.confidence == 0.95
    assert attribution.lines_by_agent == {"claude_code": 3}
    assert attribution.sessions == ["session_artifact"]


def test_tier1_matches_codex_raw_file_after_sha256() -> None:
    pr = _pr()
    commit = _commit(raw={"file_hashes": {"src/codex.py": "codex_hash"}}, additions=5, deletions=0)
    session = _session("codex", "session_codex", {}, ["agents"])
    session.raw = SimpleNamespace(codex=SimpleNamespace(files=[{"path": "src/codex.py", "after_sha256": "codex_hash"}]))
    db = Db([Result(pr), Result(rows=[commit]), Result(rows=[session]), Result(None)])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "codex"
    assert attribution.confidence == 0.90
    assert attribution.lines_by_agent == {"codex": 5}


def test_tier1_matches_copilot_raw_suggestion_content_hash() -> None:
    pr = _pr()
    commit = _commit(raw={"content_hashes": ["copilot_hash"]}, additions=4, deletions=2)
    session = _session("copilot", "session_copilot", {}, ["frontend"])
    session.raw = SimpleNamespace(copilot=SimpleNamespace(suggestions=[{"file": "src/ui.tsx", "content_hash": "copilot_hash"}]))
    db = Db([Result(pr), Result(rows=[commit]), Result(rows=[session]), Result(None)])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "copilot"
    assert attribution.confidence == 0.75
    assert attribution.lines_by_agent == {"copilot": 6}


def test_tier1_vendor_confidence_caps() -> None:
    expected = {
        "claude_code": 0.95,
        "codex": 0.90,
        "copilot": 0.75,
        "cursor": 0.80,
        "devin": 0.85,
        "human": 1.0,
    }
    for agent, confidence in expected.items():
        decision = _tier1_session_hash_match(
            [_commit(raw={"file_hashes": {"src/a.py": f"{agent}_hash"}})],
            [_session(agent, f"session_{agent}", {"src/a.py": f"{agent}_hash"}, [])],
        )
        assert decision is not None
        assert decision.primary_agent == agent
        assert decision.confidence == confidence

    mixed = _tier1_session_hash_match(
        [_commit(raw={"file_hashes": {"src/a.py": "hash_a", "src/b.py": "hash_b"}})],
        [
            _session("claude_code", "session_claude", {"src/a.py": "hash_a"}, []),
            _session("codex", "session_codex", {"src/b.py": "hash_b"}, []),
        ],
    )
    assert mixed is not None
    assert mixed.primary_agent == "mixed"
    assert mixed.confidence == 0.70


def test_human_fallback_has_empty_skills_loaded() -> None:
    db = Db([Result(_pr()), Result(rows=[_commit("Human change")]), Result(rows=[]), Result(None)])

    attribution = __import__("asyncio").run(attribute_pr("pr_1", db))

    assert attribution.primary_agent == "human"
    assert attribution.confidence == 1.0
    assert attribution.skills_loaded == []


def test_attribution_endpoint_computes_and_returns_pr_attribution() -> None:
    pr = _pr()
    db = Db([
        Result(SimpleNamespace(id="repo_1", org_id="org_1")),
        Result(pr),
        Result(None),
        Result(pr),
        Result(rows=[_commit("Fix auth\n\nCo-Authored-By: Claude <noreply@anthropic.com>")]),
        Result(rows=[]),
        Result(None),
    ])
    app = FastAPI()
    app.include_router(repos.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    client = TestClient(app)

    response = client.get("/repos/repo_1/prs/42/attribution")

    assert response.status_code == 200
    payload = response.json()
    assert payload["primary_agent"] == "claude_code"
    assert payload["confidence"] == 0.85
    assert payload["skills_loaded"] == []
    assert db.committed is True
