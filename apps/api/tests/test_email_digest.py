from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

from apps.api.api.routes import cron
from apps.api.api.services import email_digest


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

    async def get(self, model, item_id):
        if model.__name__ == "Org":
            return self.org
        return None

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def commit(self):
        self.committed = True


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.login_args = None
        self.sent = None
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, username, password):
        self.login_args = (username, password)

    def sendmail(self, from_email, to_emails, message):
        self.sent = (from_email, to_emails, message)


def _repo():
    return SimpleNamespace(id="repo_1", org_id="org_1", is_active=True)


def _pr(pr_id="pr_1", author="octocat", state="merged"):
    return SimpleNamespace(
        id=pr_id,
        author_login=author,
        opened_at=datetime.now(UTC).replace(tzinfo=None),
        merged_at=datetime.now(UTC).replace(tzinfo=None) if state == "merged" else None,
        closed_at=None,
        state=state,
        additions=10,
        deletions=2,
    )


def _attr(pr_id="pr_1", agent="codex", risk=22, findings=None):
    return SimpleNamespace(
        pr_id=pr_id,
        primary_agent=agent,
        risk_score=risk,
        risk_tier="green",
        skills_violated=findings if findings is not None else [],
    )


def test_build_digest_html_contains_agents_and_leaderboard() -> None:
    html = email_digest.build_digest_html(
        "Acme",
        {
            "agents": [
                {
                    "agent": "codex",
                    "agent_label": "Codex",
                    "prs": 3,
                    "merged": 2,
                    "compliance_percent": 96.0,
                    "violations": 1,
                    "avg_risk": 18.5,
                    "top_violations": ["Testing"],
                }
            ]
        },
        {"developers": [{"login": "octocat", "prs_merged": 2, "compliance_pct": 100.0}]},
        30,
        "2026-04-30",
    )

    assert "Codex" in html
    assert "octocat" in html
    assert "Testing" in html
    assert "Weekly Agent Intelligence Digest" in html
    assert "View Dashboard" in html


def test_send_digest_email_uses_smtp_from_to_subject(monkeypatch) -> None:
    FakeSMTP.instances = []
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM", "digest@example.com")
    monkeypatch.setattr(email_digest.smtplib, "SMTP", FakeSMTP)

    sent = email_digest.send_digest_email("team@example.com", "Weekly Digest", "<p>Hello</p>")

    assert sent is True
    smtp = FakeSMTP.instances[0]
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 2525
    assert smtp.started_tls is True
    assert smtp.login_args == ("user", "secret")
    assert smtp.sent is not None
    from_email, to_emails, message = smtp.sent
    assert from_email == "digest@example.com"
    assert to_emails == ["team@example.com"]
    assert "Subject: Weekly Digest" in message
    assert "To: team@example.com" in message


def test_build_and_send_org_digest_collects_and_sends(monkeypatch) -> None:
    FakeSMTP.instances = []
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_FROM", "digest@example.com")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    monkeypatch.setattr(email_digest.smtplib, "SMTP", FakeSMTP)
    org = SimpleNamespace(id="org_1", name="Acme", login="acme", digest_email="team@example.com", settings={})
    pr = _pr()
    attr = _attr(findings=[{"severity": "critical", "skill_name": "Security"}])
    db = Db(
        org=org,
        results=[
            Result(rows=[_repo()]),
            Result(rows=[pr]),
            Result(rows=[attr]),
            Result(rows=[_repo()]),
            Result(rows=[SimpleNamespace(engineer_login="octocat", session_start=datetime.now(UTC).replace(tzinfo=None), files_touched=["a.py"])]),
            Result(rows=[pr]),
            Result(rows=[attr]),
        ],
    )

    sent = asyncio.run(email_digest.build_and_send_org_digest("org_1", db))

    assert sent is True
    assert db.committed is True
    assert "digest_last_sent_at" in org.settings
    assert FakeSMTP.instances[0].sent is not None
    assert "Security" in FakeSMTP.instances[0].sent[2]


def test_digest_cron_skips_nonmatching_day_hour() -> None:
    db = Db(results=[Result(rows=[])])

    response = asyncio.run(cron.run_digest_cron(db, None, None))

    assert response == {"ok": True, "matched": 0, "sent": 0, "failed": []}


def test_digest_cron_sends_matching(monkeypatch) -> None:
    org = SimpleNamespace(id="org_1", digest_email="team@example.com", digest_enabled=True, digest_day=1, digest_hour=9)
    db = Db(results=[Result(rows=[org])])

    async def fake_send(org_id, db_arg):
        assert org_id == "org_1"
        assert db_arg is db
        return True

    monkeypatch.setattr(cron, "build_and_send_org_digest", fake_send)

    response = asyncio.run(cron.run_digest_cron(db, None, None))

    assert response == {"ok": True, "matched": 1, "sent": 1, "failed": []}
