from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.models import FreshnessReport
from skilgen.core.run_memory import create_run_memory, load_current_run_memory, save_run_memory


class RunMemoryTests(unittest.TestCase):
    def test_load_current_run_memory_recovers_from_concatenated_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            freshness = FreshnessReport(
                changed_files=[],
                impacted_domains=["backend"],
                stale_skill_paths=[],
                top_level_domains=["backend"],
                reason="no_source_changes",
            )
            first = create_run_memory(root, None, "local_fallback", freshness, ["backend"], ["skills/backend/SKILL.md"])
            save_run_memory(root, first)
            second = create_run_memory(root, None, "local_fallback", freshness, ["frontend"], ["skills/frontend/SKILL.md"])
            current_path = root / ".skilgen" / "memory" / "current_run.json"
            current_path.write_text(
                current_path.read_text(encoding="utf-8") + current_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            recovered = load_current_run_memory(root)

            self.assertIsNotNone(recovered)
            self.assertEqual(recovered.selected_domains, ["backend"])


if __name__ == "__main__":
    unittest.main()
