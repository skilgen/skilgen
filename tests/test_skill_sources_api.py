from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps.api.api.routes.repos import _build_coverage_map, _compute_skill_score, _coverage_score
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


def test_skill_content_update_endpoint_versions_content_and_requires_org_scope() -> None:
    source = _read("apps/api/api/routes/repos.py")

    assert "class SkillContentUpdate(BaseModel)" in source
    assert '@router.patch("/{repo_id}/skills/{skill_id}/content")' in source
    assert "current_org_id: str = Depends(get_current_org_id)" in source
    assert "await _repo_in_scope(db, repo_id, current_org_id)" in source
    assert "if skill is None or skill.repo_id != repo_id" in source
    assert "run_id=skill.run_id or str(uuid4())" in source
    assert '"updated": False' in source
    assert '"updated": True' in source
    assert '"version_number": version_number' in source
    assert '"score": _score_response(skill).model_dump()' in source


def test_compute_skill_score_for_manual_content_update() -> None:
    content = "# Backend\n\n" + "Use the existing route and service patterns. " * 80

    score = _compute_skill_score(content)

    assert score == {
        "total": 53,
        "groundedness": 5,
        "coverage": 25,
        "freshness": 10,
        "structure": 13,
    }


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
    assert skill_category_for_source_type("runbooks") == "operational_knowledge"
    assert skill_category_for_source_type("incidents") == "operational_knowledge"


def test_worker_payload_forwards_source_type_and_path_to_analysis() -> None:
    source = _read("apps/api/api/routes/worker.py")

    assert "source_type: str | None = None" in source
    assert "source_path: str | None = None" in source
    assert "source_type=payload.source_type" in source
    assert "source_path=payload.source_path" in source


def test_analysis_pipeline_uses_source_specific_skill_generation() -> None:
    source = _read("apps/api/api/analysis.py")

    assert "def _source_skill_files(" in source
    assert "run_source_parsers(" in source
    assert "source_type=source_type" in source
    assert "source_path=source_path" in source
    assert 'skill_category": skill_category_for_source_type(source.source_type)' in source
