from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.decision_planner import build_agent_decision
from skilgen.core.context import build_codebase_context
from skilgen.core.requirements import load_project_context


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


if __name__ == "__main__":
    unittest.main()
