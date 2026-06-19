from __future__ import annotations

import importlib
from datetime import datetime
from types import SimpleNamespace

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id, get_current_org_id_optional
from apps.api.api.index import app
from apps.api.api.v8.skills.router import router as v8_skills_router
from packages.db.database import get_db


skills_router_module = importlib.import_module("apps.api.api.v8.skills.router")
repo_sensitivity_migration = importlib.import_module("apps.api.alembic.versions.20260505_0001_add_repo_sensitivity_tier")


class Result:
    def __init__(self, rows=None, scalar_value=None, scalar_one_or_none_value=None) -> None:
        self.rows = rows or []
        self.scalar_value = scalar_value
        self.scalar_one_or_none_value = scalar_one_or_none_value

    def all(self):
        return self.rows

    def scalars(self):
        return self

    def scalar(self):
        return self.scalar_value

    def scalar_one_or_none(self):
        return self.scalar_one_or_none_value


class Db:
    def __init__(self, results: list[Result] | None = None) -> None:
        self.results = results or []

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)


def _client(db: Db) -> TestClient:
    test_app = FastAPI()
    test_app.include_router(v8_skills_router)
    test_app.dependency_overrides[get_db] = lambda: db
    test_app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    test_app.dependency_overrides[get_current_org_id_optional] = lambda: "org_1"
    return TestClient(test_app)


def _skill() -> SimpleNamespace:
    return SimpleNamespace(
        id="skill_1",
        skill_path="skills/backend/SKILL.md",
        domain="backend",
        score_total=88,
        score_groundedness=22,
        score_coverage=21,
        score_freshness=20,
        score_structure=25,
        is_stale=False,
        content_hash="abc123",
        updated_at=datetime(2026, 5, 1, 12, 0, 0),
    )


def _repo() -> SimpleNamespace:
    return SimpleNamespace(
        id="repo_1",
        name="api",
        full_name="platform/api",
        language="Python",
        sensitivity_tier="regulated",
        last_analysed_at=datetime(2026, 5, 1, 12, 0, 0),
    )


def test_v8_skills_router_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/skills/registry" in paths
    assert "/v8/orgs/{org_id}/skills/score" in paths
    assert "/v8/orgs/{org_id}/skills/drift" in paths
    assert "/v8/orgs/{org_id}/skills/provenance" in paths
    assert "/v8/orgs/{org_id}/skills/skillql" in paths
    assert "/v8/orgs/{org_id}/skills/repos" in paths


def test_registry_item_composes_v8_governance_fields() -> None:
    skill = _skill()
    repo = _repo()
    version = SimpleNamespace(version_number=3, content_hash="hash")
    policy = SimpleNamespace(name="Sensitive repo guard", enabled=True)

    item = skills_router_module._registry_item(skill, repo, version, ["codex", "claude_code", "codex"], [policy])

    assert item.version == "v3"
    assert item.signature_status == "verified"
    assert item.score.total == 88
    assert item.owning_team == "platform"
    assert item.dependent_agents == ["claude_code", "codex"]
    assert item.policy_bindings == ["Sensitive repo guard"]
    assert item.sensitivity_tier == "regulated"


def test_registry_endpoint_is_feature_flagged(monkeypatch) -> None:
    async def disabled(org_id, db):
        return False

    monkeypatch.setattr(skills_router_module, "is_v8", disabled)
    response = _client(Db()).get("/v8/orgs/org_1/skills/registry")

    assert response.status_code == 404


def test_registry_endpoint_keeps_existing_score_contract(monkeypatch) -> None:
    async def enabled(org_id, db):
        return True

    monkeypatch.setattr(skills_router_module, "is_v8", enabled)
    db = Db(
        [
            Result(rows=[(_skill(), _repo())]),
            Result(rows=[SimpleNamespace(name="Sensitive repo guard", enabled=True)]),
            Result(scalar_one_or_none_value=SimpleNamespace(version_number=1, content_hash="hash")),
            Result(rows=["codex"]),
            Result(scalar_value=1),
        ]
    )

    response = _client(db).get("/v8/orgs/org_1/skills/registry")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["score"] == {
        "total": 88,
        "groundedness": 22,
        "coverage": 21,
        "freshness": 20,
        "structure": 25,
    }
    assert payload["items"][0]["signature_status"] == "verified"
    assert payload["items"][0]["sensitivity_tier"] == "regulated"


def test_score_endpoint_exposes_open_rubric_and_average(monkeypatch) -> None:
    async def enabled(org_id, db):
        return True

    weak_skill = _skill()
    weak_skill.id = "skill_2"
    weak_skill.score_total = 48
    weak_skill.score_groundedness = 10
    weak_skill.score_coverage = 12
    weak_skill.score_freshness = 11
    weak_skill.score_structure = 15
    weak_skill.content_hash = None
    weak_skill.is_stale = True
    weak_repo = _repo()
    weak_repo.id = "repo_2"
    weak_repo.name = "worker"
    weak_repo.full_name = "platform/worker"

    monkeypatch.setattr(skills_router_module, "is_v8", enabled)
    db = Db(
        [
            Result(rows=[(_skill(), _repo()), (weak_skill, weak_repo)]),
            Result(rows=[SimpleNamespace(name="Sensitive repo guard", enabled=True)]),
            Result(scalar_one_or_none_value=SimpleNamespace(version_number=2, content_hash="hash")),
            Result(rows=["codex"]),
            Result(scalar_one_or_none_value=None),
            Result(rows=[]),
            Result(scalar_value=2),
        ]
    )

    response = _client(db).get("/v8/orgs/org_1/skills/score")

    assert response.status_code == 200
    payload = response.json()
    assert payload["subscores"] == ["Groundedness", "Coverage", "Freshness", "Structure"]
    assert payload["rubric_path"] == "docs/v8-refactor/skills/score-rubric.md"
    assert payload["average_score"] == 68
    assert payload["total"] == 2
    assert payload["items"][1]["signature_status"] == "unsigned"
    assert payload["items"][1]["drift_status"] == "drifted"


def test_drift_endpoint_returns_half_life_governance_signals(monkeypatch) -> None:
    async def enabled(org_id, db):
        return True

    monkeypatch.setattr(skills_router_module, "is_v8", enabled)
    half_life = SimpleNamespace(
        skill_id="skill_1",
        repo_id="repo_1",
        org_id="org_1",
        predicted_decay_date=datetime(2026, 5, 7, 12, 0, 0),
        predicted_decay_days=5.5,
        decay_confidence=0.82,
        commits_30d=17,
        file_churn_30d=42,
        regen_queued=True,
        computed_at=datetime(2026, 5, 1, 12, 0, 0),
    )
    db = Db([Result(rows=[(half_life, _skill(), _repo())])])

    response = _client(db).get("/v8/orgs/org_1/skills/drift")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["events"][0]["name"] == "skills/backend/SKILL.md"
    assert payload["events"][0]["predicted_decay_days"] == 5.5
    assert payload["events"][0]["decay_confidence"] == 0.82
    assert payload["events"][0]["commits_30d"] == 17
    assert payload["events"][0]["file_churn_30d"] == 42
    assert payload["events"][0]["regen_queued"] is True


def test_provenance_endpoint_exposes_version_hash_and_run_lineage(monkeypatch) -> None:
    async def enabled(org_id, db):
        return True

    monkeypatch.setattr(skills_router_module, "is_v8", enabled)
    created_at = datetime(2026, 5, 2, 9, 30, 0)
    version = SimpleNamespace(
        id="ver_1",
        skill_id="skill_1",
        version_number=4,
        content_hash="hash_abc",
        run_id="run_123",
        created_at=created_at,
    )
    skill = SimpleNamespace(id="skill_1")
    db = Db([Result(rows=[(version, skill)])])

    response = _client(db).get("/v8/orgs/org_1/skills/provenance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["versions"][0] == {
        "skill_id": "skill_1",
        "version_id": "ver_1",
        "version_number": 4,
        "content_hash": "hash_abc",
        "signature_status": "verified",
        "git_commit": None,
        "generation_run_id": "run_123",
        "scoring_run_id": "run_123",
        "approver": None,
        "created_at": "2026-05-02T09:30:00",
    }
    assert payload["transparency_log"] == []


def test_repos_endpoint_allows_dashboard_read_without_bearer_token(monkeypatch) -> None:
    async def enabled(org_id, db):
        return True

    monkeypatch.setattr(skills_router_module, "is_v8", enabled)
    db = Db(
        [
            Result(rows=[(_repo(), 3, 1)]),
            Result(rows=[SimpleNamespace(name="Sensitive repo guard", enabled=True)]),
        ]
    )
    client = _client(db)
    client.app.dependency_overrides[get_current_org_id_optional] = lambda: None

    response = client.get("/v8/orgs/org_1/skills/repos")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["repos"][0] == {
        "id": "repo_1",
        "full_name": "platform/api",
        "name": "api",
        "language": "Python",
        "sensitivity_tier": "regulated",
        "indexing_status": "indexed",
        "generated_skill_count": 3,
        "drift_count": 1,
        "policy_bindings": ["Sensitive repo guard"],
        "last_analysed_at": "2026-05-01T12:00:00",
    }


def test_repo_sensitivity_migration_upgrade_and_downgrade(monkeypatch) -> None:
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    sa.Table("repos", metadata, sa.Column("id", sa.String(), primary_key=True))
    metadata.create_all(engine)

    try:
        with engine.begin() as connection:
            context = MigrationContext.configure(connection)
            monkeypatch.setattr(repo_sensitivity_migration, "op", Operations(context))

            repo_sensitivity_migration.upgrade()
            columns_after_upgrade = {column["name"] for column in sa.inspect(connection).get_columns("repos")}
            assert "sensitivity_tier" in columns_after_upgrade

            repo_sensitivity_migration.downgrade()
            columns_after_downgrade = {column["name"] for column in sa.inspect(connection).get_columns("repos")}
            assert "sensitivity_tier" not in columns_after_downgrade
    finally:
        engine.dispose()
