from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.external_skills import (
    ExternalSkillSource,
    _extract_github_repo_candidates,
    _normalize_external_skill_install,
    detect_external_skill_sources,
    ensure_external_skills_for_project,
)
from skilgen.sdk import (
    activate_skill_source,
    analyze_project,
    cancel_job,
    deactivate_skill_source,
    detect_skill_sources,
    decide_project,
    deliver_project,
    get_job_status,
    init_project,
    install_skill_source,
    list_active_skill_sources,
    list_project_jobs,
    list_skill_sources,
    rank_skill_sources,
    project_report,
    project_status,
    preview_project,
    remove_skill_source,
    resume_job,
    skill_source_policy,
    show_skill_source,
    skill_source_lock,
    start_deliver_job,
    sync_all_skill_sources,
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
            (source / "README.md").write_text(
                "# Demo Pack\n\nThis is a reusable demo skill pack.\n",
                encoding="utf-8",
            )
            (source / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (source / "skills").mkdir()
            (source / "skills" / "demo-pack").mkdir(parents=True)
            (source / "skills" / "demo-pack" / "SKILL.md").write_text("# Demo Skill\n", encoding="utf-8")
            subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "tests@example.com"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Tests"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "init"], text=True, capture_output=True, check=True)

            installed = install_skill_source(root, git_url=str(source), name="demo pack")
            install_path = Path(installed["installed_skill"]["install_path"])
            self.assertTrue(install_path.exists())

            (source / "README.md").write_text(
                "# Demo Pack\n\nThis is the updated demo skill pack.\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "update"], text=True, capture_output=True, check=True)

            synced = sync_skill_source("demo-pack", root)
            self.assertIn("synced_at", synced["synced_skill"])

            activated = activate_skill_source("demo-pack", root)
            self.assertTrue(activated["activated_skill"]["active"])
            active_sources = list_active_skill_sources(root)
            self.assertEqual(active_sources["skills"][0]["slug"], "demo-pack")
            locked = skill_source_lock(root)
            self.assertEqual(locked["skills"][0]["slug"], "demo-pack")
            self.assertIn("normalized", locked["skills"][0])
            self.assertIn("trust_score", locked["skills"][0])
            self.assertEqual(locked["skills"][0]["normalized"]["license"]["summary"], "MIT License")
            self.assertEqual(locked["skills"][0]["normalized"]["readme"]["title"], "Demo Pack")
            self.assertTrue(locked["skills"][0]["normalized"]["groups"])
            ranked = rank_skill_sources(root)
            self.assertEqual(ranked["skills"][0]["slug"], "demo-pack")
            policy = skill_source_policy(root)
            self.assertEqual(policy["policy_mode"], "permissive")

            deactivated = deactivate_skill_source("demo-pack", root)
            self.assertFalse(deactivated["deactivated_skill"]["active"])

            sync_all = sync_all_skill_sources(root)
            self.assertEqual(sync_all["count"], 1)

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

    def test_review_required_policy_auto_installs_without_activation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "skilgen.yml").write_text(
                "\n".join(
                    [
                        "external_skills_policy_mode: review_required",
                        "external_skills_auto_activate: true",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text("Claude Code instructions\n", encoding="utf-8")

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
                    "active": kwargs.get("active"),
                    "detection_reasons": kwargs.get("detection_reasons", []),
                }
                manifest_path = project_root / ".skilgen" / "external-skills" / "manifest.json"
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                manifest_path.write_text(__import__("json").dumps({"skills": [metadata]}, indent=2), encoding="utf-8")
                return metadata

            with patch("skilgen.external_skills.install_external_skill", side_effect=fake_install) as install_mock:
                result = ensure_external_skills_for_project(root)

            self.assertTrue(result["newly_installed"])
            self.assertFalse(result["newly_installed"][0]["active"])
            self.assertFalse(install_mock.call_args.kwargs["active"])

    def test_official_only_policy_blocks_community_auto_installs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "skilgen.yml").write_text(
                "\n".join(
                    [
                        "external_skills_policy_mode: official_only",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "workflow-n8n.json").write_text('{"name":"n8n workflow"}', encoding="utf-8")

            result = ensure_external_skills_for_project(root)
            blocked_slugs = {entry["slug"] for entry in result["blocked"]}
            self.assertIn("n8n-mcp-patterns", blocked_slugs)

    def test_detect_skill_sources_sdk_wrapper(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "CLAUDE.md").write_text("Claude Code instructions\n", encoding="utf-8")
            detected = detect_skill_sources(root)
            self.assertTrue(detected["detected_skills"])

    def test_directory_candidates_extract_downstream_repos_from_readme(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "README.md").write_text(
                "\n".join(
                    [
                        "# Awesome Agent Skills",
                        "- https://github.com/example/alpha-skills",
                        "- https://github.com/example/beta-skills",
                    ]
                ),
                encoding="utf-8",
            )
            candidates = _extract_github_repo_candidates(root)
            repos = {entry["repo"] for entry in candidates}
            self.assertIn("example/alpha-skills", repos)
            self.assertIn("example/beta-skills", repos)

    def test_native_normalization_extracts_anthropic_skill_families(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            install = root / "anthropic-pack"
            (install / "skills" / "docs").mkdir(parents=True, exist_ok=True)
            (install / "skills" / "pdf").mkdir(parents=True, exist_ok=True)
            (install / "templates").mkdir(parents=True, exist_ok=True)
            (install / "skills" / "docs" / "SKILL.md").write_text("# Docs Skill\n", encoding="utf-8")
            (install / "skills" / "pdf" / "SKILL.md").write_text("# Pdf Skill\n", encoding="utf-8")
            (install / "templates" / "SKILL_TEMPLATE.md").write_text("# Template\n", encoding="utf-8")
            source = ExternalSkillSource(
                slug="anthropic-skills",
                name="Anthropic Skills",
                ecosystem="anthropic",
                publisher="Anthropic",
                description="Official Anthropic skills collection.",
                repository_url="https://github.com/anthropics/skills.git",
                source_path=None,
                docs_url="https://github.com/anthropics/skills/tree/main/skills",
            )
            normalized = _normalize_external_skill_install(root, source=source, install_path=install)
            families = {item["name"] for item in normalized["native_view"]["skill_families"]}
            self.assertIn("docs", families)
            self.assertIn("pdf", families)
            self.assertEqual(normalized["native_view"]["template_count"], 1)

    def test_native_normalization_extracts_langchain_families(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            install = root / "langchain-pack"
            (install / "langgraph").mkdir(parents=True, exist_ok=True)
            (install / "deep-agents").mkdir(parents=True, exist_ok=True)
            (install / "langsmith").mkdir(parents=True, exist_ok=True)
            (install / "rag").mkdir(parents=True, exist_ok=True)
            (install / "langgraph" / "README.md").write_text("# LangGraph\n", encoding="utf-8")
            (install / "deep-agents" / "README.md").write_text("# Deep Agents\n", encoding="utf-8")
            (install / "langsmith" / "README.md").write_text("# LangSmith\n", encoding="utf-8")
            (install / "rag" / "README.md").write_text("# RAG\n", encoding="utf-8")
            source = ExternalSkillSource(
                slug="langchain-skills",
                name="LangChain Skills",
                ecosystem="langchain",
                publisher="LangChain AI",
                description="Official LangChain skills.",
                repository_url="https://github.com/langchain-ai/langchain-skills.git",
                source_path=None,
                docs_url="https://github.com/langchain-ai/langchain-skills",
            )
            normalized = _normalize_external_skill_install(root, source=source, install_path=install)
            families = {item["name"] for item in normalized["native_view"]["families"]}
            self.assertIn("langgraph", families)
            self.assertIn("deep-agents", families)
            self.assertIn("langsmith", families)
            self.assertIn("rag", families)

    def test_native_normalization_extracts_huggingface_task_families(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            install = root / "hf-pack"
            (install / "datasets").mkdir(parents=True, exist_ok=True)
            (install / "trainer").mkdir(parents=True, exist_ok=True)
            (install / "evaluation").mkdir(parents=True, exist_ok=True)
            (install / "hub").mkdir(parents=True, exist_ok=True)
            (install / "datasets" / "README.md").write_text("# Datasets\n", encoding="utf-8")
            (install / "trainer" / "README.md").write_text("# Trainer\n", encoding="utf-8")
            (install / "evaluation" / "README.md").write_text("# Evaluation\n", encoding="utf-8")
            (install / "hub" / "README.md").write_text("# Hub\n", encoding="utf-8")
            source = ExternalSkillSource(
                slug="huggingface-skills",
                name="Hugging Face Skills",
                ecosystem="huggingface",
                publisher="Hugging Face",
                description="Official Hugging Face skills.",
                repository_url="https://github.com/huggingface/skills.git",
                source_path=None,
                docs_url="https://github.com/huggingface/skills",
            )
            normalized = _normalize_external_skill_install(root, source=source, install_path=install)
            families = {item["name"] for item in normalized["native_view"]["task_families"]}
            self.assertIn("datasets", families)
            self.assertIn("training", families)
            self.assertIn("evaluation", families)
            self.assertIn("hub", families)

    def test_native_normalization_extracts_directory_repo_candidates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            install = root / "directory-pack"
            install.mkdir(parents=True, exist_ok=True)
            (install / "README.md").write_text(
                "\n".join(
                    [
                        "# Awesome Agent Skills",
                        "This directory links many skills.",
                        "- https://github.com/example/alpha-skills",
                        "- https://github.com/example/beta-skills",
                    ]
                ),
                encoding="utf-8",
            )
            source = ExternalSkillSource(
                slug="awesome-agent-skills-voltagent",
                name="Awesome Agent Skills",
                ecosystem="directory",
                publisher="VoltAgent",
                description="Directory of skills.",
                repository_url="https://github.com/VoltAgent/awesome-agent-skills.git",
                source_path=None,
                docs_url="https://github.com/VoltAgent/awesome-agent-skills",
                category="directory",
                trust_level="directory",
            )
            normalized = _normalize_external_skill_install(root, source=source, install_path=install)
            self.assertEqual(normalized["native_view"]["repo_candidate_count"], 2)
            repos = {item["repo"] for item in normalized["native_view"]["top_repo_candidates"]}
            self.assertIn("example/alpha-skills", repos)
            self.assertIn("example/beta-skills", repos)


if __name__ == "__main__":
    unittest.main()
