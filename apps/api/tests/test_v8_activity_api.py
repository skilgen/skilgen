from __future__ import annotations

import importlib
from datetime import datetime
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.index import app as index_app
from apps.api.api.v8.activity import router as activity_router
from packages.db.database import get_db


activity_migration = importlib.import_module("apps.api.alembic.versions.20260505_0004_activity_heatmap_index")


class Result:
    def __init__(self, scalar: object | None = None, rows: list[object] | None = None) -> None:
        self._scalar = scalar
        self._rows = rows or []

    def scalar_one_or_none(self) -> object | None:
        return self._scalar

    def scalar(self) -> object | None:
        return self._scalar

    def scalars(self) -> "Result":
        return self

    def all(self) -> list[object]:
        return self._rows


class Db:
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.org = SimpleNamespace(settings={"feature_flags": {"IA_V8": True}})

    async def get(self, model: object, key: str) -> object | None:
        return self.org

    async def execute(self, statement: object) -> Result:
        return self.results.pop(0)


def _client(db: Db) -> TestClient:
    app = FastAPI()
    app.include_router(activity_router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    return TestClient(app)


def test_activity_router_is_registered_on_main_app() -> None:
    paths = {route.path for route in index_app.routes}

    assert "/v8/orgs/{org_id}/activity/feed" in paths
    assert "/v8/orgs/{org_id}/repos/{repo_id}/activity/sessions/{session_id}/replay" in paths
    assert "/v8/orgs/{org_id}/repos/{repo_id}/activity/heatmap" in paths


def test_replay_contract_returns_timeline_and_export_html() -> None:
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api", sensitivity_tier="internal")
    session = SimpleNamespace(
        id="sess_db",
        session_id="sess_ext",
        repo_id="repo_1",
        agent_runtime="codex",
        engineer_login="ravi",
        session_start=datetime(2026, 5, 5, 1, 0, 0),
        session_end=None,
        created_at=datetime(2026, 5, 5, 1, 0, 0),
        duration_minutes=3,
        files_touched=["src/app.py"],
        skills_loaded=["api"],
        skill_paths_loaded=[],
        produced_artifacts=[{"tool": "Write", "file_path": "src/app.py", "diff": "+ok", "after_hash": "hash", "ts": "2026-05-05T01:00:00Z"}],
        outcome="success",
        task_description="PAY-4421",
        notes=None,
        transcript_summary=None,
    )
    skill = SimpleNamespace(id="skill_1", domain="api", skill_path="skills/api/SKILL.md", content_hash="hash")
    client = _client(Db([Result(repo), Result(session), Result(rows=[skill])]))

    response = client.get("/v8/orgs/org_1/repos/repo_1/activity/sessions/sess_db/replay")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session"]["id"] == "sess_db"
    assert payload["timeline"][0]["action"] == "Write"
    assert "<!doctype html>" in payload["export_html"]


def test_feed_contract_returns_v8_view_model() -> None:
    event = SimpleNamespace(id="evt_1", org_id="org_1", repo_id="repo_1", skill_id="skill_1", agent_runtime="codex", session_id="sess_ext", loaded_at=datetime(2026, 5, 5, 1, 0, 0))
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api", sensitivity_tier="confidential")
    skill = SimpleNamespace(id="skill_1", repo_id="repo_1", domain="api", skill_path="skills/api/SKILL.md", content_hash="hash")
    session = SimpleNamespace(id="sess_db", repo_id="repo_1", session_id="sess_ext", engineer_login="ravi", files_touched=["src/app.py"], task_description="PAY-4421", notes=None)
    client = _client(Db([Result(rows=[event]), Result(rows=[repo]), Result(rows=[skill]), Result(rows=[session])]))

    response = client.get("/v8/orgs/org_1/activity/feed?hours=24&risk_band=low")

    assert response.status_code == 200
    payload = response.json()
    assert payload["events"][0]["skill_signature_status"] == "verified"
    assert payload["events"][0]["repo_sensitivity_tier"] == "confidential"
    assert payload["events"][0]["trigger"]["label"] == "PAY-4421"


def test_sessions_contract_includes_cross_provider_rollup() -> None:
    codex = SimpleNamespace(
        id="sess_codex",
        session_id="codex_ext",
        repo_id="repo_1",
        agent_runtime="codex",
        engineer_login="ravi",
        session_start=datetime(2026, 5, 5, 1, 0, 0),
        session_end=None,
        created_at=datetime(2026, 5, 5, 1, 0, 0),
        duration_minutes=3,
        files_touched=["src/app.py"],
        skills_loaded=["api"],
        skill_paths_loaded=[],
        produced_artifacts=[],
        outcome="success",
        task_description=None,
        notes=None,
    )
    claude = SimpleNamespace(
        id="sess_claude",
        session_id="claude_ext",
        repo_id="repo_1",
        agent_runtime="claude_code",
        engineer_login="nina",
        session_start=datetime(2026, 5, 5, 2, 0, 0),
        session_end=None,
        created_at=datetime(2026, 5, 5, 2, 0, 0),
        duration_minutes=6,
        files_touched=[],
        skills_loaded=[],
        skill_paths_loaded=[],
        produced_artifacts=[],
        outcome="unknown",
        task_description=None,
        notes=None,
    )
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api", sensitivity_tier="internal")
    skill = SimpleNamespace(id="skill_1", repo_id="repo_1", domain="api", skill_path="skills/api/SKILL.md", content_hash="hash")
    client = _client(Db([Result(scalar=2), Result(rows=[codex, claude]), Result(rows=[repo]), Result(rows=[skill])]))

    response = client.get("/v8/orgs/org_1/activity/sessions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["rollup"]["total_sessions"] == 2
    assert {row["agent_provider"] for row in payload["rollup"]["providers"]} == {"codex", "claude_code"}


def test_sessions_rollup_endpoint_returns_provider_summary() -> None:
    session = SimpleNamespace(
        id="sess_codex",
        session_id="codex_ext",
        repo_id="repo_1",
        agent_runtime="codex",
        engineer_login="ravi",
        session_start=datetime(2026, 5, 5, 1, 0, 0),
        session_end=None,
        created_at=datetime(2026, 5, 5, 1, 0, 0),
        duration_minutes=3,
        files_touched=["src/app.py"],
        skills_loaded=[],
        skill_paths_loaded=[],
        produced_artifacts=[],
        outcome="success",
        task_description=None,
        notes=None,
    )
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api")
    client = _client(Db([Result(rows=[session]), Result(rows=[repo]), Result(rows=[])]))

    response = client.get("/v8/orgs/org_1/activity/sessions/rollup")

    assert response.status_code == 200
    assert response.json()["providers"][0]["agent_provider"] == "codex"


def test_session_detail_accepts_db_or_external_session_id() -> None:
    session = SimpleNamespace(
        id="sess_db",
        session_id="sess_ext",
        repo_id="repo_1",
        agent_runtime="codex",
        engineer_login="ravi",
        session_start=datetime(2026, 5, 5, 1, 0, 0),
        session_end=None,
        created_at=datetime(2026, 5, 5, 1, 0, 0),
        duration_minutes=3,
        files_touched=[],
        skills_loaded=[],
        skill_paths_loaded=[],
        produced_artifacts=[],
        outcome="success",
        task_description=None,
        notes=None,
    )
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api")
    client = _client(Db([Result(session), Result(repo), Result(rows=[])]))

    response = client.get("/v8/orgs/org_1/activity/sessions/sess_ext")

    assert response.status_code == 200
    assert response.json()["session"]["id"] == "sess_db"


def test_heatmap_contract_returns_repo_hour_cells() -> None:
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api")
    rows = [SimpleNamespace(repo_id="repo_1", repo_name="api", hour=3, action_count=4)]
    client = _client(Db([Result(repo), Result(rows=rows)]))

    response = client.get("/v8/orgs/org_1/repos/repo_1/activity/heatmap")

    assert response.status_code == 200
    payload = response.json()
    assert payload["cells"] == [{"repo_id": "repo_1", "repo_name": "api", "hour": 3, "action_count": 4, "deny_rate": None, "risk_band": "low"}]


def test_activity_endpoints_are_feature_flagged() -> None:
    db = Db([])
    db.org = SimpleNamespace(settings={"feature_flags": {"IA_V8": False}})
    client = _client(db)

    response = client.get("/v8/orgs/org_1/activity/feed")

    assert response.status_code == 404


def test_activity_heatmap_migration_upgrade_and_downgrade(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    class Op:
        @staticmethod
        def create_index(name: str, table_name: str, columns: list[str]) -> None:
            calls.append(("create", name))
            assert table_name == "skill_usage_events"
            assert columns == ["org_id", "repo_id", "loaded_at"]

        @staticmethod
        def drop_index(name: str, table_name: str) -> None:
            calls.append(("drop", name))
            assert table_name == "skill_usage_events"

    monkeypatch.setattr(activity_migration, "op", Op)

    activity_migration.upgrade()
    activity_migration.downgrade()

    assert calls == [("create", "ix_skill_usage_events_activity_heatmap"), ("drop", "ix_skill_usage_events_activity_heatmap")]
