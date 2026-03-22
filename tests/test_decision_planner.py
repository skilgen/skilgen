from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import subprocess

from skilgen.agents.decision_planner import build_agent_decision
from skilgen.core.context import build_codebase_context
from skilgen.core.requirements import load_project_context
from skilgen.external_skills import install_external_skill, remove_external_skill


class DecisionPlannerTests(unittest.TestCase):
    def test_decision_recommends_refresh_for_initial_generation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "users.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            context = load_project_context(root, None)
            codebase_context = build_codebase_context(root, context)

            decision = build_agent_decision(root, context, codebase_context.domain_graph, codebase_context.skill_tree)

            self.assertTrue(decision.should_refresh)
            self.assertIn("backend", decision.prioritized_domains)
            self.assertTrue(decision.prioritized_skill_paths)
            self.assertIn(".skilgen/state/freshness.json", decision.memory_to_load)

    def test_decision_includes_ranked_external_skill_memory(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "CLAUDE.md").write_text("Use Claude Code in this repo.\n", encoding="utf-8")
            source = root / "external-source"
            source.mkdir()
            (source / "README.md").write_text("demo\n", encoding="utf-8")
            (source / "skills").mkdir()
            (source / "skills" / "demo").mkdir()
            (source / "skills" / "demo" / "SKILL.md").write_text("# Demo Skill\n", encoding="utf-8")
            subprocess.run(["git", "init", str(source)], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "tests@example.com"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Tests"], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "add", "."], text=True, capture_output=True, check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "init"], text=True, capture_output=True, check=True)

            installed = install_external_skill(project_root=root, git_url=str(source), name="demo pack", active=True)
            context = load_project_context(root, None)
            codebase_context = build_codebase_context(root, context)
            decision = build_agent_decision(root, context, codebase_context.domain_graph, codebase_context.skill_tree)

            self.assertIn(".skilgen/external-skills/lock.json", decision.memory_to_load)
            self.assertTrue(any("external-skills/normalized" in path for path in decision.memory_to_load))
            self.assertTrue(any("external-skills/normalized" in path for path in decision.prioritized_skill_paths))

            remove_external_skill(project_root=root, slug=installed["slug"])


if __name__ == "__main__":
    unittest.main()
