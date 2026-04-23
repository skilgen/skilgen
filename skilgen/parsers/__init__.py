"""Structured parsers for code-adjacent enterprise source artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from skilgen.parsers.dbt import DbtProjectAnalysis, DbtProjectParseError, parse_dbt_project
from skilgen.parsers.helm import HelmChartParseResult, HelmParserError, parse_helm_chart
from skilgen.parsers.kafka import KafkaAnalysis, KafkaParseError, parse_kafka_artifact
from skilgen.parsers.kubernetes import KubernetesManifestParseResult, KubernetesParserError, parse_kubernetes_manifests
from skilgen.parsers.runbook import ProcessParserError, ProcessSource, parse_runbook_file, parse_runbook_source
from skilgen.parsers.sarif import SarifFinding, SarifResult, SarifTool, parse_sarif
from skilgen.parsers.sbom import SbomPackage, SbomResult, parse_sbom
from skilgen.parsers.security_policy import SecurityPolicyResult, parse_security_policy
from skilgen.parsers.sql_schema import SqlSchemaAnalysis, SqlSchemaParseError, parse_sql_schema
from skilgen.parsers.terraform import TerraformParseResult, TerraformParserError, parse_terraform_directory


class ApiSpecParserError(ValueError):
    """Raised when an API specification cannot be parsed safely."""


@dataclass(frozen=True)
class ApiSpecFinding:
    """A parser finding with evidence suitable for generated skills."""

    category: str
    message: str
    evidence: list[str] = field(default_factory=list)
    location: str | None = None


@dataclass(frozen=True)
class ApiSpecItem:
    """A parsed endpoint, request, or GraphQL field."""

    group: str
    name: str
    kind: str
    path: str
    method: str | None = None
    url: str | None = None
    operation_id: str | None = None
    auth: list[str] = field(default_factory=list)
    deprecated: bool = False
    directives: list[str] = field(default_factory=list)
    type_name: str | None = None
    rate_limits: list[str] = field(default_factory=list)
    error_responses: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ApiSpecParseResult:
    """Normalized output from an API specification parser."""

    source_type: str
    title: str
    version: str | None
    groups: dict[str, list[ApiSpecItem]]
    auth_schemes: list[str] = field(default_factory=list)
    rate_limits: list[str] = field(default_factory=list)
    error_responses: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    patterns: list[ApiSpecFinding] = field(default_factory=list)
    anti_patterns: list[ApiSpecFinding] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    @property
    def items(self) -> list[ApiSpecItem]:
        """Return all parsed items in group order."""
        return [item for group_items in self.groups.values() for item in group_items]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of the parse result."""
        return asdict(self)


__all__ = [
    "ApiSpecFinding",
    "ApiSpecItem",
    "ApiSpecParseResult",
    "ApiSpecParserError",
    "DbtProjectAnalysis",
    "DbtProjectParseError",
    "HelmChartParseResult",
    "HelmParserError",
    "KafkaAnalysis",
    "KafkaParseError",
    "KubernetesManifestParseResult",
    "KubernetesParserError",
    "ProcessParserError",
    "ProcessSource",
    "SarifFinding",
    "SarifResult",
    "SarifTool",
    "SbomPackage",
    "SbomResult",
    "SecurityPolicyResult",
    "SqlSchemaAnalysis",
    "SqlSchemaParseError",
    "TerraformParseResult",
    "TerraformParserError",
    "parse_dbt_project",
    "parse_helm_chart",
    "parse_kafka_artifact",
    "parse_kubernetes_manifests",
    "parse_runbook_file",
    "parse_runbook_source",
    "parse_sarif",
    "parse_sbom",
    "parse_security_policy",
    "parse_sql_schema",
    "parse_terraform_directory",
]
