from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.api.routes import repos


class Result:
    def __init__(self, rows=None, scalar=None) -> None:
        self.rows = rows or []
        self.scalar = scalar

    def scalar_one_or_none(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, results) -> None:
        self.results = list(results)
        self.rolled_back = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def rollback(self):
        self.rolled_back = True


def _repo(org_id: str = "org_1"):
    return SimpleNamespace(id="repo_1", org_id=org_id, name="api", is_active=True)


def _skill(skill_id: str, source_type: str, domain: str, score: int, created_offset: int = 0):
    return SimpleNamespace(
        id=skill_id,
        repo_id="repo_1",
        source_type=source_type,
        skill_category=None,
        domain=domain,
        score_total=score,
        created_at=datetime.utcnow() - timedelta(minutes=created_offset),
    )


def test_repo_skill_sources_returns_sources_and_coverage_map() -> None:
    db = Db(
        [
            Result(scalar=_repo()),
            Result(rows=[_skill("skill_1", "code", "backend", 90), _skill("skill_2", "openapi", "public-api", 70)]),
        ]
    )

    response = asyncio.run(repos.get_repo_skill_sources("repo_1", db, "org_1"))

    sources = {item.source_type: item for item in response.sources}
    assert sources["code"].detected is True
    assert sources["openapi"].skill_count == 1
    assert response.coverage_map["codebase_architecture"].covered is True
    assert response.coverage_map["internal_tools"].covered is True
    assert response.coverage_score > 0


def test_repo_skill_sources_forbidden_when_repo_outside_org() -> None:
    db = Db([Result(scalar=_repo("org_other"))])

    with pytest.raises(HTTPException) as exc:
        asyncio.run(repos.get_repo_skill_sources("repo_1", db, "org_1"))

    assert exc.value.status_code == 403


def test_latest_repo_skills_keeps_newest_per_domain() -> None:
    older = _skill("old", "code", "backend", 50, created_offset=10)
    newer = _skill("new", "code", "backend", 90)
    db = Db([Result(rows=[newer, older])])

    response = asyncio.run(repos._latest_repo_skills(db, "repo_1"))

    assert [skill.id for skill in response] == ["new"]
