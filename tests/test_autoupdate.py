from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from skilgen.autoupdate import diff_history, run_auto_update_worker


class AutoUpdateHistoryTests(unittest.TestCase):
    def test_diff_history_returns_empty_when_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            payload = diff_history(Path(tmp), limit=10)
            self.assertEqual(payload["entries"], [])
            self.assertEqual(payload["entry_count"], 0)

    def test_diff_history_returns_latest_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            history_path = root / ".skilgen" / "state" / "diff-history.jsonl"
            history_path.parent.mkdir(parents=True, exist_ok=True)
            lines = [
                json.dumps({"timestamp": f"2026-04-05T10:{index:02d}:00+00:00", "reason": "source_changes_detected"})
                for index in range(12)
            ]
            history_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            trimmed = diff_history(root, limit=10)
            self.assertEqual(trimmed["entry_count"], 10)
            self.assertEqual(trimmed["entries"][0]["timestamp"], "2026-04-05T10:02:00+00:00")

    def test_autoupdate_worker_logs_diff_snapshot_before_delivery(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshots = [
                {"files": {"src/app.py": 1}, "git": {"head": "a"}},
                {"files": {"src/app.py": 2}, "git": {"head": "a"}},
            ]
            diff_payload = {
                "changed_files": [{"path": "src/app.py", "change_type": "modified"}],
                "changed_file_count": 1,
                "impacted_domains": ["backend"],
                "stale_skill_paths": ["skills/backend/SKILL.md"],
                "current_domains": [],
                "reason": "source_changes_detected",
                "freshness_score": 15.0,
                "freshness_max": 25,
                "git": {"event_type": "manual_edit"},
            }

            with (
                patch("skilgen.autoupdate._snapshot", side_effect=[snapshots[0], snapshots[1]]),
                patch("skilgen.autoupdate.classify_repo_change", return_value={"event_type": "manual_edit"}),
                patch("skilgen.autoupdate.compute_diff", return_value=diff_payload),
                patch("skilgen.autoupdate.run_delivery", return_value=[]),
                patch("skilgen.autoupdate.time.sleep", side_effect=[None, KeyboardInterrupt]),
            ):
                with self.assertRaises(KeyboardInterrupt):
                    run_auto_update_worker(root, interval_seconds=0.0)

            history = diff_history(root, limit=10)
            self.assertEqual(history["entry_count"], 1)
            self.assertEqual(history["entries"][0]["reason"], "source_changes_detected")
            self.assertEqual(history["entries"][0]["changed_file_count"], 1)
