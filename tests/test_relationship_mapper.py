from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.relationship_mapper import build_import_graph


class RelationshipMapperTests(unittest.TestCase):
    def test_build_import_graph_collects_python_imports(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("import json\nfrom pathlib import Path\n", encoding="utf-8")
            graph = build_import_graph(root)
            self.assertIn("app.py", graph)
            self.assertIn("json", graph["app.py"])
            self.assertIn("pathlib", graph["app.py"])

    def test_build_import_graph_ignores_external_skill_sources(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("import json\n", encoding="utf-8")
            external = root / ".skilgen" / "external-skills" / "sources" / "anthropic-skills" / "skills" / "docx" / "scripts"
            external.mkdir(parents=True)
            (external / "pack.py").write_text("import argparse\n", encoding="utf-8")

            graph = build_import_graph(root)

            self.assertIn("app.py", graph)
            self.assertNotIn(".skilgen/external-skills/sources/anthropic-skills/skills/docx/scripts/pack.py", graph)

    def test_build_import_graph_resolves_repo_local_ts_imports(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "routes").mkdir(parents=True)
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "routes" / "dashboard.tsx").write_text(
                "import { SkillCard } from '../components/SkillCard';\nexport default function Dashboard(){ return SkillCard(); }\n",
                encoding="utf-8",
            )
            (root / "src" / "components" / "SkillCard.tsx").write_text("export function SkillCard(){ return null; }\n", encoding="utf-8")

            graph = build_import_graph(root)

            self.assertIn("src/routes/dashboard.tsx", graph)
            self.assertIn("src/components/SkillCard.tsx", graph["src/routes/dashboard.tsx"])

    def test_build_import_graph_ignores_invalid_utf8_python_bytes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_bytes(b"import json\n# \xb1\n")

            graph = build_import_graph(root)

            self.assertIn("app.py", graph)
            self.assertIn("json", graph["app.py"])


if __name__ == "__main__":
    unittest.main()
