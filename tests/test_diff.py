from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

from skilgen.core.context import build_codebase_context
from skilgen.core.diff import compute_diff
from skilgen.core.freshness import save_freshness_state, snapshot_freshness_state
from skilgen.core.requirements import load_project_context


def _save_baseline(root: Path) -> None:
    context = load_project_context(root, None)
    codebase_context = build_codebase_context(root, context)
    save_freshness_state(root, snapshot_freshness_state(root, context, codebase_context.domain_graph))


class DiffTests(unittest.TestCase):
    def test_diff_without_previous_state_reports_missing_baseline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            payload = compute_diff(root)
            self.assertEqual(payload["reason"], "missing_freshness_state")
            self.assertTrue(payload["impacted_domains"])

    def test_diff_with_no_changes_reports_current(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            _save_baseline(root)
            payload = compute_diff(root)
            self.assertEqual(payload["reason"], "no_source_changes")
            self.assertEqual(payload["changed_files"], [])
            self.assertEqual(payload["changed_file_count"], 0)
            self.assertTrue(payload["current_domains"])

    def test_diff_ignores_generated_output_changes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            _save_baseline(root)
            for file_name in [
                "AGENTS.md",
                "ANALYSIS.md",
                "ARCHITECTURE.md",
                "FEATURES.md",
                "REPORT.md",
                "TRACEABILITY.md",
                "skilgen-dashboard.html",
                "skilgen.yml",
            ]:
                (root / file_name).write_text("generated update\n", encoding="utf-8")
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text("# Backend\n", encoding="utf-8")
            (root / ".skilgen" / "state").mkdir(parents=True, exist_ok=True)
            (root / ".skilgen" / "state" / "autoupdate.json").write_text("{}", encoding="utf-8")

            payload = compute_diff(root)

            self.assertEqual(payload["reason"], "no_source_changes")
            self.assertEqual(payload["changed_files"], [])

    def test_diff_detects_modified_file_and_impacted_domain(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            target = root / "api" / "routes" / "users.py"
            target.write_text("def handler():\n    return {}\n", encoding="utf-8")
            _save_baseline(root)
            target.write_text("def handler():\n    return {'users': []}\n", encoding="utf-8")
            payload = compute_diff(root)
            self.assertEqual(payload["reason"], "source_changes_detected")
            self.assertIn({"path": "api/routes/users.py", "change_type": "modified"}, payload["changed_files"])
            self.assertTrue(payload["impacted_domains"])

    def test_diff_detects_added_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            _save_baseline(root)
            (root / "api" / "routes" / "payments.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            payload = compute_diff(root)
            self.assertIn({"path": "api/routes/payments.py", "change_type": "added"}, payload["changed_files"])

    def test_diff_detects_deleted_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            target = root / "api" / "routes" / "users.py"
            target.write_text("def handler():\n    return {}\n", encoding="utf-8")
            _save_baseline(root)
            target.unlink()
            payload = compute_diff(root)
            self.assertIn({"path": "api/routes/users.py", "change_type": "deleted"}, payload["changed_files"])

    def test_current_domains_excludes_impacted_domains(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            target = root / "api" / "routes" / "users.py"
            target.write_text("def handler():\n    return {}\n", encoding="utf-8")
            _save_baseline(root)
            target.write_text("def handler():\n    return {'users': []}\n", encoding="utf-8")
            payload = compute_diff(root)
            self.assertTrue(set(payload["current_domains"]).isdisjoint(set(payload["impacted_domains"])))

    def test_diff_cli_json_flag_outputs_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "diff", "--project-root", str(root), "--json"],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertIn("reason", payload)
            self.assertIn("freshness_score", payload)

    def test_diff_cli_accepts_requirements_argument(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "README.md"
            requirements.write_text("# Repo\nbackend api\nfrontend route\n", encoding="utf-8")
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "diff",
                    "--project-root",
                    str(root),
                    "--requirements",
                    str(requirements),
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertIn("reason", payload)
            self.assertIn("git", payload)


if __name__ == "__main__":
    unittest.main()
