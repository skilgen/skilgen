from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import UTC, datetime, timedelta
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from skilgen.autoupdate import stop_auto_update_worker
from skilgen.cli.main import main
from skilgen.generators.package import _analysis_bundle, render_dependency_network_data
from skilgen.core.requirements import load_project_context


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
            try:
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
                self.assertEqual(html.count("Skilgen Operating System"), 1)
                self.assertIn("The Pulse", html)
                self.assertIn("The Foundry", html)
                self.assertIn("Graph Studio", html)
                self.assertIn("Architecture Sunburst", html)
                self.assertIn("Evidence Flow", html)
                self.assertIn("d3-sankey", html)
                self.assertIn("skilgen-dashboard.html", html)
                self.assertIn("trend-ticks", html)
                self.assertIn("data-sankey='skills'", html)
                self.assertIn("data-radial='analytics'", html)
                self.assertIn("data-detail='analytics'", html)
                self.assertIn("role='tab'", html)
                self.assertIn("role='tabpanel'", html)
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
                self.assertTrue(any(marker in html for marker in ("Modeled attention", "Live usage")))
                self.assertTrue(any(marker in html for marker in ("depth + content", "content signal only")))
                self.assertNotIn(">---<", html)
                self.assertTrue(
                    any(
                        marker in html
                        for marker in (
                            "No meaningful trend yet",
                            "Stable across recent snapshots.",
                            "Improving compared with the previous snapshot.",
                            "Falling compared with the previous snapshot.",
                            "This is the current baseline.",
                        )
                    )
                )
                self.assertIn("Architecture ·", html)
                self.assertIn("Dependency Explorer", html)
                self.assertIn("Bubble — who's the chokepoint?", html)
                self.assertIn("Cycle — where's the risk?", html)
                self.assertIn("Matrix — domain coupling", html)
                self.assertIn("Usage ·", html)
                self.assertIn("Recommended profiles", html)
                self.assertIn("No git metadata; freshness is file-state based", html)
                self.assertIn("viewportWidth", html)
                self.assertIn("integrity='sha384-", html)
                self.assertIn("aria-label='Interactive dependency explorer showing chokepoints, cycles, and domain coupling.'", html)
                self.assertNotIn("vis-network.min.js", html)
                self.assertNotIn("Architecture Legend", html)
                self.assertNotIn("Outer rings represent planned or generated child skills.", html)
                self.assertTrue(any(marker in html for marker in ("Live Usage", "Modeled Usage")))
                self.assertNotIn(">No diff since baseline<", html)
            finally:
                stop_auto_update_worker(root)

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

    def test_dependency_network_payload_uses_explorer_shape(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Track dependency coupling and chokepoints.\n", encoding="utf-8")
            (root / "core").mkdir()
            (root / "agents").mkdir()
            (root / "api").mkdir()
            (root / "core" / "models.py").write_text("class Model:\n    pass\n", encoding="utf-8")
            (root / "core" / "helpers.py").write_text("from core.models import Model\n", encoding="utf-8")
            (root / "agents" / "runner.py").write_text("from core.models import Model\nfrom api.server import run\n", encoding="utf-8")
            (root / "api" / "server.py").write_text("from core.helpers import Model\nfrom agents.runner import run\n", encoding="utf-8")

            context = load_project_context(root, requirements)
            bundle = _analysis_bundle(context, root)
            payload = render_dependency_network_data(context, root, bundle)

            self.assertEqual(sorted(payload.keys()), ["domainCoupling", "edges", "nodes"])
            self.assertTrue(payload["nodes"])
            self.assertTrue(payload["edges"])
            self.assertTrue(payload["domainCoupling"])
            first_node = payload["nodes"][0]
            self.assertTrue({"id", "fanIn", "fanOut", "risk", "domain", "inCycle"} <= set(first_node))
            self.assertIn(first_node["risk"], {"high", "med", "low"})
            first_edge = payload["edges"][0]
            self.assertTrue({"source", "target", "isCycle"} <= set(first_edge))
            first_coupling = payload["domainCoupling"][0]
            self.assertTrue({"from", "to", "count"} <= set(first_coupling))

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
            self.assertIn("Score has stayed at", html)
            self.assertLessEqual(html.count("<div class='spark-point'"), 2)
            self.assertIn(">Stable<", html)

    def test_dashboard_command_handles_fallback_payload_shapes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_path = root / "dashboard.html"
            stdout = StringIO()
            stderr = StringIO()
            payload = {
                "html": "<html><body>fallback</body></html>",
                "score": 7,
                "graphs": {"domain_graph": {"nodes": []}},
                "architecture": {"domainSummary": {"backend": {"confidence": 0.8}}},
            }

            with (
                patch("skilgen.cli.main.dashboard_payload", return_value=payload),
                patch("skilgen.cli.main.current_runtime_mode", return_value="model_backed"),
                patch.object(sys, "argv", ["skilgen", "dashboard", "--project-root", str(root), "--output", str(output_path)]),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                main()

            result = json.loads(stdout.getvalue())
            self.assertEqual(result["dashboard_file"], str(output_path.resolve()))
            self.assertEqual(result["headline"], f"Dashboard for {root.name}")
            self.assertEqual(result["score"], 7)
            self.assertEqual(result["stale_skill_count"], 0)
            self.assertEqual(result["graph_panels"], ["domain_graph"])
            self.assertEqual(output_path.read_text(encoding="utf-8"), "<html><body>fallback</body></html>")


if __name__ == "__main__":
    unittest.main()
