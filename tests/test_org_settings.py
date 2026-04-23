from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from apps.api.api.auth import get_current_org_id
from apps.api.api import analysis
from apps.api.api.routes import orgs
from packages.db.database import get_db


class FakeScalars:
    """Async SQLAlchemy scalars double."""

    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def all(self) -> list[object]:
        """Return configured scalar rows."""
        return self.rows


class FakeResult:
    """Async SQLAlchemy result double for org settings routes."""

    def __init__(self, *, scalar_one_or_none_value: object | None = None, scalar_rows: list[object] | None = None) -> None:
        self.scalar_one_or_none_value = scalar_one_or_none_value
        self.scalar_rows = scalar_rows or []

    def scalar_one_or_none(self) -> object | None:
        """Return a configured scalar value."""
        return self.scalar_one_or_none_value

    def scalars(self) -> FakeScalars:
        """Return configured scalar rows."""
        return FakeScalars(self.scalar_rows)


class FakeDb:
    """Async DB double for org settings tests."""

    def __init__(self, org: object | None, results: list[FakeResult] | None = None, *, fail_get: bool = False) -> None:
        self.org = org
        self.results = results or []
        self.fail_get = fail_get
        self.flush_count = 0
        self.commit_count = 0
        self.rollback_count = 0

    async def get(self, model: object, key: str) -> object | None:
        """Return the configured org or raise a DB error."""
        if self.fail_get:
            raise SQLAlchemyError("database unavailable")
        return self.org

    async def execute(self, statement: object) -> FakeResult:
        """Return the next configured result."""
        return self.results.pop(0)

    async def flush(self) -> None:
        """Record flush calls."""
        self.flush_count += 1

    async def commit(self) -> None:
        """Record commit calls."""
        self.commit_count += 1

    async def rollback(self) -> None:
        """Record rollback calls."""
        self.rollback_count += 1


def _org(**overrides: object) -> SimpleNamespace:
    """Build a fake org with settings defaults."""
    values: dict[str, object] = {
        "id": "org_123",
        "login": "acme",
        "name": "Acme",
        "plan": "team",
        "score_threshold": 60,
        "slack_webhook_url": "https://hooks.slack.com/services/T/B/C",
        "notify_on_pr": True,
        "notify_on_stale": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _client(db: FakeDb, *, with_auth: bool = True) -> TestClient:
    """Build a FastAPI client for org settings routes."""
    app = FastAPI()
    app.include_router(orgs.router)

    async def override_org_id() -> str:
        return "org_123"

    async def override_db() -> Any:
        yield db

    if with_auth:
        app.dependency_overrides[get_current_org_id] = override_org_id
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def _settings_results() -> list[FakeResult]:
    """Return DB result doubles needed by the settings response builder."""
    run = SimpleNamespace(id="run_1", status="complete", trigger="push", created_at=datetime(2026, 4, 23, 12, 0, 0))
    return [FakeResult(scalar_one_or_none_value=12345), FakeResult(scalar_rows=[run])]


def test_get_org_settings_returns_org_and_github_state() -> None:
    """GET settings returns current org settings and lightweight GitHub App state."""
    response = _client(FakeDb(_org(), _settings_results())).get("/orgs/org_123/settings")

    assert response.status_code == 200
    assert response.json()["score_threshold"] == 60
    assert response.json()["github_app_installed"] is True
    assert response.json()["recent_deliveries"][0]["status"] == "complete"


def test_update_org_settings_persists_fields() -> None:
    """PATCH settings updates mutable org fields and commits."""
    org = _org()
    db = FakeDb(org, _settings_results())

    response = _client(db).patch(
        "/orgs/org_123/settings",
        json={
            "name": "Acme Platform",
            "score_threshold": 72,
            "slack_webhook_url": None,
            "notify_on_pr": False,
            "notify_on_stale": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Acme Platform"
    assert response.json()["score_threshold"] == 72
    assert response.json()["slack_webhook_url"] is None
    assert org.name == "Acme Platform"
    assert db.flush_count == 1
    assert db.commit_count == 1


def test_update_org_settings_rejects_out_of_range_threshold() -> None:
    """PATCH settings rejects score thresholds outside 0-100."""
    response = _client(FakeDb(_org())).patch("/orgs/org_123/settings", json={"score_threshold": 101})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_org_settings_enforces_org_scope() -> None:
    """Org settings routes reject cross-org access."""
    response = _client(FakeDb(_org())).get("/orgs/org_other/settings")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_org_settings_requires_auth() -> None:
    """Org settings routes require the shared org auth dependency."""
    response = _client(FakeDb(_org()), with_auth=False).get("/orgs/org_123/settings")

    assert response.status_code in {401, 403}
    assert "detail" in response.json()


def test_update_org_settings_rolls_back_on_db_failure() -> None:
    """PATCH settings rolls back and returns a structured error after DB failures."""
    db = FakeDb(None, fail_get=True)

    response = _client(db).patch("/orgs/org_123/settings", json={"score_threshold": 70})

    assert response.status_code == 400
    assert response.json() == {"detail": "Could not update org settings", "code": "ORG_SETTINGS_UPDATE_FAILED"}
    assert db.rollback_count == 1


def test_test_notification_posts_to_slack(monkeypatch) -> None:
    """Test notification sends a Slack payload using the saved org webhook."""
    sent: dict[str, object] = {}

    async def fake_post(webhook_url: str, payload: dict[str, object]) -> None:
        sent["webhook_url"] = webhook_url
        sent["payload"] = payload

    monkeypatch.setattr(orgs, "post_slack_message", fake_post)

    response = _client(FakeDb(_org())).post("/orgs/org_123/test-notification")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert sent["webhook_url"] == "https://hooks.slack.com/services/T/B/C"


def test_analysis_stale_skill_alert_is_nonfatal(monkeypatch) -> None:
    """Analysis stale skill Slack failures should be logged and not raised."""
    db = FakeDb(_org())
    db.results = [FakeResult(scalar_one_or_none_value=_org())]
    skill = SimpleNamespace(domain="backend", score_freshness=10, load_count_30d=8)

    async def failing_post(webhook_url: str, payload: dict[str, object]) -> None:
        raise RuntimeError("slack down")

    monkeypatch.setattr(analysis, "post_slack_message", failing_post)

    asyncio.run(analysis._notify_stale_skills(db, "repo_1", "acme/repo", [skill]))  # type: ignore[list-item]


def test_dashboard_settings_page_is_wired() -> None:
    """Dashboard settings should expose tabs, controls, and billing content."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    page = (root / "apps/dashboard/app/dashboard/settings/page.tsx").read_text(encoding="utf-8")
    controls = (root / "apps/dashboard/app/dashboard/settings/settings-controls.tsx").read_text(encoding="utf-8")

    assert 'label: "General"' in page
    assert 'label: "Notifications"' in page
    assert 'label: "GitHub App"' in page
    assert 'label: "Billing"' in page
    assert "Score threshold" in controls
    assert "Slack webhook URL" in controls
    assert "test-notification" in controls
    assert "ManageBillingButton" in page
