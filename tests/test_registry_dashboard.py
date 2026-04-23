from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_registry_dashboard_uses_real_api_and_tabs() -> None:
    page = (ROOT / "apps/dashboard/app/dashboard/registry/page.tsx").read_text(encoding="utf-8")
    data = (ROOT / "apps/dashboard/lib/data.ts").read_text(encoding="utf-8")

    assert "StubPage" not in page
    assert "getRegistrySkills(query)" in page
    assert "/registry${query ? `?${query}` : \"\"}" in data
    assert "Browse" in page
    assert "Published" in page
    assert "Search skills" in page


def test_registry_dashboard_renders_skill_cards_with_filters() -> None:
    page = (ROOT / "apps/dashboard/app/dashboard/registry/page.tsx").read_text(encoding="utf-8")

    assert "function RegistryCard" in page
    assert "skill.import_count" in page
    assert "skill.score_total" in page
    assert "name=\"tag\"" in page
    assert "name=\"sort\"" in page
    assert "org_id" in page
