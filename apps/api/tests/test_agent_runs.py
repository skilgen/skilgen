from __future__ import annotations

from datetime import datetime
import hashlib
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import agent_runs
from packages.db.database import get_db
from packages.db.models import AgentSession, AuditEvent


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
        if not self.results:
            return Result(None)
        return self.results.pop(0)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", full_name="acme/api", name="api", is_active=True, last_analysed_at=None)


def _client(db: Db) -> TestClient:
    app = FastAPI()
    app.include_router(agent_runs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    return TestClient(app)


def test_agent_run_ingest_creates_session_from_http_payload() -> None:
    repo = _repo()
    db = Db([Result(repo), Result(None)])
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
            "metadata": {
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
                "access_scope": "full-access",
                "full_access": True,
                "activity_metrics": {"edited_files": 1, "explored_files": 4, "searches": 2, "lists": 1, "commands": 5, "tool_calls": 6},
                "activity_details": {"edited_files": ["apps/api/routes/review.py"], "searches": ["rg TODO apps"], "commands": ["rg TODO apps"], "tools": ["shell"]},
                "external_api_calls": {"OpenAI/api.openai.com/model": 3, "GitHub/api.github.com/repos": 2},
                "tool_calls": [{"name": "shell", "parameters": {"command": "cat secret.txt"}, "content": "raw tool payload"}],
            },
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
    assert repo.last_analysed_at is not None
    audit = db.added[1]
    assert isinstance(audit, AuditEvent)
    assert audit.event_type == "agent.compliance"
    assert audit.resource_type == "agent_run"
    assert audit.resource_id == "codex-run-1"
    assert audit.metadata_json["provider"] == "OpenAI Codex CLI"
    assert audit.metadata_json["model"] == "gpt-5.2"
    assert audit.metadata_json["intelligence_tier"] == "very-high"
    assert audit.metadata_json["access_scope"] == "full-access"
    assert audit.metadata_json["content_retention"] == "metadata-only"
    assert audit.metadata_json["redaction_state"] == "raw-content-dropped"
    assert audit.metadata_json["tool_permissions"] == ["Write", "shell"]
    assert audit.metadata_json["activity_metrics"]["edited_files"] == 1
    assert audit.metadata_json["activity_metrics"]["explored_files"] == 4
    assert audit.metadata_json["activity_metrics"]["searches"] == 2
    assert audit.metadata_json["activity_metrics"]["lists"] == 1
    assert audit.metadata_json["activity_metrics"]["commands"] == 5
    assert audit.metadata_json["activity_metrics"]["tool_calls"] == 6
    assert audit.metadata_json["activity_details"]["edited_files"] == ["apps/api/routes/review.py"]
    assert audit.metadata_json["activity_details"]["searches"] == ["rg TODO apps"]
    assert audit.metadata_json["edited_files"] == 1
    assert audit.metadata_json["commands"] == 5
    assert audit.metadata_json["external_api_call_count"] == 5
    assert audit.metadata_json["external_api_calls"] == [
        {"provider": "OpenAI", "domain": "api.openai.com", "category": "model", "count": 3},
        {"provider": "GitHub", "domain": "api.github.com", "category": "repos", "count": 2},
    ]
    assert "source_envelope_hash" in audit.metadata_json
    assert "diff" not in audit.metadata_json
    assert "content" not in audit.metadata_json
    assert "secret.txt" not in str(audit.metadata_json)
    assert "raw tool payload" not in str(audit.metadata_json)


def test_agent_run_ingest_preserves_intelligence_and_pr_metadata() -> None:
    pr = SimpleNamespace(id="pr_128", repo_id="repo_1", github_pr_number=128, title="Activity intelligence layer", head_sha="abc123")
    db = Db([Result(_repo()), Result(pr), Result(None)])
    client = _client(db)
    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "codex-run-pr-128",
            "agent": {"vendor": "OpenAI", "product": "Codex"},
            "repo_id": "repo_1",
            "code_artifacts": [{"file_path": "apps/api/api/v8/insights/router.py", "tool": "apply_patch", "after_hash": "abc"}],
            "metadata": {
                "model": "gpt-5.2-high",
                "intelligence_tier": "high",
                "task_type": "test and verification",
                "tokens_input": 12000,
                "tokens_output": 3000,
                "tokens_cached_input": 4000,
                "tokens_reasoning_output": 700,
                "token_source": "codex_jsonl_last_token_usage",
                "cost_usd": "1.25",
                "cost_source": "estimated_from_provider_token_usage",
                "cost_estimate": True,
                "latency_ms": 2400,
                "pr_number": 128,
                "head_sha": "abc123",
                "branch": "feature/intelligence-layer",
                "policy_decision": "require_approval",
                "approval_status": "pending",
                "mcp_tools": ["browser"],
            },
        },
    )

    assert response.status_code == 200
    audit = db.added[1]
    assert audit.metadata_json["session_id"] == "codex-run-pr-128"
    assert audit.metadata_json["task_type"] == "test and verification"
    assert audit.metadata_json["tokens_input"] == 12000
    assert audit.metadata_json["tokens_output"] == 3000
    assert audit.metadata_json["tokens_total"] == 15000
    assert audit.metadata_json["tokens_cached_input"] == 4000
    assert audit.metadata_json["tokens_reasoning_output"] == 700
    assert audit.metadata_json["token_source"] == "codex_jsonl_last_token_usage"
    assert audit.metadata_json["cost_usd"] == 1.25
    assert audit.metadata_json["cost_source"] == "estimated_from_provider_token_usage"
    assert audit.metadata_json["cost_estimate"] is True
    assert audit.metadata_json["latency_ms"] == 2400.0
    assert audit.metadata_json["pr_id"] == "pr_128"
    assert audit.metadata_json["pr_number"] == 128
    assert audit.metadata_json["pr_title"] == "Activity intelligence layer"
    assert audit.metadata_json["head_sha"] == "abc123"
    assert audit.metadata_json["branch"] == "feature/intelligence-layer"
    assert audit.metadata_json["policy_decision"] == "require_approval"
    assert audit.metadata_json["approval_status"] == "pending"
    assert audit.metadata_json["file_targets"] == ["apps/api/api/v8/insights/router.py"]
    assert audit.metadata_json["mcp_tools"] == ["browser"]


def test_agent_run_ingest_matches_commit_sha_to_commit_row() -> None:
    repo = _repo()
    commit = SimpleNamespace(repo_id="repo_1", sha="def456", pr_id=None)
    db = Db([Result(repo), Result(None), Result(None), Result(commit), Result(None), Result(None)])
    client = _client(db)

    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "codex-run-commit-1",
            "agent": {"vendor": "OpenAI", "product": "Codex"},
            "repo_id": "repo_1",
            "code_artifacts": [{"file_path": "apps/api/api/v8/settings/router.py", "tool": "apply_patch", "after_hash": "abc"}],
            "metadata": {
                "commit_sha": "def456",
                "branch": "main",
                "model": "gpt-5.2",
                "tokens_input": 100,
                "tokens_output": 25,
                "cost_usd": 0.012,
            },
        },
    )

    assert response.status_code == 200
    audit = next(item for item in db.added if isinstance(item, AuditEvent))
    assert audit.metadata_json["github_enrichment_status"] == "matched"
    assert audit.metadata_json["github_enrichment_source"] == "commits"
    assert audit.metadata_json["commit_sha"] == "def456"
    assert audit.metadata_json["git_url"] == "https://github.com/acme/api/commit/def456"


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
    assert len(db.added) == 1
    assert isinstance(db.added[0], AuditEvent)
    assert db.added[0].metadata_json["provider"] == "Anthropic Claude Code"
    assert session.skills_loaded == ["auth", "security"]
    assert session.closed_at == datetime(2026, 4, 27, 10, 15, 0)
    assert session.produced_file_hashes["src/auth.py"] == "def"


def test_agent_run_ingest_updates_existing_audit_event_idempotently() -> None:
    repo = _repo()
    existing_audit = AuditEvent(
        id="audit_1",
        org_id="org_1",
        event_type="agent.compliance",
        action="ingested",
        summary="old",
        repo_id="repo_1",
        repo_name="acme/api",
        resource_type="agent_run",
        resource_id="codex-run-1",
        metadata_json={"model": "old"},
        severity="info",
    )
    db = Db([Result(repo), Result(None), Result(existing_audit)])
    client = _client(db)
    response = client.post(
        "/orgs/org_1/agent-runs",
        json={
            "spec_version": "0",
            "session_id": "codex-run-1",
            "agent": {"vendor": "OpenAI", "product": "Codex Desktop", "runtime": "codex_cli"},
            "repo_id": "repo_1",
            "metadata": {"model": "gpt-5.5", "tokens_total": 42},
        },
    )

    assert response.status_code == 200
    assert len([item for item in db.added if isinstance(item, AuditEvent)]) == 0
    assert existing_audit.metadata_json["model"] == "gpt-5.5"
    assert existing_audit.metadata_json["tokens_total"] == 42
    assert repo.last_analysed_at is not None


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
