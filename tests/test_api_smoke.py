from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from skilgen.api.server import create_server


def get_json(url: str) -> dict[str, object]:
    with urlopen(url) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


class ApiSmokeTests(unittest.TestCase):
    def test_api_endpoints_smoke(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text(
                "\n".join(
                    [
                        "Feature: API delivery",
                        "Backend API endpoint for scan",
                        "Frontend flow for dashboard",
                    ]
                ),
                encoding="utf-8",
            )
            server = create_server("127.0.0.1", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = server.server_address
                base = f"http://{host}:{port}"

                health = get_json(f"{base}/health")
                self.assertEqual(health["status"], "ok")
                self.assertEqual(health["api_version"], "1.0")
                self.assertIn("runtime", health)

                doctor = get_json(f"{base}/doctor?{urlencode({'project_root': str(root)})}")
                self.assertIn("runtime", doctor)
                self.assertIn("recommendations", doctor)
                self.assertIn("retry_attempts", doctor)
                self.assertIn("retry_base_delay_seconds", doctor)

                skills_list = get_json(f"{base}/skills?{urlencode({'project_root': str(root), 'search': 'langsmith'})}")
                self.assertTrue(skills_list["skills"])

                skills_detect = get_json(f"{base}/skills/detect?{urlencode({'project_root': str(root)})}")
                self.assertIn("detected_skills", skills_detect)

                langchain_skill = get_json(f"{base}/skills/langchain-skills?{urlencode({'project_root': str(root)})}")
                self.assertEqual(langchain_skill["skill"]["slug"], "langchain-skills")

                decision = get_json(f"{base}/decide?{urlencode({'project_root': str(root), 'requirements': str(requirements)})}")
                self.assertIn("should_refresh", decision)
                self.assertIn("prioritized_skill_paths", decision)

                fingerprint = post_json(f"{base}/fingerprint", {"project_root": str(root)})
                self.assertIn("build_tool", fingerprint)

                mapping = post_json(f"{base}/map", {"project_root": str(root)})
                self.assertIn("import_graph", mapping)

                analysis = post_json(f"{base}/analyze", {"project_root": str(root), "requirements": str(requirements)})
                self.assertIn("signals", analysis)
                self.assertIn("domain_graph", analysis)
                self.assertEqual(analysis["api_version"], "1.0")

                intent = post_json(f"{base}/intent", {"requirements": str(requirements)})
                self.assertTrue(intent["features"])

                plan = post_json(f"{base}/plan", {"requirements": str(requirements), "project_root": str(root)})
                self.assertTrue(plan["steps"])
                self.assertIn("runtime_diagnostics", plan)

                features = post_json(f"{base}/features", {"requirements": str(requirements), "project_root": str(root)})
                self.assertTrue(features["features"])
                self.assertIn("runtime_diagnostics", features)

                preview = post_json(f"{base}/preview", {"requirements": str(requirements), "project_root": str(root), "targets": ["docs"]})
                self.assertTrue(preview["planned_files"])
                self.assertFalse((root / "ANALYSIS.md").exists())

                deliver = post_json(f"{base}/deliver", {"requirements": str(requirements), "project_root": str(root)})
                self.assertTrue(deliver["generated_files"])
                self.assertIn("runtime_diagnostics", deliver)

                deliver_job = post_json(f"{base}/jobs/deliver", {"requirements": str(requirements), "project_root": str(root)})
                self.assertIn(deliver_job["status"], {"queued", "running", "completed"})
                self.assertEqual(deliver_job["job_type"], "deliver")
                self.assertIn("progress", deliver_job)

                job_id = deliver_job["job_id"]
                polled: dict[str, object] = {}
                for _ in range(80):
                    polled = get_json(f"{base}/jobs/{job_id}?{urlencode({'project_root': str(root)})}")
                    if polled["status"] in {"completed", "failed"}:
                        break
                    time.sleep(0.05)
                self.assertEqual(polled["status"], "completed")
                self.assertEqual(polled["progress"], 100)
                self.assertIn("generated_files", polled["result"])

                jobs = get_json(f"{base}/jobs?{urlencode({'project_root': str(root)})}")
                self.assertTrue(jobs["jobs"])

                source = root / "external-source"
                source.mkdir()
                (source / "README.md").write_text("demo\n", encoding="utf-8")
                import subprocess
                subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True)
                subprocess.run(["git", "-C", str(source), "config", "user.email", "tests@example.com"], text=True, capture_output=True, check=True)
                subprocess.run(["git", "-C", str(source), "config", "user.name", "Tests"], text=True, capture_output=True, check=True)
                subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
                subprocess.run(["git", "-C", str(source), "commit", "-m", "init"], text=True, capture_output=True, check=True)

                installed_skill = post_json(
                    f"{base}/skills/install",
                    {"project_root": str(root), "git_url": str(source), "name": "demo pack", "active": True},
                )
                self.assertEqual(installed_skill["installed_skill"]["slug"], "demo-pack")

                active_skills = get_json(f"{base}/skills/active?{urlencode({'project_root': str(root)})}")
                self.assertTrue(active_skills["skills"])

                lock = get_json(f"{base}/skills/lock?{urlencode({'project_root': str(root)})}")
                self.assertTrue(lock["skills"])
                exported_lock = get_json(f"{base}/skills/lock/export?{urlencode({'project_root': str(root)})}")
                self.assertIn("export_path", exported_lock)
                policy = get_json(f"{base}/skills/policy?{urlencode({'project_root': str(root)})}")
                self.assertEqual(policy["policy_mode"], "permissive")
                ranked = get_json(f"{base}/skills/rank?{urlencode({'project_root': str(root)})}")
                self.assertTrue(ranked["skills"])

                imported_root = root / "imported-project"
                imported_root.mkdir()
                imported_lock = post_json(
                    f"{base}/skills/lock/import",
                    {"project_root": str(imported_root), "input_path": exported_lock["export_path"]},
                )
                self.assertGreaterEqual(imported_lock["count"], 1)

                deactivated = post_json(f"{base}/skills/deactivate", {"project_root": str(root), "slug": "demo-pack"})
                self.assertFalse(deactivated["deactivated_skill"]["active"])
                activated = post_json(f"{base}/skills/activate", {"project_root": str(root), "slug": "demo-pack"})
                self.assertTrue(activated["activated_skill"]["active"])
                synced = post_json(f"{base}/skills/sync", {"project_root": str(root), "all": True})
                self.assertGreaterEqual(synced["count"], 1)
                self.assertIn("demo-pack", {item["slug"] for item in synced["skills"]})

                directory_source = root / ".skilgen" / "external-skills" / "sources" / "awesome-agent-skills-voltagent"
                directory_source.mkdir(parents=True)
                repo_candidate = {"repo": "example/candidate-pack", "url": str(source)}
                manifest_path = root / ".skilgen" / "external-skills" / "manifest.json"
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest_data["skills"].append(
                    {
                        "slug": "awesome-agent-skills-voltagent",
                        "name": "Awesome Agent Skills",
                        "ecosystem": "directory",
                        "publisher": "VoltAgent",
                        "category": "directory",
                        "trust_level": "directory",
                        "trust_score": 4,
                        "install_path": str(directory_source),
                        "normalized": {"repo_candidates": [repo_candidate]},
                    }
                )
                manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
                lock_path = root / ".skilgen" / "external-skills" / "lock.json"
                lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
                lock_data["skills"].append({"slug": "awesome-agent-skills-voltagent", "normalized": {"repo_candidates": [repo_candidate]}})
                lock_path.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")
                imported_candidates = post_json(
                    f"{base}/skills/import",
                    {"project_root": str(root), "slug": "awesome-agent-skills-voltagent", "limit": 1, "active": True},
                )
                self.assertEqual(imported_candidates["count"], 1)

                removed = post_json(f"{base}/skills/remove", {"project_root": str(root), "slug": "demo-pack"})
                self.assertTrue(removed["removed_skill"]["removed"])

                status = get_json(f"{base}/status?{urlencode({'project_root': str(root)})}")
                self.assertTrue(status["manifest_exists"])
                self.assertTrue(status["graph_exists"])
                self.assertTrue(status["analysis_exists"])
                self.assertTrue(status["report_exists"])
                self.assertTrue(status["traceability_exists"])
                self.assertGreaterEqual(status["skill_count"], 1)
                self.assertIn("runtime_diagnostics", status)
                self.assertIn("freshness", status)
                self.assertIn("current_run_memory", status)
                self.assertIsNotNone(status["current_run_memory"])
                self.assertIn("agent_decision", status)
                self.assertIn("installed_external_skills", status)
                self.assertIn("active_external_skills", status)
                self.assertIn("ranked_external_skills", status)
                self.assertIn("external_skill_lock", status)
                self.assertIn("external_skill_policy", status)
                self.assertIn("external_skill_recommendations", status)
                self.assertIn("pending_validations", status["current_run_memory"])
                self.assertIn("resumable_steps", status["current_run_memory"])

                report = get_json(f"{base}/report?{urlencode({'project_root': str(root)})}")
                self.assertIn("summary", report)
                self.assertIn("signal_counts", report)
                self.assertIn("data_models", report["signal_counts"])

                validate = get_json(f"{base}/validate?{urlencode({'project_root': str(root)})}")
                self.assertIn("valid", validate)
                self.assertIn("warnings", validate)
                self.assertIn("coverage", validate)
                self.assertIn("completeness_score", validate)
                self.assertIn("recommendations", validate)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
