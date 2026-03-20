import unittest

from skilgen.agents.roadmap_planner import build_roadmap_plan
from skilgen.core.models import ProjectIntent, SkilgenConfig


class RoadmapPlannerTests(unittest.TestCase):
    def test_build_roadmap_plan_includes_endpoint_and_ui_steps(self) -> None:
        config = SkilgenConfig(
            include_paths=["."],
            exclude_paths=[],
            domains_override=[],
            skill_depth=2,
            update_trigger="manual",
            langsmith_project=None,
            model_provider="openai",
            model="gpt-5",
            api_key_env="OPENAI_API_KEY",
            model_retry_attempts=3,
            model_retry_base_delay_seconds=1.0,
        )
        intent = ProjectIntent(
            features=["feature one"],
            domain_concepts=["backend"],
            entities=["SkillVersion"],
            endpoints=["/scan"],
            ui_flows=["dashboard"],
        )
        plan = build_roadmap_plan(config, intent)
        titles = {step.title for step in plan.steps}
        self.assertIn("Add endpoint-aware feature extraction", titles)
        self.assertIn("Add UI flow and route extraction", titles)


if __name__ == "__main__":
    unittest.main()
