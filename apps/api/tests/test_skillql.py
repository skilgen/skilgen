from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from apps.api.api.services import skillql
from apps.api.api.services.llm import LLMNotConfiguredError
from packages.db.database import get_db
from packages.db.models import Org


class Result:
    def __init__(self, rows=None) -> None:
        self.rows = rows or []

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, results: list[Result] | None = None) -> None:
        self.results = results or []
        self.org = SimpleNamespace(id="org_1", settings={"llm_provider": "openai", "llm_api_key_enc": "enc", "llm_model": "gpt-test"})

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    async def get(self, model, id_):
        if model is Org and id_ == "org_1":
            return self.org
        return None


def _client(db: Db) -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    return TestClient(app)


def _plan(**overrides):
    payload = {
        "intent": "Find unhealthy skills",
        "data_sources": ["skills"],
        "filters": {
            "time_window_days": None,
            "agent_runtime": None,
            "risk_tier": None,
            "engineer_login": None,
            "skill_category": "testing_conventions",
            "event_type": None,
        },
        "group_by": None,
        "sort_by": "score_total",
        "limit": 10,
        "result_format": "table",
    }
    payload.update(overrides)
    return json.dumps(payload)


def test_skillql_valid_plan_executes_rows(monkeypatch) -> None:
    calls: list[str] = []

    async def fake_call_llm(settings, system_prompt, user_prompt, max_tokens=1024):
        calls.append(system_prompt)
        if len(calls) == 1:
            return _plan()
        return json.dumps(["Which testing skills are stale?", "Which agents load these skills?", "Show low score skills by category."])

    monkeypatch.setattr(skillql, "call_llm", fake_call_llm)
    skill = SimpleNamespace(
        domain="testing",
        skill_category="testing_conventions",
        score_total=42,
        load_count_30d=8,
        last_loaded_at=datetime(2026, 4, 27, 12, 0, 0),
        created_at=datetime(2026, 4, 20, 12, 0, 0),
    )
    client = _client(Db([Result([skill])]))

    response = client.post("/orgs/org_1/skillql", json={"query": "Which testing skills are weak?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "Which testing skills are weak?"
    assert payload["intent"] == "Find unhealthy skills"
    assert payload["data_sources"] == ["skills"]
    assert payload["columns"] == ["domain", "skill_category", "score_total", "load_count_30d", "last_loaded_at", "updated_at"]
    assert payload["rows"][0]["domain"] == "testing"
    assert payload["rows"][0]["score_total"] == 42
    assert payload["row_count"] == 1
    assert payload["answer"]
    assert len(payload["suggested_followups"]) == 3


def test_skillql_normalises_question_dict_string(monkeypatch) -> None:
    prompts: list[str] = []

    async def fake_call_llm(settings, system_prompt, user_prompt, max_tokens=1024):
        prompts.append(user_prompt)
        if len(prompts) == 1:
            return _plan()
        if len(prompts) == 2:
            return "Testing skills are weak: testing is 42/100."
        return json.dumps(["Which testing skills are stale?", "Which agents load these skills?", "Show low score skills by category."])

    monkeypatch.setattr(skillql, "call_llm", fake_call_llm)
    skill = SimpleNamespace(
        domain="testing",
        skill_category="testing_conventions",
        score_total=42,
        load_count_30d=8,
        last_loaded_at=datetime(2026, 4, 27, 12, 0, 0),
        created_at=datetime(2026, 4, 20, 12, 0, 0),
    )
    client = _client(Db([Result([skill])]))

    response = client.post("/orgs/org_1/skillql", json={"query": "{'question': 'Which testing skills are weak?'}"})

    assert response.status_code == 200
    assert response.json()["query"] == "Which testing skills are weak?"
    assert prompts[0] == "Which testing skills are weak?"


def test_skillql_llm_not_configured_shape(monkeypatch) -> None:
    async def fake_call_llm(settings, system_prompt, user_prompt, max_tokens=1024):
        raise LLMNotConfiguredError("missing")

    monkeypatch.setattr(skillql, "call_llm", fake_call_llm)
    client = _client(Db())

    response = client.post("/orgs/org_1/skillql", json={"query": "Show risky PRs"})

    assert response.status_code == 422
    assert response.json() == {"error": "llm_not_configured", "message": "SkillQL requires an LLM configured. Go to Settings → LLM."}


def test_skillql_malformed_llm_json_query_parse_failed(monkeypatch) -> None:
    async def fake_call_llm(settings, system_prompt, user_prompt, max_tokens=1024):
        return "not json"

    monkeypatch.setattr(skillql, "call_llm", fake_call_llm)
    client = _client(Db())

    response = client.post("/orgs/org_1/skillql", json={"query": "Show risky PRs"})

    assert response.status_code == 422
    assert response.json()["error"] == "query_parse_failed"


def test_skillql_suggestions_endpoint_has_four_categories() -> None:
    client = _client(Db())

    response = client.get("/orgs/org_1/skillql/suggestions")

    assert response.status_code == 200
    payload = response.json()
    assert list(payload) == ["Agent Activity", "Developer Insights", "Skill Health", "Policy & Risk"]
    assert all(len(items) == 3 for items in payload.values())


def test_skillql_query_over_500_chars_returns_422() -> None:
    client = _client(Db())

    response = client.post("/orgs/org_1/skillql", json={"query": "x" * 501})

    assert response.status_code == 422
