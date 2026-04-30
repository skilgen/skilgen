from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.api.index import app
from apps.api.api.routes import orgs
from packages.db.llm_key import decrypt_key
from packages.db.models import AnalysisRun
from packages.db.models import SourceConnection as SourceConnectionModel


class Result:
    def __init__(self, rows=None, scalar=None) -> None:
        self.rows = rows or []
        self._scalar = scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows

    def fetchall(self):
        return self.rows

    def scalar(self):
        return self._scalar

    def scalar_one_or_none(self):
        return self._scalar

    def scalar_one(self):
        return self._scalar


class Db:
    def __init__(self, *, org=None, repo=None, results=None) -> None:
        self.org = org
        self.repo = repo
        self.results = list(results or [])
        self.added = []
        self.committed = False
        self.rolled_back = False
        self.flushed = False

    async def get(self, model, key):
        if model.__name__ == "Org":
            return self.org
        if model.__name__ == "Repo":
            return self.repo
        return None

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    def add(self, item):
        if not getattr(item, "id", None):
            item.id = f"run_{len(self.added) + 1}"
        self.added.append(item)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _org():
    return SimpleNamespace(id="org_1")


def _repo(repo_id: str = "repo_1", org_id: str = "org_1"):
    return SimpleNamespace(id=repo_id, org_id=org_id, name="api", full_name="acme/api", default_branch="main", is_active=True, last_analysed_at=datetime.utcnow())


def _skill(skill_id: str, repo_id: str, source_type: str, *, domain: str = "backend", score: int = 80, loads: int = 0, stale: bool = False):
    return SimpleNamespace(
        id=skill_id,
        repo_id=repo_id,
        source_type=source_type,
        skill_category=orgs.skill_category_for_source_type(source_type),
        domain=domain,
        skill_path=f"skills/{domain}/SKILL.md",
        created_at=datetime.utcnow(),
        score_total=score,
        score_freshness=score // 4,
        load_count_30d=loads,
        is_enterprise=False,
        is_stale=stale,
        last_loaded_at=datetime.utcnow() - timedelta(days=1),
    )


def test_org_router_is_registered_on_existing_app() -> None:
    paths = {route.path for route in app.routes}

    assert "/orgs/{org_id}/sources" in paths
    assert "/orgs/{org_id}/sources/test" in paths
    assert "/orgs/{org_id}/sources/connect" in paths
    assert "/orgs/{org_id}/enterprise-skills" in paths
    assert "/orgs/{org_id}/intelligence/insights" in paths


def test_org_stats_counts_active_agent_runtimes_from_skill_usage() -> None:
    db = Db(
        results=[
            Result(scalar=2),
            Result(scalar=72),
            Result(rows=["repo_1", "repo_2"]),
            Result(scalar=SimpleNamespace(skill_count=12)),
            Result(scalar=SimpleNamespace(skill_count=25)),
            Result(rows=["codex", "codex_cli", "claude_code", None]),
            Result(rows=[]),
        ],
    )

    response = asyncio.run(orgs.get_org_stats("org_1", db))

    assert response["repo_count"] == 2
    assert response["skill_count"] == 37
    assert response["avg_score"] == 72
    assert response["active_agents"] == 2


def test_org_sources_include_detected_and_common_unconnected_sources() -> None:
    db = Db(
        org=_org(),
        results=[
            Result(rows=[_repo()]),
            Result(rows=[_skill("skill_1", "repo_1", "openapi"), _skill("skill_2", "repo_1", "dbt", domain="models")]),
            Result(rows=[]),
        ],
    )

    response = asyncio.run(orgs.get_org_sources("org_1", db, "org_1"))

    by_type = {item.source_type: item for item in response}
    assert by_type["openapi"].connected is True
    assert by_type["openapi"].skill_count == 1
    assert by_type["openapi"].coverage_domains == ["backend"]
    assert by_type["sarif"].connected is False
    assert by_type["sarif"].can_generate_skills is True


def test_org_sources_include_persisted_source_connections() -> None:
    connection = SimpleNamespace(
        id="conn_1",
        source_type="confluence",
        display_name="Confluence",
        status="configured",
        last_tested_at=datetime.utcnow(),
        last_connected_at=datetime.utcnow(),
        last_error=None,
    )
    db = Db(
        org=_org(),
        results=[
            Result(rows=[_repo()]),
            Result(rows=[]),
            Result(rows=[connection]),
        ],
    )

    response = asyncio.run(orgs.get_org_sources("org_1", db, "org_1"))

    by_type = {item.source_type: item for item in response}
    assert by_type["confluence"].connected is True
    assert by_type["confluence"].connection_id == "conn_1"


def test_source_test_accepts_mocked_success_without_driver() -> None:
    db = Db(org=_org())

    response = asyncio.run(orgs.test_org_source("org_1", orgs.SourceConnectionRequest(source_type="notion", params={"mock_success": True}), db, "org_1"))

    assert response.success is True
    assert response.status == "connected"


def test_source_connect_encrypts_params_and_commits() -> None:
    db = Db(org=_org(), results=[Result(scalar=None)])

    response = asyncio.run(
        orgs.connect_org_source(
            "org_1",
            orgs.SourceConnectionRequest(source_type="notion", params={"api_key": "secret-token", "workspace": "eng", "mock_success": True}),
            db,
            "org_1",
        )
    )

    assert response.connected is True
    assert db.committed is True
    added = db.added[0]
    assert isinstance(added, SourceConnectionModel)
    assert "secret-token" not in added.encrypted_params
    assert "secret-token" in decrypt_key(added.encrypted_params)
    assert added.params_hint["api_key_hint"] == "...oken"


def test_enterprise_skills_can_be_marked_and_listed() -> None:
    skill = _skill("skill_1", "repo_1", "code")
    repo = _repo()
    db = Db(
        org=_org(),
        results=[
            Result(rows=[(skill, repo)]),
        ],
    )

    updated = asyncio.run(orgs.save_enterprise_skills("org_1", orgs.EnterpriseSkillRequest(skill_id="skill_1"), db, "org_1"))

    assert updated[0].is_enterprise is True
    assert skill.is_enterprise is True
    assert db.committed is True

    db = Db(org=_org(), results=[Result(rows=[(skill, repo)])])
    listed = asyncio.run(orgs.get_enterprise_skills("org_1", db, "org_1"))
    assert listed[0].id == "skill_1"


def test_source_refresh_queues_analysis_run() -> None:
    repo = _repo()
    db = Db(org=_org(), repo=repo)

    response = asyncio.run(orgs.refresh_org_source("org_1", orgs.SourceRefreshRequest(repo_id="repo_1", source_type="openapi"), db, "org_1"))

    assert response["queued"] is True
    assert db.committed is True
    assert db.flushed is True
    assert isinstance(db.added[0], AnalysisRun)
    assert db.added[0].trigger == "source:openapi"
    assert db.added[0].created_at is not None


def test_source_refresh_rejects_repo_outside_org() -> None:
    db = Db(org=_org(), repo=_repo(org_id="org_other"))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(orgs.refresh_org_source("org_1", orgs.SourceRefreshRequest(repo_id="repo_1", source_type="openapi"), db, "org_1"))

    assert exc.value.status_code == 403


def test_intelligence_insights_return_gap_and_stale_active_signals() -> None:
    stale_skill = _skill("skill_1", "repo_1", "code", score=45, loads=12, stale=True)
    db = Db(
        org=_org(),
        results=[
            Result(rows=[_repo()]),
            Result(rows=[stale_skill]),
            Result(rows=[{"skill_id": "skill_1", "loads_30d": 12}]),
            Result(rows=[]),
        ],
    )

    response = asyncio.run(orgs.get_org_intelligence_insights("org_1", db, "org_1"))

    assert {item.type for item in response} >= {"gap", "anomaly", "opportunity"}
    assert any("stale" in item.title.lower() for item in response)


def test_intelligence_insights_rolls_back_on_lookup_failure() -> None:
    db = Db(org=_org(), results=[])

    with pytest.raises(HTTPException) as exc:
        asyncio.run(orgs.get_org_intelligence_insights("org_1", db, "org_1"))

    assert exc.value.status_code == 400
    assert db.rolled_back is True


def test_analytics_criticality_prioritises_loaded_low_quality_skill() -> None:
    now = datetime.utcnow()
    weak = _skill("skill_weak", "repo_1", "code", domain="security_compliance", score=45, loads=6)
    strong = _skill("skill_strong", "repo_1", "code", domain="code_style", score=92, loads=1)
    db = Db(
        org=_org(),
        results=[
            Result(rows=[(weak, "api"), (strong, "api")]),
            Result(rows=[
                SimpleNamespace(skill_id="skill_weak", loads=6, sessions=5, last_loaded_at=now),
                SimpleNamespace(skill_id="skill_strong", loads=1, sessions=1, last_loaded_at=now),
            ]),
            Result(scalar=5),
        ],
    )

    response = asyncio.run(orgs.get_analytics_criticality("org_1", db, "org_1"))

    assert response[0].skill_id == "skill_weak"
    assert response[0].risk_level == "critical"
    assert response[0].is_every_session is True
    assert "weak guidance" in response[0].risk_reason


def test_skill_coload_tree_groups_runtime_clusters_by_cooccurrence() -> None:
    now = datetime.utcnow()
    db = Db(
        org=_org(),
        results=[
            Result(rows=[
                ("sess_1", "codex", "skill_a", "backend", "api", 80, 4, 20, False),
                ("sess_1", "codex", "skill_b", "testing", "api", 70, 4, 18, False),
                ("sess_2", "codex", "skill_a", "backend", "api", 80, 4, 20, False),
                ("sess_2", "codex", "skill_b", "testing", "api", 70, 4, 18, False),
                ("sess_3", "codex", "skill_a", "backend", "api", 80, 4, 20, False),
                ("sess_3", "codex", "skill_b", "testing", "api", 70, 4, 18, False),
                ("sess_4", "codex", "skill_c", "docs", "api", 95, 1, 24, False),
            ]),
        ],
    )

    response = asyncio.run(orgs.get_skill_coload_tree("org_1", db, "org_1"))

    assert response.name == "All sessions"
    runtime = response.children[0]
    assert runtime.runtime == "codex_cli"
    core = runtime.children[0]
    assert core.always_together is True
    assert {child.skill_id for child in core.children} == {"skill_a", "skill_b"}
    assert core.children[0].skill_id == "skill_a"


def test_runtime_breakdown_returns_breadth_quality_and_pattern() -> None:
    now = datetime.utcnow()
    db = Db(
        org=_org(),
        results=[
            Result(rows=[SimpleNamespace(runtime="Codex", loads_30d=24, unique_skills=4, unique_domains=2, avg_skill_score=55, most_recent_load=now)]),
            Result(scalar=8),
            Result(rows=[
                SimpleNamespace(runtime="Codex", domain="agents", loads=18),
                SimpleNamespace(runtime="Codex", domain="security_compliance", loads=6),
            ]),
        ],
    )

    response = asyncio.run(orgs.get_runtime_breakdown("org_1", db))
    item = response.runtimes[0]

    assert item.unique_domains == 2
    assert item.avg_skill_score == 55
    assert item.top_domains == ["agents", "security_compliance"]
    assert item.knowledge_breadth_score == 25
    assert item.runtime == "codex_cli"
    assert item.display_name == "Codex CLI"
    assert item.pattern == "High-volume agent loading low-quality guidance"


def test_org_session_tag_updates_existing_session() -> None:
    session = SimpleNamespace(session_id="sess_1", org_id="org_1", outcome=None, notes=None)
    db = Db(org=_org(), results=[Result(scalar=session)])

    response = asyncio.run(
        orgs.tag_org_session(
            "org_1",
            "sess_1",
            orgs.SessionTagPayload(outcome="success", notes="Reviewed"),
            db,
            "org_1",
        )
    )

    assert response == {"updated": True}
    assert session.outcome == "success"
    assert session.notes == "Reviewed"
    assert db.committed is True


def test_list_teams_derives_owner_groups_and_distribution() -> None:
    repo_api = _repo("repo_1")
    repo_web = _repo("repo_2")
    repo_web.full_name = "acme/web"
    repo_web.name = "web"
    db = Db(
        org=_org(),
        results=[
            Result(rows=[repo_api, repo_web]),
            Result(rows=[
                _skill("skill_1", "repo_1", "code", score=80),
                _skill("skill_2", "repo_2", "code", score=40, stale=True),
            ]),
            Result(rows=[
                ("repo_1", "codex", 3),
                ("repo_2", "cursor", 1),
            ]),
        ],
    )

    response = asyncio.run(orgs.list_teams("org_1", "all", "name", 20, 0, db, "org_1"))

    assert response["error"] is False
    assert response["total"] == 1
    assert response["teams"][0]["team_name"] == "acme"
    assert response["teams"][0]["repo_count"] == 2
    assert response["score_distribution"]["41-60"] == 1


def test_list_teams_returns_empty_error_payload_on_lookup_failure() -> None:
    db = Db(org=_org(), results=[])

    response = asyncio.run(orgs.list_teams("org_1", "all", "score", 20, 0, db, "org_1"))

    assert response["teams"] == []
    assert response["error"] is True
    assert db.rolled_back is True
