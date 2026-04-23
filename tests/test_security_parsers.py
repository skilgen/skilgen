"""Coverage for Pillar 4 security and compliance parsers."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from skilgen.parsers.sarif import parse_sarif
from skilgen.parsers.sbom import parse_sbom
from skilgen.parsers.security_policy import parse_security_policy


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class SarifParserTests(unittest.TestCase):
    def test_parse_sarif_extracts_tools_rules_cwes_paths_and_patterns(self) -> None:
        result = parse_sarif(FIXTURES / "semgrep_results.sarif")

        self.assertEqual(result.tools[0].name, "Semgrep")
        self.assertEqual(result.tools[0].version, "1.75.0")
        self.assertIn("python.lang.security.audit.sql-injection", result.rule_ids)
        self.assertEqual(result.severities["error"], 1)
        self.assertEqual(result.severities["warning"], 1)
        self.assertEqual(result.cwes, ["CWE-79", "CWE-89"])
        self.assertEqual(result.file_paths, ["src/app.py", "src/templates.py"])
        self.assertIn("injection", result.categories)
        self.assertIn("security", result.tags)
        self.assertTrue(any("Configured SARIF tool: Semgrep 1.75.0" == item for item in result.patterns))
        self.assertIn("Injection-prone input handling", result.anti_patterns)
        self.assertIn("Cross-site scripting exposure", result.anti_patterns)
        self.assertFalse(any("redacted by parser tests" in str(finding) for finding in result.findings))

    def test_parse_sarif_rejects_malformed_json(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.sarif"
            path.write_text("{not-json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "SARIF JSON is invalid"):
                parse_sarif(path)

    def test_parse_sarif_rejects_empty_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.sarif"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "SARIF file .* is empty"):
                parse_sarif(path)


class SbomParserTests(unittest.TestCase):
    def test_parse_cyclonedx_json_extracts_inventory_risk_keys_and_license_issues(self) -> None:
        result = parse_sbom(FIXTURES / "cyclonedx_bom.json")

        self.assertEqual(result.format, "CycloneDX")
        self.assertEqual(result.spec_version, "1.5")
        self.assertEqual(result.package_count, 3)
        self.assertEqual(result.package_count_by_ecosystem["pip"], 1)
        self.assertEqual(result.package_count_by_ecosystem["npm"], 1)
        self.assertEqual(result.package_count_by_ecosystem["cpe"], 1)
        self.assertEqual(result.license_distribution["NOASSERTION"], 1)
        self.assertIn("django", result.purl_evidence)
        self.assertIn("openssl", result.cpe_evidence)
        self.assertIn("pip:django", result.dependency_risk_keys)
        self.assertIn("npm:left-pad", result.dependency_risk_keys)
        self.assertIn("Package `left-pad` has no declared license", result.anti_patterns)
        self.assertIn("Package `openssl` declares copyleft license `Apache-2.0 OR GPL-2.0`", result.anti_patterns)

    def test_parse_spdx_json_extracts_purls_cpes_and_copyleft(self) -> None:
        result = parse_sbom(FIXTURES / "spdx_sbom.json")

        self.assertEqual(result.format, "SPDX")
        self.assertEqual(result.spec_version, "SPDX-2.3")
        self.assertEqual(result.package_count, 3)
        self.assertEqual(result.package_count_by_ecosystem["pip"], 1)
        self.assertEqual(result.package_count_by_ecosystem["cpe"], 1)
        self.assertIn("requests", result.purl_evidence)
        self.assertIn("gpl-helper", result.cpe_evidence)
        self.assertIn("Package `internal-tool` has no declared license", result.anti_patterns)
        self.assertIn("Package `gpl-helper` declares copyleft license `GPL-3.0-only`", result.anti_patterns)

    def test_parse_cyclonedx_xml_is_supported(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bom.xml"
            path.write_text(
                """<?xml version="1.0"?>
<bom xmlns="http://cyclonedx.org/schema/bom/1.5" version="1">
  <components>
    <component type="library">
      <name>urllib3</name>
      <version>2.2.1</version>
      <purl>pkg:pypi/urllib3@2.2.1</purl>
      <licenses><license><id>MIT</id></license></licenses>
    </component>
  </components>
</bom>
""",
                encoding="utf-8",
            )

            result = parse_sbom(path)

            self.assertEqual(result.format, "CycloneDX")
            self.assertEqual(result.package_count, 1)
            self.assertEqual(result.package_count_by_ecosystem["pip"], 1)
            self.assertIn("pip:urllib3", result.dependency_risk_keys)

    def test_parse_sbom_rejects_malformed_json(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not-json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "SBOM JSON is invalid"):
                parse_sbom(path)

    def test_parse_sbom_rejects_empty_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.json"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "SBOM file .* is empty"):
                parse_sbom(path)


class SecurityPolicyParserTests(unittest.TestCase):
    def test_parse_structured_security_policy_maps_controls_to_patterns(self) -> None:
        result = parse_security_policy(FIXTURES / "security_policy.yml")

        self.assertEqual(result.kind, "structured-policy")
        self.assertEqual(result.blocked_licenses, ["AGPL-3.0", "GPL-3.0-only"])
        self.assertIn("pip:requests", result.approved_packages)
        self.assertIn("npm:@company/design-system", result.approved_packages)
        self.assertIn("Strict-Transport-Security", result.required_headers)
        self.assertIn("https://app.example.com", result.allowed_origins)
        self.assertIn("Forbidden pattern policy includes `eval(`", result.anti_patterns)
        self.assertIn("Blocked license policy includes `AGPL-3.0`", result.anti_patterns)
        self.assertIn("Required header policy includes `Content-Security-Policy`", result.patterns)

    def test_parse_security_md_extracts_reporting_process(self) -> None:
        result = parse_security_policy(FIXTURES / "SECURITY.md")

        self.assertEqual(result.kind, "security-md")
        self.assertIn("security@example.com", result.process["contacts"])
        self.assertIn("2 business days", result.process["response_timelines"])
        self.assertIn("coordinated disclosure", result.process["disclosure_terms"])
        self.assertTrue(result.process["supported_versions"])
        self.assertFalse(result.anti_patterns)

    def test_parse_json_security_policy(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(
                json.dumps(
                    {
                        "blocked_licenses": ["SSPL-1.0"],
                        "approved_packages": ["pip:requests"],
                        "forbidden_patterns": ["pickle.loads"],
                        "required_headers": {"http": ["Strict-Transport-Security"]},
                        "allowed_origins": ["https://example.com"],
                    }
                ),
                encoding="utf-8",
            )

            result = parse_security_policy(path)

            self.assertIn("SSPL-1.0", result.blocked_licenses)
            self.assertIn("http:Strict-Transport-Security", result.required_headers)
            self.assertIn("Forbidden pattern policy includes `pickle.loads`", result.anti_patterns)

    def test_parse_security_policy_rejects_malformed_yaml(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.yml"
            path.write_text("blocked_licenses: [AGPL-3.0", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Security policy YAML is invalid"):
                parse_security_policy(path)

    def test_parse_security_policy_rejects_empty_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.yml"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Security policy .* is empty"):
                parse_security_policy(path)


if __name__ == "__main__":
    unittest.main()
