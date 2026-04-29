from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import orgs
from packages.db.database import get_db
from packages.db.models import AgentSession, PRAttribution, PullRequest


class Result:
    def __init__(self, scalar=None, rows=None) -> None:
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, results: list[Result], objects: dict[tuple[object, str], object] | None = None) -> None:
        self.results = results
        self.objects = objects or {}

    async def execute(self, statement):
        if not self.results:
            raise AssertionError(f"Unexpected DB execute: {statement}")
        return self.results.pop(0)

    async def get(self, model, id_):
        return self.objects.get((model, id_))


def _repo(repo_id: str = "repo_1"):
    return SimpleNamespace(id=repo_id, org_id="org_1", name="api", full_name="acme/api")


def _pr(index: int, title: str, state: str = "open") -> PullRequest:
    pr = PullRequest(repo_id="repo_1", github_pr_number=index)
    pr.id = f"pr_{index}"
    pr.title = title
    pr.body = ""
    pr.state = state
    pr.author_login = "codex-bot"
    pr.opened_at = datetime(2026, 4, 28, 10, index, 0)
    pr.additions = index
    pr.deletions = 1
    pr.changed_files = 2
    pr.raw = {"html_url": f"https://github.com/acme/api/pull/{index}"}
    return pr


def _attr(pr_id: str, agent: str, risk: int) -> PRAttribution:
    attr = PRAttribution(pr_id=pr_id, primary_agent=agent, confidence=0.9)
    attr.id = f"attr_{pr_id}"
    attr.skills_loaded = ["auth", "testing"]
    attr.skills_violated = [{"severity": "critical"}] if risk >= 70 else []
    attr.risk_score = risk
    attr.risk_tier = "red" if risk >= 70 else "green"
    attr.risk_breakdown = {"violations": {"points": min(40, risk)}}
    attr.sessions = ["session_1"]
    return attr


def _client(db: Db) -> TestClient:
    app = FastAPI()
    app.include_router(orgs.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"
    return TestClient(app)


def test_agent_prs_pagination_returns_all_fixture_prs() -> None:
    prs = [_pr(i, f"Change {i}") for i in range(1, 7)]
    attrs = [_attr(pr.id, "codex", i * 10) for i, pr in enumerate(prs, start=1)]
    cursors: list[str | None] = [None]
    seen: list[str] = []

    for _ in range(3):
        db = Db([Result(rows=[_repo()]), Result(rows=prs), Result(rows=attrs)])
        client = _client(db)
        cursor_param = f"&cursor={cursors[-1]}" if cursors[-1] else ""
        response = client.get(f"/orgs/org_1/agent-prs?state=all&limit=2&order=asc{cursor_param}")
        assert response.status_code == 200
        payload = response.json()
        seen.extend(item["pr_id"] for item in payload["items"])
        cursors.append(payload["next_cursor"])

    assert seen == [f"pr_{i}" for i in range(1, 7)]
    assert cursors[-1] is None


def test_agent_prs_filter_by_agent() -> None:
    prs = [_pr(1, "Codex change"), _pr(2, "Claude change")]
    attrs = [_attr("pr_1", "codex", 10), _attr("pr_2", "claude_code", 10)]
    db = Db([Result(rows=[_repo()]), Result(rows=prs), Result(rows=attrs)])
    client = _client(db)

    response = client.get("/orgs/org_1/agent-prs?state=all&agent=codex")

    assert response.status_code == 200
    assert [item["primary_agent"] for item in response.json()["items"]] == ["codex"]


def test_agent_prs_search_matches_title_substring() -> None:
    prs = [_pr(1, "Fix OAuth refresh"), _pr(2, "Update docs")]
    attrs = [_attr("pr_1", "codex", 10), _attr("pr_2", "codex", 10)]
    db = Db([Result(rows=[_repo()]), Result(rows=prs), Result(rows=attrs)])
    client = _client(db)

    response = client.get("/orgs/org_1/agent-prs?state=all&search=oauth")

    assert response.status_code == 200
    assert [item["title"] for item in response.json()["items"]] == ["Fix OAuth refresh"]


def test_agent_prs_sort_risk_score_desc_puts_red_first() -> None:
    prs = [_pr(1, "Low risk"), _pr(2, "High risk")]
    attrs = [_attr("pr_1", "codex", 5), _attr("pr_2", "codex", 90)]
    db = Db([Result(rows=[_repo()]), Result(rows=prs), Result(rows=attrs)])
    client = _client(db)

    response = client.get("/orgs/org_1/agent-prs?state=all&sort=risk_score&order=desc")

    assert response.status_code == 200
    assert response.json()["items"][0]["risk_tier"] == "red"


def test_agent_pr_detail_includes_replay_link() -> None:
    pr = _pr(1, "Replay me")
    attr = _attr("pr_1", "codex", 90)
    session = AgentSession(
        id="session_1",
        repo_id="repo_1",
        org_id="org_1",
        session_id="session_1",
        agent_runtime="codex",
        skills_loaded=["auth"],
        session_start=datetime(2026, 4, 28, 10, 0, 0),
        created_at=datetime(2026, 4, 28, 10, 0, 0),
    )
    db = Db(
        [Result(attr), Result(rows=[session])],
        objects={(PullRequest, "pr_1"): pr, (type(_repo()), "repo_1"): _repo()},
    )
    # SimpleNamespace has a dynamic class, so register the repo under the concrete model import path.
    from packages.db.models import Repo

    db.objects[(Repo, "repo_1")] = _repo()
    client = _client(db)

    response = client.get("/orgs/org_1/agent-prs/pr_1")

    assert response.status_code == 200
    assert response.json()["sessions"][0]["replay_url"] == "/dashboard/repos/repo_1/sessions/session_1"
