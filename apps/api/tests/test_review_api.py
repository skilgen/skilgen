from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks
from fastapi import HTTPException

from apps.api.api.routes import review
from packages.db.models import Job, ReviewRun


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
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def get(self, model, key):
        for item in self.added:
            if isinstance(item, model) and item.id == key:
                return item
        return None

    def add(self, item):
        item.id = item.id or "review_1"
        self.added.append(item)

    async def flush(self):
        return None

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo(org_id: str = "org_1"):
    return SimpleNamespace(id="repo_1", org_id=org_id, name="api")


def _skill():
    return SimpleNamespace(
        id="skill_1",
        repo_id="repo_1",
        domain="database",
        anti_patterns=["avoid raw sql"],
        content=None,
    )


def test_review_diff_comments_on_matching_anti_pattern() -> None:
    diff = """diff --git a/app.py b/app.py
+++ b/app.py
@@ -1,0 +1,1 @@
+result = db.execute("use raw sql for performance")
"""
    db = Db([Result(scalar=_repo()), Result(rows=[_skill()])])

    response = asyncio.run(review.review_diff("repo_1", review.ReviewBody(diff=diff, pr_url="https://example.test/pr/1"), db, "org_1"))

    assert response["comments"][0]["skill_name"] == "database"
    assert response["lines_scanned"] == 1
    assert isinstance(db.added[0], ReviewRun)
    assert db.committed is True


def test_review_history_returns_recent_runs() -> None:
    run = SimpleNamespace(id="review_1", repo_id="repo_1", pr_url=None, comment_count=2, skills_checked=3, lines_scanned=4, created_at=datetime.utcnow())
    db = Db([Result(scalar=_repo()), Result(rows=[run])])

    response = asyncio.run(review.review_history("repo_1", db, "org_1"))

    assert response["runs"][0]["id"] == "review_1"
    assert response["runs"][0]["comment_count"] == 2


def test_review_forbidden_when_repo_outside_org() -> None:
    db = Db([Result(scalar=_repo("org_other"))])

    with pytest.raises(HTTPException) as exc:
        asyncio.run(review.review_diff("repo_1", review.ReviewBody(diff="", pr_url=None), db, "org_1"))

    assert exc.value.status_code == 403


def test_scan_repo_prs_queues_non_blocking_job() -> None:
    db = Db([])
    background_tasks = BackgroundTasks()

    response = asyncio.run(review.scan_repo_prs("org_1", background_tasks, None, db, "org_1"))

    assert response.job_id == "review_1"
    assert isinstance(db.added[0], Job)
    assert db.added[0].status == "queued"
    assert db.committed is True
    assert len(background_tasks.tasks) == 1


def test_scan_repo_prs_status_returns_job_counts() -> None:
    db = Db([])
    job = Job(org_id="org_1", type="review.scan_repo_prs", status="completed", result_json={"scanned": 3, "queued": 2, "skipped": 1})
    job.id = "job_1"
    db.added.append(job)

    response = asyncio.run(review.scan_repo_prs_status("org_1", "job_1", db, "org_1"))

    assert response.job_id == "job_1"
    assert response.status == "completed"
    assert response.scanned == 3
    assert response.queued == 2
    assert response.skipped == 1
