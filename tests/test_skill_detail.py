from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

from apps.api.api.routes.skills import _build_skill_response


ROOT = Path(__file__).resolve().parents[1]


class _ScalarResult:
    def __init__(self, scalar: object = None, scalar_one: object = None, scalar_one_or_none: object = None) -> None:
        self._scalar = scalar
        self._scalar_one = scalar_one
        self._scalar_one_or_none = scalar_one_or_none

    def scalar_one(self) -> object:
        return self._scalar_one

    def scalar_one_or_none(self) -> object:
        return self._scalar_one_or_none

    def scalar(self) -> object:
        return self._scalar


class _FakeDb:
    def __init__(self) -> None:
        self._results = [
            _ScalarResult(scalar_one=2),
            _ScalarResult(scalar_one_or_none=SimpleNamespace(version_number=3)),
        ]

    async def execute(self, _query: object) -> _ScalarResult:
        return self._results.pop(0)


def test_skill_response_includes_full_content_repo_and_usage_metadata() -> None:
    skill = SimpleNamespace(
        id="skill_1",
        domain="backend/api",
        skill_path="skills/backend/api/SKILL.md",
        content="# API\n\nUse the FastAPI route patterns.",
        content_hash="abcdef1234567890",
        is_stale=True,
        load_count_30d=7,
        last_loaded_at=None,
        score_total=82,
        score_groundedness=20,
        score_coverage=21,
        score_freshness=22,
        score_structure=19,
    )
    repo = SimpleNamespace(id="repo_1", name="AnomalyDetector")

    response = asyncio.run(_build_skill_response(_FakeDb(), skill, repo))  # type: ignore[arg-type]

    assert response.repo_id == "repo_1"
    assert response.repo_name == "AnomalyDetector"
    assert response.content == "# API\n\nUse the FastAPI route patterns."
    assert response.content_hash == "abcdef1234567890"
    assert response.is_stale is True
    assert response.load_count_30d == 7
    assert response.version_count == 2
    assert response.latest_version_number == 3
    assert response.score.total == 82


def test_skill_detail_page_and_viewer_show_content_versions_and_usage() -> None:
    page = (ROOT / "apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/page.tsx").read_text(encoding="utf-8")
    viewer = (ROOT / "apps/dashboard/src/components/skill-detail-viewer.tsx").read_text(encoding="utf-8")

    assert "SKILL.md — what agents receive" in viewer
    assert "Version history" in viewer
    assert "Usage stats" in viewer
    assert "loads in last 30 days" in viewer
    assert "Last loaded" in viewer
    assert "CopySkillButton content={content} domain={skill.domain}" in viewer
    assert "fetch(`${API_URL}/skills/${skillId}/versions/${versionId}`" in viewer
    assert "SkillViewTracker" in page
    assert "skill_viewed" in (ROOT / "apps/dashboard/src/components/skill-view-tracker.tsx").read_text(encoding="utf-8")
    assert "<StaleBadge isStale={skill.is_stale}" in page
    assert "<VersionBadge versionNumber={skill.latest_version_number}" in page


def test_copy_button_copies_content_and_resets_success_state() -> None:
    source = (ROOT / "apps/dashboard/src/components/copy-skill-button.tsx").read_text(encoding="utf-8")

    assert "navigator.clipboard.writeText(content)" in source
    assert "skill_content_copied" in source
    assert "setCopied(true)" in source
    assert "setTimeout(() => setCopied(false), 2000)" in source
    assert "Copied!" in source


def test_stale_badge_shows_when_skill_is_stale() -> None:
    source = (ROOT / "apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/page.tsx").read_text(encoding="utf-8")

    assert "isStale ? \"Stale\" : \"Fresh\"" in source
    assert "bg-red-900/40" in source
    assert "text-red-300" in source
