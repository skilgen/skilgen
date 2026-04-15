from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.core.models import ArchitectureBlueprint, ArchitectureDomain, SkillMaterializationPlan
from skilgen.core.score import compute_skillgen_score
from skilgen.delivery import run_delivery, watch_delivery


class DeliveryTests(unittest.TestCase):
    def test_run_delivery_works_with_requirements_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoints\nFrontend routes\nRoadmap phases\n", encoding="utf-8")

            generated = run_delivery(requirements, root)

            self.assertTrue((root / "ANALYSIS.md").exists())
            self.assertTrue((root / "ARCHITECTURE.md").exists())
            self.assertTrue((root / "skilgen-dashboard.html").exists())
            self.assertTrue((root / "FEATURES.md").exists())
            self.assertTrue((root / "skills" / "MANIFEST.md").exists())
            self.assertTrue((root / "skills" / "requirements" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "roadmap" / "SKILL.md").exists())
            self.assertGreaterEqual(len(generated), 4)

    def test_run_delivery_generates_docs_and_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            requirements = root / "requirements.md"
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "services").mkdir(parents=True)
            (root / "services" / "users_service.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "models").mkdir(parents=True)
            (root / "models" / "users_model.py").write_text("class User: pass\n", encoding="utf-8")
            (root / "src" / "routes").mkdir(parents=True)
            (root / "src" / "routes" / "dashboard.tsx").write_text("export default function Dashboard() { return null; }\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")
            (root / "src" / "theme").mkdir(parents=True)
            (root / "src" / "theme" / "tokens.ts").write_text("export const tokens = {};\n", encoding="utf-8")
            requirements.write_text("Backend endpoints\nFrontend routes\n", encoding="utf-8")

            generated = run_delivery(requirements, root)

            self.assertTrue((root / "ANALYSIS.md").exists())
            self.assertTrue((root / "ARCHITECTURE.md").exists())
            self.assertTrue((root / "FEATURES.md").exists())
            self.assertTrue((root / "REPORT.md").exists())
            self.assertTrue((root / "TRACEABILITY.md").exists())
            self.assertTrue((root / "skilgen-dashboard.html").exists())
            self.assertTrue((root / "skills" / "MANIFEST.md").exists())
            self.assertTrue((root / "skills" / "GRAPH.md").exists())
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertTrue((root / "skills" / "backend" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "backend" / "routes" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "backend" / "services" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "backend" / "data" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "backend" / "SUMMARY.md").exists())
            self.assertTrue((root / "skills" / "frontend" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "frontend" / "routes" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "frontend" / "design-system" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "frontend" / "SUMMARY.md").exists())
            self.assertTrue((root / "skills" / "frontend" / "components" / "SUMMARY.md").exists())
            self.assertFalse((root / "skilgen" / "delivery.py").exists())
            self.assertGreaterEqual(len(generated), 4)

    def test_run_delivery_can_limit_to_backend_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            requirements = root / "requirements.md"
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "src" / "routes").mkdir(parents=True)
            (root / "src" / "routes" / "dashboard.tsx").write_text("export default function Dashboard() { return null; }\n", encoding="utf-8")
            requirements.write_text("Backend endpoints\nFrontend routes\n", encoding="utf-8")

            run_delivery(requirements, root, targets=("skills",), domains=("backend",))

            self.assertTrue((root / "skills" / "backend" / "SKILL.md").exists())
            self.assertFalse((root / "skills" / "frontend" / "SKILL.md").exists())
            self.assertFalse((root / "ANALYSIS.md").exists())

    def test_run_delivery_works_with_codebase_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "services").mkdir(parents=True)
            (root / "services" / "users_service.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")

            generated = run_delivery(None, root)

            self.assertTrue((root / "ANALYSIS.md").exists())
            self.assertTrue((root / "ARCHITECTURE.md").exists())
            self.assertTrue((root / "skilgen-dashboard.html").exists())
            self.assertTrue((root / "FEATURES.md").exists())
            self.assertTrue((root / "skills" / "MANIFEST.md").exists())
            self.assertTrue((root / "skills" / "backend" / "SKILL.md").exists())
            self.assertGreaterEqual(len(generated), 4)

    def test_run_delivery_end_to_end_handles_src_package_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            package_root = root / "src" / "sample_sdk"
            package_root.mkdir(parents=True)
            for file_name in ["__init__.py", "client.py", "query.py", "types.py", "_errors.py", "version.py"]:
                (package_root / file_name).write_text("VALUE = 1\n", encoding="utf-8")
            (package_root / "_internal").mkdir()
            (package_root / "_internal" / "__init__.py").write_text("", encoding="utf-8")
            (package_root / "_internal" / "transport.py").write_text("def run():\n    return None\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_client.py").write_text("def test_client():\n    assert True\n", encoding="utf-8")
            (root / "e2e-tests").mkdir()
            (root / "e2e-tests" / "test_cli.py").write_text("def test_cli():\n    assert True\n", encoding="utf-8")
            (root / "examples").mkdir()
            (root / "examples" / "basic.py").write_text("from sample_sdk import client\n", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "release.py").write_text("print('release')\n", encoding="utf-8")

            generated = run_delivery(None, root, skip_index=True)
            score = compute_skillgen_score(root)

            self.assertTrue((root / "skilgen-dashboard.html").exists())
            self.assertTrue((root / "skills" / "sample-sdk-core" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "sample_sdk" / "client" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "sample_sdk" / "testing" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "sample_sdk" / "e2e" / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "sample_sdk" / "examples" / "SKILL.md").exists())
            self.assertFalse((root / "skills" / "backend" / "SKILL.md").exists())
            self.assertGreaterEqual(score["score"], 80)
            self.assertGreaterEqual(len(generated), 4)

    def test_run_delivery_persists_freshness_and_regenerates_impacted_domains(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "services").mkdir(parents=True)
            (root / "services" / "users_service.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")

            first_generated = run_delivery(None, root)
            self.assertTrue((root / ".skilgen" / "state" / "freshness.json").exists())
            self.assertTrue((root / ".skilgen" / "memory" / "current_run.json").exists())
            self.assertIn(root / "skills" / "backend" / "SKILL.md", first_generated)
            self.assertIn(root / "skills" / "frontend" / "SKILL.md", first_generated)
            memory_text = (root / ".skilgen" / "memory" / "current_run.json").read_text(encoding="utf-8")
            self.assertIn("pending_validations", memory_text)
            self.assertIn("resumable_steps", memory_text)
            self.assertIn("active_file_focus", memory_text)

            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {'ok': True}\n", encoding="utf-8")

            second_generated = run_delivery(None, root)

            self.assertIn(root / "skills" / "backend" / "SKILL.md", second_generated)
            self.assertNotIn(root / "skills" / "frontend" / "SKILL.md", second_generated)
            self.assertTrue((root / "AGENTS.md").exists())

    def test_run_delivery_skips_skill_regeneration_when_no_changes_are_detected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")

            run_delivery(None, root)
            second_generated = run_delivery(None, root)

            self.assertIn(root / "AGENTS.md", second_generated)
            self.assertNotIn(root / "skills" / "backend" / "SKILL.md", second_generated)
            self.assertNotIn(root / "skills" / "roadmap" / "SKILL.md", second_generated)
            memory_text = (root / ".skilgen" / "memory" / "current_run.json").read_text(encoding="utf-8")
            self.assertIn("Reuse the current skill tree", memory_text)

    def test_watch_delivery_ignores_generated_output_churn(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
            calls: list[str] = []

            def fake_run_delivery(*args, **kwargs):
                calls.append("run")
                (root / "skills" / "backend").mkdir(parents=True, exist_ok=True)
                (root / "skills" / "backend" / "SKILL.md").write_text(f"# Backend {len(calls)}\n", encoding="utf-8")
                (root / ".skilgen" / "state").mkdir(parents=True, exist_ok=True)
                (root / ".skilgen" / "state" / "freshness.json").write_text("{}", encoding="utf-8")
                (root / "ARCHITECTURE.md").write_text(f"# Architecture {len(calls)}\n", encoding="utf-8")
                (root / "skilgen-dashboard.html").write_text(f"<html>{len(calls)}</html>\n", encoding="utf-8")
                return [root / "skilgen-dashboard.html"]

            def mutate_generated_only(_seconds: float) -> None:
                (root / "skilgen-dashboard.html").write_text("<html>generated churn</html>\n", encoding="utf-8")
                (root / "ARCHITECTURE.md").write_text("# generated churn\n", encoding="utf-8")

            with patch("skilgen.delivery.run_delivery", side_effect=fake_run_delivery), patch("skilgen.delivery.time.sleep", side_effect=mutate_generated_only):
                runs = watch_delivery(None, root, cycles=1)

            self.assertEqual(len(calls), 1)
            self.assertEqual(len(runs), 1)

    def test_watch_delivery_regenerates_once_after_source_change(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src").mkdir()
            source = root / "src" / "app.py"
            source.write_text("def run():\n    return True\n", encoding="utf-8")
            calls: list[str] = []
            sleep_calls = 0

            def fake_run_delivery(*args, **kwargs):
                calls.append("run")
                (root / "skills" / "backend").mkdir(parents=True, exist_ok=True)
                (root / "skills" / "backend" / "SKILL.md").write_text(f"# Backend {len(calls)}\n", encoding="utf-8")
                (root / "skilgen-dashboard.html").write_text(f"<html>{len(calls)}</html>\n", encoding="utf-8")
                return [root / "skilgen-dashboard.html"]

            def mutate_source_once(_seconds: float) -> None:
                nonlocal sleep_calls
                sleep_calls += 1
                if sleep_calls == 1:
                    source.write_text("def run():\n    return False\n", encoding="utf-8")
                else:
                    (root / "skilgen-dashboard.html").write_text("<html>generated churn</html>\n", encoding="utf-8")

            with patch("skilgen.delivery.run_delivery", side_effect=fake_run_delivery), patch("skilgen.delivery.time.sleep", side_effect=mutate_source_once):
                runs = watch_delivery(None, root, cycles=2)

            self.assertEqual(len(calls), 2)
            self.assertEqual(len(runs), 2)

    def test_agents_contract_reflects_inferred_domains_and_prioritized_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")

            run_delivery(None, root)

            agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
            architecture_text = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
            graph_text = (root / "skills" / "GRAPH.md").read_text(encoding="utf-8")
            self.assertIn("## Inferred Domains", agents_text)
            self.assertIn("Decision planner refresh recommendation", agents_text)
            self.assertIn("Load these prioritized skills first:", agents_text)
            self.assertIn("## Skill Telemetry Hook", agents_text)
            self.assertIn("analytics --project-root . --record-skill", agents_text)
            self.assertIn("skills/backend/SKILL.md", agents_text)
            self.assertIn("## Architecture Domains", architecture_text)
            self.assertIn("## Architecture Blueprint", graph_text)

    def test_run_delivery_generates_freeform_top_level_domain_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src" / "theme").mkdir(parents=True)
            (root / "src" / "theme" / "tokens.ts").write_text("export const tokens = {};\n", encoding="utf-8")

            generated = run_delivery(None, root)

            self.assertIn(root / "skills" / "design-system" / "SKILL.md", generated)
            self.assertTrue((root / "skills" / "design-system" / "SUMMARY.md").exists())
            self.assertIn("skills/design-system/SKILL.md", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_run_delivery_surfaces_auto_installed_external_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "pyproject.toml").write_text("dependencies = ['langchain', 'langsmith']\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("Use Claude Code for this repo.\n", encoding="utf-8")

            installed = [
                {
                    "slug": "anthropic-skills",
                    "ecosystem": "anthropic",
                    "install_path": str(root / ".skilgen" / "external-skills" / "sources" / "anthropic-skills"),
                },
                {
                    "slug": "langchain-skills",
                    "ecosystem": "langchain",
                    "install_path": str(root / ".skilgen" / "external-skills" / "sources" / "langchain-skills"),
                },
            ]
            with patch(
                "skilgen.delivery.ensure_external_skills_for_project",
                return_value={
                    "detected_skills": [],
                    "manual_recommendations": [],
                    "installed_skills": installed,
                    "newly_installed": installed,
                    "already_installed": [],
                    "errors": [],
                },
            ) as ensure_mock, patch(
                "skilgen.generators.package.installed_external_skills",
                return_value=installed,
            ), patch(
                "skilgen.generators.package.detect_external_skill_sources",
                return_value={"manual_recommendations": []},
            ):
                run_delivery(None, root)

            ensure_mock.assert_called_once()
            agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## External Skill Packs", agents_text)
            self.assertIn("anthropic-skills", agents_text)
            self.assertIn("langchain-skills", agents_text)
            self.assertIn("## Preferred External Skill Packs", agents_text)

    def test_report_and_traceability_surface_external_skill_provenance(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            installed = [
                {
                    "slug": "candidate-pack",
                    "ecosystem": "imported",
                    "publisher": "example",
                    "repository_url": "https://github.com/example/candidate-pack",
                    "trust_level": "community",
                    "trust_score": 6,
                    "license": {"summary": "MIT License"},
                    "provenance": {
                        "repository_url": "https://github.com/example/candidate-pack",
                        "resolved_revision": "abc123",
                        "imported_from": "awesome-agent-skills-voltagent",
                    },
                    "install_path": str(root / ".skilgen" / "external-skills" / "sources" / "candidate-pack"),
                }
            ]
            ranked = [
                {
                    "slug": "candidate-pack",
                    "priority_score": 62,
                    "priority_reason": "Detected repo fit from imported directory skills.",
                    "trust_level": "community",
                    "lock_metadata": {"license": {"summary": "MIT License"}},
                }
            ]
            with patch(
                "skilgen.generators.package.installed_external_skills",
                return_value=installed,
            ), patch(
                "skilgen.generators.package.active_external_skills",
                return_value=installed,
            ), patch(
                "skilgen.generators.package.ranked_external_skills",
                return_value={"skills": ranked},
            ), patch(
                "skilgen.generators.package.external_skill_policy",
                return_value={
                    "policy_mode": "permissive",
                    "auto_install_enabled": True,
                    "auto_activate_enabled": True,
                },
            ):
                run_delivery(None, root)

            report_text = (root / "REPORT.md").read_text(encoding="utf-8")
            traceability_text = (root / "TRACEABILITY.md").read_text(encoding="utf-8")
            architecture_text = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
            self.assertIn("## External Skill Provenance", report_text)
            self.assertIn("awesome-agent-skills-voltagent", report_text)
            self.assertIn("## External Skill Traceability", traceability_text)
            self.assertIn("candidate-pack", traceability_text)
            self.assertIn("## Architecture Domains", architecture_text)

    def test_run_delivery_ingests_configured_enterprise_skills_and_connectors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            enterprise_source = root / "internal-platform"
            enterprise_source.mkdir(parents=True)
            (enterprise_source / "README.md").write_text("# Platform Skill\n\nUse Jira and Confluence for delivery.\n", encoding="utf-8")
            (root / "ops.md").write_text("Terraform provisions infra and Jira tracks work.\n", encoding="utf-8")
            (root / "skilgen.yml").write_text(
                "\n".join(
                    [
                        "enterprise_skill_paths:",
                        f"  - {enterprise_source}",
                        "auto_activate_mcp_connectors: true",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_delivery(None, root)

            agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
            traceability_text = (root / "TRACEABILITY.md").read_text(encoding="utf-8")
            self.assertIn("## Enterprise Skill Packs", agents_text)
            self.assertIn("internal-platform", agents_text)
            self.assertIn("## MCP Connectors", agents_text)
            self.assertIn("jira", agents_text)
            self.assertIn("## Enterprise Skill Traceability", traceability_text)
            self.assertIn("internal-platform", traceability_text)
            self.assertIn("## MCP Connector Traceability", traceability_text)
            self.assertTrue((root / ".skilgen" / "enterprise-skills" / "manifest.json").exists())
            self.assertTrue((root / ".skilgen" / "connectors" / "manifest.json").exists())

    def test_run_delivery_preserves_existing_skilgen_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            config_text = "\n".join(
                [
                    "update_trigger: auto",
                    "enterprise_skill_paths:",
                    "  - ./internal-skills/platform",
                ]
            ) + "\n"
            (root / "skilgen.yml").write_text(config_text, encoding="utf-8")

            run_delivery(None, root)

            self.assertEqual((root / "skilgen.yml").read_text(encoding="utf-8"), config_text)

    def test_architecture_split_materializes_dynamic_child_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")

            blueprint = ArchitectureBlueprint(
                headline="Backend architecture",
                system_summary="Split backend into focused child skills.",
                domains=[
                    ArchitectureDomain(
                        name="backend",
                        summary="Backend domain",
                        confidence=0.92,
                        responsibilities=["Serve backend requests"],
                        evidence_paths=["api/routes/users.py"],
                        related_domains=[],
                        recommended_skill_path="skills/backend/SKILL.md",
                    )
                ],
                hotspots=[],
                recommendations=[],
                materialization_plan=[
                    SkillMaterializationPlan(
                        domain="backend",
                        parent_skill_path="skills/backend/SKILL.md",
                        child_skill_paths=[
                            "skills/backend/api/SKILL.md",
                            "skills/backend/routes/SKILL.md",
                        ],
                        cross_links=[],
                        decision="split",
                        rationale="Backend has multiple concrete surfaces.",
                    )
                ],
            )

            with patch("skilgen.generators.skills.build_architecture_blueprint", return_value=blueprint):
                run_delivery(None, root)

            graph_text = (root / "skills" / "GRAPH.md").read_text(encoding="utf-8")
            self.assertIn("Materialization Decisions", graph_text)
            self.assertIn("`skills/backend/api/SKILL.md` (materialized)", graph_text)
            self.assertTrue((root / "skills" / "backend" / "api" / "SKILL.md").exists())

    def test_architecture_merge_skips_child_skill_materialization(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")
            (root / "src" / "state").mkdir(parents=True)
            (root / "src" / "state" / "store.ts").write_text("export const store = {};\n", encoding="utf-8")

            blueprint = ArchitectureBlueprint(
                headline="Frontend architecture",
                system_summary="Merge weak frontend child surfaces into the parent skill.",
                domains=[
                    ArchitectureDomain(
                        name="frontend",
                        summary="Frontend domain",
                        confidence=0.55,
                        responsibilities=["Serve UI routes"],
                        evidence_paths=["src/components/SkillCard.tsx"],
                        related_domains=[],
                        recommended_skill_path="skills/frontend/SKILL.md",
                    )
                ],
                hotspots=[],
                recommendations=[],
                materialization_plan=[
                    SkillMaterializationPlan(
                        domain="frontend",
                        parent_skill_path="skills/frontend/SKILL.md",
                        child_skill_paths=["skills/frontend/state/SKILL.md"],
                        cross_links=[],
                        decision="merge",
                        rationale="Weak child evidence should stay merged into the parent.",
                    )
                ],
            )

            with patch("skilgen.generators.skills.build_architecture_blueprint", return_value=blueprint):
                run_delivery(None, root)

            self.assertFalse((root / "skills" / "frontend" / "state" / "SKILL.md").exists())
            graph_text = (root / "skills" / "GRAPH.md").read_text(encoding="utf-8")
            self.assertIn("- decision: `merge`", graph_text)


if __name__ == "__main__":
    unittest.main()
