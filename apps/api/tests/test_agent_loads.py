from __future__ import annotations

import asyncio
from types import SimpleNamespace

from apps.api.api.routes.repos import load_skills_for_agent
from packages.db.models import SkillUsageEvent


class Headers(dict):
    def get(self, key: str, default=None):
        return super().get(key.lower(), default)


class Request:
    def __init__(self, headers: dict[str, str]) -> None:
        self.headers = Headers({key.lower(): value for key, value in headers.items()})


class Result:
    def __init__(self, scalar=None, rows=None) -> None:
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def all(self):
        return self.rows


class Db:
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.events: list[SkillUsageEvent] = []

    async def execute(self, statement):
        return self.results.pop(0)

    def add(self, item):
        if isinstance(item, SkillUsageEvent):
            self.events.append(item)

    async def commit(self):
        return None

    async def rollback(self):
        return None


def _skill():
    return SimpleNamespace(id="skill_1", domain="auth", score_total=80, score_freshness=20, load_count_30d=0, last_loaded_at=None)


def _version():
    return SimpleNamespace(content="# Auth\n\nUse shared auth service.", version_number=1)


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", name="demo")


def _org():
    return SimpleNamespace(id="org_1", api_key="sk-test")


def _call(headers: dict[str, str], current_org_id: str | None):
    skill = _skill()
    results = []
    if headers.get("API-Key") and not current_org_id:
        results.append(Result(_org()))
    results.extend([Result(_repo()), Result(rows=[(skill, _version())])])
    db = Db(results)
    response = asyncio.run(load_skills_for_agent("repo_1", Request(headers), db, current_org_id))
    return response, db


def test_agent_load_variants_create_usage_events_with_runtime_detection() -> None:
    variants = [
        ({"Authorization": "Bearer generic"}, "org_1", "unidentified_agent"),
        ({"API-Key": "sk-test"}, None, "codex_cli"),
        ({"API-Key": "sk-test", "User-Agent": "codex/1.0"}, None, "codex_cli"),
        ({"API-Key": "sk-test", "User-Agent": "claude-code/1.0 anthropic"}, None, "claude_code"),
        ({"API-Key": "sk-test", "X-Agent": "gemini"}, None, "gemini_cli"),
    ]

    all_events = []
    for headers, current_org_id, expected_runtime in variants:
        response, db = _call(headers, current_org_id)
        assert "skills" in response
        assert response["skill_count"] == 1
        assert len(db.events) == 1
        assert db.events[0].agent_runtime == expected_runtime
        all_events.extend(db.events)

    assert len(all_events) == 5
