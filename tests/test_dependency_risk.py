from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from skilgen.core.dependency_risk import build_dependency_risk_graph


class DependencyRiskTests(unittest.TestCase):
    def test_dependency_risk_graph_detects_cycles_and_manifest_risks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app").mkdir()
            (root / "app" / "__init__.py").write_text("", encoding="utf-8")
            (root / "app" / "a.py").write_text("from . import b\n", encoding="utf-8")
            (root / "app" / "b.py").write_text("from . import a\n", encoding="utf-8")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "left-pad": "^1.3.0",
                            "react": "^18.0.0",
                        }
                    }
                ),
                encoding="utf-8",
            )

            graph = build_dependency_risk_graph(root)

            self.assertTrue(graph.cycles)
            self.assertTrue(any(node.id == "package:left-pad" for node in graph.nodes))
            left_pad = next(node for node in graph.nodes if node.id == "package:left-pad")
            self.assertTrue(any(signal.startswith("deprecated:") for signal in left_pad.signals))
            self.assertTrue(any(edge.target == "package:left-pad" for edge in graph.edges))


if __name__ == "__main__":
    unittest.main()
