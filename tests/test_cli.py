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
            config_path = Path(payload["config_path"])
            self.assertTrue(config_path.exists())
            config_text = config_path.read_text(encoding="utf-8")
            self.assertIn("model_provider:", config_text)
            self.assertNotIn("model_provider: openai", config_text)

    def test_init_can_scaffold_provider_specific_defaults(self) -> None:
        with TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "init",
                    "--project-root",
                    tmp,
                    "--provider",
                    "anthropic",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            config_text = Path(payload["config_path"]).read_text(encoding="utf-8")
            self.assertIn("model_provider: anthropic", config_text)
            self.assertIn("model: claude-sonnet-4-5", config_text)
            self.assertIn("api_key_env: ANTHROPIC_API_KEY", config_text)

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

    def test_skills_list_returns_curated_sources(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "skilgen.cli.main", "skills", "list"],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        slugs = {entry["slug"] for entry in payload["skills"]}
        self.assertIn("anthropic-skills", slugs)
        self.assertIn("langchain-skills", slugs)
        self.assertIn("huggingface-skills", slugs)
        self.assertIn("langsmith-skills", slugs)
        self.assertIn("awesome-agent-skills-voltagent", slugs)
        self.assertGreaterEqual(payload["count"], 10)

    def test_skills_install_can_install_custom_git_source(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source-skill-repo"
            source.mkdir()
            (source / "README.md").write_text("demo skills\n", encoding="utf-8")
            subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "tests@example.com"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Tests"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "init"], text=True, capture_output=True, check=True)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "skills",
                    "install",
                    "--git-url",
                    str(source),
                    "--name",
                    "demo skill pack",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            install_path = Path(payload["installed_skill"]["install_path"])
            self.assertTrue(install_path.exists())
            self.assertTrue((root / ".skilgen" / "external-skills" / "manifest.json").exists())

            (source / "README.md").write_text("demo skills v2\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "update"], text=True, capture_output=True, check=True)

            sync_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "skills",
                    "sync",
                    "demo-skill-pack",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            sync_payload = json.loads(sync_result.stdout)
            self.assertIn("synced_at", sync_payload["synced_skill"])

            remove_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "skills",
                    "remove",
                    "demo-skill-pack",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            remove_payload = json.loads(remove_result.stdout)
            self.assertTrue(remove_payload["removed_skill"]["removed"])
            self.assertFalse(install_path.exists())


if __name__ == "__main__":
    unittest.main()
