from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace

from apps.api.api.routes import orgs


class Result:
    def __init__(self, rows=None, scalar=None) -> None:
        self.rows = rows or []
        self.scalar = scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows

    def scalar_one_or_none(self):
        return self.scalar


class Db:
    def __init__(self, results=None) -> None:
        self.results = list(results or [])
        self.added = []
        self.deleted = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    def add(self, item):
        item.id = item.id or "dismissal_1"
        self.added.append(item)

    async def delete(self, item):
        self.deleted.append(item)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", name="api", is_active=True)


def _skill(skill_id: str = "skill_1"):
    return SimpleNamespace(
        id=skill_id,
        repo_id="repo_1",
        domain="backend",
        skill_category="codebase_architecture",
        score_freshness=10,
        score_total=85,
        load_count_30d=12,
        last_loaded_at=datetime.utcnow(),
        content=None,
    )


def test_org_red_flags_counts_and_filters_by_severity() -> None:
    db = Db([Result(rows=[_repo()]), Result(rows=[_skill()])])

    response = asyncio.run(orgs.get_org_red_flags("org_1", "critical", None, db, "org_1"))

    assert response.critical_count >= 1
    assert all(flag.severity == "critical" for flag in response.flags)
    assert response.flags[0].flag_type == "stale_but_active"


def test_dismiss_red_flag_creates_dismissal() -> None:
    db = Db([Result(scalar=None)])
    payload = orgs.RedFlagDismissPayload(flag_type="stale_but_active", repo_id="repo_1", skill_id="skill_1", reason="accepted")
    request = SimpleNamespace(headers={})

    response = asyncio.run(orgs.dismiss_red_flag("org_1", payload, request, db, "org_1"))

    assert response == {"dismissed": True}
    assert db.added[0].flag_type == "stale_but_active"
    assert db.added[0].dismissed_at is not None
    assert db.committed is True


def test_restore_red_flag_deletes_existing_dismissal() -> None:
    dismissal = SimpleNamespace(flag_type="stale_but_active", repo_id="repo_1", skill_id="skill_1")
    db = Db([Result(scalar=dismissal)])
    payload = orgs.RedFlagRestorePayload(flag_type="stale_but_active", repo_id="repo_1", skill_id="skill_1")

    response = asyncio.run(orgs.restore_red_flag("org_1", payload, db, "org_1"))

    assert response == {"restored": True}
    assert db.deleted == [dismissal]
    assert db.committed is True
