from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest


class DashboardCliTests(unittest.TestCase):
    def test_dashboard_command_writes_branded_html(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Support backend APIs, dashboard flows, and quality scoring.\n", encoding="utf-8")
            (root / "src" / "routes").mkdir(parents=True)
            (root / "src" / "routes" / "dashboard.tsx").write_text(
                "export default function Dashboard() { return null; }\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "deliver",
                    "--project-root",
                    str(root),
                    "--requirements",
                    str(requirements),
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            output_path = (root / "dashboard.html").resolve()
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "dashboard",
                    "--project-root",
                    str(root),
                    "--requirements",
                    str(requirements),
                    "--output",
                    str(output_path),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["dashboard_file"], str(output_path))
            html = output_path.read_text(encoding="utf-8")
            self.assertIn("Skilgen Operating System", html)
            self.assertIn("All your skill intelligence", html)
            self.assertIn("Graph Studio", html)
            self.assertIn("Architecture Sunburst", html)
            self.assertIn("Evidence Flow", html)
            self.assertIn("d3-sankey", html)
            self.assertIn("skilgen-dashboard.html", html)
            self.assertIn("trend-ticks", html)
            self.assertIn("data-sankey='skills'", html)
            self.assertIn("ops-tab active", html)
            self.assertIn("surface-tab active", html)
            self.assertIn("graph-copy active", html)
            self.assertIn(".page{max-width:1500px", html)
            self.assertLess(html.index("Usage Analytics"), html.index("Graph Studio"))

    def test_dashboard_command_json_payload_contains_html_and_graphs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Track architecture, evidence, and analytics.\n", encoding="utf-8")
            (root / "api").mkdir()
            (root / "api" / "service.py").write_text("def handler():\n    return True\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "dashboard",
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
            payload = json.loads(result.stdout)
            self.assertIn("html", payload)
            self.assertIn("graph_export", payload)
            self.assertIn("dependencies", payload["graph_export"])


if __name__ == "__main__":
    unittest.main()
