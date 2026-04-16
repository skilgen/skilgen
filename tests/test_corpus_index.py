from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.codebase_signals import collect_code_evidence
from skilgen.core.corpus_index import build_corpus_index
from skilgen.core.deep_sampler import select_deep_read_targets


class CorpusIndexTests(unittest.TestCase):
    def test_build_corpus_index_covers_repo_and_excludes_generated_content(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "legacy" / "payroll").mkdir(parents=True)
            (root / "legacy" / "payroll" / "engine.py").write_text(
                "from legacy.payroll.helpers import helper\n\ndef run_engine():\n    return helper()\n",
                encoding="utf-8",
            )
            (root / "legacy" / "payroll" / "helpers.py").write_text(
                "from legacy.payroll.jobs import load_jobs\n\ndef helper():\n    return load_jobs()\n",
                encoding="utf-8",
            )
            (root / "legacy" / "payroll" / "jobs.py").write_text(
                "from legacy.payroll.engine import run_engine\n\ndef load_jobs():\n    return [run_engine]\n",
                encoding="utf-8",
            )
            (root / "infra").mkdir()
            (root / "infra" / "main.tf").write_text('resource "aws_s3_bucket" "logs" {}\n', encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n\nSubsystem overview.\n", encoding="utf-8")
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text("# ignored\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "ignored.js").write_text("export const bad = true;\n", encoding="utf-8")
            (root / "dist").mkdir()
            (root / "dist" / "bundle.min.js").write_text("const x=1;\n", encoding="utf-8")

            payload = build_corpus_index(root)
            paths = {entry["path"] for entry in payload["entries"]}

            self.assertIn("legacy/payroll/engine.py", paths)
            self.assertIn("infra/main.tf", paths)
            self.assertIn("docs/ARCHITECTURE.md", paths)
            self.assertNotIn("skills/backend/SKILL.md", paths)
            self.assertNotIn("node_modules/ignored.js", paths)
            self.assertNotIn("dist/bundle.min.js", paths)
            self.assertTrue((root / ".skilgen" / "corpus" / "index.json").exists())

    def test_sampler_and_collect_code_evidence_cover_clusters_docs_and_configs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "legacy" / "payroll").mkdir(parents=True)
            (root / "legacy" / "payroll" / "engine.py").write_text(
                "from legacy.payroll.helpers import helper\n\ndef run_engine():\n    return helper()\n",
                encoding="utf-8",
            )
            (root / "legacy" / "payroll" / "helpers.py").write_text(
                "from legacy.payroll.jobs import load_jobs\n\ndef helper():\n    return load_jobs()\n",
                encoding="utf-8",
            )
            (root / "legacy" / "payroll" / "jobs.py").write_text(
                "from legacy.payroll.engine import run_engine\n\ndef load_jobs():\n    return [run_engine]\n",
                encoding="utf-8",
            )
            (root / "infra").mkdir()
            (root / "infra" / "main.tf").write_text('resource "aws_s3_bucket" "logs" {}\n', encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n\nSubsystem overview.\n", encoding="utf-8")

            payload = build_corpus_index(root)
            selected = select_deep_read_targets(payload, project_root=root, total_budget=4)
            evidence = collect_code_evidence(root, limit=8)
            evidence_paths = {item["path"] for item in evidence}

            self.assertIn("docs/ARCHITECTURE.md", selected)
            self.assertIn("infra/main.tf", selected)
            self.assertTrue(any(path.startswith("legacy/payroll/") for path in selected))
            self.assertIn("docs/ARCHITECTURE.md", evidence_paths)
            self.assertIn("infra/main.tf", evidence_paths)
            self.assertTrue(any(path.startswith("legacy/payroll/") for path in evidence_paths))


if __name__ == "__main__":
    unittest.main()
