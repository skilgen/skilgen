from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.repo_state import classify_repo_change
from skilgen.core.score import compute_skillgen_score


class ScoreTests(unittest.TestCase):
    def test_score_includes_quality_gates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")
            payload = compute_skillgen_score(root)
            self.assertIn("raw_score", payload)
            self.assertIn("quality_gates", payload)
            self.assertTrue(payload["quality_gates"])
            self.assertLessEqual(payload["score"], payload["raw_score"])

    def test_classify_repo_change_detects_manual_edits(self) -> None:
        previous = {
            "files": {"src/app.py": 1},
            "git": {
                "head": "abc",
                "branch": "main",
                "merge_in_progress": False,
                "rebase_in_progress": False,
                "staged_changes": 0,
                "unstaged_changes": 0,
                "untracked_files": 0,
                "head_parent_count": 1,
            },
        }
        current = {
            "files": {"src/app.py": 2},
            "git": {
                "head": "abc",
                "branch": "main",
                "merge_in_progress": False,
                "rebase_in_progress": False,
                "staged_changes": 0,
                "unstaged_changes": 1,
                "untracked_files": 0,
                "head_parent_count": 1,
            },
        }
        payload = classify_repo_change(previous, current)
        self.assertEqual(payload["event_type"], "manual_edit")

    def test_classify_repo_change_detects_merge_commit(self) -> None:
        previous = {
            "files": {"src/app.py": 1},
            "git": {
                "head": "abc",
                "branch": "main",
                "merge_in_progress": False,
                "rebase_in_progress": False,
                "staged_changes": 0,
                "unstaged_changes": 0,
                "untracked_files": 0,
                "head_parent_count": 1,
            },
        }
        current = {
            "files": {"src/app.py": 2},
            "git": {
                "head": "def",
                "branch": "main",
                "merge_in_progress": False,
                "rebase_in_progress": False,
                "staged_changes": 0,
                "unstaged_changes": 0,
                "untracked_files": 0,
                "head_parent_count": 2,
            },
        }
        payload = classify_repo_change(previous, current)
        self.assertEqual(payload["event_type"], "merge_commit")


if __name__ == "__main__":
    unittest.main()
