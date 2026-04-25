from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_registry_dashboard_uses_real_api_and_tabs() -> None:
    page = (ROOT / "apps/dashboard/app/dashboard/registry/page.tsx").read_text(encoding="utf-8")
    shell = (ROOT / "apps/dashboard/app/dashboard/registry/registry-shell.tsx").read_text(encoding="utf-8")
    data = (ROOT / "apps/dashboard/lib/data.ts").read_text(encoding="utf-8")

    assert "StubPage" not in page
    assert "getOrgRegistryEntries" in page
    assert "getMarketplaceEntries" in page
    assert "/registry/orgs/${orgId}/entries" in data
    assert "/registry/marketplace" in data
    assert "Org Registry" in shell
    assert "Marketplace" in shell
    assert "Compatibility" in shell


def test_registry_dashboard_renders_skill_cards_with_filters() -> None:
    page = (ROOT / "apps/dashboard/app/dashboard/registry/registry-shell.tsx").read_text(encoding="utf-8")

    assert "function SkillCard" in page
    assert "entry.install_count" in page
    assert "entry.score_total" in page
    assert "Search registry skills" in page
    assert "PublishModal" in page
    assert "orgId" in page
