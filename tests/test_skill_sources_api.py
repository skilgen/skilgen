from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps.api.api.routes.repos import _build_coverage_map, _coverage_score
from packages.db.models.skill import skill_category_for_source_type


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_repo_skill_sources_endpoint_requires_auth_and_returns_coverage_contract() -> None:
    source = _read("apps/api/api/routes/repos.py")

    assert '@router.get("/{repo_id}/skill-sources", response_model=RepoSkillSourcesResponse)' in source
    assert "current_org_id: str = Depends(get_current_org_id)" in source
    assert "await _repo_in_scope(db, repo_id, current_org_id)" in source
    assert "coverage_map = _build_coverage_map(skills)" in source


def test_analyze_source_endpoint_validates_body_and_queues_job() -> None:
    source = _read("apps/api/api/routes/repos.py")

    assert "class AnalyzeSourceRequest(BaseModel)" in source
    assert '@router.post("/{repo_id}/analyze-source", response_model=AnalyzeSourceResponse)' in source
    assert '"source_type": payload.source_type' in source
    assert '"source_path": payload.path' in source


def test_org_coverage_summary_endpoint_requires_org_scope() -> None:
    source = _read("apps/api/api/routes/orgs.py")

    assert '@router.get("/{org_id}/coverage-summary", response_model=OrgCoverageSummaryResponse)' in source
    assert "current_org_id: str = Depends(get_current_org_id)" in source
    assert "_assert_org_scope(org_id, current_org_id)" in source


def test_coverage_score_calculation_with_known_skill_data() -> None:
    skills = [
        SimpleNamespace(source_type="code", skill_category=None, score_total=80),
        SimpleNamespace(source_type="openapi", skill_category=None, score_total=70),
        SimpleNamespace(source_type="dbt", skill_category=None, score_total=60),
        SimpleNamespace(source_type="sarif", skill_category=None, score_total=50),
    ]

    coverage_map = _build_coverage_map(skills)  # type: ignore[arg-type]

    assert coverage_map["codebase_architecture"].covered is True
    assert coverage_map["internal_tools"].avg_score == 70
    assert coverage_map["data_schema"].skill_count == 1
    assert coverage_map["operational_knowledge"].covered is False
    assert _coverage_score(coverage_map) == 50


def test_source_type_to_skill_category_mapping_is_complete_for_new_sources() -> None:
    assert skill_category_for_source_type("openapi") == "internal_tools"
    assert skill_category_for_source_type("terraform") == "codebase_architecture"
    assert skill_category_for_source_type("dbt") == "data_schema"
    assert skill_category_for_source_type("sarif") == "security_compliance"
    assert skill_category_for_source_type("runbook") == "operational_knowledge"
