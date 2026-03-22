from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.external_skills import detect_external_skill_sources, ensure_external_skills_for_project
from skilgen.sdk import (
    analyze_project,
    cancel_job,
    decide_project,
    deliver_project,
    get_job_status,
    init_project,
    install_skill_source,
    list_project_jobs,
    list_skill_sources,
    project_report,
    project_status,
    preview_project,
    remove_skill_source,
    resume_job,
    show_skill_source,
    start_deliver_job,
    sync_skill_source,
    update_project,
    validate_project_outputs,
    watch_project,
)
import time
import subprocess


class SdkTests(unittest.TestCase):
    def test_sdk_end_to_end_flow(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            requirements.write_text("Backend endpoint\nFrontend route\n", encoding="utf-8")

            config_path = init_project(root)
            self.assertTrue(config_path.exists())

            analysis = analyze_project(root, requirements)
            self.assertIn("signals", analysis)
            self.assertEqual(analysis["api_version"], "1.0")

            decision = decide_project(root, requirements)
            self.assertIn("should_refresh", decision)
            self.assertTrue(decision["prioritized_skill_paths"])

            preview = preview_project(requirements, root, targets=("docs",))
            self.assertTrue(preview["planned_files"])
            self.assertFalse((root / "ANALYSIS.md").exists())

            generated = deliver_project(requirements, root, targets=("skills",), domains=("backend",))
            self.assertTrue(generated)

            dry_run = update_project(requirements, root, targets=("docs",), dry_run=True)
            self.assertTrue(dry_run)
            self.assertFalse((root / "ANALYSIS.md").exists())

            watch_runs = watch_project(requirements, root, once=True)
            self.assertEqual(len(watch_runs), 1)

            job = start_deliver_job(requirements, root)
            self.assertEqual(job["job_type"], "deliver")
            self.assertIn("progress", job)
            job_id = job["job_id"]
            current = {}
            for _ in range(80):
                current = get_job_status(job_id, root)
                if current["status"] in {"completed", "failed"}:
                    break
                time.sleep(0.05)
            self.assertEqual(current["status"], "completed")
            self.assertTrue(list_project_jobs(root)["jobs"])

            status = project_status(root)
            self.assertIn("skill_count", status)
            self.assertTrue(status["traceability_exists"])
            self.assertIn("current_run_memory", status)
            self.assertIsNotNone(status["current_run_memory"])
            self.assertIn("agent_decision", status)
            self.assertIn("pending_validations", status["current_run_memory"])
            self.assertIn("resumable_steps", status["current_run_memory"])

            report = project_report(root)
            self.assertIn("summary", report)
            self.assertIn("data_models", report["signal_counts"])

            validation = validate_project_outputs(root)
            self.assertIn("valid", validation)
            self.assertIn("warnings", validation)
            self.assertIn("completeness_score", validation)

            cancelled = cancel_job(job_id, root)
            self.assertIn(cancelled["status"], {"completed", "cancelled"})
            resumed = resume_job(job_id, root)
            self.assertIn(resumed.get("error", "ok"), {"resume_not_allowed", "ok"})

    def test_sdk_external_skills_catalog_and_install(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = list_skill_sources(root)
            self.assertTrue(catalog["skills"])
            self.assertTrue(any(entry["slug"] == "anthropic-skills" for entry in catalog["skills"]))
            self.assertTrue(any(entry["slug"] == "langsmith-skills" for entry in catalog["skills"]))

            details = show_skill_source("langchain-skills", root)
            self.assertEqual(details["skill"]["ecosystem"], "langchain")

            source = root / "external-source"
            source.mkdir()
            (source / "README.md").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "tests@example.com"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Tests"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "init"], text=True, capture_output=True, check=True)

            installed = install_skill_source(root, git_url=str(source), name="demo pack")
            install_path = Path(installed["installed_skill"]["install_path"])
            self.assertTrue(install_path.exists())

            (source / "README.md").write_text("demo v2\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "update"], text=True, capture_output=True, check=True)

            synced = sync_skill_source("demo-pack", root)
            self.assertIn("synced_at", synced["synced_skill"])

            removed = remove_skill_source("demo-pack", root)
            self.assertTrue(removed["removed_skill"]["removed"])
            self.assertFalse(install_path.exists())

    def test_detect_external_skill_sources_finds_supported_ecosystems(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "CLAUDE.md").write_text("Claude Code instructions\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "dependencies = ['langchain', 'langsmith', 'transformers', 'crewai']\n",
                encoding="utf-8",
            )
            (root / ".github").mkdir()
            (root / ".github" / "copilot-instructions.md").write_text("Use Copilot\n", encoding="utf-8")
            (root / "workflow-n8n.json").write_text('{"name":"n8n workflow"}', encoding="utf-8")

            detected = detect_external_skill_sources(root)
            slugs = {entry["slug"] for entry in detected["detected_skills"]}
            manual = {entry["slug"] for entry in detected["manual_recommendations"]}

            self.assertIn("anthropic-skills", slugs)
            self.assertIn("langchain-skills", slugs)
            self.assertIn("langsmith-skills", slugs)
            self.assertIn("huggingface-skills", slugs)
            self.assertIn("awesome-copilot", slugs)
            self.assertIn("n8n-mcp-patterns", slugs)
            self.assertIn("ai-research-skills", slugs)
            self.assertIn("skills-benchmarks", manual)

    def test_ensure_external_skills_installs_detected_sources_once(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "CLAUDE.md").write_text("Claude Code instructions\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("dependencies = ['langchain']\n", encoding="utf-8")

            def fake_install(**kwargs: object) -> dict[str, object]:
                project_root = Path(str(kwargs["project_root"]))
                slug = str(kwargs["slug"])
                install_path = project_root / ".skilgen" / "external-skills" / "sources" / slug
                install_path.mkdir(parents=True, exist_ok=True)
                metadata = {
                    "slug": slug,
                    "ecosystem": slug.split("-")[0],
                    "install_path": str(install_path),
                    "install_mode": kwargs.get("install_mode", "manual"),
                    "detection_reasons": kwargs.get("detection_reasons", []),
                }
                manifest_path = project_root / ".skilgen" / "external-skills" / "manifest.json"
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                existing = []
                if manifest_path.exists():
                    import json
                    existing = json.loads(manifest_path.read_text(encoding="utf-8")).get("skills", [])
                manifest_path.write_text(__import__("json").dumps({"skills": [*existing, metadata]}, indent=2), encoding="utf-8")
                return metadata

            with patch("skilgen.external_skills.install_external_skill", side_effect=fake_install) as install_mock:
                first = ensure_external_skills_for_project(root)
                second = ensure_external_skills_for_project(root)

            self.assertTrue(first["newly_installed"])
            self.assertTrue(second["already_installed"])
            self.assertEqual(install_mock.call_count, 2)
            slugs = {call.kwargs["slug"] for call in install_mock.call_args_list}
            self.assertEqual(slugs, {"anthropic-skills", "langchain-skills"})


if __name__ == "__main__":
    unittest.main()
