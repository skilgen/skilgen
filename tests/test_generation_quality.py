from __future__ import annotations

import asyncio
import json
import os
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from skilgen.core.analytics import _compute_richness_score, analytics_summary
from skilgen.core.models import SkillSpec
from skilgen.delivery import _auto_sync_to_skillayer, _write_claude_code_hook
from skilgen.generators.skills import _extract_code_example, render_skill
from skilgen.hooks.claude_code_hook import record_read
from skilgen.hooks.cursor_watcher import watch_skills


def _spec(**overrides: object) -> SkillSpec:
    values = {
        "path": "backend/api/SKILL.md",
        "name": "api",
        "domain": "api",
        "sub_domain": "routes",
        "overview": "API guidance grounded in route handlers.",
        "checks": [],
        "patterns": [("Patterns", ["Always validate input at the API boundary"])],
        "how_to": ["Inspect the route.", "Trace the service.", "Run endpoint tests."],
        "references": ["../SKILL.md"],
    }
    values.update(overrides)
    return SkillSpec(**values)


class GenerationQualityTests(unittest.TestCase):
    def test_antipattern_section_is_present_for_any_domain(self) -> None:
        rendered = render_skill(_spec(domain="billing", sub_domain="payments"), "source-hash")

        self.assertIn("## Anti-patterns", rendered)
        self.assertGreaterEqual(rendered.split("## Anti-patterns", 1)[1].count("- **"), 3)

    def test_code_example_extracted_from_python_file_has_fenced_block(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "api" / "routes.py"
            source.parent.mkdir(parents=True)
            source.write_text("#!/usr/bin/env python\n\nasync def handler(request):\n    return {'ok': True}\n", encoding="utf-8")

            rendered = render_skill(_spec(checks=["{{project_root}}/api/routes.py"]), "source-hash", root)

            self.assertIn("## Code Examples", rendered)
            self.assertIn("```python", rendered)
            self.assertIn("async def handler", rendered)

    def test_extract_code_example_returns_none_for_inaccessible_file(self) -> None:
        self.assertIsNone(_extract_code_example("/path/that/does/not/exist.py"))
        self.assertNotIn("## Code Examples", render_skill(_spec(checks=["/path/that/does/not/exist.py"]), "source-hash"))

    def test_score_formula_rewards_code_examples_and_antipatterns(self) -> None:
        plain = "# API\n\n## Patterns\n- Always validate input.\n"
        rich = plain + "\n## Anti-patterns\n- Don't skip validation.\n\n```python\nprint('ok')\n```\n"

        self.assertGreater(_compute_richness_score(rich, _spec())["total"], _compute_richness_score(plain, _spec())["total"])

    def test_score_formula_groundedness_maxes_at_25(self) -> None:
        content = "\n".join(["```python\nprint('ok')\n```" for _ in range(10)])

        self.assertEqual(_compute_richness_score(content, _spec())["groundedness"], 25)

    def test_auto_sync_uploads_when_skillayer_env_is_set(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "api" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# API\n", encoding="utf-8")

            async def fake_upload(api_url: str, repo_id: str, api_key: str, project_root: str | Path = ".") -> dict[str, int]:
                self.assertEqual(api_key, "sk-test")
                self.assertEqual(repo_id, "repo-1")
                return {"synced": 1, "skipped": 0}

            with patch.dict(os.environ, {"SKILLAYER_API_KEY": "sk-test", "SKILLAYER_REPO_ID": "repo-1"}, clear=False):
                with patch("skilgen.delivery._upload_analytics", side_effect=fake_upload) as upload:
                    synced = asyncio.run(_auto_sync_to_skillayer(root, [skill]))

            self.assertTrue(synced)
            self.assertEqual(upload.call_count, 1)
            self.assertEqual(analytics_summary(root)["live_event_count"], 1)

    def test_auto_sync_noops_without_skillayer_env(self) -> None:
        with TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {}, clear=True):
                synced = asyncio.run(_auto_sync_to_skillayer(tmp, ["skills/api/SKILL.md"]))

            self.assertFalse(synced)

    def test_write_claude_code_hook_creates_settings_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            settings = _write_claude_code_hook(tmp)
            data = json.loads(Path(settings).read_text(encoding="utf-8"))

            command = data["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
            self.assertIn("skilgen.hooks.claude_code_hook", command)

    def test_write_claude_code_hook_does_not_duplicate(self) -> None:
        with TemporaryDirectory() as tmp:
            _write_claude_code_hook(tmp)
            _write_claude_code_hook(tmp)
            data = json.loads((Path(tmp) / ".claude" / "settings.json").read_text(encoding="utf-8"))

            self.assertEqual(len(data["hooks"]["PostToolUse"]), 1)

    def test_watch_command_detects_file_access_and_logs_usage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "api" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# API\n", encoding="utf-8")

            def touch_after_scan(_seconds: int) -> None:
                future = time.time() + 5
                os.utime(skill, (future, future))

            with patch("skilgen.hooks.cursor_watcher.time.sleep", side_effect=touch_after_scan):
                with patch("skilgen.hooks.cursor_watcher.subprocess.Popen"):
                    watch_skills(str(root), "repo-1", "sk-test", poll_interval=0, max_cycles=1)

            summary = analytics_summary(root)
            self.assertEqual(summary["live_event_count"], 1)
            self.assertEqual(summary["skill_usage"][0]["contexts"], ["cursor_watcher"])

    def test_claude_code_hook_records_skill_reads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "backend" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Backend\n", encoding="utf-8")

            self.assertTrue(record_read(str(skill)))
            self.assertEqual(analytics_summary(root)["live_event_count"], 1)


if __name__ == "__main__":
    unittest.main()
