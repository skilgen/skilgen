from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from skilgen.core.runtime_signals import collect_runtime_signals


class RuntimeSignalsTests(unittest.TestCase):
    def test_collect_runtime_signals_ingests_coverage_junit_sarif_and_traces(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "billing.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "reports").mkdir()
            (root / "reports" / "coverage.xml").write_text(
                "\n".join(
                    [
                        "<coverage>",
                        "  <packages>",
                        "    <package>",
                        "      <classes>",
                        "        <class filename=\"src/billing.py\" line-rate=\"0.75\" />",
                        "      </classes>",
                        "    </package>",
                        "  </packages>",
                        "</coverage>",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "reports" / "junit.xml").write_text(
                "\n".join(
                    [
                        "<testsuite tests=\"2\" failures=\"1\">",
                        "  <testcase classname=\"src.billing\" file=\"src/billing.py\" name=\"test_run\" />",
                        "  <testcase classname=\"src.billing\" file=\"src/billing.py\" name=\"test_error\"><failure /></testcase>",
                        "</testsuite>",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "reports" / "findings.sarif").write_text(
                json.dumps(
                    {
                        "runs": [
                            {
                                "results": [
                                    {
                                        "ruleId": "PY001",
                                        "level": "error",
                                        "locations": [
                                            {
                                                "physicalLocation": {
                                                    "artifactLocation": {"uri": "src/billing.py"}
                                                }
                                            }
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (root / "reports" / "otel-traces.json").write_text(
                json.dumps(
                    {
                        "resourceSpans": [
                            {
                                "resource": {
                                    "attributes": [
                                        {"key": "service.name", "value": {"stringValue": "billing-api"}}
                                    ]
                                },
                                "scopeSpans": [
                                    {
                                        "spans": [
                                            {
                                                "name": "run",
                                                "attributes": [
                                                    {"key": "code.filepath", "value": {"stringValue": "src/billing.py"}}
                                                ],
                                            }
                                        ]
                                    }
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            signals = collect_runtime_signals(root)

            self.assertEqual(signals.coverage_by_path["src/billing.py"], 0.75)
            self.assertEqual(signals.test_results["src/billing.py"]["failed"], 1)
            self.assertIn("error:PY001", signals.sast_findings["src/billing.py"])
            self.assertIn("billing-api", signals.trace_services)
            self.assertEqual(len(signals.artifacts), 4)


if __name__ == "__main__":
    unittest.main()
