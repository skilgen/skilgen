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


if __name__ == "__main__":
    unittest.main()
