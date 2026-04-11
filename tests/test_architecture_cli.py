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


if __name__ == "__main__":
    unittest.main()
