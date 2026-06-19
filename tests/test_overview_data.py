from __future__ import annotations

from pathlib import Path

from packages.db.schemas import RepoResponse


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(path: str) -> str:
    """Return a repository file as text for lightweight dashboard checks."""
    return (ROOT / path).read_text(encoding="utf-8")


def test_metric_cards_render_with_real_data_and_zero_scores() -> None:
    """Overview metrics should render concrete stats without dropping zero values."""
    source = read_repo_file("apps/dashboard/src/components/overview-live-data.tsx")
    metric_source = read_repo_file("apps/dashboard/src/components/metric-card.tsx")

    assert 'value={stats.repo_count}' in source
    assert 'value={`${stats.avg_score}/100`}' in source
    assert "stats?.avg_score ?" not in source
    assert "MetricSkeleton" in source
    assert "stats === null" in source
    assert "String(value)" in metric_source
    assert 'return normalizedValue.length > 0 ? normalizedValue : "—";' in metric_source


def test_repos_table_shows_score_badge_colors() -> None:
    """Repo rows should expose the requested score bands and not-analysed state."""
    source = read_repo_file("apps/dashboard/src/components/repos-table.tsx")

    assert "bg-red-900/30 text-red-400" in source
    assert "bg-amber-900/30 text-amber-400" in source
    assert "bg-green-900/30 text-green-400" in source
    assert "Not analysed" in source


def test_relative_time_formatting_covers_short_and_old_dates() -> None:
    """Relative time helper should format recent changes and older dates."""
    source = read_repo_file("apps/dashboard/src/components/repos-table.tsx")

    assert "minute${minutes === 1" in source
    assert "hour${hours === 1" in source
    assert "day${days === 1" in source
    assert "days < 7" in source
    assert "Intl.DateTimeFormat" in source


def test_empty_state_shows_onboarding_cta() -> None:
    """The empty overview should show the GitHub onboarding CTA."""
    source = read_repo_file("apps/dashboard/src/components/overview-live-data.tsx")

    assert "OnboardingCard" in source
    assert "Install GitHub App" in source
    assert "<ReposTable repos={repos} />" in source
    assert "repos.length > 0" in source


def test_overview_uses_server_loaded_props_without_browser_refetch() -> None:
    """Overview should render server-loaded props immediately without client fetch timing."""
    source = read_repo_file("apps/dashboard/src/components/overview-live-data.tsx")

    assert '"use client"' not in source
    assert "useEffect" not in source
    assert "fetch(" not in source
    assert "const stats = initialStats;" in source
    assert "const repos = initialRepos;" in source


def test_overview_page_logs_sanitized_fetch_state() -> None:
    """Server preload logs should be structured and avoid secret values."""
    source = read_repo_file("apps/dashboard/app/dashboard/page.tsx")

    assert "logOverviewEvent" in source
    assert "JSON.stringify" in source
    assert 'scope: "dashboard.overview"' in source
    assert '"org_loaded"' in source
    assert '"stats_loaded"' in source
    assert '"repos_loaded"' in source
    assert "accessToken:" not in source
    assert "token: accessToken" not in source
    assert "apiHost: safeApiHost(API_URL)" in source


def test_overview_sections_have_error_fallbacks() -> None:
    """Fetch failures should render visible error sections instead of blank panels."""
    source = read_repo_file("apps/dashboard/src/components/overview-live-data.tsx")
    repos_source = read_repo_file("apps/dashboard/src/components/repos-table.tsx")
    fallback_source = read_repo_file("apps/dashboard/src/components/section-fallback.tsx")

    assert "SectionFallback" in source
    assert "Unable to load {section}." in fallback_source
    assert "Refresh the page or contact support." in fallback_source
    assert "reposErrorDetail" in source
    assert "No repositories to display" in repos_source


def test_org_repos_include_installation_id_for_manual_analysis() -> None:
    """Repo API schema and org response should include GitHub installation id."""
    orgs_source = read_repo_file("apps/api/api/routes/orgs.py")

    assert "installation_id=repo.github_installation_id" in orgs_source
    assert "round(avg_score or 0)" in orgs_source
    assert "ScoreHistory.recorded_at >= start_at" in orgs_source
    assert "_last_30_score_dates" in orgs_source
    assert "score_trend" in orgs_source
    assert "installation_id" in RepoResponse.model_fields
