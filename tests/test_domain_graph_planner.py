from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.agents.domain_graph_planner import build_domain_graph
from skilgen.core.requirements import load_requirements


class DomainGraphPlannerTests(unittest.TestCase):
    def test_build_domain_graph_infers_platform_domains_for_tool_repo_shapes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "README.md"
            requirements.write_text("Skilgen style tooling repo with backend api and planning.\n", encoding="utf-8")
            (root / "skilgen").mkdir()
            (root / "skilgen" / "__init__.py").write_text("", encoding="utf-8")
            (root / "skilgen" / "sdk.py").write_text("VALUE = 1\n", encoding="utf-8")
            for area, file_name in [
                ("agents", "planner.py"),
                ("core", "score.py"),
                ("cli", "main.py"),
                ("generators", "skills.py"),
            ]:
                directory = root / "skilgen" / area
                directory.mkdir(parents=True)
                (directory / file_name).write_text("def run():\n    return None\n", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "run_requirements_pipeline.py").write_text("print('ok')\n", encoding="utf-8")

            graph = build_domain_graph(root, load_requirements(requirements))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("platform", graph_names)
            self.assertIn("platform-agents", graph_names)
            self.assertIn("platform-core", graph_names)
            self.assertIn("platform-cli", graph_names)
            self.assertIn("platform-generators", graph_names)
            self.assertIn("platform-scripts", graph_names)

    def test_build_domain_graph_passes_code_evidence_to_llm_prompt(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Support COBOL transaction flows.\n", encoding="utf-8")
            (root / "cobol" / "transactions").mkdir(parents=True)
            (root / "cobol" / "transactions" / "customer_lookup.cbl").write_text(
                "IDENTIFICATION DIVISION.\nPROGRAM-ID. CUSTOMER-LOOKUP.\nPROCEDURE DIVISION.\nDISPLAY 'OK'.\n",
                encoding="utf-8",
            )
            (root / "copybooks").mkdir(parents=True)
            (root / "copybooks" / "customer_record.cpy").write_text(
                "01 CUSTOMER-RECORD.\n   05 CUSTOMER-ID PIC X(10).\n",
                encoding="utf-8",
            )

            captured: dict[str, str] = {}

            def fake_run_deep_json(task: str, prompt: str, fallback, *, project_root: str | Path = ".") -> dict[str, object]:
                captured["task"] = task
                captured["prompt"] = prompt
                return fallback()

            with patch("skilgen.agents.domain_graph_planner.run_deep_json", side_effect=fake_run_deep_json):
                graph = build_domain_graph(root, load_requirements(requirements))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("backend", graph_names)
            self.assertIn("backend-copybooks", graph_names)
            self.assertIn("Code evidence JSON:", captured["prompt"])
            self.assertIn("PROGRAM-ID. CUSTOMER-LOOKUP.", captured["prompt"])
            self.assertIn("customer_record.cpy", captured["prompt"])


if __name__ == "__main__":
    unittest.main()
