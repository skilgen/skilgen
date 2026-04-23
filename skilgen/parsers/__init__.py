"""Structured parsers for external evidence and compliance artifacts."""

from skilgen.parsers.sarif import SarifFinding, SarifResult, SarifTool, parse_sarif
from skilgen.parsers.sbom import SbomPackage, SbomResult, parse_sbom
from skilgen.parsers.security_policy import SecurityPolicyResult, parse_security_policy

__all__ = [
    "SarifFinding",
    "SarifResult",
    "SarifTool",
    "SbomPackage",
    "SbomResult",
    "SecurityPolicyResult",
    "parse_sarif",
    "parse_sbom",
    "parse_security_policy",
]
