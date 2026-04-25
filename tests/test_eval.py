from __future__ import annotations

from datetime import datetime, timedelta
import importlib
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db


eval_routes = importlib.import_module("apps.api.api.routes.eval")


class FakeScalars:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def all(self) -> list[object]:
        return self.rows


class FakeResult:
    def __init__(self, rows: list[object] | None = None, one: object | None = None) -> None:
        self.rows = rows or []
        self.one = one

    def scalars(self) -> FakeScalars:
        return FakeScalars(self.rows)

    def scalar_one_or_none(self) -> object | None:
        return self.one

    def all(self) -> list[object]:
        return self.rows


class FakeDb:
    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.added: list[object] = []
        self.commit_count = 0

    async def execute(self, statement: object) -> FakeResult:
        return self.results.pop(0)

    def add(self, item: object) -> None:
        self.added.append(item)

    def add_all(self, items: list[object]) -> None:
        self.added.extend(items)

    async def flush(self) -> None:
        return None

    async def commit(self) -> None:
        self.commit_count += 1


def repo() -> SimpleNamespace:
    return SimpleNamespace(id="repo_1", org_id="org_1", is_active=True, name="Repo")


def skill(domain: str = "auth", score: int = 80, freshness: int = 25) -> SimpleNamespace:
    return SimpleNamespace(id=f"skill_{domain}", repo_id="repo_1", domain=domain, score_total=score, score_freshness=freshness, created_at=datetime.utcnow())


def task(outcome: str = "failure", domains: list[str] | None = None, score: float | None = None, session_id: str = "s1") -> SimpleNamespace:
    return SimpleNamespace(
        id=f"task_{session_id}_{outcome}",
        org_id="org_1",
        repo_id="repo_1",
        session_id=session_id,
        agent_runtime="claude_code",
        task_description="Fix auth",
        task_type="debugging",
        outcome=outcome,
        failure_reason="Missing context",
        skills_loaded=["skill_auth"] if domains else [],
        skill_domains_loaded=domains or [],
        skill_score_at_task=score,
        duration_seconds=10,
        token_count=100,
        started_at=datetime.utcnow(),
        completed_at=None,
        created_at=datetime.utcnow(),
    )


def client(db: FakeDb, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    app = FastAPI()
    app.include_router(eval_routes.router, prefix="/eval")

    async def org_id() -> str:
        return "org_1"

    async def override_db() -> Any:
        yield db

    async def noop(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr(eval_routes, "_detect_skill_gaps_background", noop)
    monkeypatch.setattr(eval_routes, "_audit_task_recorded", noop)
    app.dependency_overrides[get_current_org_id] = org_id
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def payload(outcome: str = "success", skills_loaded: list[str] | None = None) -> dict[str, object]:
    return {
        "repo_id": "repo_1",
        "session_id": "s1",
        "agent_runtime": "claude_code",
        "task_description": "Fix auth",
        "task_type": "debugging",
        "outcome": outcome,
        "failure_reason": "bad context" if outcome == "failure" else None,
        "skills_loaded": skills_loaded or [],
        "duration_seconds": 45,
        "token_count": 4200,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
    }


def test_post_task_creates_agent_task(monkeypatch: pytest.MonkeyPatch) -> None:
    db = FakeDb([FakeResult(one=repo()), FakeResult(rows=[]), FakeResult(rows=[])])
    response = client(db, monkeypatch).post("/eval/orgs/org_1/tasks", json=payload())
    assert response.status_code == 200
    assert db.added[0].outcome == "success"


def test_post_task_populates_domains(monkeypatch: pytest.MonkeyPatch) -> None:
    db = FakeDb([FakeResult(one=repo()), FakeResult(rows=[skill("auth")]), FakeResult(rows=[])])
    client(db, monkeypatch).post("/eval/orgs/org_1/tasks", json=payload(skills_loaded=["skill_auth"]))
    assert db.added[0].skill_domains_loaded == ["auth"]


def test_post_task_sets_average_score(monkeypatch: pytest.MonkeyPatch) -> None:
    db = FakeDb([FakeResult(one=repo()), FakeResult(rows=[skill("auth", 80), skill("api", 60)]), FakeResult(rows=[])])
    client(db, monkeypatch).post("/eval/orgs/org_1/tasks", json=payload(skills_loaded=["skill_auth", "skill_api"]))
    assert db.added[0].skill_score_at_task == 70


@pytest.mark.anyio
async def test_gap_detection_missing_skill() -> None:
    db = FakeDb([FakeResult(rows=[task(domains=["auth"], session_id=str(i)) for i in range(3)]), FakeResult(rows=[]), FakeResult(one=None)])
    changed = await eval_routes._detect_skill_gaps("org_1", "repo_1", db)
    assert changed == 1
    assert db.added[0].gap_type == "missing_skill"


@pytest.mark.anyio
async def test_gap_detection_weak_skill() -> None:
    db = FakeDb([FakeResult(rows=[task(domains=["auth"], session_id=str(i)) for i in range(3)]), FakeResult(rows=[]), FakeResult(one=skill("auth", 25))])
    await eval_routes._detect_skill_gaps("org_1", "repo_1", db)
    assert db.added[0].gap_type == "weak_skill"


@pytest.mark.anyio
async def test_gap_detection_stale_skill() -> None:
    db = FakeDb([FakeResult(rows=[task(domains=["auth"], session_id=str(i)) for i in range(3)]), FakeResult(rows=[]), FakeResult(one=skill("auth", 80, 10))])
    await eval_routes._detect_skill_gaps("org_1", "repo_1", db)
    assert db.added[0].gap_type == "stale_skill"


@pytest.mark.anyio
async def test_gap_detection_updates_existing_gap() -> None:
    gap = SimpleNamespace(domain="auth", failure_count=1, task_ids=[], existing_skill_id=None, existing_skill_score=None, gap_type="missing_skill", status="open")
    db = FakeDb([FakeResult(rows=[task(domains=["auth"], session_id=str(i)) for i in range(3)]), FakeResult(rows=[gap]), FakeResult(one=None)])
    await eval_routes._detect_skill_gaps("org_1", "repo_1", db)
    assert db.added == []
    assert gap.failure_count == 3


def test_roi_multiplier_computed(monkeypatch: pytest.MonkeyPatch) -> None:
    tasks = [task("success", ["api"], 80, f"h{i}") for i in range(5)] + [task("failure", ["api"], 20, f"l{i}") for i in range(5)]
    db = FakeDb([FakeResult(rows=tasks), FakeResult(rows=[])])
    response = client(db, monkeypatch).get("/eval/orgs/org_1/roi")
    assert response.json()["multiplier"] == 10


def test_roi_multiplier_null_with_small_buckets(monkeypatch: pytest.MonkeyPatch) -> None:
    tasks = [task("success", ["api"], 80, "h1"), task("failure", ["api"], 20, "l1")]
    db = FakeDb([FakeResult(rows=tasks), FakeResult(rows=[])])
    assert client(db, monkeypatch).get("/eval/orgs/org_1/roi").json()["multiplier"] is None


def test_create_ab_test_creates_sessions(monkeypatch: pytest.MonkeyPatch) -> None:
    db = FakeDb([FakeResult(one=skill("auth")), FakeResult(one=repo())])
    response = client(db, monkeypatch).post("/eval/orgs/org_1/ab-tests", json={"skill_id": "skill_auth", "name": "auth v1 vs v2", "control_version_id": "v1", "treatment_version_id": "v2"})
    assert response.status_code == 200
    assert len(db.added) == 3


def test_conclude_ab_test_treatment_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    test = SimpleNamespace(id="ab1", org_id="org_1", skill_id="skill_auth", name="AB", status="running", winner=None, control_success_rate=None, treatment_success_rate=None, improvement_pct=None, confidence=None, recommendation=None, created_at=datetime.utcnow(), completed_at=None, control_session_id="control", treatment_session_id="treatment")
    control = [task("success", session_id="control"), task("failure", session_id="control")]
    treatment = [task("success", session_id="treatment") for _ in range(2)]
    db = FakeDb([FakeResult(one=test), FakeResult(rows=control), FakeResult(rows=treatment)])
    response = client(db, monkeypatch).post("/eval/orgs/org_1/ab-tests/ab1/conclude")
    assert response.json()["winner"] == "treatment"
    assert response.json()["recommendation"]


def test_conclude_ab_test_low_confidence(monkeypatch: pytest.MonkeyPatch) -> None:
    test = SimpleNamespace(id="ab1", org_id="org_1", skill_id="skill_auth", name="AB", status="running", winner=None, control_success_rate=None, treatment_success_rate=None, improvement_pct=None, confidence=None, recommendation=None, created_at=datetime.utcnow(), completed_at=None, control_session_id="control", treatment_session_id="treatment")
    db = FakeDb([FakeResult(one=test), FakeResult(rows=[task(session_id="control")]), FakeResult(rows=[task(session_id="treatment")])])
    assert client(db, monkeypatch).post("/eval/orgs/org_1/ab-tests/ab1/conclude").json()["confidence"] == "low"


def test_skill_gaps_lists_open_with_action(monkeypatch: pytest.MonkeyPatch) -> None:
    gap = SimpleNamespace(id="gap1", domain="auth", failure_count=3, gap_type="missing_skill", existing_skill_id=None, existing_skill_score=None, status="open", suggested_action=None, detected_at=datetime.utcnow(), task_ids=[])
    db = FakeDb([FakeResult(rows=[gap])])
    body = client(db, monkeypatch).get("/eval/orgs/org_1/skill-gaps").json()
    assert body[0]["suggested_action"].startswith("Generate a new skill")


def test_patch_gap_resolved(monkeypatch: pytest.MonkeyPatch) -> None:
    gap = SimpleNamespace(id="gap1", domain="auth", failure_count=3, gap_type="missing_skill", existing_skill_id=None, existing_skill_score=None, status="open", detected_at=datetime.utcnow(), task_ids=[], resolved_at=None, resolution_note=None)
    db = FakeDb([FakeResult(one=gap)])
    body = client(db, monkeypatch).patch("/eval/orgs/org_1/skill-gaps/gap1", json={"status": "resolved", "resolution_note": "fixed"}).json()
    assert body["status"] == "resolved"
    assert gap.resolved_at is not None
