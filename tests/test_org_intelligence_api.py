from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Org, Repo, ScoreHistory, Skill


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class FakeScalarResult:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


class FakeResult:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.values)

    def all(self) -> list[object]:
        return self.values


class FakeDb:
    def __init__(self, org: Org | None, results: list[list[object]]) -> None:
        self.org = org
        self.results = results
        self.rollback_count = 0

    async def get(self, model: object, key: str) -> Org | None:
        return self.org

    async def execute(self, statement: object) -> FakeResult:
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return FakeResult(self.results.pop(0))

    async def rollback(self) -> None:
        self.rollback_count += 1


def _client(db: FakeDb, *, auth_org_id: str = "org_123") -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)

    async def override_org_id() -> str:
        return auth_org_id

    async def override_db() -> Any:
        yield db

    app.dependency_overrides[get_current_org_id] = override_org_id
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def _repo(repo_id: str, name: str, *, analysed_days_ago: int = 2) -> Repo:
    analysed_at = _now() - timedelta(days=analysed_days_ago)
    return Repo(
        id=repo_id,
        org_id="org_123",
        github_repo_id=int(repo_id[-1]),
        full_name=f"acme/{name}",
        name=name,
        last_analysed_at=analysed_at,
        is_active=True,
    )


def _run(run_id: str, repo_id: str, score: int, *, days_ago: int = 1, skill_count: int = 1) -> AnalysisRun:
    return AnalysisRun(
        id=run_id,
        repo_id=repo_id,
        trigger="manual",
        status="complete",
        score_total=score,
        skill_count=skill_count,
        created_at=_now() - timedelta(days=days_ago),
    )


def _history(history_id: str, repo_id: str, run_id: str, score: int, *, days_ago: int) -> ScoreHistory:
    return ScoreHistory(
        id=history_id,
        repo_id=repo_id,
        run_id=run_id,
        score_total=score,
        score_groundedness=score // 4,
        score_coverage=score // 4,
        score_freshness=score // 4,
        score_structure=score // 4,
        recorded_at=_now() - timedelta(days=days_ago),
    )


def _skill(
    skill_id: str,
    repo_id: str,
    domain: str,
    category: str,
    score: int,
    loads: int,
    *,
    is_stale: bool = False,
    last_loaded_days_ago: int | None = 1,
    created_days_ago: int = 40,
) -> Skill:
    return Skill(
        id=skill_id,
        repo_id=repo_id,
        run_id=f"run_{repo_id}",
        domain=domain,
        skill_path=f"skills/{domain}/SKILL.md",
        skill_category=category,
        source_type="code",
        score_total=score,
        score_groundedness=score // 4,
        score_coverage=score // 4,
        score_freshness=score // 4,
        score_structure=score // 4,
        load_count_30d=loads,
        is_stale=is_stale,
        last_loaded_at=None if last_loaded_days_ago is None else _now() - timedelta(days=last_loaded_days_ago),
        created_at=_now() - timedelta(days=created_days_ago),
    )


def _populated_db() -> FakeDb:
    org = Org(id="org_123", github_org_id=1, login="acme", name="Acme")
    repo_a = _repo("repo_1", "api")
    repo_b = _repo("repo_2", "web", analysed_days_ago=45)
    skills = [
        _skill("skill_dead", "repo_1", "backend", "codebase_architecture", 30, 0, last_loaded_days_ago=None),
        _skill("skill_new", "repo_1", "new-skill", "code_style", 45, 0, last_loaded_days_ago=None, created_days_ago=1),
        _skill("skill_stale", "repo_1", "testing", "testing_conventions", 55, 3, is_stale=True),
        _skill("skill_top", "repo_2", "frontend", "design_system", 88, 12),
        _skill("skill_dormant", "repo_2", "ops", "operational_knowledge", 70, 1),
    ]
    results: list[list[object]] = [
        [repo_a, repo_b],
        skills,
        [_run("run_repo_2", "repo_2", 90), _run("run_repo_1", "repo_1", 30)],
        [
            {"repo_id": "repo_2", "created_at": _now() - timedelta(days=45)},
            {"repo_id": "repo_1", "created_at": _now() - timedelta(days=1)},
        ],
        [
            _history("h1", "repo_1", "run_repo_1", 20, days_ago=29),
            _history("h2", "repo_1", "run_repo_1", 30, days_ago=1),
            _history("h3", "repo_2", "run_repo_2", 95, days_ago=29),
            _history("h4", "repo_2", "run_repo_2", 90, days_ago=1),
        ],
        [
            {"skill_id": "skill_stale", "loads_30d": 3, "last_loaded_at": _now() - timedelta(days=1)},
            {"skill_id": "skill_top", "loads_30d": 12, "last_loaded_at": _now() - timedelta(days=1)},
            {"skill_id": "skill_dormant", "loads_30d": 1, "last_loaded_at": _now() - timedelta(days=1)},
        ],
    ]
    return FakeDb(org, results)


def test_org_intelligence_returns_200_with_shape_when_org_has_repos_and_skills() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "org_health_score",
        "org_health_trend",
        "total_repos",
        "total_skills",
        "total_loads_30d",
        "repos",
        "category_matrix",
        "stale_alerts",
        "top_skills",
    }
    assert payload["total_repos"] == 2
    assert payload["total_skills"] == 5
    assert payload["total_loads_30d"] == 16


def test_org_health_score_is_mean_of_latest_repo_scores() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    assert response.status_code == 200
    assert response.json()["org_health_score"] == 60


def test_repos_are_sorted_worst_first() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    assert [repo["id"] for repo in response.json()["repos"]] == ["repo_1", "repo_2"]


def test_stale_alerts_put_dead_skills_before_stale_skills() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    alerts = response.json()["stale_alerts"]
    assert alerts[0]["alert_type"] == "dead"
    assert alerts[0]["skill_id"] == "skill_dead"
    assert [alert["alert_type"] for alert in alerts[:3]] == ["dead", "stale_but_active", "dormant_repo"]


def test_new_never_loaded_skills_are_not_dead_during_grace_period() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    payload = response.json()
    repo = next(item for item in payload["repos"] if item["id"] == "repo_1")
    assert repo["dead_skill_count"] == 1
    assert "skill_new" not in {alert["skill_id"] for alert in payload["stale_alerts"]}


def test_top_skills_are_ordered_by_loads_desc() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    assert [skill["skill_id"] for skill in response.json()["top_skills"][:2]] == ["skill_top", "skill_stale"]
    assert "skill_dead" not in {skill["skill_id"] for skill in response.json()["top_skills"]}


def test_loads_30d_are_derived_from_usage_events_not_denormalized_counters() -> None:
    db = _populated_db()
    response = _client(db).get("/orgs/org_123/intelligence")

    payload = response.json()
    assert payload["total_loads_30d"] == 16
    assert next(skill for skill in payload["top_skills"] if skill["skill_id"] == "skill_top")["loads_30d"] == 12


def test_recent_stale_zero_load_skill_is_not_reported_active() -> None:
    db = _populated_db()
    skills = db.results[1]
    assert isinstance(skills, list)
    skills.append(
        _skill(
            "skill_recent_stale",
            "repo_1",
            "recent-stale",
            "code_style",
            42,
            99,
            is_stale=True,
            last_loaded_days_ago=None,
            created_days_ago=1,
        )
    )

    response = _client(db).get("/orgs/org_123/intelligence")

    alerts = response.json()["stale_alerts"]
    assert "skill_recent_stale" not in {alert["skill_id"] for alert in alerts}


def test_category_matrix_has_all_eight_categories() -> None:
    response = _client(_populated_db()).get("/orgs/org_123/intelligence")

    assert list(response.json()["category_matrix"]) == orgs.SKILL_CATEGORIES


def test_org_intelligence_returns_403_for_mismatched_org_scope() -> None:
    response = _client(_populated_db(), auth_org_id="org_other").get("/orgs/org_123/intelligence")

    assert response.status_code == 403


def test_org_intelligence_returns_zeroed_stats_when_org_has_no_repos() -> None:
    db = FakeDb(Org(id="org_123", github_org_id=1, login="acme", name="Acme"), [[]])
    response = _client(db).get("/orgs/org_123/intelligence")

    assert response.status_code == 200
    assert response.json() == {
        "org_health_score": 0,
        "org_health_trend": None,
        "total_repos": 0,
        "total_skills": 0,
        "total_loads_30d": 0,
        "repos": [],
        "category_matrix": {category: [] for category in orgs.SKILL_CATEGORIES},
        "stale_alerts": [],
        "top_skills": [],
    }
