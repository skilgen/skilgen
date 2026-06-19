from __future__ import annotations

import hashlib
import hmac
import time
from datetime import datetime, timedelta
from types import SimpleNamespace
from urllib.parse import urlencode

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.routes import slack
from packages.db.database import get_db


SECRET = "slack-secret"


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

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)


def _org():
    return SimpleNamespace(id="org_1", slack_signing_secret=SECRET, slack_team_id="T123")


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", is_active=True)


def _skill():
    return SimpleNamespace(id="skill_1", repo_id="repo_1")


def _session(login: str = "alice"):
    return SimpleNamespace(
        id="sess_1",
        org_id="org_1",
        repo_id="repo_1",
        engineer_login=login,
        session_start=datetime.utcnow() - timedelta(days=1),
    )


def _pr(login: str = "alice"):
    return SimpleNamespace(
        id="pr_1",
        repo_id="repo_1",
        author_login=login,
        opened_at=datetime.utcnow() - timedelta(days=1),
    )


def _attr(violations=None, *, risk_score: int = 12):
    return SimpleNamespace(
        pr_id="pr_1",
        primary_agent="codex",
        skills_violated=violations or [],
        risk_score=risk_score,
    )


def _body(text: str) -> bytes:
    return urlencode(
        {
            "command": "/skillayer",
            "text": text,
            "user_name": "alice",
            "team_id": "T123",
            "response_url": "",
            "channel_id": "C123",
        }
    ).encode("utf-8")


def _signature(body: bytes, timestamp: int) -> str:
    base = b"v0:" + str(timestamp).encode("utf-8") + b":" + body
    return "v0=" + hmac.new(SECRET.encode("utf-8"), base, hashlib.sha256).hexdigest()


def _client(db: Db, monkeypatch):
    app = FastAPI()
    app.include_router(slack.router)
    app.dependency_overrides[get_db] = lambda: db

    async def load_org(_db, team_id):
        assert team_id == "T123"
        return _org()

    monkeypatch.setattr(slack, "_load_org", load_org)
    return TestClient(app)


def _post(client: TestClient, text: str, *, timestamp: int | None = None, signature: str | None = None):
    body = _body(text)
    ts = timestamp or int(time.time())
    sig = signature or _signature(body, ts)
    return client.post(
        "/webhooks/slack/command",
        content=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Slack-Request-Timestamp": str(ts),
            "X-Slack-Signature": sig,
        },
    )


def test_slack_signature_valid_expired_and_wrong() -> None:
    body = _body("help")
    now = int(time.time())

    assert slack._verify_slack_signature(body, str(now), _signature(body, now), SECRET) is True
    assert slack._verify_slack_signature(body, str(now - 600), _signature(body, now - 600), SECRET) is False
    assert slack._verify_slack_signature(body, str(now), "v0=wrong", SECRET) is False


def test_skillayer_help_returns_help_blocks(monkeypatch) -> None:
    client = _client(Db(), monkeypatch)

    response = _post(client, "help")

    assert response.status_code == 200
    payload = response.json()
    assert payload["response_type"] == "ephemeral"
    assert "Skillayer command help" in str(payload["blocks"])


def test_skillayer_status_returns_metrics_section(monkeypatch) -> None:
    db = Db(
        [
            Result(rows=[_repo()]),
            Result(rows=[_skill()]),
            Result(rows=[_session()]),
            Result(rows=[_repo()]),
            Result(rows=[_pr()]),
            Result(rows=[_attr()]),
        ]
    )
    client = _client(db, monkeypatch)

    response = _post(client, "status")

    assert response.status_code == 200
    blocks = response.json()["blocks"]
    rendered = str(blocks)
    assert "Skillayer Status" in rendered
    assert "*Skills*\\n1" in rendered
    assert "*Repos*\\n1" in rendered
    assert "*Sessions 30d*\\n1" in rendered
    assert "*PRs attributed 30d*\\n1" in rendered


def test_skillayer_leaderboard_returns_numbered_list(monkeypatch) -> None:
    db = Db(
        [
            Result(rows=[_repo()]),
            Result(rows=[_session("alice"), _session("bob")]),
            Result(rows=[_repo()]),
            Result(rows=[_pr("alice")]),
            Result(rows=[_attr()]),
        ]
    )
    client = _client(db, monkeypatch)

    response = _post(client, "leaderboard 30")

    assert response.status_code == 200
    payload = response.json()
    assert payload["response_type"] == "in_channel"
    assert "1. `alice`" in str(payload["blocks"])
    assert "Full leaderboard" in str(payload["blocks"])


def test_skillayer_standup_returns_standup_blocks(monkeypatch) -> None:
    client = _client(Db(), monkeypatch)

    async def blocks(org_id, date, db):
        assert org_id == "org_1"
        return [{"type": "header", "text": {"type": "plain_text", "text": "Skillayer Daily Standup"}}]

    monkeypatch.setattr(slack, "build_standup_blocks", blocks)

    response = _post(client, "standup 2026-04-28")

    assert response.status_code == 200
    payload = response.json()
    assert payload["response_type"] == "in_channel"
    assert "Skillayer Daily Standup" in str(payload["blocks"])


def test_skillayer_unknown_returns_help(monkeypatch) -> None:
    client = _client(Db(), monkeypatch)

    response = _post(client, "nonsense")

    assert response.status_code == 200
    assert "Skillayer command help" in str(response.json()["blocks"])
