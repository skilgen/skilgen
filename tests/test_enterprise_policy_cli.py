from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory


def _run_cli(args: list[str], project_root: Path) -> subprocess.CompletedProcess[str]:
    """Run the Skilgen CLI against a temporary project root."""
    return subprocess.run(
        [sys.executable, "-m", "skilgen.cli.main", *args, "--project-root", str(project_root)],
        text=True,
        capture_output=True,
        check=False,
    )


def _write_policy(root: Path, *, required_domains: list[str] | None = None, max_stale_days: int = 30) -> None:
    """Write a valid policy tuned for focused CLI tests."""
    (root / ".skilgen").mkdir(parents=True, exist_ok=True)
    domains = "\n".join(f"  - {domain}" for domain in required_domains or [])
    blocked = "\n".join(f"  - {license_id}" for license_id in ["AGPL-3.0", "GPL-3.0"])
    required_domains_yaml = "required_domains:" if required_domains else "required_domains: []"
    (root / ".skilgen" / "policy.yml").write_text(
        "\n".join(
            [
                "min_score: 0",
                required_domains_yaml,
                *([domains] if domains else []),
                f"max_stale_days: {max_stale_days}",
                "blocked_licenses:",
                blocked,
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_skill(root: Path, domain: str, *, days_old: int = 0) -> None:
    """Create a generated skill with a configurable last_updated date."""
    skill_dir = root / "skills" / domain
    skill_dir.mkdir(parents=True, exist_ok=True)
    last_updated = (datetime.now(UTC).date() - timedelta(days=days_old)).isoformat()
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {domain}",
                f"domain: {domain}",
                f"last_updated: {last_updated}",
                "---",
                "",
                f"# {domain.title()}",
                "",
                "## Check These Paths First",
                "- {{project_root}}/src/app.py",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _minimal_source(root: Path) -> None:
    """Create a tiny source file so score and dependency scans have a project."""
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("def handler():\n    return {}\n", encoding="utf-8")


def test_enterprise_policy_init_creates_default_policy() -> None:
    """enterprise policy init should write the default policy.yml contract."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        result = _run_cli(["enterprise", "policy", "init"], root)
        policy_path = root / ".skilgen" / "policy.yml"

        assert result.returncode == 0
        assert json.loads(result.stdout)["policy_path"] == str(policy_path.resolve())
        content = policy_path.read_text(encoding="utf-8")
        assert "min_score: 60" in content
        assert "required_domains: []" in content
        assert "max_stale_days: 30" in content
        assert "AGPL-3.0" in content
        assert "GPL-3.0" in content


def test_enterprise_policy_validate_accepts_and_rejects_policy_files() -> None:
    """enterprise policy validate should catch malformed policy fields."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_policy(root)

        valid = _run_cli(["enterprise", "policy", "validate"], root)
        assert valid.returncode == 0
        assert "Enterprise policy is valid" in valid.stdout

        (root / ".skilgen" / "policy.yml").write_text("min_score: high\n", encoding="utf-8")
        invalid = _run_cli(["enterprise", "policy", "validate"], root)
        assert invalid.returncode == 1
        assert "`min_score` must be an integer" in invalid.stdout


def test_enterprise_policy_check_passes_when_project_satisfies_policy() -> None:
    """enterprise policy check should print pass markers and exit zero."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _minimal_source(root)
        _write_skill(root, "backend")
        _write_policy(root, required_domains=["backend"])

        result = _run_cli(["enterprise", "policy", "check"], root)

        assert result.returncode == 0
        assert "✓ score threshold" in result.stdout
        assert "✓ required domains" in result.stdout
        assert "✓ skill freshness" in result.stdout
        assert "✓ license compliance" in result.stdout


def test_enterprise_policy_check_fails_for_missing_domain_and_stale_skill() -> None:
    """enterprise policy check should exit one for concrete policy violations."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _minimal_source(root)
        _write_skill(root, "backend", days_old=45)
        _write_policy(root, required_domains=["backend", "frontend"], max_stale_days=30)

        result = _run_cli(["enterprise", "policy", "check"], root)

        assert result.returncode == 1
        assert "✗ required domains" in result.stdout
        assert "Missing domains: frontend" in result.stdout
        assert "✗ skill freshness" in result.stdout
        assert "skills/backend/SKILL.md" in result.stdout


def test_enterprise_report_json_contains_compliance_shape() -> None:
    """enterprise report --json should expose the compliance report contract."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _minimal_source(root)
        _write_skill(root, "backend")
        _write_policy(root, required_domains=["backend"])

        result = _run_cli(["enterprise", "report", "--json"], root)
        payload = json.loads(result.stdout)

        assert result.returncode == 0
        assert set(payload) >= {
            "timestamp",
            "score",
            "policy_violations",
            "stale_skills",
            "missing_domains",
            "dependency_risks",
            "overall_status",
        }
        assert payload["missing_domains"] == []
        assert payload["overall_status"] == "pass"
