from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id_optional
from apps.api.api.routes import repos
from apps.api.api.services.snapshot import auto_snapshot_skill, rollback_skill, snapshot_repo_skills
from packages.db.database import get_db
from packages.db.models import Org, Repo, Skill, SkillSnapshot


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
    def __init__(self, results: list[Result] | None = None, objects: dict[tuple[object, str], object] | None = None) -> None:
        self.results = results or []
        self.objects = objects or {}
        self.added: list[object] = []
        self.committed = False
        self.rolled_back = False
        self._next_id = 1

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    async def get(self, model, id_):
        return self.objects.get((model, id_))

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        for item in self.added:
            if getattr(item, "id", None) is None:
                item.id = f"snapshot_{self._next_id}"
                self._next_id += 1

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo():
    return Repo(id="repo_1", org_id="org_1", github_repo_id=1, full_name="acme/api", name="api")


def _org():
    return SimpleNamespace(id="org_1", login="acme", api_key="sk-test")


def _skill(skill_id: str = "skill_1", content: str = "current", score: int = 70) -> Skill:
    skill = Skill(repo_id="repo_1", run_id="run_1", domain="backend", skill_path=".skilgen/backend/SKILL.md", content=content)
    skill.id = skill_id
    skill.score_total = score
    skill.score_groundedness = 10
    skill.score_coverage = 20
    skill.score_freshness = 15
    skill.score_structure = 25
    skill.content_hash = "hash-current"
    return skill


def _snapshot(snapshot_id: str = "snap_1", content: str = "old", created_at: datetime | None = None) -> SkillSnapshot:
    snapshot = SkillSnapshot(
        skill_id="skill_1",
        repo_id="repo_1",
        snapshot_type="auto",
        label="Before",
        content=content,
        score_total=41,
        score_groundedness=4,
        score_coverage=10,
        score_freshness=12,
        score_structure=15,
        created_by="api_key:acme",
    )
    snapshot.id = snapshot_id
    snapshot.created_at = created_at or datetime(2026, 4, 28, 10, 0, 0)
    return snapshot


def _client(db: Db) -> TestClient:
    app = FastAPI()
    app.include_router(repos.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id_optional] = lambda: None
    return TestClient(app)


def test_auto_snapshot_skill_fields() -> None:
    skill = _skill(content="snapshot me", score=82)
    db = Db([Result(scalar=None)])

    snapshot = asyncio.run(auto_snapshot_skill(skill, db))

    assert snapshot.skill_id == "skill_1"
    assert snapshot.repo_id == "repo_1"
    assert snapshot.snapshot_type == "auto"
    assert snapshot.content == "snapshot me"
    assert snapshot.score_total == 82
    assert snapshot.score_structure == 25
    assert db.added == [snapshot]


def test_snapshot_repo_skills_one_per_skill() -> None:
    skills = [_skill("skill_1", "one"), _skill("skill_2", "two")]
    db = Db([Result(rows=skills), Result(scalar=None), Result(scalar=None)])

    snapshots = asyncio.run(snapshot_repo_skills("repo_1", db))

    assert len(snapshots) == 2
    assert [snapshot.skill_id for snapshot in snapshots] == ["skill_1", "skill_2"]
    assert len(db.added) == 2


def test_rollback_creates_pre_edit_before_restoring_content_and_scores() -> None:
    skill = _skill(content="current content", score=90)
    snapshot = _snapshot(content="restored content")
    db = Db(objects={(Skill, "skill_1"): skill, (SkillSnapshot, "snap_1"): snapshot})

    restored, pre_edit = asyncio.run(rollback_skill("skill_1", "snap_1", db, "api_key:acme"))

    assert pre_edit.snapshot_type == "pre_edit"
    assert pre_edit.content == "current content"
    assert pre_edit.score_total == 90
    assert restored.content == "restored content"
    assert restored.score_total == 41
    assert restored.score_groundedness == 4
    assert restored.updated_at is not None


def test_get_snapshots_newest_first() -> None:
    newest = _snapshot("snap_new", created_at=datetime(2026, 4, 28, 12, 0, 0))
    older = _snapshot("snap_old", created_at=datetime(2026, 4, 27, 12, 0, 0))
    db = Db(
        [Result(scalar=_org()), Result(scalar=_repo()), Result(rows=[newest, older])],
        objects={(Skill, "skill_1"): _skill()},
    )
    client = _client(db)

    response = client.get("/repos/repo_1/skills/skill_1/snapshots", headers={"API-Key": "sk-test"})

    assert response.status_code == 200
    payload = response.json()
    assert [item["id"] for item in payload] == ["snap_new", "snap_old"]
    assert "content" not in payload[0]


def test_get_diff_returns_unified_diff() -> None:
    skill = _skill(content="old\nnew\n")
    snapshot = _snapshot(content="old\nremoved\n")
    db = Db(
        [Result(scalar=_org()), Result(scalar=_repo())],
        objects={(Skill, "skill_1"): skill, (SkillSnapshot, "snap_1"): snapshot},
    )
    client = _client(db)

    response = client.get("/repos/repo_1/skills/skill_1/snapshots/snap_1/diff", headers={"API-Key": "sk-test"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "--- snapshot/snap_1" in response.text
    assert "+new" in response.text
    assert "-removed" in response.text


def test_post_rollback_returns_pre_edit_snapshot_id() -> None:
    skill = _skill(content="current content", score=88)
    snapshot = _snapshot(content="restored content")
    db = Db(
        [Result(scalar=_org()), Result(scalar=_repo())],
        objects={(Skill, "skill_1"): skill, (SkillSnapshot, "snap_1"): snapshot},
    )
    client = _client(db)

    response = client.post("/repos/repo_1/skills/skill_1/rollback/snap_1", headers={"API-Key": "sk-test"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["snapshot_id"] == "snap_1"
    assert payload["pre_edit_snapshot_id"] == "snapshot_1"
    assert skill.content == "restored content"
    assert db.committed is True
