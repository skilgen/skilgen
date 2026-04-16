from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest


class ArchitectureCliTests(unittest.TestCase):
    def test_architecture_command_outputs_markdown_and_json_export(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Support COBOL transaction flows and backend services.\n", encoding="utf-8")
            (root / "cobol" / "transactions").mkdir(parents=True)
            (root / "cobol" / "transactions" / "customer_lookup.cbl").write_text(
                "IDENTIFICATION DIVISION.\nPROGRAM-ID. CUSTOMER-LOOKUP.\nPROCEDURE DIVISION.\nDISPLAY 'OK'.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                "architecture",
                "--project-root",
                str(root),
                "--requirements",
                str(requirements),
                "--graph-file",
                str(root / "architecture.mmd"),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# Architecture", result.stdout)
            self.assertTrue((root / "architecture.mmd").exists())
            json_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "architecture",
                    "--project-root",
                    str(root),
                    "--requirements",
                    str(requirements),
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(json_result.stdout)
            self.assertIn("architecture", payload)
            self.assertIn("evidence_graph", payload)
            self.assertIn("graph_export", payload)
            self.assertTrue(payload["architecture"]["domains"])
            self.assertIn("materialization_plan", payload["architecture"])
            self.assertIn("parser_summary", payload["evidence_graph"])
            self.assertIn("html", payload["graph_export"])

    def test_architecture_command_writes_html_graph_export(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Support backend services and frontend routes.\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "service.py").write_text(
                "class BillingService:\n    pass\n\ndef sync_payments():\n    return True\n",
                encoding="utf-8",
            )
            html_graph = root / "architecture.html"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "architecture",
                    "--project-root",
                    str(root),
                    "--requirements",
                    str(requirements),
                    "--graph-format",
                    "html",
                    "--graph-file",
                    str(html_graph),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            html = html_graph.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html.lower())
            self.assertIn("Skill Materialization Plan", html)
            self.assertIn("Parser Backends", html)


if __name__ == "__main__":
    unittest.main()
