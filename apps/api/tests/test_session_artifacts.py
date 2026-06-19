from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient

from apps.api.api.routes import sessions as session_routes
from apps.api.api.auth import get_current_org_id
from apps.api.api.services.session_artifacts import (
    append_session_artifact,
    close_session,
    make_artifact_record,
    parse_tool_artifact,
    sha256_text,
    should_run_close_pass,
    unified_diff,
)
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
    return SimpleNamespace(id="repo_1", org_id="org_1", name="demo")


def test_sha256_and_diff_generation() -> None:
    assert sha256_text("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    diff = unified_diff("src/app.py", "old\n", "new\n")
    assert "--- a/src/app.py" in diff
    assert "+++ b/src/app.py" in diff
    assert "-old" in diff
    assert "+new" in diff


def test_make_artifact_record_has_required_shape() -> None:
    artifact = make_artifact_record(
        file_path="src/app.py",
        tool="Edit",
        before_content="old",
        after_content="new",
        ts=datetime(2026, 4, 27, 9, 0, 0),
    )
    assert artifact["file_path"] == "src/app.py"
    assert artifact["tool"] == "Edit"
    assert artifact["before_hash"]
    assert artifact["after_hash"]
    assert artifact["diff"]
    assert artifact["ts"] == "2026-04-27T09:00:00Z"


def test_parse_tool_artifact_handles_distinct_payload_shapes() -> None:
    edit = parse_tool_artifact("Edit", {"file_path": "a.py", "old_string": "a", "new_string": "b"}, {"content": "b"})
    write = parse_tool_artifact("Write", {"file_path": "b.py", "content": "hello"}, {})
    notebook = parse_tool_artifact("NotebookEdit", {"notebook_path": "c.ipynb", "new_source": "print(1)"}, {})
    assert edit and edit.file_path == "a.py" and edit.after_content == "b"
    assert write and write.file_path == "b.py" and write.after_content == "hello"
    assert notebook and notebook.file_path == "c.ipynb" and notebook.after_content == "print(1)"
    assert parse_tool_artifact("Read", {"file_path": "x.py"}, {}) is None


def test_should_run_close_pass_uses_half_timeout_gate() -> None:
    now = datetime(2026, 4, 27, 9, 0, 0)
    fresh = SimpleNamespace(last_artifact_at=now - timedelta(minutes=10), inactivity_timeout_minutes=30)
    stale = SimpleNamespace(last_artifact_at=now - timedelta(minutes=16), inactivity_timeout_minutes=30)
    assert should_run_close_pass(None, now) is True
    assert should_run_close_pass(fresh, now) is False
    assert should_run_close_pass(stale, now) is True


def test_append_session_artifact_creates_session_and_hashes() -> None:
    db = Db([Result(None), Result(rows=[])])
    session, artifact, closed = asyncio.run(
        append_session_artifact(
            db,
            repo=_repo(),
            agent_runtime="claude_code",
            file_path="src/a.py",
            tool="Write",
            before_content=None,
            after_content="print('hi')\n",
            external_session_id="claude-session-1",
            ts=datetime(2026, 4, 27, 9, 0, 0),
        )
    )
    assert closed == []
    assert session in db.added
    assert session.session_id == "claude-session-1"
    assert session.produced_artifacts == [artifact]
    assert session.produced_file_hashes["src/a.py"] == artifact["after_hash"]
    assert session.files_touched == ["src/a.py"]
    assert "print('hi')" in session.code_produced


def test_append_session_artifact_closes_stale_session_before_new_one() -> None:
    old = AgentSession(
        id="session_old",
        repo_id="repo_1",
        org_id="org_1",
        session_id="old",
        agent_runtime="claude_code",
        session_start=datetime(2026, 4, 27, 8, 0, 0),
        created_at=datetime(2026, 4, 27, 8, 0, 0),
        last_artifact_at=datetime(2026, 4, 27, 8, 0, 0),
        inactivity_timeout_minutes=30,
    )
    db = Db([Result(None), Result(rows=[old])])
    session, _, closed = asyncio.run(
        append_session_artifact(
            db,
            repo=_repo(),
            agent_runtime="claude_code",
            file_path="src/new.py",
            tool="Write",
            before_content=None,
            after_content="new",
            external_session_id="new",
            ts=datetime(2026, 4, 27, 9, 0, 0),
        )
    )
    assert old in closed
    assert old.closed_at == datetime(2026, 4, 27, 9, 0, 0)
    assert session.session_id == "new"


def test_close_session_is_idempotent_and_matches_external_session_id() -> None:
    session = AgentSession(
        id="db-id",
        repo_id="repo_1",
        org_id="org_1",
        session_id="external-id",
        agent_runtime="claude_code",
    )
    db = Db([Result(session)])
    closed = asyncio.run(close_session(db, repo_id="repo_1", session_id="external-id", now=datetime(2026, 4, 27, 9, 0, 0)))
    assert closed is session
    assert session.closed_at == datetime(2026, 4, 27, 9, 0, 0)
    assert session.session_end == datetime(2026, 4, 27, 9, 0, 0)


def test_record_session_artifact_endpoint_writes_to_db_state() -> None:
    db = Db([Result(_repo()), Result(None), Result(rows=[])])
    body = session_routes.SessionArtifactBody(
        session_id="claude-session-1",
        agent_runtime="claude_code",
        tool="Write",
        file_path="src/a.py",
        before_content="",
        after_content="print('hi')\n",
    )
    response = asyncio.run(session_routes.record_session_artifact("repo_1", body, BackgroundTasks(), db, "org_1"))
    assert db.committed is True
    assert response["external_session_id"] == "claude-session-1"
    assert response["artifact_count"] == 1
    assert response["artifact"]["after_hash"]


def test_close_agent_session_endpoint_commits_and_returns_payload() -> None:
    session = AgentSession(
        id="db-id",
        repo_id="repo_1",
        org_id="org_1",
        session_id="external-id",
        agent_runtime="claude_code",
        session_start=datetime(2026, 4, 27, 8, 55, 0),
        created_at=datetime(2026, 4, 27, 8, 55, 0),
    )
    db = Db([Result(_repo()), Result(session)])
    response = asyncio.run(session_routes.close_agent_session("repo_1", "external-id", BackgroundTasks(), db, "org_1"))
    assert db.committed is True
    assert response["id"] == "db-id"
    assert response["closed_at"] is not None


def test_record_session_artifact_http_path_writes_response_from_db_state() -> None:
    db = Db([Result(_repo()), Result(None), Result(rows=[])])
    app = FastAPI()
    app.include_router(session_routes.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    client = TestClient(app)

    response = client.post(
        "/repos/repo_1/sessions/artifacts",
        json={
            "session_id": "claude-session-http",
            "agent_runtime": "claude_code",
            "tool": "Edit",
            "file_path": "src/http.py",
            "before_content": "old\n",
            "after_content": "new\n",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert db.committed is True
    assert payload["external_session_id"] == "claude-session-http"
    assert payload["artifact"]["file_path"] == "src/http.py"
    assert payload["artifact"]["before_hash"]
    assert payload["artifact"]["after_hash"]
