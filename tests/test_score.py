from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import threading
import unittest

from skilgen.core.repo_state import classify_repo_change
from skilgen.core.score import compute_skillgen_score, load_score_history, record_score_history, score_history_payload


class ScoreTests(unittest.TestCase):
    def _git(self, root: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

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
            self.assertIn("domains", payload)
            self.assertIn("skills", payload)

    def test_score_exposes_domain_and_skill_drilldowns(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text(
                "\n".join(
                    [
                        "# Backend",
                        "references:",
                        "- ../MANIFEST.md",
                        "## Check These Paths First",
                        "- {{project_root}}/api/routes/scan.py",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "skills" / "backend" / "SUMMARY.md").write_text("Backend summary\n", encoding="utf-8")
            (root / "skills" / "MANIFEST.md").write_text("# Manifest\n", encoding="utf-8")
            (root / "skills" / "GRAPH.md").write_text("# Graph\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            (root / "FEATURES.md").write_text("# Features\n", encoding="utf-8")
            (root / "TRACEABILITY.md").write_text("# Traceability\n", encoding="utf-8")

            payload = compute_skillgen_score(root)
            self.assertTrue(payload["domains"])
            self.assertTrue(payload["skills"])
            self.assertIn("domain", payload["domains"][0])
            self.assertIn("path", payload["skills"][0])
            self.assertEqual(payload["materialized_domains"], ["backend"])
            self.assertIn("backend-api", payload["inferred_only_domains"])

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

    def test_classify_repo_change_infers_semantic_commit_intent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._git(root, "init")
            self._git(root, "config", "user.name", "Skilgen Test")
            self._git(root, "config", "user.email", "test@example.com")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def existing():\n    return True\n", encoding="utf-8")
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "initial")
            branch = self._git(root, "rev-parse", "--abbrev-ref", "HEAD")
            previous = {
                "project_root": str(root),
                "files": {"src/app.py": 1},
                "git": {
                    "head": self._git(root, "rev-parse", "HEAD"),
                    "branch": branch,
                    "merge_in_progress": False,
                    "rebase_in_progress": False,
                    "staged_changes": 0,
                    "unstaged_changes": 0,
                    "untracked_files": 0,
                    "head_parent_count": 1,
                },
            }
            (root / "src" / "app.py").write_text(
                "def existing():\n    return True\n\nclass BillingService:\n    pass\n",
                encoding="utf-8",
            )
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "add billing service")
            current_head = self._git(root, "rev-parse", "HEAD")
            current = {
                "project_root": str(root),
                "files": {"src/app.py": 2},
                "git": {
                    "head": current_head,
                    "branch": branch,
                    "merge_in_progress": False,
                    "rebase_in_progress": False,
                    "staged_changes": 0,
                    "unstaged_changes": 0,
                    "untracked_files": 0,
                    "head_parent_count": 1,
                },
            }

            payload = classify_repo_change(previous, current)

            self.assertEqual(payload["event_type"], "git_head_changed")
            self.assertEqual(payload["semantic_intent"], "new_feature")
            self.assertGreaterEqual(payload["semantic_confidence"], 0.7)

    def test_score_history_tracks_trends(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")
            record_score_history(root, source="delivery")
            (root / "skills").mkdir()
            (root / "skills" / "backend").mkdir()
            (root / "skills" / "backend" / "SKILL.md").write_text("# Backend\n", encoding="utf-8")
            (root / "skills" / "backend" / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
            (root / "skills" / "MANIFEST.md").write_text("# Manifest\n", encoding="utf-8")
            (root / "skills" / "GRAPH.md").write_text("# Graph\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            (root / "FEATURES.md").write_text("# Features\n", encoding="utf-8")
            (root / "TRACEABILITY.md").write_text("# Traceability\n", encoding="utf-8")
            record_score_history(root, source="score")

            history = load_score_history(root, limit=5)
            payload = score_history_payload(root, limit=5)

            self.assertEqual(len(history), 2)
            self.assertIn("trend", payload)
            self.assertIn("delta_from_previous", payload["trend"])

    def test_score_history_append_is_safe_under_concurrent_writes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")

            threads = [
                threading.Thread(target=record_score_history, args=(root,), kwargs={"source": f"worker-{index}"})
                for index in range(6)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            history = load_score_history(root, limit=10)
            self.assertEqual(len(history), 6)
            self.assertEqual({entry["source"] for entry in history}, {f"worker-{index}" for index in range(6)})

    def test_coverage_ignores_non_code_repo_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "api" / "routes").mkdir(parents=True)
            (root / "api" / "routes" / "scan.py").write_text("def handler():\n    return {}\n", encoding="utf-8")
            (root / "README.md").write_text("# Project\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "notes.md").write_text("notes\n", encoding="utf-8")
            (root / ".github").mkdir()
            (root / ".github" / "workflow.yml").write_text("name: CI\n", encoding="utf-8")
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text(
                "\n".join(
                    [
                        "# Backend",
                        "references:",
                        "- ../MANIFEST.md",
                        "## Check These Paths First",
                        "- {{project_root}}/api/routes/scan.py",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "skills" / "backend" / "SUMMARY.md").write_text("Backend summary\n", encoding="utf-8")
            (root / "skills" / "MANIFEST.md").write_text("# Manifest\n", encoding="utf-8")
            (root / "skills" / "GRAPH.md").write_text("# Graph\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            (root / "FEATURES.md").write_text("# Features\n", encoding="utf-8")
            (root / "TRACEABILITY.md").write_text("# Traceability\n", encoding="utf-8")

            payload = compute_skillgen_score(root)

            self.assertEqual(payload["subscores"]["coverage"]["source_file_count"], 1)
            self.assertEqual(payload["subscores"]["coverage"]["mapped_file_count"], 1)
            self.assertEqual(payload["subscores"]["coverage"]["coverage_ratio"], 1.0)

    def test_coverage_uses_logical_code_areas_for_repo_scale(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skilgen").mkdir(parents=True, exist_ok=True)
            (root / "skilgen" / "__init__.py").write_text("", encoding="utf-8")
            (root / "skilgen" / "api").mkdir(parents=True)
            (root / "skilgen" / "core").mkdir(parents=True)
            (root / "tests").mkdir()
            (root / "scripts").mkdir()
            (root / "skilgen" / "api" / "server.py").write_text("def serve():\n    return None\n", encoding="utf-8")
            (root / "skilgen" / "api" / "service.py").write_text("def service():\n    return None\n", encoding="utf-8")
            (root / "skilgen" / "core" / "config.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "tests" / "test_api.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
            (root / "scripts" / "run_pipeline.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "setup.py").write_text("from setuptools import setup\n", encoding="utf-8")
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text(
                "\n".join(
                    [
                        "# Backend",
                        "references:",
                        "- ../MANIFEST.md",
                        "## Check These Paths First",
                        "- {{project_root}}/skilgen/api/server.py",
                        "- {{project_root}}/tests/test_api.py",
                        "- {{project_root}}/scripts/run_pipeline.py",
                        "- {{project_root}}/setup.py",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "skills" / "backend" / "SUMMARY.md").write_text("Backend summary\n", encoding="utf-8")
            (root / "skills" / "MANIFEST.md").write_text("# Manifest\n", encoding="utf-8")
            (root / "skills" / "GRAPH.md").write_text("# Graph\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            (root / "FEATURES.md").write_text("# Features\n", encoding="utf-8")
            (root / "TRACEABILITY.md").write_text("# Traceability\n", encoding="utf-8")

            payload = compute_skillgen_score(root)
            coverage = payload["subscores"]["coverage"]

            self.assertEqual(coverage["source_file_count"], 7)
            self.assertEqual(coverage["source_unit_count"], 6)
            self.assertGreaterEqual(coverage["mapped_unit_count"], 2)
            self.assertGreater(coverage["coverage_ratio"], 0.2)


if __name__ == "__main__":
    unittest.main()
