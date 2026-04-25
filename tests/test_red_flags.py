from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from apps.api.api.services.redflags import compute_repo_red_flags
from packages.db.database import get_db
from packages.db.models import Org, Repo, Skill


def _repo() -> Repo:
    return Repo(id="repo_1", org_id="org_123", github_repo_id=1, full_name="acme/api", name="api")


def _skill(
    skill_id: str,
    domain: str,
    *,
    freshness: int = 25,
    loads: int = 0,
    score: int = 60,
    category: str = "codebase_architecture",
    content: str | None = None,
    last_loaded_at: datetime | None = None,
) -> Skill:
    return Skill(
        id=skill_id,
        repo_id="repo_1",
        run_id="run_1",
        domain=domain,
        skill_path=f"skills/{domain}/SKILL.md",
        skill_category=category,
        content=content,
        score_total=score,
        score_freshness=freshness,
        load_count_30d=loads,
        last_loaded_at=last_loaded_at,
    )


def test_stale_but_active_flag() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "auth", freshness=10, loads=50)])
    assert any(flag.flag_type == "stale_but_active" and flag.severity == "critical" for flag in flags)


def test_no_stale_flag_when_freshness_ok() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "auth", freshness=22, loads=50, category="security_compliance")])
    assert not any(flag.flag_type == "stale_but_active" for flag in flags)


def test_no_stale_flag_when_loads_low() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "auth", freshness=5, loads=3, category="security_compliance")])
    assert not any(flag.flag_type == "stale_but_active" for flag in flags)


def test_missing_security_flag() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "auth"), _skill("s2", "db"), _skill("s3", "ui")])
    assert any(flag.flag_type == "missing_security" and flag.severity == "high" for flag in flags)


def test_no_missing_security_when_security_skill_exists() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "security", category="security_compliance")])
    assert not any(flag.flag_type == "missing_security" for flag in flags)


def test_conflict_detection() -> None:
    flags = compute_repo_red_flags(
        _repo(),
        [
            _skill("s1", "database", content="never use raw sql in queries"),
            _skill("s2", "performance", content="use raw sql for performance critical paths"),
        ],
    )
    assert any(flag.flag_type == "conflict" and "database" in flag.title and "performance" in flag.title for flag in flags)


def test_dead_high_quality_flag() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "auth", score=80, loads=0, last_loaded_at=None, category="security_compliance")])
    assert any(flag.flag_type == "dead_high_quality" and flag.severity == "medium" for flag in flags)


def test_freshness_critical_flag() -> None:
    flags = compute_repo_red_flags(_repo(), [_skill("s1", "auth", freshness=0, loads=1, category="security_compliance")])
    assert any(flag.flag_type == "freshness_critical" and flag.severity == "critical" for flag in flags)


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


class FakeDb:
    def __init__(self, results: list[list[object]]) -> None:
        self.results = results

    async def execute(self, statement: object) -> FakeResult:
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return FakeResult(self.results.pop(0))


def _client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)

    async def override_org_id() -> str:
        return "org_123"

    async def override_db() -> Any:
        yield db

    app.dependency_overrides[get_current_org_id] = override_org_id
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_red_flags_endpoint_counts_and_sorts_by_severity() -> None:
    repo = _repo()
    db = FakeDb([[repo], [_skill("s1", "auth", freshness=10, loads=50), _skill("s2", "quality", score=80, last_loaded_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=40))]])
    response = _client(db).get("/orgs/org_123/red-flags")
    payload = response.json()
    assert response.status_code == 200
    assert payload["critical_count"] >= 1
    assert [flag["severity"] for flag in payload["flags"]] == sorted([flag["severity"] for flag in payload["flags"]], key=lambda value: {"critical": 0, "high": 1, "medium": 2}[value])


def test_red_flags_endpoint_filters_critical() -> None:
    repo = _repo()
    db = FakeDb([[repo], [_skill("s1", "auth", freshness=10, loads=50), _skill("s2", "quality", score=80, last_loaded_at=None)]])
    response = _client(db).get("/orgs/org_123/red-flags?severity=critical")
    assert response.status_code == 200
    assert response.json()["flags"]
    assert {flag["severity"] for flag in response.json()["flags"]} == {"critical"}
