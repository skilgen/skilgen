from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.parsers.incident import (
    IncidentParseError,
    fetch_github_incident_issues,
    parse_incident_sources,
    parse_markdown_postmortem,
    parse_pagerduty_export,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class IncidentParserTests(unittest.TestCase):
    def test_parse_structured_markdown_postmortem(self) -> None:
        incident = parse_markdown_postmortem(FIXTURES / "postmortem_database_outage.md")

        self.assertEqual(incident.title, "Database Outage PIR")
        self.assertIsNone(incident.service_domain)
        self.assertIn("database outage", incident.incident_patterns)
        self.assertIn("The primary Postgres cluster rejected write connections", incident.description)
        self.assertTrue(any("Error budget burn alert fired" in item for item in incident.timeline_evidence))
        self.assertIn("Connection pool saturation exhausted writer slots on the primary database.", incident.root_cause_patterns)
        self.assertTrue(any("backfills during peak traffic" in item for item in incident.check_paths))
        self.assertTrue(any("Runbook links" in item for item in incident.success_patterns))
        self.assertTrue(any("concurrency budget" in item for item in incident.anti_patterns))

    def test_parse_markdown_derives_service_domain_from_title(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "payments-service-incident.md"
            path.write_text(
                "\n".join(
                    [
                        "# Payments Service Incident Postmortem",
                        "",
                        "## Summary",
                        "Payment authorization requests failed for card users.",
                        "",
                        "## Root Cause",
                        "- A provider credential rotated without a matching deploy.",
                    ]
                ),
                encoding="utf-8",
            )

            incident = parse_markdown_postmortem(path)

        self.assertEqual(incident.service_domain, "payments")
        self.assertEqual(incident.incident_patterns, [])
        self.assertIn("provider credential rotated", incident.root_cause_patterns[0])

    def test_parse_pagerduty_export_metrics(self) -> None:
        analysis = parse_pagerduty_export(FIXTURES / "pagerduty_export.json")

        self.assertEqual(len(analysis.incidents), 4)
        self.assertIsNotNone(analysis.pagerduty_metrics)
        metrics = analysis.pagerduty_metrics
        assert metrics is not None
        self.assertEqual(metrics.urgency_groups["high"], ["Checkout Service P1 outage", "Checkout Service P2 latency"])
        self.assertEqual(metrics.urgency_groups["low"], ["Search Service P3 degraded", "Billing API P4 alert"])
        self.assertEqual(metrics.mean_time_to_resolve_minutes["P1"], 30)
        self.assertEqual(metrics.mean_time_to_resolve_minutes["P2"], 45)
        self.assertEqual(metrics.mean_time_to_resolve_minutes["P3"], 120)
        self.assertEqual(metrics.mean_time_to_resolve_minutes["P4"], 20)
        self.assertEqual(metrics.incidents_per_month, {"2026-01": 2, "2026-02": 2})
        self.assertIn("checkout (2 incidents)", metrics.common_title_clusters)

    def test_parse_incident_sources_discovers_markdown_and_pagerduty_fixtures(self) -> None:
        analysis = parse_incident_sources([FIXTURES])

        self.assertEqual(len(analysis.incidents), 5)
        self.assertTrue(any("Promote database pool saturation alerts" in item for item in analysis.check_paths))
        self.assertIn("database outage", analysis.incident_patterns)
        self.assertIsNotNone(analysis.pagerduty_metrics)
        self.assertTrue(any("PagerDuty incidents in 2026-01: 2" in item for item in analysis.patterns))

    def test_malformed_sources_raise_helpful_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            malformed_markdown = root / "incident-notes.md"
            malformed_markdown.write_text("# Notes\n\n## Random\nNo postmortem fields here.\n", encoding="utf-8")
            malformed_json = root / "pagerduty_export.json"
            malformed_json.write_text('{"incidents": [', encoding="utf-8")

            with self.assertRaisesRegex(IncidentParseError, "recognizable postmortem sections"):
                parse_markdown_postmortem(malformed_markdown)
            with self.assertRaisesRegex(IncidentParseError, "Invalid PagerDuty JSON export"):
                parse_pagerduty_export(malformed_json)

    def test_empty_sources_raise_helpful_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty_markdown = root / "empty-incident.md"
            empty_markdown.write_text("", encoding="utf-8")
            empty_json = root / "pagerduty_export.json"
            empty_json.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(IncidentParseError, "empty"):
                parse_markdown_postmortem(empty_markdown)
            with self.assertRaisesRegex(IncidentParseError, "does not contain incidents"):
                parse_pagerduty_export(empty_json)

    @patch.dict("os.environ", {}, clear=True)
    def test_github_helper_is_noop_without_env_token(self) -> None:
        self.assertEqual(fetch_github_incident_issues("owner/repo"), [])


if __name__ == "__main__":
    unittest.main()
