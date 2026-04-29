from __future__ import annotations

from datetime import datetime
import hashlib
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import agent_runs
from packages.db.database import get_db
from packages.db.models import AgentSession


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
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        return self.results.pop(0)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", full_name="acme/api", name="api", is_active=True)


def _client(db: Db) -> TestClient:
    app = FastAPI()
    app.include_router(agent_runs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    return TestClient(app)


def test_agent_run_ingest_creates_session_from_http_payload() -> None:
    db = Db([Result(_repo()), Result(None)])
    client = _client(db)
    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "codex-run-1",
            "agent": {"vendor": "OpenAI", "product": "Codex CLI"},
            "repo_id": "repo_1",
            "skills_loaded": ["agents", {"domain": "cli"}],
            "code_artifacts": [{"file_path": "apps/api/routes/review.py", "tool": "Write", "after_hash": "abc", "diff": "+hello"}],
            "outcome": "success",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "created"
    assert db.committed is True
    session = db.added[0]
    assert isinstance(session, AgentSession)
    assert session.session_id == "codex-run-1"
    assert session.agent_runtime == "codex_cli"
    assert session.skills_loaded == ["agents", "cli"]
    assert session.produced_file_hashes == {"apps/api/routes/review.py": "abc"}
    assert session.files_touched == ["apps/api/routes/review.py"]
    assert "+hello" in session.code_produced


def test_agent_run_ingest_derives_after_hash_from_artifact_content() -> None:
    db = Db([Result(_repo()), Result(None)])
    client = _client(db)
    content = "def generated():\n    return 'ok'\n"
    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "codex-run-content",
            "agent": {"vendor": "OpenAI", "product": "Codex CLI"},
            "repo_id": "repo_1",
            "code_artifacts": [{"file_path": "src/generated.py", "content": content}],
        },
    )

    assert response.status_code == 200
    session = db.added[0]
    assert session.produced_file_hashes == {"src/generated.py": expected_hash}
    assert session.produced_artifacts[0]["after_hash"] == expected_hash
    assert session.produced_artifacts[0]["content"] == content


def test_agent_run_ingest_updates_existing_session_idempotently() -> None:
    session = AgentSession(
        id="session_1",
        repo_id="repo_1",
        org_id="org_1",
        session_id="claude-run-1",
        agent_runtime="claude_code",
        skills_loaded=["auth"],
        skill_paths_loaded=["auth"],
        produced_artifacts=[],
        produced_file_hashes={},
        session_start=datetime(2026, 4, 27, 10, 0, 0),
        created_at=datetime(2026, 4, 27, 10, 0, 0),
    )
    db = Db([Result(_repo()), Result(session)])
    client = _client(db)
    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "claude-run-1",
            "agent": {"vendor": "Anthropic", "product": "Claude Code"},
            "repo_id": "repo_1",
            "skills_loaded": ["auth", "security"],
            "code_artifacts": [{"file_path": "src/auth.py", "after_hash": "def", "diff": "-old\n+new"}],
            "ended_at": "2026-04-27T10:15:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"session_id": "session_1", "status": "updated"}
    assert db.added == []
    assert session.skills_loaded == ["auth", "security"]
    assert session.closed_at == datetime(2026, 4, 27, 10, 15, 0)
    assert session.produced_file_hashes["src/auth.py"] == "def"


def test_agent_run_requires_repo_scope() -> None:
    db = Db([Result(rows=[_repo(), SimpleNamespace(id="repo_2", org_id="org_1", is_active=True)])])
    client = _client(db)
    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "cursor-run-1",
            "agent": {"vendor": "Anysphere", "product": "Cursor"},
            "skills_loaded": [],
        },
    )

    assert response.status_code == 400
