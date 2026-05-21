from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from packages.db.database import get_db
from packages.db.models import AuditEvent, Org, SourceConnection


class Result:
    def __init__(self, scalar=None, rows=None) -> None:
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def scalar_one(self):
        return self.scalar

    def scalar(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None


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


def _client(db: Db, runtime_status: dict[str, dict]) -> TestClient:
    async def _runtime_stub(org_id: str, _db) -> dict[str, dict]:
        return runtime_status

    orgs.get_agent_connection_status = _runtime_stub  # type: ignore[assignment]

    app = FastAPI()
    app.include_router(orgs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    return TestClient(app)


def _repo():
    return SimpleNamespace(
        id="repo_1",
        org_id="org_1",
        full_name="acme/api",
        name="api",
        is_active=True,
        github_installation_id=123,
    )


def test_connect_status_empty_org_returns_next_step() -> None:
    db = Db([Result(rows=[])])
    client = _client(db, runtime_status={"codex_cli": {"connected": False, "last_seen_at": None, "load_count_30d": 0}})
    response = client.get("/orgs/org_1/connect/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["repos_connected"] == 0
    assert payload["github_app_installed"] is False
    assert payload["github_enrichment_active"] is False
    assert payload["next_step"] == "Connect a GitHub repository"


def test_connect_status_counts_github_enrichment_and_join_gaps() -> None:
    repo = _repo()
    recent_missing = AuditEvent(
        org_id="org_1",
        event_type="agent.compliance",
        action="ingested",
        summary="missing join",
        severity="warning",
        metadata_json={"github_enrichment_status": "missing"},
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    results = [
        Result(rows=[repo]),  # repos
        Result(scalar=SimpleNamespace(skill_count=3)),  # latest analysis run
        Result(scalar=5),  # PR count
        Result(scalar=7),  # commit count
        Result(scalar=datetime.utcnow() - timedelta(hours=3)),  # last PR updated_at
        Result(scalar=datetime.utcnow() - timedelta(hours=1)),  # last commit updated_at
        Result(rows=[recent_missing]),  # recent audit events
    ]
    db = Db(results)
    client = _client(db, runtime_status={"codex_cli": {"connected": True, "last_seen_at": "2026-05-20T00:00:00", "load_count_30d": 4}})
    response = client.get("/orgs/org_1/connect/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["repos_connected"] == 1
    assert payload["skills_generated"] == 3
    assert payload["github_app_installed"] is True
    assert payload["github_repo_count"] == 1
    assert payload["github_pr_count"] == 5
    assert payload["github_commit_count"] == 7
    assert payload["github_enrichment_active"] is True
    assert payload["github_join_missing_30d"] == 1
    assert payload["agent_runtimes"]["codex_cli"]["connected"] is True


def test_connect_status_surfaces_provider_sync_health() -> None:
    repo = _repo()
    org = Org(
        id="org_1",
        github_org_id=1,
        login="acme",
        name="Acme",
        settings={
            "v8_agent_compliance_connectors": {
                "openai-compliance": {
                    "enabled": True,
                    "cursor": "openai-cursor-1",
                    "last_sync_status": "success",
                    "last_sync_mode": "provider-pull",
                    "last_success_at": "2026-05-20T18:00:00+00:00",
                    "next_sync_at": "2026-05-20T18:15:00+00:00",
                    "last_ingested_count": 25,
                    "total_ingested_count": 125,
                    "last_provider_sync_job": {"status": "completed", "job_id": "job-openai-1"},
                },
                "anthropic-compliance": {
                    "enabled": True,
                    "last_sync_status": "queued",
                    "last_provider_sync_job": {"status": "running", "job_id": "job-anthropic-1", "next_sync_at": "2026-05-20T18:20:00+00:00"},
                },
            }
        },
    )
    openai_connection = SourceConnection(
        org_id="org_1",
        source_type="agent_compliance:openai-compliance",
        status="configured",
    )
    results = [
        Result(rows=[repo]),  # repos
        Result(scalar=SimpleNamespace(skill_count=3)),  # latest analysis run
        Result(scalar=0),  # PR count
        Result(scalar=0),  # commit count
        Result(scalar=None),  # last PR updated_at
        Result(scalar=None),  # last commit updated_at
        Result(rows=[]),  # recent audit events
        Result(scalar=org),  # org settings
        Result(rows=[openai_connection]),  # provider credential connections
    ]
    db = Db(results)
    client = _client(db, runtime_status={"codex_cli": {"connected": True, "last_seen_at": "2026-05-20T00:00:00", "load_count_30d": 4}})

    response = client.get("/orgs/org_1/connect/status")

    assert response.status_code == 200
    providers = {item["id"]: item for item in response.json()["provider_sync"]}
    assert providers["openai-compliance"]["connected"] is True
    assert providers["openai-compliance"]["credential_state"] == "encrypted"
    assert providers["openai-compliance"]["last_sync_status"] == "success"
    assert providers["openai-compliance"]["active_job_status"] == "completed"
    assert providers["openai-compliance"]["last_ingested_count"] == 25
    assert providers["openai-compliance"]["total_ingested_count"] == 125
    assert providers["openai-compliance"]["last_cursor"] == "openai-cursor-1"
    assert providers["anthropic-compliance"]["connected"] is False
    assert providers["anthropic-compliance"]["active_job_status"] == "running"
