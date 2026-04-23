"""Focused coverage for the dependency risk graph workstream."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json

from apps.api.api.routes.repos import _dependency_response, _dependency_risk_score
from skilgen.core.dependency_risk import (
    analyze_dependency_risks,
    dependency_report_to_dict,
    render_dependency_risk_report,
)


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    """Read a repository file as UTF-8 text."""
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_dependency_report_classifies_cves_and_upgrade_commands() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(
            json.dumps({"dependencies": {"left-pad": "^1.3.0", "react": "18.2.0"}}),
            encoding="utf-8",
        )
        vulnerabilities = {"npm:left-pad": [{"id": "GHSA-test", "aliases": ["CVE-2026-0001"]}]}

        report = analyze_dependency_risks(root, vulnerabilities)
        payload = dependency_report_to_dict(report)
        rendered = render_dependency_risk_report(report)

        assert report.total_count == 2
        assert report.high_risk[0].name == "left-pad"
        assert report.high_risk[0].cves == ["CVE-2026-0001"]
        assert report.high_risk[0].upgrade_command == "npm install left-pad"
        assert payload["risk_score"] >= 30
        assert "Dependency risk report" in rendered
        assert "CVE-2026-0001" in rendered


def test_cli_analyze_deps_is_wired_to_human_readable_report() -> None:
    source = _read("skilgen/cli/main.py")

    assert 'analyze.add_argument("--deps"' in source
    assert "analyze_dependency_risks(Path(args.project_root).resolve())" in source
    assert "render_dependency_risk_report(report)" in source


def test_dependency_table_model_and_migration_have_required_indexes() -> None:
    model = _read("packages/db/models/dependency.py")
    migration = _read("apps/api/alembic/versions/b7d4a6f2c9e1_add_dependencies_table.py")

    assert 'Index("ix_dependencies_repo_id", "repo_id")' in model
    assert 'Index("ix_dependencies_run_id", "run_id")' in model
    assert 'Index("ix_dependencies_risk_level", "risk_level")' in model
    assert 'op.create_table(\n        "dependencies"' in migration
    assert 'sa.ForeignKeyConstraint(["repo_id"], ["repos.id"])' in migration
    assert 'sa.ForeignKeyConstraint(["run_id"], ["analysis_runs.id"])' in migration
    assert 'op.drop_table("dependencies")' in migration


def test_dependency_api_endpoint_is_auth_scoped_and_structured() -> None:
    source = _read("apps/api/api/routes/repos.py")

    assert '@router.get("/{repo_id}/dependencies", response_model=DependencyReportResponse)' in source
    assert "current_org_id: str = Depends(get_current_org_id)" in source
    assert "await _repo_in_scope(db, repo_id, current_org_id)" in source
    assert '"code": "DEPENDENCY_REPORT_FAILED"' in source


def test_dependency_response_and_risk_score_helpers() -> None:
    dependency = SimpleNamespace(
        id="dep_1",
        name="requests",
        version="2.0.0",
        ecosystem="pip",
        risk_level="high",
        cves=["CVE-2026-0002"],
        latest_version=None,
        license="Apache-2.0",
        created_at=datetime(2026, 4, 23),
    )

    response = _dependency_response(dependency)  # type: ignore[arg-type]
    score = _dependency_risk_score([dependency])  # type: ignore[list-item]

    assert response.name == "requests"
    assert response.upgrade_command == "python -m pip install --upgrade requests"
    assert response.cves == ["CVE-2026-0002"]
    assert score == 30


def test_analysis_pipeline_stores_dependency_results_with_osv_retry_hooks() -> None:
    source = _read("apps/api/api/analysis.py")

    assert "OSV_ENDPOINT = \"https://api.osv.dev/v1/querybatch\"" in source
    assert "async def _fetch_osv_vulnerabilities" in source
    assert "httpx.AsyncClient(timeout=5.0)" in source
    assert "for attempt in range(3)" in source
    assert "await analyze_and_store_dependencies(db, repo_id, run_id, tmpdir)" in source
    assert "await save_dependencies(db, repo_id, run_id, report)" in source


def test_dashboard_repo_detail_renders_dependencies_tab() -> None:
    data = _read("apps/dashboard/lib/data.ts")
    page = _read("apps/dashboard/app/dashboard/repos/[repoId]/page.tsx")

    assert "export type DependencyReport" in data
    assert "getRepoDependencies" in data
    assert "Dependency risk summary for the latest analysis run" in page
    assert "High risk CVEs" in page
    assert "<DependenciesSection report={dependencies} />" in page
