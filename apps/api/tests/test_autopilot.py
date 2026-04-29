from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace

from apps.api.api.routes.autopilot import approve_autopilot_task, skip_autopilot_task
from apps.api.api.services.autopilot import compute_autopilot_queue
from packages.db.models import AutopilotTask


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


class QueueDb:
    def __init__(self) -> None:
        self.tasks: list[AutopilotTask] = []
        self.lookup_calls = 0

    async def execute(self, statement):
        self.lookup_calls += 1
        if self.lookup_calls <= self.expected_lookup_calls:
            return Result()
        return Result(rows=self.tasks)

    def add(self, item):
        item.id = item.id or f"task_{len(self.tasks) + 1}"
        self.tasks.append(item)

    async def flush(self):
        return None


class ActionDb:
    def __init__(self, task: AutopilotTask) -> None:
        self.task = task
        self.committed = False
        self.rolled_back = False
        self.execute_calls = 0

    async def get(self, model, item_id: str):
        return self.task if item_id == self.task.id else None

    async def execute(self, statement):
        self.execute_calls += 1
        if self.execute_calls == 1:
            return Result(rows=[SimpleNamespace(id="repo_1", name="Demo", org_id="org_1", is_active=True)])
        return Result(rows=[SimpleNamespace(id="skill_1", domain="api", skill_path="skills/api/SKILL.md")])

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", is_active=True)


def _skill(score: int):
    return SimpleNamespace(id=f"skill_{score}", repo_id="repo_1", score_freshness=score)


def test_autopilot_queue_empty() -> None:
    db = QueueDb()
    db.expected_lookup_calls = 0

    tasks = asyncio.run(compute_autopilot_queue(db, "org_1", [_repo()], [_skill(20)]))

    assert tasks == []


def test_autopilot_queue_stale() -> None:
    db = QueueDb()
    db.expected_lookup_calls = 1

    tasks = asyncio.run(compute_autopilot_queue(db, "org_1", [_repo()], [_skill(14)]))

    assert len(tasks) == 1
    assert tasks[0].status == "pending"
    assert tasks[0].task_type == "regenerate"
    assert tasks[0].trigger_reason == "Freshness 14/25 — below 60% threshold"


def test_autopilot_skip() -> None:
    task = AutopilotTask(id="task_1", org_id="org_1", repo_id="repo_1", skill_id="skill_1", task_type="regenerate", trigger_reason="Freshness 10/25 — below 60% threshold", freshness_at_trigger=10, status="pending", created_at=datetime.utcnow())
    db = ActionDb(task)

    response = asyncio.run(skip_autopilot_task("org_1", "task_1", db, "org_1"))

    assert response.status == "skipped"
    assert task.resolved_at is not None
    assert db.committed is True


def test_autopilot_approve() -> None:
    task = AutopilotTask(id="task_1", org_id="org_1", repo_id="repo_1", skill_id="skill_1", task_type="regenerate", trigger_reason="Freshness 10/25 — below 60% threshold", freshness_at_trigger=10, status="pending", created_at=datetime.utcnow())
    db = ActionDb(task)

    response = asyncio.run(approve_autopilot_task("org_1", "task_1", db, "org_1"))

    assert response.status == "approved"
    assert task.resolved_at is not None
    assert db.committed is True
