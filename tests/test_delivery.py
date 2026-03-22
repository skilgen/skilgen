from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.delivery import run_delivery


class DeliveryTests(unittest.TestCase):
    def test_run_delivery_works_with_requirements_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            requirements = root / "requirements.md"
            requirements.write_text("Backend endpoints\nFrontend routes\nRoadmap phases\n", encoding="utf-8")

            generated = run_delivery(requirements, root)

            self.assertTrue((root / "ANALYSIS.md").exists())
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
            self.assertTrue((root / "FEATURES.md").exists())
            self.assertTrue((root / "REPORT.md").exists())
            self.assertTrue((root / "TRACEABILITY.md").exists())
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
            self.assertTrue((root / "FEATURES.md").exists())
            self.assertTrue((root / "skills" / "MANIFEST.md").exists())
            self.assertTrue((root / "skills" / "backend" / "SKILL.md").exists())
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

    def test_agents_contract_reflects_inferred_domains_and_prioritized_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")

            run_delivery(None, root)

            agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## Inferred Domains", agents_text)
            self.assertIn("Decision planner refresh recommendation", agents_text)
            self.assertIn("Load these prioritized skills first:", agents_text)
            self.assertIn("skills/backend/SKILL.md", agents_text)

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


if __name__ == "__main__":
    unittest.main()
