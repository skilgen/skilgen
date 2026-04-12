from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.analytics import analytics_summary, log_skill_usage


class AnalyticsTests(unittest.TestCase):
    def test_analytics_summary_includes_skill_usage_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "backend" / "api"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "# Backend API\n\nUse this skill for route handling.\n\n## Signals\n- routes\n- auth\n`src/api/routes.py`\n",
                encoding="utf-8",
            )
            log_skill_usage(root, ["skills/backend/api/SKILL.md", "skills/backend/api/SKILL.md"])

            summary = analytics_summary(root, limit=10)

            self.assertIn("skill_usage", summary)
            self.assertEqual(summary["skill_usage"][0]["skill"], "skills/backend/api/SKILL.md")
            self.assertEqual(summary["skill_usage"][0]["loads"], 2)
            self.assertEqual(summary["skill_usage"][0]["family"], "backend")
            self.assertGreater(summary["skill_usage"][0]["richness"], 0)
            self.assertIn("summary", summary["skill_usage"][0])

    def test_analytics_summary_excludes_decision_planner_from_live_usage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "backend"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Backend\n\nCore backend skill.\n", encoding="utf-8")

            log_skill_usage(root, ["skills/backend/SKILL.md"], context="decision_planner")
            log_skill_usage(root, ["skills/backend/SKILL.md"], context="claude_code")

            summary = analytics_summary(root, limit=10)

            self.assertEqual(summary["planner_event_count"], 1)
            self.assertEqual(summary["live_event_count"], 1)
            self.assertEqual(summary["skill_usage"][0]["loads"], 1)

    def test_analytics_summary_models_attention_when_no_live_usage_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "frontend" / "components").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text(
                "---\nkind: repo\n---\n# Backend\n\nCoordinates routes, services, persistence, and tests.\n\n## References\n- `src/api/routes.py`\n- `src/services/users.py`\n",
                encoding="utf-8",
            )
            (root / "skills" / "frontend" / "components" / "SKILL.md").write_text(
                "# Components\n\nReusable UI building blocks.\n\n- buttons\n- cards\n",
                encoding="utf-8",
            )

            summary = analytics_summary(root, limit=10)

            self.assertEqual(summary["usage_mode"], "modeled")
            self.assertGreater(summary["skill_usage"][0]["effective_loads"], summary["skill_usage"][-1]["effective_loads"])
            self.assertNotEqual(summary["top_skills"][0]["skill"], summary["least_used"][0]["skill"])
            self.assertEqual(summary["skill_usage"][0]["usage_label"], "Modeled attention")
            self.assertNotEqual(summary["skill_usage"][0]["summary"], "---")
            self.assertNotEqual(summary["skill_usage"][0]["title"], "Overview")

    def test_skill_title_and_summary_falls_back_when_summary_is_placeholder(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "backend"
            skill_dir.mkdir(parents=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("---\nname: backend\n---\n# Backend Skill\n\n---\n", encoding="utf-8")

            summary = analytics_summary(root, limit=10)

            self.assertNotEqual(summary["skill_usage"][0]["summary"], "---")


if __name__ == "__main__":
    unittest.main()
