from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace

from apps.api.api.routes import autopilot
from packages.db.models import AutopilotTask


class Result:
    def __init__(self, rows=None) -> None:
        self.rows = rows or []

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, task: AutopilotTask | None = None) -> None:
        self.task = task
        self.committed = False
        self.rolled_back = False
        self.execute_calls = 0

    async def execute(self, statement):
        self.execute_calls += 1
        if self.execute_calls == 1:
            return Result([SimpleNamespace(id="repo_1", name="api", org_id="org_1", is_active=True)])
        if self.execute_calls == 2:
            return Result([SimpleNamespace(id="skill_1", repo_id="repo_1", domain="backend", skill_path="skills/backend/SKILL.md")])
        return Result([self.task] if self.task else [])

    async def get(self, model, item_id):
        return self.task if self.task and self.task.id == item_id else None

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _task(status: str = "pending") -> AutopilotTask:
    return AutopilotTask(
        id="task_1",
        org_id="org_1",
        repo_id="repo_1",
        skill_id="skill_1",
        task_type="regenerate",
        trigger_reason="Freshness 10/25 - below threshold",
        freshness_at_trigger=10,
        status=status,
        created_at=datetime.utcnow(),
    )


def test_autopilot_queue_endpoint_returns_task_responses(monkeypatch) -> None:
    task = _task()

    async def fake_queue(db, org_id, repos, skills):
        return [task]

    monkeypatch.setattr(autopilot, "compute_autopilot_queue", fake_queue)
    response = asyncio.run(autopilot.get_autopilot_queue("org_1", Db(task), "org_1"))

    assert response[0].id == "task_1"
    assert response[0].repo_name == "api"
    assert response[0].skill_domain == "backend"


def test_autopilot_queue_forbidden_returns_json_response() -> None:
    response = asyncio.run(autopilot.get_autopilot_queue("org_1", Db(), "org_other"))

    assert response.status_code == 403
    assert response.body == b'{"detail":"Forbidden"}'


def test_autopilot_approve_missing_task_returns_404() -> None:
    response = asyncio.run(autopilot.approve_autopilot_task("org_1", "missing", Db(), "org_1"))

    assert response.status_code == 404


def test_autopilot_skip_rolls_back_on_db_error() -> None:
    class BrokenDb(Db):
        async def commit(self):
            raise RuntimeError("nope")

    db = BrokenDb(_task())
    response = asyncio.run(autopilot.skip_autopilot_task("org_1", "task_1", db, "org_1"))

    assert response.status_code == 400
    assert db.rolled_back is True


def test_autopilot_deduplicate_endpoint_returns_count() -> None:
    task = _task()
    db = Db(task)

    response = asyncio.run(autopilot.deduplicate_autopilot_queue("org_1", db, "org_1"))

    assert response.deduplicated == 0
    assert response.tasks[0].id == "task_1"
    assert db.committed is True


def test_autopilot_preview_returns_task_plan() -> None:
    task = _task()
    db = Db(task)

    response = asyncio.run(autopilot.preview_autopilot_task("org_1", "task_1", db, "org_1"))

    assert response.task.id == "task_1"
    assert response.risk_level == "low"
    assert "skills/backend/SKILL.md" in response.title


def test_generate_improvement_endpoint_returns_side_by_side_payload(monkeypatch) -> None:
    task = _task()
    org = SimpleNamespace(id="org_1", settings={})
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api")
    skill = SimpleNamespace(id="skill_1", repo_id="repo_1", domain="backend", skill_path="skills/backend/SKILL.md")

    class RichDb(Db):
        async def get(self, model, item_id):
            if model.__name__ == "AutopilotTask":
                return task if item_id == task.id else None
            if model.__name__ == "Org":
                return org
            if model.__name__ == "Repo":
                return repo
            if model.__name__ == "Skill":
                return skill
            return None

    async def fake_generate(db, task_arg, org_arg, repo_arg, skill_arg):
        task_arg.original_content = "old"
        task_arg.generated_content = "new"
        task_arg.improvement_status = "generated"
        return task_arg

    monkeypatch.setattr(autopilot, "generate_autopilot_improvement", fake_generate)
    response = asyncio.run(autopilot.generate_autopilot_task_improvement("org_1", "task_1", RichDb(task), "org_1"))

    assert response.original_content == "old"
    assert response.generated_content == "new"
    assert response.task.improvement_status == "generated"


def test_approve_improvement_uses_final_content(monkeypatch) -> None:
    task = _task()
    task.generated_content = "generated"
    org = SimpleNamespace(id="org_1", settings={})
    repo = SimpleNamespace(id="repo_1", org_id="org_1", name="api", full_name="acme/api")
    skill = SimpleNamespace(id="skill_1", repo_id="repo_1", domain="backend", skill_path="skills/backend/SKILL.md")

    class RichDb(Db):
        async def get(self, model, item_id):
            if model.__name__ == "AutopilotTask":
                return task if item_id == task.id else None
            if model.__name__ == "Org":
                return org
            if model.__name__ == "Repo":
                return repo
            if model.__name__ == "Skill":
                return skill
            return None

    async def fake_apply(db, task_arg, repo_arg, skill_arg, final_content, *, create_pr=False):
        task_arg.final_content = final_content
        task_arg.status = "approved"
        task_arg.improvement_status = "approved"
        return task_arg

    monkeypatch.setattr(autopilot, "apply_autopilot_improvement", fake_apply)
    response = asyncio.run(
        autopilot.approve_autopilot_task(
            "org_1",
            "task_1",
            RichDb(task),
            "org_1",
            autopilot.ApproveAutopilotRequest(final_content="edited", create_skill_pr=False),
        )
    )

    assert response.status == "approved"
    assert task.final_content == "edited"


def test_reject_improvement_marks_task_rejected() -> None:
    task = _task()
    db = Db(task)

    response = asyncio.run(autopilot.reject_autopilot_task("org_1", "task_1", autopilot.RejectAutopilotRequest(reason="not right"), db, "org_1"))

    assert response.status == "rejected"
    assert task.improvement_status == "rejected"
    assert db.committed is True
