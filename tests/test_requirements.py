from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from skilgen.core.requirements import load_project_context, load_requirements


class RequirementsTests(unittest.TestCase):
    def test_markdown_requirements_detect_domains(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "requirements.md"
            path.write_text("Backend API endpoints\nFrontend React components\n", encoding="utf-8")
            context = load_requirements(path)
            self.assertTrue(context.domains["backend"])
            self.assertTrue(context.domains["frontend"])
            self.assertTrue(context.summary)

    def test_load_project_context_uses_remembered_requirements_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "docs" / "requirements.md"
            requirements.parent.mkdir(parents=True)
            requirements.write_text("Backend API endpoints\n", encoding="utf-8")
            memory_dir = root / ".skilgen" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "current_run.json").write_text(
                json.dumps({"requirements_path": str(requirements.resolve())}),
                encoding="utf-8",
            )
            context = load_project_context(root, None)
            self.assertEqual(context.requirements_path, requirements.resolve())
            self.assertNotEqual(context.requirements_path.name, "CODEBASE_ONLY")


if __name__ == "__main__":
    unittest.main()
