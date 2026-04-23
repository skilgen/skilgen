from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from skilgen.parsers.confluence import parse_confluence_file, parse_confluence_source
from skilgen.parsers.notion import parse_notion_api_json, parse_notion_file, parse_notion_source
from skilgen.parsers.runbook import ProcessParserError, parse_runbook_file, parse_runbook_source


FIXTURES = Path(__file__).parent / "fixtures"


class RunbookParserTests(unittest.TestCase):
    def test_parse_runbook_file_extracts_process_guidance(self) -> None:
        source = parse_runbook_file(FIXTURES / "runbook_deploy.md")

        self.assertEqual(source.source_type, "runbook")
        self.assertEqual(source.title, "Deploy Service Runbook")
        self.assertEqual(source.description, "Use this runbook when deploying the payments API to production.")
        self.assertIn("Confirm the release candidate and freeze window.", source.steps)
        self.assertTrue(any("Check /health returns 200" in item for item in source.check_paths))
        self.assertTrue(any("Do NOT skip the database backup." in item for item in source.anti_patterns))
        self.assertTrue(any("kubectl rollout status" in item for item in source.evidence))
        self.assertIn("owner", source.metadata)

    def test_parse_runbook_source_supports_runbook_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs" / "runbooks"
            root.mkdir(parents=True)
            target = root / "deploy.md"
            target.write_text((FIXTURES / "runbook_deploy.md").read_text(encoding="utf-8"), encoding="utf-8")

            parsed = parse_runbook_source(Path(tmp))

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].title, "Deploy Service Runbook")

    def test_parse_runbook_file_rejects_malformed_frontmatter(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.md"
            path.write_text("---\nowner: ops\n# Missing close\n", encoding="utf-8")

            with self.assertRaisesRegex(ProcessParserError, "frontmatter"):
                parse_runbook_file(path)

    def test_parse_runbook_file_rejects_empty_sources(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.md"
            path.write_text(" \n", encoding="utf-8")

            with self.assertRaisesRegex(ProcessParserError, "empty"):
                parse_runbook_file(path)


class ConfluenceParserTests(unittest.TestCase):
    def test_parse_confluence_html_extracts_labels_code_tables_and_sections(self) -> None:
        source = parse_confluence_file(FIXTURES / "confluence_page.html")

        self.assertEqual(source.source_type, "confluence")
        self.assertEqual(source.title, "Payments Deploy Procedure")
        self.assertIn("payments", source.labels)
        self.assertIn("Open the approved release ticket.", source.steps)
        self.assertTrue(any("Confirm every region reports healthy." in item for item in source.check_paths))
        self.assertTrue(any("Avoid deploying during the freeze window." in item for item in source.anti_patterns))
        self.assertTrue(any("helm upgrade payments" in item for item in source.evidence))
        self.assertTrue(any("Signal | Expected" in item for item in source.evidence))

    def test_parse_confluence_source_supports_zip_exports(self) -> None:
        with TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "confluence.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.write(FIXTURES / "confluence_page.html", arcname="pages/confluence_page.html")

            parsed = parse_confluence_source(archive_path)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].title, "Payments Deploy Procedure")

    def test_parse_confluence_xml_extracts_export_content(self) -> None:
        source = parse_confluence_file(FIXTURES / "confluence_page.xml")

        self.assertEqual(source.title, "Incident Response Procedure")
        self.assertIn("incident", source.labels)
        self.assertTrue(any("curl https://status.example.com/incidents" in item for item in source.evidence))

    def test_parse_confluence_file_rejects_malformed_xml(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.xml"
            path.write_text("<confluence><page>", encoding="utf-8")

            with self.assertRaisesRegex(ProcessParserError, "Could not parse Confluence XML"):
                parse_confluence_file(path)

    def test_parse_confluence_file_rejects_empty_sources(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.html"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ProcessParserError, "empty"):
                parse_confluence_file(path)


class NotionParserTests(unittest.TestCase):
    def test_parse_notion_markdown_export_extracts_process_guidance(self) -> None:
        source = parse_notion_file(FIXTURES / "notion_export.md")

        self.assertEqual(source.source_type, "notion")
        self.assertEqual(source.title, "Database Failover Checklist")
        self.assertIn("Announce the maintenance window.", source.steps)
        self.assertTrue(any("Confirm writer endpoint resolves" in item for item in source.check_paths))
        self.assertTrue(any("Never promote a lagging replica." in item for item in source.anti_patterns))
        self.assertTrue(any("select pg_is_in_recovery" in item for item in source.evidence))

    def test_parse_notion_source_supports_export_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "notion-export"
            root.mkdir()
            target = root / "database-failover.md"
            target.write_text((FIXTURES / "notion_export.md").read_text(encoding="utf-8"), encoding="utf-8")

            parsed = parse_notion_source(root)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].title, "Database Failover Checklist")

    def test_parse_notion_api_json_extracts_page_blocks_and_labels(self) -> None:
        payload = {
            "page": {
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "API Incident Checklist"}]},
                    "Tags": {"type": "multi_select", "multi_select": [{"name": "incident"}, {"name": "api"}]},
                }
            },
            "blocks": [
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "API response playbook."}]}},
                {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "Steps"}]}},
                {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"plain_text": "Check API latency."}]}},
                {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "Validation"}]}},
                {"type": "to_do", "to_do": {"rich_text": [{"plain_text": "Confirm SLO burn rate recovered."}], "checked": False}},
            ],
        }

        source = parse_notion_api_json(payload)

        self.assertEqual(source.title, "API Incident Checklist")
        self.assertIn("api", source.labels)
        self.assertIn("Check API latency.", source.steps)
        self.assertTrue(any("Confirm SLO burn rate recovered." in item for item in source.check_paths))

    def test_parse_notion_file_rejects_malformed_json(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text("{not-json", encoding="utf-8")

            with self.assertRaisesRegex(ProcessParserError, "Could not parse Notion JSON"):
                parse_notion_file(path)

    def test_parse_notion_file_rejects_empty_sources(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.md"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ProcessParserError, "empty"):
                parse_notion_file(path)

    def test_parse_notion_api_json_rejects_empty_payload(self) -> None:
        with self.assertRaisesRegex(ProcessParserError, "empty"):
            parse_notion_api_json(json.loads("{}"))


if __name__ == "__main__":
    unittest.main()
