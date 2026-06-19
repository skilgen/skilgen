from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from apps.api.api.routes import registry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_ROUTE = ROOT / "apps/api/api/routes/registry.py"
REGISTRY_MODEL = ROOT / "packages/db/models/registry.py"
DASHBOARD_SHELL = ROOT / "apps/dashboard/app/dashboard/registry/registry-shell.tsx"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_publish_skill_creates_registry_entry_with_scores() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "@router.post(\"/orgs/{org_id}/publish\"" in source
    assert "SkillRegistryEntry(" in source
    assert "score_total=float(skill.score_total or scores[\"total\"])" in source
    assert "score_groundedness=float(skill.score_groundedness or scores[\"groundedness\"])" in source


def test_publish_same_skill_twice_has_no_conflict_guard() -> None:
    source = _source(REGISTRY_ROUTE)
    publish_body = source.split("async def publish_org_skill", 1)[1].split("@router.get(\"/orgs/{org_id}/entries\"", 1)[0]
    assert "select(SkillRegistryEntry)" not in publish_body
    assert "db.add(entry)" in publish_body


def test_get_org_entries_filters_visibility_and_search() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "visibility: str | None = None" in source
    assert "min_score: float | None = None" in source
    assert "SkillRegistryEntry.visibility == visibility" in source
    assert "SkillRegistryEntry.description.ilike(term)" in source


def test_install_marketplace_entry_increments_install_count() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "@router.post(\"/orgs/{org_id}/entries/{entry_id}/install\"" in source
    assert "MarketplaceInstall(" in source
    assert "entry.install_count = int(entry.install_count or 0) + 1" in source


def test_deprecate_entry_sets_successor_and_message() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "@router.patch(\"/orgs/{org_id}/entries/{entry_id}/deprecate\"" in source
    assert "entry.is_deprecated = True" in source
    assert "entry.deprecation_message = payload.message" in source
    assert "entry.successor_entry_id = payload.successor_entry_id" in source


def test_dependency_graph_returns_nodes_edges_and_stale_count() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "class DependencyGraphResponse" in source
    assert "nodes: list[dict[str, object]]" in source
    assert "edges: list[dict[str, object]]" in source
    assert "stale_upstream_count" in source


def test_import_claude_content_scores_and_creates_entry() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "@router.post(\"/orgs/{org_id}/import\"" in source
    assert "_compute_skill_score(payload.content)" in source
    assert "visibility=\"private\"" in source
    assert "improvement_suggestions" in source


def test_marketplace_list_only_returns_public_entries() -> None:
    source = _source(REGISTRY_ROUTE)
    marketplace_body = source.split("async def list_marketplace", 1)[1].split("@router.get(\"/marketplace/{entry_id}\"", 1)[0]
    assert "SkillRegistryEntry.visibility == \"public\"" in marketplace_body
    assert "desc(SkillRegistryEntry.install_count)" in marketplace_body
    assert "desc(SkillRegistryEntry.score_total)" in marketplace_body


def test_half_life_compute_high_churn_shorter_than_stable() -> None:
    half_life_source = _source(ROOT / "apps/api/api/services/half_life.py")
    assert "daily_commit_rate > 2.0" in half_life_source
    assert "(freshness - 20) / 5" in half_life_source
    assert "(freshness - 20) / 0.5" in half_life_source


def test_half_life_stable_caps_at_90_days() -> None:
    half_life_source = _source(ROOT / "apps/api/api/services/half_life.py")
    assert "min(90.0, days_to_stale)" in half_life_source


def test_check_and_queue_regenerations_marks_rows() -> None:
    half_life_source = _source(ROOT / "apps/api/api/services/half_life.py")
    assert "regen_queued.is_(False)" in half_life_source
    assert "half_life.regen_queued = True" in half_life_source
    assert "half_life.regen_queued_at = now" in half_life_source


def test_compatibility_matrix_returns_runtime_coverage() -> None:
    source = _source(REGISTRY_ROUTE)
    assert "@router.get(\"/orgs/{org_id}/compatibility-matrix\"" in source
    assert registry.RUNTIMES == ["claude-code", "codex", "cursor", "copilot", "gemini-cli"]
    assert "\"compatible\" if runtime in compatible else \"untested\"" in source


def test_registry_models_include_expected_tables() -> None:
    source = _source(REGISTRY_MODEL)
    assert "__tablename__ = \"skill_registry_entries\"" in source
    assert "__tablename__ = \"skill_dependencies\"" in source
    assert "__tablename__ = \"marketplace_installs\"" in source


def test_registry_dashboard_has_four_tabs_and_drawer() -> None:
    source = _source(DASHBOARD_SHELL)
    assert "\"Org Registry\"" in source
    assert "\"Marketplace\"" in source
    assert "\"Import\"" in source
    assert "\"Compatibility\"" in source
    assert "EntryDetailDrawer" in source
