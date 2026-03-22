from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

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
    resume_job,
    show_skill_source,
    start_deliver_job,
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
            for _ in range(20):
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
            self.assertTrue(Path(installed["installed_skill"]["install_path"]).exists())


if __name__ == "__main__":
    unittest.main()
