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
            self.assertEqual(payload["auto_update"]["update_trigger"], "auto")
            subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "autoupdate", "disable", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )

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
            subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "autoupdate", "disable", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )

    def test_version_outputs_package_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "skilgen.cli.main", "--version"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("0.4.0", result.stdout)

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

    def test_enterprise_ingest_and_connector_recommend(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "enterprise-pack"
            source.mkdir()
            (source / "README.md").write_text("# Platform Skill\n\nShared platform guidance.\n", encoding="utf-8")
            ingest = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "enterprise",
                    "ingest",
                    "--project-root",
                    str(root),
                    "--name",
                    "platform skill",
                    "--path",
                    str(source),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            ingest_payload = json.loads(ingest.stdout)
            self.assertEqual(ingest_payload["enterprise_skill"]["slug"], "platform-skill")

            (root / "ops.md").write_text("Use Jira and Confluence for delivery. Terraform runs production infra.\n", encoding="utf-8")
            connectors = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "connectors",
                    "recommend",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            connector_payload = json.loads(connectors.stdout)
            jira = connector_payload["connectors"][0]
            self.assertEqual(jira["slug"], "jira")
            self.assertTrue(jira["official_source_url"])
            self.assertEqual(jira["auth_scheme"], "oauth2")

    def test_connectors_activate_rejects_unverified_connector(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "connectors",
                    "activate",
                    "kubernetes",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("official source", result.stderr.lower())

    def test_autoupdate_status_and_disable(self) -> None:
        with TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "init", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )
            status = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "autoupdate", "status", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(status.stdout)
            self.assertEqual(payload["update_trigger"], "auto")
            self.assertTrue(payload["enabled"])
            disable = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "autoupdate", "disable", "--project-root", tmp],
                text=True,
                capture_output=True,
                check=True,
            )
            disabled_payload = json.loads(disable.stdout)
            self.assertFalse(disabled_payload["running"])

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

    def test_skills_detect_active_lock_and_activation_flow(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("Use Claude Code\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("dependencies = ['langchain']\n", encoding="utf-8")

            detected = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "detect", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(detected.stdout)
            slugs = {entry["slug"] for entry in payload["detected_skills"]}
            self.assertIn("anthropic-skills", slugs)
            self.assertIn("langchain-skills", slugs)

            source = root / "external-source"
            source.mkdir()
            (source / "README.md").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "tests@example.com"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Tests"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "init"], text=True, capture_output=True, check=True)
            revision = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], text=True, capture_output=True, check=True).stdout.strip()

            installed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "skills",
                    "install",
                    "--git-url",
                    str(source),
                    "--name",
                    "demo pack",
                    "--project-root",
                    str(root),
                    "--ref",
                    revision,
                    "--activate",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            installed_payload = json.loads(installed.stdout)
            self.assertEqual(installed_payload["installed_skill"]["requested_ref"], revision)

            active = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "active", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("demo-pack", active.stdout)

            deactivated = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "deactivate", "demo-pack", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertFalse(json.loads(deactivated.stdout)["deactivated_skill"]["active"])

            activated = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "activate", "demo-pack", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertTrue(json.loads(activated.stdout)["activated_skill"]["active"])

            locked = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "lock", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("resolved_revision", locked.stdout)
            self.assertIn("normalized", locked.stdout)

            exported = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "lock-export", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            export_payload = json.loads(exported.stdout)
            self.assertTrue(Path(export_payload["export_path"]).exists())

            imported_root = root / "imported-project"
            imported_root.mkdir()
            imported = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "skills",
                    "lock-import",
                    "--project-root",
                    str(imported_root),
                    "--input-path",
                    export_payload["export_path"],
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(imported.stdout)["count"], 1)

            policy = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "policy", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("policy_mode", policy.stdout)

            ranked = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "skills", "rank", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("priority_score", ranked.stdout)

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
