from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def test_init_creates_config(self) -> None:
        with TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "init", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(Path(payload["config_path"]).exists())

    def test_version_outputs_package_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "skilgen.cli.main", "--version"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("0.2.0", result.stdout)

    def test_analyze_outputs_signal_payload(self) -> None:
        with TemporaryDirectory() as tmp:
            Path(tmp, "api", "routes").mkdir(parents=True)
            Path(tmp, "api", "routes", "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "analyze", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertIn("signals", payload)
            self.assertIn("backend_routes", payload["signals"])

    def test_update_dry_run_can_scope_to_backend_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\nFrontend route\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "update",
                    "--requirements",
                    str(requirements),
                    "--project-root",
                    str(root),
                    "--target",
                    "skills",
                    "--domain",
                    "backend",
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            joined = "\n".join(payload["generated_files"])
            self.assertIn("skills/backend/SKILL.md", joined)
            self.assertNotIn("skills/frontend/SKILL.md", joined)

    def test_preview_returns_planned_files_without_writing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\nFrontend route\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "preview",
                    "--requirements",
                    str(requirements),
                    "--project-root",
                    str(root),
                    "--target",
                    "docs",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["planned_files"])
            self.assertFalse((root / "ANALYSIS.md").exists())

    def test_watch_once_runs_single_generation_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "watch",
                    "--requirements",
                    str(requirements),
                    "--project-root",
                    str(root),
                    "--once",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(len(payload["runs"]), 1)
            self.assertTrue(payload["runs"][0])

    def test_features_works_with_codebase_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "features",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["features"])

    def test_features_works_with_requirements_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\nFrontend route\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "features",
                    "--requirements",
                    str(requirements),
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["features"])

    def test_deliver_works_with_codebase_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "deliver",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["generated_files"])
            self.assertTrue((root / "FEATURES.md").exists())

    def test_deliver_works_with_requirements_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\nFrontend route\nRoadmap phase\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "deliver",
                    "--requirements",
                    str(requirements),
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["generated_files"])
            self.assertTrue((root / "FEATURES.md").exists())

    def test_doctor_outputs_runtime_diagnostics(self) -> None:
        with TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "doctor",
                    "--project-root",
                    tmp,
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertIn("runtime", payload)
            self.assertIn("recommendations", payload)
            self.assertIn("api_key_env", payload)
            self.assertIn("retry_attempts", payload)
            self.assertIn("retry_base_delay_seconds", payload)


if __name__ == "__main__":
    unittest.main()
