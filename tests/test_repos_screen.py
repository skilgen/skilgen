from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    """Read a repository file as UTF-8 text."""
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_repos_list_renders_with_data() -> None:
    page = _read("apps/dashboard/app/dashboard/repos/page.tsx")
    browser = _read("apps/dashboard/app/dashboard/repos/repos-browser.tsx")

    assert "fetch(`${API_URL}/orgs/bootstrap`" in page
    assert "fetch(`${API_URL}/orgs/${org.id}/repos`" in page
    assert "Repositories" in page
    assert "{repos.length} repos connected" in page
    assert "https://github.com/apps/skillayer/installations/new" in page
    assert "ReposBrowser" in page
    assert "Search repositories" in browser
    assert "score-desc" in browser
    assert "router.push(`/dashboard/repos/${repo.id}`)" in browser


def test_repo_detail_shows_subscores() -> None:
    detail = _read("apps/dashboard/app/dashboard/repos/[repoId]/page.tsx")

    assert "getRepo(accessToken, repoId)" in detail
    assert "getRepoSkills(accessToken, repoId)" in detail
    assert "getRepoScoreHistory(accessToken, repoId)" in detail
    assert "AnalyseNowButton" in detail
    assert "conic-gradient(#C9973A" in detail
    assert "Groundedness" in detail
    assert "Coverage" in detail
    assert "Freshness" in detail
    assert "Structure" in detail
    assert "href={`/dashboard/repos/${repoId}/skills/${skill.id}`}" in detail


def test_score_history_chart_data() -> None:
    detail = _read("apps/dashboard/app/dashboard/repos/[repoId]/page.tsx")
    api = _read("apps/api/api/routes/repos.py")

    assert "<polyline" in detail
    assert "point.score_total" in detail
    assert ".limit(10)" in api
    assert "for row in reversed(rows)" in api
    assert '"score_total": row.score_total' in api


def test_analyse_button_triggers_run() -> None:
    button = _read("apps/dashboard/app/dashboard/repos/[repoId]/analyse-now-button.tsx")
    api = _read("apps/api/api/routes/repos.py")

    assert 'method: "POST"' in button
    assert "`${apiUrl}/repos/${repoId}/analyse`" in button
    assert 'Authorization: `Bearer ${accessToken}`' in button
    assert 'trigger="manual"' in api
    assert "await db.commit()" in api
    assert '"ref": repo.default_branch' in api
    assert 'return {"queued": run.id}' in api
