from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.context import build_codebase_context
from skilgen.core.requirements import load_requirements


class ContextTests(unittest.TestCase):
    def test_build_codebase_context_includes_domains_and_skill_tree(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Backend API endpoints\nFrontend routes\n", encoding="utf-8")
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "services").mkdir(parents=True)
            (root / "services" / "scan_service.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "models").mkdir(parents=True)
            (root / "models" / "scan_model.py").write_text("class Scan: pass\n", encoding="utf-8")
            (root / "src" / "routes").mkdir(parents=True)
            (root / "src" / "routes" / "dashboard.tsx").write_text("export default function Dashboard() { return null; }\n", encoding="utf-8")
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard() { return null; }\n", encoding="utf-8")
            (root / "src" / "theme").mkdir(parents=True)
            (root / "src" / "theme" / "tokens.ts").write_text("export const tokens = {};\n", encoding="utf-8")
            context = build_codebase_context(root, load_requirements(requirements))
            domain_names = {record.name for record in context.detected_domains}
            self.assertIn("requirements", domain_names)
            self.assertIn("backend", domain_names)
            self.assertIn("frontend", domain_names)
            self.assertIn("roadmap", domain_names)
            graph_names = {node.name for node in context.domain_graph.nodes}
            self.assertIn("backend-data", graph_names)
            self.assertIn("frontend-design-system", graph_names)
            self.assertTrue(context.skill_tree)
            backend_node = next(node for node in context.skill_tree if node.domain == "backend")
            frontend_node = next(node for node in context.skill_tree if node.domain == "frontend")
            self.assertIn("skills/backend/routes/SKILL.md", backend_node.child_skills)
            self.assertIn("skills/backend/services/SKILL.md", backend_node.child_skills)
            self.assertIn("skills/backend/data/SKILL.md", backend_node.child_skills)
            self.assertIn("skills/frontend/routes/SKILL.md", frontend_node.child_skills)
            self.assertIn("skills/frontend/design-system/SKILL.md", frontend_node.child_skills)

    def test_build_codebase_context_can_infer_freeform_top_level_domains(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Shared tokens and design language\n", encoding="utf-8")
            (root / "src" / "theme").mkdir(parents=True)
            (root / "src" / "theme" / "tokens.ts").write_text("export const tokens = {};\n", encoding="utf-8")

            context = build_codebase_context(root, load_requirements(requirements))

            domain_names = {record.name for record in context.detected_domains}
            self.assertIn("design-system", domain_names)
            design_node = next(node for node in context.skill_tree if node.domain == "design-system")
            self.assertEqual(design_node.path, "skills/design-system/SKILL.md")


if __name__ == "__main__":
    unittest.main()
