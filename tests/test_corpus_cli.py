from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest


class CorpusCliTests(unittest.TestCase):
    def test_index_command_writes_corpus_cache(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "index", "--project-root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )

            payload = json.loads(result.stdout)
            self.assertTrue((root / ".skilgen" / "corpus" / "index.json").exists())
            self.assertGreaterEqual(payload["entry_count"], 1)
            self.assertEqual(Path(payload["index_path"]).resolve(), (root / ".skilgen" / "corpus" / "index.json").resolve())

    def test_architecture_skip_index_leaves_cache_unwritten(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

            subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "architecture", "--project-root", str(root), "--json", "--skip-index"],
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertFalse((root / ".skilgen" / "corpus" / "index.json").exists())

    def test_deliver_skip_index_leaves_cache_unwritten(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

            subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "deliver", "--project-root", str(root), "--dry-run", "--skip-index"],
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertFalse((root / ".skilgen" / "corpus" / "index.json").exists())


if __name__ == "__main__":
    unittest.main()
