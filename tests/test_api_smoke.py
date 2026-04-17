from __future__ import annotations

import io
import json
import logging
import os
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from skilgen.api.server import create_server


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    token: str | None = "test-token",
    expect_status: int = 200,
) -> tuple[int, dict[str, object], dict[str, str]]:
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request) as response:  # noqa: S310
            body = json.loads(response.read().decode("utf-8"))
            status = response.getcode()
            response_headers = dict(response.headers.items())
    except HTTPError as exc:
        status = exc.code
        body = json.loads(exc.read().decode("utf-8"))
        response_headers = dict(exc.headers.items())
    if status != expect_status:
        raise AssertionError(f"expected HTTP {expect_status} for {url}, got {status} with body {body}")
    return status, body, response_headers


def get_json(url: str, *, token: str | None = "test-token", expect_status: int = 200) -> tuple[dict[str, object], dict[str, str]]:
    _status, body, headers = request_json(url, token=token, expect_status=expect_status)
    return body, headers


def post_json(
    url: str,
    payload: dict[str, object],
    *,
    token: str | None = "test-token",
    expect_status: int = 200,
) -> tuple[dict[str, object], dict[str, str]]:
    _status, body, headers = request_json(url, method="POST", payload=payload, token=token, expect_status=expect_status)
    return body, headers


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
            env = {
                "SKILGEN_API_TOKEN": "test-token",
                "SKILGEN_ALLOWED_PROJECT_ROOTS": str(root.resolve()),
            }
            with unittest.mock.patch.dict(os.environ, env, clear=False):
                server = create_server("127.0.0.1", 0)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    host, port = server.server_address
                    base = f"http://{host}:{port}"

                    health, health_headers = get_json(f"{base}/health", token=None)
                    self.assertEqual(health["status"], "ok")
                    self.assertEqual(health["api_version"], "1.0")
                    self.assertIn("runtime", health)
                    self.assertIn("X-Request-Id", health_headers)

                    doctor, _ = get_json(f"{base}/doctor?{urlencode({'project_root': str(root)})}")
                    self.assertIn("runtime", doctor)
                    self.assertIn("recommendations", doctor)
                    self.assertIn("retry_attempts", doctor)
                    self.assertIn("retry_base_delay_seconds", doctor)

                    diff, _ = get_json(f"{base}/diff?{urlencode({'project_root': str(root), 'requirements': str(requirements)})}")
                    self.assertIn("reason", diff)
                    self.assertIn("git", diff)

                    skills_list, _ = get_json(f"{base}/skills?{urlencode({'project_root': str(root), 'search': 'langsmith'})}")
                    self.assertTrue(skills_list["skills"])

                    skills_detect, _ = get_json(f"{base}/skills/detect?{urlencode({'project_root': str(root)})}")
                    self.assertIn("detected_skills", skills_detect)

                    langchain_skill, _ = get_json(f"{base}/skills/langchain-skills?{urlencode({'project_root': str(root)})}")
                    self.assertEqual(langchain_skill["skill"]["slug"], "langchain-skills")

                    decision, _ = get_json(f"{base}/decide?{urlencode({'project_root': str(root), 'requirements': str(requirements)})}")
                    self.assertIn("should_refresh", decision)
                    self.assertIn("prioritized_skill_paths", decision)

                    fingerprint, _ = post_json(f"{base}/fingerprint", {"project_root": str(root)})
                    self.assertIn("build_tool", fingerprint)

                    mapping, _ = post_json(f"{base}/map", {"project_root": str(root)})
                    self.assertIn("import_graph", mapping)

                    analysis, _ = post_json(f"{base}/analyze", {"project_root": str(root), "requirements": str(requirements)})
                    self.assertIn("signals", analysis)
                    self.assertIn("evidence_graph", analysis)
                    self.assertIn("domain_graph", analysis)
                    self.assertEqual(analysis["api_version"], "1.0")

                    architecture, _ = get_json(f"{base}/architecture?{urlencode({'project_root': str(root), 'requirements': str(requirements)})}")
                    self.assertIn("architecture", architecture)
                    self.assertIn("evidence_graph", architecture)
                    self.assertIn("graph_export", architecture)
                    self.assertTrue(architecture["architecture"]["domains"])

                    dashboard, _ = get_json(f"{base}/dashboard?{urlencode({'project_root': str(root), 'requirements': str(requirements)})}")
                    self.assertIn("html", dashboard)
                    self.assertIn("score", dashboard)
                    self.assertIn("graph_export", dashboard)

                    intent, _ = post_json(f"{base}/intent", {"requirements": str(requirements)})
                    self.assertTrue(intent["features"])

                    plan, _ = post_json(f"{base}/plan", {"requirements": str(requirements), "project_root": str(root)})
                    self.assertTrue(plan["steps"])
                    self.assertIn("runtime_diagnostics", plan)

                    features, _ = post_json(f"{base}/features", {"requirements": str(requirements), "project_root": str(root)})
                    self.assertTrue(features["features"])
                    self.assertIn("runtime_diagnostics", features)

                    preview, _ = post_json(f"{base}/preview", {"requirements": str(requirements), "project_root": str(root), "targets": ["docs"]})
                    self.assertTrue(preview["planned_files"])
                    self.assertFalse((root / "ANALYSIS.md").exists())

                    deliver, _ = post_json(f"{base}/deliver", {"requirements": str(requirements), "project_root": str(root)})
                    self.assertTrue(deliver["generated_files"])
                    self.assertIn("runtime_diagnostics", deliver)

                    score, _ = get_json(f"{base}/score?{urlencode({'project_root': str(root)})}")
                    self.assertIn("score", score)
                    self.assertIn("subscores", score)
                    score_history, _ = get_json(f"{base}/score?{urlencode({'project_root': str(root), 'history': '1'})}")
                    self.assertIn("history", score_history)

                    analytics, _ = get_json(f"{base}/analytics?{urlencode({'project_root': str(root)})}")
                    self.assertIn("top_skills", analytics)

                    request = Request(
                        f"{base}/badge.svg?{urlencode({'project_root': str(root)})}",
                        headers={"Authorization": "Bearer test-token"},
                    )
                    with urlopen(request) as response:  # noqa: S310
                        badge = response.read().decode("utf-8")
                    self.assertIn("<svg", badge)

                    deliver_job, _ = post_json(f"{base}/jobs/deliver", {"requirements": str(requirements), "project_root": str(root)}, expect_status=202)
                    self.assertIn(deliver_job["status"], {"queued", "running", "completed"})
                    self.assertEqual(deliver_job["job_type"], "deliver")
                    self.assertIn("progress", deliver_job)

                    job_id = deliver_job["job_id"]
                    polled: dict[str, object] = {}
                    deadline = time.monotonic() + 180.0
                    while time.monotonic() < deadline:
                        polled, _ = get_json(f"{base}/jobs/{job_id}?{urlencode({'project_root': str(root)})}")
                        if polled["status"] in {"completed", "failed"}:
                            break
                        time.sleep(0.1)
                    self.assertEqual(polled["status"], "completed")
                    self.assertEqual(polled["progress"], 100)
                    self.assertIn("generated_files", polled["result"])

                    jobs, _ = get_json(f"{base}/jobs?{urlencode({'project_root': str(root)})}")
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

                    installed_skill, _ = post_json(
                        f"{base}/skills/install",
                        {"project_root": str(root), "git_url": str(source), "name": "demo pack", "active": True},
                    )
                    self.assertEqual(installed_skill["installed_skill"]["slug"], "demo-pack")

                    active_skills, _ = get_json(f"{base}/skills/active?{urlencode({'project_root': str(root)})}")
                    self.assertTrue(active_skills["skills"])

                    lock, _ = get_json(f"{base}/skills/lock?{urlencode({'project_root': str(root)})}")
                    self.assertTrue(lock["skills"])
                    exported_lock, _ = get_json(f"{base}/skills/lock/export?{urlencode({'project_root': str(root)})}")
                    self.assertIn("export_path", exported_lock)
                    policy, _ = get_json(f"{base}/skills/policy?{urlencode({'project_root': str(root)})}")
                    self.assertEqual(policy["policy_mode"], "permissive")
                    ranked, _ = get_json(f"{base}/skills/rank?{urlencode({'project_root': str(root)})}")
                    self.assertTrue(ranked["skills"])

                    enterprise_source = root / "enterprise-source"
                    enterprise_source.mkdir()
                    (enterprise_source / "README.md").write_text("# Enterprise Skill\n\nInternal engineering guidance.\n", encoding="utf-8")
                    enterprise_ingest, _ = post_json(
                        f"{base}/enterprise/ingest",
                        {"project_root": str(root), "name": "enterprise skill", "path": str(enterprise_source)},
                    )
                    self.assertEqual(enterprise_ingest["enterprise_skill"]["slug"], "enterprise-skill")
                    enterprise_list, _ = get_json(f"{base}/enterprise?{urlencode({'project_root': str(root)})}")
                    self.assertTrue(enterprise_list["skills"])

                    runbook = root / "incident-runbook.md"
                    runbook.write_text("# Incident\n\nUse Jira, Slack, and Datadog during incidents.\n", encoding="utf-8")
                    enterprise_generated, _ = post_json(
                        f"{base}/enterprise/generate",
                        {"project_root": str(root), "name": "incident runbook", "source_paths": [str(runbook)], "kind": "runbook"},
                    )
                    self.assertEqual(enterprise_generated["enterprise_skill"]["slug"], "incident-runbook")

                    connectors, _ = get_json(f"{base}/connectors?{urlencode({'search': 'jira'})}")
                    self.assertTrue(connectors["connectors"])
                    self.assertTrue(connectors["connectors"][0]["official_source_url"])
                    self.assertEqual(connectors["connectors"][0]["auth_scheme"], "oauth2")
                    connector_recommend, _ = get_json(f"{base}/connectors/recommend?{urlencode({'project_root': str(root)})}")
                    self.assertTrue(connector_recommend["connectors"])
                    connector_activated, _ = post_json(f"{base}/connectors/activate", {"project_root": str(root), "slug": "jira"})
                    self.assertTrue(connector_activated["connector"]["active"])
                    self.assertEqual(connector_activated["connector"]["authorization"]["status"], "pending_oauth")
                    connector_active, _ = get_json(f"{base}/connectors/active?{urlencode({'project_root': str(root)})}")
                    self.assertTrue(connector_active["connectors"])
                    connector_deactivated, _ = post_json(f"{base}/connectors/deactivate", {"project_root": str(root), "slug": "jira"})
                    self.assertFalse(connector_deactivated["connector"]["active"])

                    imported_root = root / "imported-project"
                    imported_root.mkdir()
                    imported_lock, _ = post_json(
                        f"{base}/skills/lock/import",
                        {"project_root": str(imported_root), "input_path": exported_lock["export_path"]},
                    )
                    self.assertGreaterEqual(imported_lock["count"], 1)

                    deactivated, _ = post_json(f"{base}/skills/deactivate", {"project_root": str(root), "slug": "demo-pack"})
                    self.assertFalse(deactivated["deactivated_skill"]["active"])
                    activated, _ = post_json(f"{base}/skills/activate", {"project_root": str(root), "slug": "demo-pack"})
                    self.assertTrue(activated["activated_skill"]["active"])
                    synced, _ = post_json(f"{base}/skills/sync", {"project_root": str(root), "all": True})
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
                    imported_candidates, _ = post_json(
                        f"{base}/skills/import",
                        {"project_root": str(root), "slug": "awesome-agent-skills-voltagent", "limit": 1, "active": True},
                    )
                    self.assertEqual(imported_candidates["count"], 1)

                    removed, _ = post_json(f"{base}/skills/remove", {"project_root": str(root), "slug": "demo-pack"})
                    self.assertTrue(removed["removed_skill"]["removed"])

                    status, _ = get_json(f"{base}/status?{urlencode({'project_root': str(root)})}")
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
                    self.assertIn("skilgen_score", status)
                    self.assertIn("pending_validations", status["current_run_memory"])
                    self.assertIn("resumable_steps", status["current_run_memory"])

                    report, _ = get_json(f"{base}/report?{urlencode({'project_root': str(root)})}")
                    self.assertIn("summary", report)
                    self.assertIn("signal_counts", report)
                    self.assertIn("data_models", report["signal_counts"])

                    validate, _ = get_json(f"{base}/validate?{urlencode({'project_root': str(root)})}")
                    self.assertIn("valid", validate)
                    self.assertIn("warnings", validate)
                    self.assertIn("coverage", validate)
                    self.assertIn("completeness_score", validate)
                    self.assertIn("recommendations", validate)
                    self.assertIn("skilgen_score", validate)
                finally:
                    server.shutdown()
                    server.server_close()

    def test_api_auth_limits_and_metrics(self) -> None:
        with TemporaryDirectory() as tmp, TemporaryDirectory() as disallowed_tmp:
            root = Path(tmp)
            disallowed_root = Path(disallowed_tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoint\n", encoding="utf-8")
            env = {
                "SKILGEN_API_TOKEN": "test-token",
                "SKILGEN_ALLOWED_PROJECT_ROOTS": str(root.resolve()),
                "SKILGEN_API_MAX_BODY_BYTES": "64",
            }
            with unittest.mock.patch.dict(os.environ, env, clear=False):
                log_buffer = io.StringIO()
                handler = logging.StreamHandler(log_buffer)
                handler.setFormatter(logging.Formatter("%(message)s %(request_id)s"))
                server = create_server("127.0.0.1", 0)
                logger = logging.getLogger("skilgen.api")
                original_handlers = list(logger.handlers)
                logger.addHandler(handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    host, port = server.server_address
                    base = f"http://{host}:{port}"

                    unauthorized, _ = get_json(
                        f"{base}/doctor?{urlencode({'project_root': str(root)})}",
                        token=None,
                        expect_status=401,
                    )
                    self.assertEqual(unauthorized["error"], "unauthorized")

                    invalid, _ = get_json(
                        f"{base}/doctor?{urlencode({'project_root': str(root)})}",
                        token="wrong-token",
                        expect_status=401,
                    )
                    self.assertEqual(invalid["error"], "unauthorized")

                    forbidden, _ = get_json(
                        f"{base}/doctor?{urlencode({'project_root': str(disallowed_root)})}",
                        expect_status=403,
                    )
                    self.assertEqual(forbidden["error"], "forbidden")

                    oversized, _ = post_json(
                        f"{base}/deliver",
                        {"project_root": str(root), "requirements": "x" * 2048},
                        expect_status=413,
                    )
                    self.assertEqual(oversized["error"], "payload_too_large")

                    doctor, doctor_headers = get_json(f"{base}/doctor?{urlencode({'project_root': str(root)})}")
                    self.assertIn("runtime", doctor)
                    self.assertIn("X-Request-Id", doctor_headers)

                    metrics_request = Request(
                        f"{base}/metrics",
                        headers={"Authorization": "Bearer test-token"},
                    )
                    with urlopen(metrics_request) as response:  # noqa: S310
                        metrics = response.read().decode("utf-8")
                    self.assertIn("skilgen_http_requests_total", metrics)
                    self.assertIn('skilgen_http_requests_by_status_total{status="200"}', metrics)
                    self.assertIn('skilgen_http_requests_by_status_total{status="401"}', metrics)

                    handler.flush()
                    access_logs = log_buffer.getvalue()
                    self.assertIn("request_complete", access_logs)
                    self.assertIn(doctor_headers["X-Request-Id"], access_logs)
                finally:
                    server.shutdown()
                    server.server_close()
                    logger.handlers = original_handlers


if __name__ == "__main__":
    unittest.main()
