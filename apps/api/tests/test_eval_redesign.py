from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

from apps.api.api.routes import eval as eval_routes
from packages.db.models import SkillGap


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
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _repo(repo_id: str = "repo_1"):
    return SimpleNamespace(id=repo_id, org_id="org_1", name="api", is_active=True)


def _skill(skill_id: str, domain: str, *, score: int = 80, loads: int = 0, stale: bool = False, created_at=None):
    return SimpleNamespace(
        id=skill_id,
        repo_id="repo_1",
        domain=domain,
        score_total=score,
        score_groundedness=10,
        score_coverage=20,
        score_freshness=8,
        score_structure=10,
        load_count_30d=loads,
        is_stale=stale,
        created_at=created_at or datetime.utcnow(),
    )


def test_eval_summary_counts_strong_mixed_and_weak_sessions(monkeypatch) -> None:
    now = datetime.utcnow()
    sessions = [
        eval_routes.EvalSessionQualityResponse(session_id="s1", repo_id="repo_1", agent_runtime="Codex", repo_name="api", started_at=now, duration_seconds=None, skills_loaded=["security"], avg_skill_quality=84, quality_signal="strong", session_context="Security-sensitive work", outcome="unknown"),
        eval_routes.EvalSessionQualityResponse(session_id="s2", repo_id="repo_1", agent_runtime="Codex", repo_name="api", started_at=now, duration_seconds=None, skills_loaded=["core"], avg_skill_quality=62, quality_signal="mixed", session_context="General development session", outcome="unknown"),
        eval_routes.EvalSessionQualityResponse(session_id="s3", repo_id="repo_1", agent_runtime="Claude Code", repo_name="api", started_at=now, duration_seconds=None, skills_loaded=["legacy"], avg_skill_quality=42, quality_signal="weak", session_context="Focused legacy work", outcome="unknown"),
    ]

    async def fake_loader(_db, _org_id):
        return sessions

    monkeypatch.setattr(eval_routes, "_load_session_quality", fake_loader)

    response = asyncio.run(eval_routes.get_eval_summary("org_1", Db(), "org_1"))

    assert response.total_sessions == 3
    assert response.strong_sessions == 1
    assert response.mixed_sessions == 1
    assert response.weak_sessions == 1
    assert response.top_skill_impact[0]["domain"] in {"core", "legacy", "security"}


def test_eval_summary_hides_skill_impact_until_data_is_sufficient(monkeypatch) -> None:
    now = datetime.utcnow()
    sessions = [
        eval_routes.EvalSessionQualityResponse(session_id="s1", repo_id="repo_1", agent_runtime="codex_cli", repo_name="api", started_at=now, duration_seconds=None, skills_loaded=["security"], avg_skill_quality=84, quality_signal="strong", session_context="Security-sensitive work", outcome="unknown"),
        eval_routes.EvalSessionQualityResponse(session_id="s2", repo_id="repo_1", agent_runtime="codex_cli", repo_name="api", started_at=now, duration_seconds=None, skills_loaded=["core"], avg_skill_quality=62, quality_signal="mixed", session_context="General development session", outcome="unknown"),
    ]

    async def fake_loader(_db, _org_id):
        return sessions

    monkeypatch.setattr(eval_routes, "_load_session_quality", fake_loader)

    response = asyncio.run(eval_routes.get_eval_summary("org_1", Db(), "org_1"))

    assert response.top_skill_impact == []
    assert "at least 3 sessions" in response.insight


def test_skill_gaps_detects_missing_low_quality_stale_and_never_loaded() -> None:
    stale_loaded = _skill(
        "skill_security",
        "security_compliance",
        score=45,
        loads=4,
        stale=True,
        created_at=datetime.utcnow() - timedelta(days=45),
    )
    never_loaded = _skill("skill_style", "code_style", score=85, loads=0)
    db = Db(
        results=[
            Result(rows=[_repo()]),
            Result(rows=[stale_loaded, never_loaded]),
            Result(rows=[]),
            Result(rows=[SimpleNamespace(skill_id="skill_security", repo_id="repo_1")]),
        ]
    )

    response = asyncio.run(eval_routes.list_skill_gaps("org_1", "all", db, "org_1"))
    gap_types = {gap.gap_type for gap in response.gaps}

    assert response.checked_repos == 1
    assert response.checked_skills == 2
    assert response.critical_gap_count >= 1
    assert {"missing_skill", "low_quality", "stale", "never_loaded"} <= gap_types
    assert any(isinstance(item, SkillGap) for item in db.added)
    assert db.committed is True
