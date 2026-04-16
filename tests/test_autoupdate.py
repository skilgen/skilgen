from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.autoupdate import _file_snapshot


class AutoUpdateTests(unittest.TestCase):
    def test_file_snapshot_ignores_generated_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
            for file_name in [
                "AGENTS.md",
                "ANALYSIS.md",
                "ARCHITECTURE.md",
                "FEATURES.md",
                "REPORT.md",
                "TRACEABILITY.md",
                "skilgen-dashboard.html",
                "skilgen.yml",
            ]:
                (root / file_name).write_text("generated\n", encoding="utf-8")
            (root / "skills" / "backend").mkdir(parents=True)
            (root / "skills" / "backend" / "SKILL.md").write_text("# Backend\n", encoding="utf-8")
            (root / ".skilgen" / "state").mkdir(parents=True)
            (root / ".skilgen" / "state" / "freshness.json").write_text("{}", encoding="utf-8")

            snapshot = _file_snapshot(root)

            self.assertEqual(set(snapshot), {"src/app.py"})


if __name__ == "__main__":
    unittest.main()
