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

    assert 'value={stats.repo_count}' in source
    assert 'value={`${stats.avg_score}/100`}' in source
    assert "stats?.avg_score ?" not in source
    assert "MetricSkeleton" in source
    assert "stats === null" in source


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


def test_org_repos_include_installation_id_for_manual_analysis() -> None:
    """Repo API schema and org response should include GitHub installation id."""
    orgs_source = read_repo_file("apps/api/api/routes/orgs.py")

    assert "installation_id=repo.github_installation_id" in orgs_source
    assert "round(avg_score or 0)" in orgs_source
    assert ".limit(7)" in orgs_source
    assert "score_trend" in orgs_source
    assert "installation_id" in RepoResponse.model_fields
