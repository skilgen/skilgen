from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import UTC, datetime, timedelta
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
            self.assertIn("data-radial='analytics'", html)
            self.assertIn("ops-tab active", html)
            self.assertIn("surface-tab active", html)
            self.assertIn("graph-copy active", html)
            self.assertIn(".page{max-width:1500px", html)
            self.assertLess(html.index("Usage Analytics"), html.index("Graph Studio"))
            self.assertEqual(html.count("data-copy='evidence'"), 1)
            self.assertIn("data-detail='architecture'", html)
            self.assertIn("data-detail='evidence'", html)
            self.assertIn("data-detail='dependencies'", html)
            self.assertIn("data-detail='skills'", html)
            self.assertIn("data-copy-title='architecture'", html)
            self.assertIn("data-copy-body='architecture'", html)
            self.assertIn("setDetail=(", html)
            self.assertIn("Agent Intelligence Surface", html)
            self.assertEqual(html.count("aria-label='Skilgen logo'"), 1)
            self.assertIn("&copy; Skilgen", html)
            self.assertIn("Skill Usage", html)
            self.assertIn("usage + depth + content", html)
            self.assertTrue(
                any(
                    marker in html
                    for marker in (
                        "No meaningful trend yet",
                        "Improving compared with the previous snapshot.",
                        "Falling compared with the previous snapshot.",
                        "This is the current baseline.",
                    )
                )
            )
            self.assertIn("Architecture ·", html)
            self.assertIn("Dependency Network", html)
            self.assertIn("Usage ·", html)

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

    def test_dashboard_trend_collapses_repeated_delivery_snapshots(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Track architecture, evidence, and analytics.\n", encoding="utf-8")
            (root / "api").mkdir()
            (root / "api" / "service.py").write_text("def handler():\n    return True\n", encoding="utf-8")
            score_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "score",
                    "--project-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            current_score = json.loads(score_result.stdout)
            history_dir = root / ".skilgen" / "state"
            history_dir.mkdir(parents=True, exist_ok=True)
            base = datetime(2026, 4, 12, 15, 53, 0, tzinfo=UTC)
            snapshots = []
            for index in range(8):
                snapshots.append(
                    json.dumps(
                        {
                            "timestamp": (base + timedelta(seconds=index)).isoformat(),
                            "source": "delivery",
                            "score": current_score["score"],
                            "raw_score": current_score["raw_score"],
                            "rating": current_score["rating"],
                            "domain_scores": {entry["domain"]: entry["score"] for entry in current_score.get("domains", [])},
                        }
                    )
                )
            (history_dir / "score-history.jsonl").write_text("\n".join(snapshots) + "\n", encoding="utf-8")

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
            html = payload["html"]
            self.assertNotIn(">delivery<", html)
            self.assertIn("No meaningful trend yet", html)
            self.assertLessEqual(html.count("<div class='spark-point'"), 2)


if __name__ == "__main__":
    unittest.main()
