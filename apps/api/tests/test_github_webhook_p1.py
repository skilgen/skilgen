from __future__ import annotations

import hashlib
import hmac
import json
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.routes import webhook
from packages.db.config import settings
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Commit, PullRequest


class Result:
    def __init__(self, scalar=None) -> None:
        self.scalar = scalar

    def scalar_one_or_none(self):
        return self.scalar

    def first(self):
        return self.scalar


class Db:
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.added: list[Any] = []
        self.commits = 0

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        for index, item in enumerate(self.added, start=1):
            if getattr(item, "id", None) is None:
                item.id = f"generated_{index}"

    async def commit(self):
        self.commits += 1


def _repo():
    return SimpleNamespace(
        id="repo_1",
        org_id="org_1",
        full_name="acme/api",
        name="api",
        default_branch="main",
        github_installation_id=123,
        is_active=True,
    )


def _client(db: Db, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    app = FastAPI()
    app.include_router(webhook.router)
    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setattr(settings, "GITHUB_WEBHOOK_SECRET", "secret")

    async def queue_analysis(*args, **kwargs):
        return True

    async def attribution_job(*args, **kwargs):
        return None

    async def commit_check_job(*args, **kwargs):
        return None

    monkeypatch.setattr(webhook, "_queue_analysis", queue_analysis)
    monkeypatch.setattr(webhook, "_run_attribution_job", attribution_job)
    monkeypatch.setattr(webhook, "_run_pr_commit_check_job", commit_check_job)
    return TestClient(app)


def _post(client: TestClient, event: str, payload: dict[str, Any]):
    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    return client.post(
        "/webhook/github",
        content=body,
        headers={
            "X-GitHub-Event": event,
            "X-Hub-Signature-256": signature,
            "Content-Type": "application/json",
        },
    )


def _pull_request_payload(action: str = "opened") -> dict[str, Any]:
    return {
        "action": action,
        "number": 42,
        "installation": {"id": 123},
        "repository": {"full_name": "acme/api"},
        "sender": {"login": "octocat"},
        "pull_request": {
            "number": 42,
            "title": "Add API auth",
            "body": "Implements auth",
            "state": "open",
            "created_at": "2026-04-27T10:00:00Z",
            "updated_at": "2026-04-27T10:01:00Z",
            "closed_at": None,
            "merged_at": None,
            "merged": False,
            "additions": 12,
            "deletions": 3,
            "changed_files": 2,
            "user": {"login": "codex[bot]", "type": "Bot"},
            "head": {"sha": "head_sha_1", "ref": "codex/auth"},
            "base": {"sha": "base_sha_1", "ref": "main"},
        },
    }


def test_pull_request_opened_webhook_persists_pr_and_queues_analysis(monkeypatch: pytest.MonkeyPatch) -> None:
    db = Db([Result(_repo()), Result(None), Result(None)])
    client = _client(db, monkeypatch)

    response = _post(client, "pull_request", _pull_request_payload())

    assert response.status_code == 200
    assert db.commits == 1
    pr = next(item for item in db.added if isinstance(item, PullRequest))
    assert pr.repo_id == "repo_1"
    assert pr.github_pr_number == 42
    assert pr.author_login == "codex[bot]"
    assert pr.author_type == "Bot"
    assert pr.head_sha == "head_sha_1"
    assert pr.base_sha == "base_sha_1"
    assert pr.state == "open"
    assert pr.raw["last_event"] == "opened"
    assert pr.raw["check_runs"] == []
    assert any(isinstance(item, AnalysisRun) for item in db.added)


def test_push_webhook_persists_all_commits_and_links_optional_pr(monkeypatch: pytest.MonkeyPatch) -> None:
    pr = PullRequest(repo_id="repo_1", github_pr_number=42)
    pr.id = "pr_1"
    db = Db([Result(_repo()), Result(pr), Result(None), Result(None), Result(None)])
    client = _client(db, monkeypatch)
    payload = {
        "ref": "refs/heads/codex/auth",
        "after": "c3",
        "installation": {"id": 123},
        "repository": {"full_name": "acme/api"},
        "pull_request": _pull_request_payload()["pull_request"],
        "commits": [
            {"id": "c1", "message": "one", "author": {"email": "a@example.com", "date": "2026-04-27T10:01:00Z"}, "added": ["a.py"], "removed": []},
            {"id": "c2", "message": "two", "author": {"email": "a@example.com", "date": "2026-04-27T10:02:00Z"}, "added": ["b.py"], "removed": ["old.py"]},
            {"id": "c3", "message": "three", "author": {"email": "a@example.com", "date": "2026-04-27T10:03:00Z"}, "added": [], "removed": []},
        ],
    }

    response = _post(client, "push", payload)

    assert response.status_code == 200
    commits = [item for item in db.added if isinstance(item, Commit)]
    assert [commit.sha for commit in commits] == ["c1", "c2", "c3"]
    assert all(commit.pr_id == "pr_1" for commit in commits)
    assert commits[0].additions == 1
    assert commits[1].deletions == 1


def test_pull_request_duplicate_event_updates_existing_pr_without_new_row(monkeypatch: pytest.MonkeyPatch) -> None:
    existing = PullRequest(repo_id="repo_1", github_pr_number=42)
    existing.id = "pr_1"
    db = Db([Result(_repo()), Result(existing), Result(None)])
    client = _client(db, monkeypatch)

    response = _post(client, "pull_request", _pull_request_payload())

    assert response.status_code == 200
    assert existing.title == "Add API auth"
    assert existing.raw["last_event"] == "opened"
    assert not any(isinstance(item, PullRequest) for item in db.added)


def test_check_run_upserts_by_name_and_head_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    existing = PullRequest(repo_id="repo_1", github_pr_number=42)
    existing.id = "pr_1"
    existing.head_sha = "head_sha_1"
    existing.raw = {
        "check_runs": [
            {"name": "Skillayer Skill Review", "head_sha": "head_sha_1", "status": "queued", "conclusion": None}
        ]
    }
    db = Db([Result(_repo()), Result(existing)])
    client = _client(db, monkeypatch)

    response = _post(
        client,
        "check_run",
        {
            "action": "completed",
            "repository": {"full_name": "acme/api"},
            "check_run": {
                "name": "Skillayer Skill Review",
                "head_sha": "head_sha_1",
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/acme/api/runs/1",
            },
        },
    )

    assert response.status_code == 200
    assert existing.raw["check_runs"] == [
        {
            "name": "Skillayer Skill Review",
            "head_sha": "head_sha_1",
            "status": "completed",
            "conclusion": "success",
            "started_at": None,
            "completed_at": None,
            "html_url": "https://github.com/acme/api/runs/1",
            "external_id": None,
            "action": "completed",
            "raw": {
                "name": "Skillayer Skill Review",
                "head_sha": "head_sha_1",
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/acme/api/runs/1",
            },
        }
    ]
