from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.routes import orgs, repos
from packages.db.database import get_db
from skilgen.core.score import ci_result, score_badge_markdown, shield_badge_color


class FakeResult:
    """Small async SQLAlchemy result double for route tests."""

    def __init__(
        self,
        *,
        scalar_value: object | None = None,
        scalar_one_or_none_value: object | None = None,
        scalar_list: list[object] | None = None,
        rows: list[object] | None = None,
    ) -> None:
        self.scalar_value = scalar_value
        self.scalar_one_or_none_value = scalar_one_or_none_value
        self.scalar_list = scalar_list or []
        self.rows = rows or []

    def scalar(self) -> object | None:
        """Return the configured scalar value."""
        return self.scalar_value

    def scalar_one_or_none(self) -> object | None:
        """Return the configured optional scalar value."""
        return self.scalar_one_or_none_value

    def scalars(self) -> "FakeResult":
        """Return self so tests can call all()."""
        return self

    def all(self) -> list[object]:
        """Return configured scalar rows."""
        return self.scalar_list

    def fetchall(self) -> list[object]:
        """Return configured row tuples."""
        return self.rows


class FakeDb:
    """Async database double with a fixed execute sequence."""

    def __init__(self, execute_results: list[FakeResult], repo: object | None = None) -> None:
        self.execute_results = execute_results
        self.repo = repo

    async def get(self, model: object, key: str) -> object | None:
        """Return the configured repository."""
        return self.repo

    async def execute(self, statement: object) -> FakeResult:
        """Return the next configured query result."""
        if not self.execute_results:
            raise AssertionError("Unexpected query")
        return self.execute_results.pop(0)


def _minimal_project(root: Path) -> None:
    """Create a small analyzable project for CLI score tests."""
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("def handler():\n    return {}\n", encoding="utf-8")


def _run_cli(args: list[str], project_root: Path) -> subprocess.CompletedProcess[str]:
    """Run the Skilgen CLI in a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "skilgen.cli.main", *args, "--project-root", str(project_root)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_ci_result_threshold_messages() -> None:
    """CI scoring should fail and pass with explicit human-readable messages."""
    payload = {
        "score": 45,
        "subscores": {
            "groundedness": {"score": 16},
            "coverage": {"score": 16},
            "freshness": {"score": 8},
            "structure": {"score": 5},
        },
    }

    passed, message = ci_result(payload, min_score=60, min_groundedness=15, min_coverage=15)
    assert passed is False
    assert message == "CI FAIL: Skilgen Score 45/100 is below minimum 60/100. Run skilgen deliver to fix."

    passed, message = ci_result(payload, min_score=40, min_groundedness=15, min_coverage=15)
    assert passed is True
    assert message == "CI PASS: Skilgen Score 45/100 ✓"


def test_score_ci_cli_exit_codes_and_badge_output() -> None:
    """The score command should support CI exits and shields.io Markdown badges."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _minimal_project(root)

        pass_result = _run_cli(["score", "--ci", "--min-score", "0", "--min-groundedness", "0", "--min-coverage", "0"], root)
        assert pass_result.returncode == 0
        assert pass_result.stdout.startswith("CI PASS: Skilgen Score")

        fail_result = _run_cli(["score", "--ci", "--min-score", "101"], root)
        assert fail_result.returncode == 1
        assert "CI FAIL: Skilgen Score" in fail_result.stdout
        assert "below minimum 101/100" in fail_result.stdout

        badge_result = _run_cli(["score", "--badge"], root)
        assert badge_result.returncode == 0
        assert badge_result.stdout.startswith("![Skilgen Score](https://img.shields.io/badge/Skilgen_Score-")
        assert badge_result.stdout.strip().endswith(("brightgreen)", "green)", "yellow)", "red)"))


def test_score_badge_colors_match_thresholds() -> None:
    """Badge color thresholds should match the product contract."""
    assert shield_badge_color(85) == "brightgreen"
    assert shield_badge_color(70) == "green"
    assert shield_badge_color(50) == "yellow"
    assert shield_badge_color(49) == "red"
    assert "Skilgen_Score-74%2F100-green" in score_badge_markdown({"score": 74})


def test_init_ci_writes_github_actions_workflow() -> None:
    """skilgen init --ci should create a PR workflow with score and policy gates."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        result = _run_cli(["init", "--ci"], root)
        payload = json.loads(result.stdout)
        workflow = root / ".github" / "workflows" / "skilgen.yml"

        assert result.returncode == 0
        assert payload["ci_workflow_path"] == str(workflow.resolve())
        assert workflow.exists()
        content = workflow.read_text(encoding="utf-8")
        assert "on:\n  pull_request:" in content
        assert "skilgen deliver --project-root ." in content
        assert "skilgen score --ci --min-score 60 --min-groundedness 15 --min-coverage 15 --project-root ." in content
        assert "skilgen enterprise policy check --project-root ." in content


def test_repo_score_badge_endpoint_returns_svg() -> None:
    """Repo score badge endpoint should return an SVG for the latest stored score."""
    app = FastAPI()
    app.include_router(repos.router)

    async def override_db() -> Any:
        yield FakeDb(
            [FakeResult(scalar_one_or_none_value=74)],
            repo=SimpleNamespace(id="repo_1"),
        )

    app.dependency_overrides[get_db] = override_db
    response = TestClient(app).get("/repos/repo_1/score-badge?style=flat-square")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "Skilgen Score" in response.text
    assert "74/100" in response.text
    assert 'rx="0"' in response.text


def test_repo_score_badge_endpoint_validates_style() -> None:
    """Invalid badge styles should fail validation instead of rendering arbitrary SVG."""
    app = FastAPI()
    app.include_router(repos.router)

    async def override_db() -> Any:
        yield FakeDb([], repo=SimpleNamespace(id="repo_1"))

    app.dependency_overrides[get_db] = override_db
    response = TestClient(app).get("/repos/repo_1/score-badge?style=rounded")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "style"


@pytest.mark.anyio
async def test_org_stats_returns_30_day_score_trend() -> None:
    """Org stats should return a 30-day chronological daily average trend."""
    today = datetime.now(UTC).date().isoformat()
    db = FakeDb(
        [
            FakeResult(scalar_value=1),
            FakeResult(scalar_value=74),
            FakeResult(scalar_list=["repo_1"]),
            FakeResult(scalar_one_or_none_value=SimpleNamespace(skill_count=9)),
            FakeResult(rows=[SimpleNamespace(date=today, avg_score=74.4)]),
        ]
    )

    payload = await orgs.get_org_stats("org_1", db=db)  # type: ignore[arg-type]

    assert payload["repo_count"] == 1
    assert payload["avg_score"] == 74
    assert payload["skill_count"] == 9
    assert len(payload["score_trend"]) == 30
    assert payload["score_trend"][-1] == {"date": today, "score": 74}
