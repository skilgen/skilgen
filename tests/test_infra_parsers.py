from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.parsers.helm import HelmParserError, parse_helm_chart
from skilgen.parsers.kubernetes import KubernetesParserError, parse_kubernetes_manifests
from skilgen.parsers.terraform import TerraformParserError, parse_terraform_directory


FIXTURES = Path(__file__).parent / "fixtures"


class TerraformParserTests(unittest.TestCase):
    def test_parse_valid_terraform_directory(self) -> None:
        result = parse_terraform_directory(FIXTURES)

        self.assertEqual(result.resource_counts["aws_s3_bucket"], 1)
        self.assertEqual(result.resource_counts["kubernetes_namespace"], 1)
        self.assertEqual(result.resource_counts_by_category["cloud_infrastructure"], 2)
        self.assertEqual(result.resource_counts_by_category["k8s_infrastructure"], 1)
        self.assertIn("aws", result.providers)
        self.assertEqual(result.variables["environment"]["description"], "Deployment environment name.")
        self.assertTrue(result.variables["environment"]["has_validation"])
        self.assertIn("artifact_bucket", result.outputs)
        self.assertIn("vpc", result.modules)
        self.assertIn("s3", result.backend_config)
        self.assertIn("remote_state_backend", result.patterns)
        self.assertIn("variable_validation", result.patterns)
        self.assertIn("resource_without_tags:aws_iam_role.worker", result.anti_patterns)

    def test_parse_malformed_terraform_raises_helpful_error(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "main.tf").write_text('resource "aws_s3_bucket" "bad" {\n  bucket = "bad"\n', encoding="utf-8")

            with self.assertRaisesRegex(TerraformParserError, "Terraform parser"):
                parse_terraform_directory(path)

    def test_parse_empty_terraform_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            result = parse_terraform_directory(tmp)

        self.assertEqual(result.files, [])
        self.assertEqual(result.resource_counts, {})
        self.assertEqual(result.anti_patterns, [])


class KubernetesParserTests(unittest.TestCase):
    def test_parse_valid_kubernetes_manifests_without_secret_values(self) -> None:
        result = parse_kubernetes_manifests(FIXTURES / "k8s_deployment.yaml")

        self.assertEqual(result.counts_by_kind["Deployment"], 1)
        self.assertEqual(result.counts_by_kind["Secret"], 1)
        self.assertEqual(result.deployments[0].details["container_count"], 1)
        self.assertIn("resource_limits", result.patterns)
        self.assertIn("health_probes", result.patterns)
        self.assertIn("non_root_containers", result.patterns)
        self.assertEqual(result.secrets[0].details["keys"], ["password"])
        self.assertNotIn("super-secret-value", repr(result))
        self.assertIn("configmap_secret_key:app-config:API_TOKEN", result.anti_patterns)

    def test_parse_malformed_kubernetes_manifest_raises_helpful_error(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.yaml"
            path.write_text("apiVersion: v1\nkind: Service\nmetadata: [\n", encoding="utf-8")

            with self.assertRaisesRegex(KubernetesParserError, "Kubernetes parser"):
                parse_kubernetes_manifests(path)

    def test_parse_empty_kubernetes_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            result = parse_kubernetes_manifests(tmp)

        self.assertEqual(result.files, [])
        self.assertEqual(result.counts_by_kind, {})


class HelmParserTests(unittest.TestCase):
    def test_parse_valid_helm_chart(self) -> None:
        result = parse_helm_chart(FIXTURES / "helm_chart")

        self.assertEqual(result.chart_metadata["name"], "skillayer")
        self.assertEqual(result.dependencies[0]["name"], "postgresql")
        self.assertEqual(result.values_schema["image.repository"], "str")
        self.assertEqual(result.values_schema["service.port"], "int")
        self.assertEqual(result.template_kinds["Deployment"], 1)
        self.assertIn("skillayer.name", result.helpers)
        self.assertIn("pre-install", result.hooks)
        self.assertIn("template_values_configurability", result.patterns)
        self.assertIn("helm_hooks", result.patterns)
        self.assertIn("deprecated_api_version:templates/ingress.yaml:extensions/v1beta1", result.anti_patterns)
        self.assertNotIn("sk_live_secret", repr(result))

    def test_parse_malformed_helm_chart_raises_helpful_error(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "Chart.yaml").write_text("apiVersion: v2\nname: [\n", encoding="utf-8")

            with self.assertRaisesRegex(HelmParserError, "Helm parser"):
                parse_helm_chart(path)

    def test_parse_empty_helm_chart_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            result = parse_helm_chart(tmp)

        self.assertEqual(result.chart_metadata, {})
        self.assertEqual(result.values_schema, {})
        self.assertEqual(result.template_kinds, {})


if __name__ == "__main__":
    unittest.main()
