from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

from apps.api.api.routes import orgs
from apps.api.api.services.standup import collect_standup_summary
from packages.db.models import AgentSession, PRAttribution, PullRequest, Repo


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
    def __init__(self, *, org=None, results=None) -> None:
        self.org = org
        self.results = list(results or [])
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def get(self, model, key):
        if model.__name__ == "Org":
            return self.org
        return None

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _session(session_id: str = "session_1") -> AgentSession:
    return AgentSession(
        id=session_id,
        repo_id="repo_1",
        org_id="org_1",
        session_id=session_id,
        agent_runtime="codex",
        engineer_login="ravi",
        files_touched=["src/auth.py", "tests/test_auth.py"],
        skills_loaded=["auth", "testing"],
        session_start=datetime(2026, 4, 28, 10, 0, 0),
        session_end=datetime(2026, 4, 28, 10, 15, 0),
        outcome="success",
    )


def _pr() -> PullRequest:
    pr = PullRequest(repo_id="repo_1", github_pr_number=42)
    pr.id = "pr_1"
    pr.title = "Fix auth refresh"
    pr.state = "open"
    pr.opened_at = datetime(2026, 4, 28, 10, 20, 0)
    pr.raw = {}
    return pr


def _attr() -> PRAttribution:
    attr = PRAttribution(pr_id="pr_1", primary_agent="codex", confidence=0.95)
    attr.id = "attr_1"
    attr.sessions = ["session_1"]
    attr.risk_tier = "red"
    attr.skills_violated = [{"severity": "critical"}, {"severity": "warning"}]
    attr.skills_loaded = ["auth"]
    return attr


def test_my_code_today_links_sessions_to_pr_attribution() -> None:
    db = Db(results=[Result(rows=[_session()]), Result(rows=[_pr()]), Result(rows=[_pr()]), Result(rows=[_attr()])])

    response = asyncio.run(orgs.get_my_code_today("org_1", login="ravi", date="2026-04-28", db=db, current_org_id="org_1"))

    assert response.summary.total_sessions == 1
    assert response.summary.total_files == 2
    assert response.summary.skills_used == ["auth", "testing"]
    assert response.summary.prs_opened == 1
    assert response.summary.violations == 1
    assert response.summary.warnings == 1
    assert response.prs[0].github_pr_number == 42
    assert response.sessions[0].pr is not None
    assert response.sessions[0].pr.risk_tier == "red"


def test_my_code_today_empty_date_returns_empty_summary() -> None:
    db = Db(results=[Result(rows=[]), Result(rows=[])])

    response = asyncio.run(orgs.get_my_code_today("org_1", login="ravi", date="2026-04-28", db=db, current_org_id="org_1"))

    assert response.sessions == []
    assert response.summary.total_sessions == 0
    assert response.summary.skills_used == []
    assert response.prs == []


def test_my_code_today_includes_pr_activity_without_sessions() -> None:
    db = Db(results=[Result(rows=[]), Result(rows=[_pr()]), Result(rows=[_attr()])])

    response = asyncio.run(orgs.get_my_code_today("org_1", login="ravi", date="2026-04-28", db=db, current_org_id="org_1"))

    assert response.sessions == []
    assert response.prs[0].title == "Fix auth refresh"
    assert response.prs[0].risk_tier == "red"
    assert response.summary.prs_opened == 1
    assert response.summary.violations == 1
    assert response.summary.warnings == 1


def test_my_code_today_handles_timezone_aware_pr_timestamps() -> None:
    pr = _pr()
    pr.opened_at = datetime(2026, 4, 28, 10, 20, 0, tzinfo=timezone.utc)
    pr.merged_at = datetime(2026, 4, 28, 11, 20, 0, tzinfo=timezone.utc)
    db = Db(results=[Result(rows=[]), Result(rows=[pr]), Result(rows=[_attr()])])

    response = asyncio.run(orgs.get_my_code_today("org_1", login="ravi", date="2026-04-28", db=db, current_org_id="org_1"))

    assert response.summary.prs_opened == 1
    assert response.summary.prs_merged == 1
    assert response.prs[0].github_pr_number == 42


def test_standup_summary_aggregates_daily_activity() -> None:
    repo = Repo(org_id="org_1", github_repo_id=123, full_name="acme/api", name="api")
    repo.id = "repo_1"
    db = Db(results=[Result(rows=[_session()]), Result(rows=[repo]), Result(rows=[_pr()]), Result(rows=[_attr()])])

    summary = asyncio.run(collect_standup_summary("org_1", "2026-04-28", db))

    assert summary["agent_sessions"] == 1
    assert summary["files_changed"] == 2
    assert summary["prs_opened"] == 1
    assert summary["top_engineers"][0] == {"login": "ravi", "sessions": 1, "files": 2}
    assert summary["top_skills_used"] == ["auth", "testing"]
    assert summary["violations_total"] == 1
    assert summary["warnings_total"] == 1
    assert summary["risk_summary"] == {"red": 1, "yellow": 0, "green": 0}


def test_slack_settings_patch_persists_standup_fields() -> None:
    org = SimpleNamespace(
        id="org_1",
        slack_webhook_url=None,
        slack_standup_enabled=False,
        slack_standup_hour=9,
    )
    db = Db(org=org)

    response = asyncio.run(
        orgs.update_org_slack_settings(
            "org_1",
            orgs.SlackSettingsPayload(
                webhook_url="https://hooks.slack.test/services/T/ABC",
                standup_enabled=True,
                standup_hour=14,
            ),
            db,
            "org_1",
        )
    )

    assert response["ok"] is True
    assert org.slack_webhook_url == "https://hooks.slack.test/services/T/ABC"
    assert org.slack_standup_enabled is True
    assert org.slack_standup_hour == 14
    assert db.committed is True
