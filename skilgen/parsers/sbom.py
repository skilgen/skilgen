"""Parse SPDX and CycloneDX SBOMs into dependency compliance signals."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import unquote
from xml.etree import ElementTree

try:
    from skilgen.core.dependency_risk import _dependency_key as _dependency_risk_key
except ImportError:  # pragma: no cover - defensive for partial installs
    _dependency_risk_key = None  # type: ignore[assignment]


@dataclass(frozen=True)
class SbomPackage:
    """One package component extracted from an SBOM."""

    name: str
    version: str | None
    ecosystem: str
    licenses: list[str] = field(default_factory=list)
    purls: list[str] = field(default_factory=list)
    cpes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SbomResult:
    """Aggregated SBOM inventory and compliance signals."""

    format: str
    spec_version: str | None
    packages: list[SbomPackage]
    package_count: int
    package_count_by_ecosystem: dict[str, int]
    license_distribution: dict[str, int]
    purl_evidence: dict[str, list[str]]
    cpe_evidence: dict[str, list[str]]
    dependency_risk_keys: list[str]
    patterns: list[str]
    anti_patterns: list[str]


_NO_LICENSE_VALUES = {"", "none", "noassertion", "not declared", "unknown", "unlicensed"}
_COPYLEFT_LICENSE_HINTS = (
    "agpl",
    "gpl",
    "lgpl",
    "mpl",
    "epl",
    "cddl",
    "osl",
    "sspl",
)
_PURL_ECOSYSTEM_MAP = {
    "cargo": "cargo",
    "gem": "rubygems",
    "golang": "go",
    "maven": "maven",
    "npm": "npm",
    "nuget": "nuget",
    "pypi": "pip",
}


def parse_sbom(path: str | Path) -> SbomResult:
    """Parse SPDX JSON or CycloneDX JSON/XML into package compliance evidence."""
    sbom_path = Path(path)
    raw = _read_non_empty(sbom_path, "SBOM")
    if sbom_path.suffix.lower() == ".xml" or raw.lstrip().startswith("<"):
        return _parse_cyclonedx_xml(raw, sbom_path)
    payload = _load_json(raw, sbom_path)
    if _is_spdx(payload):
        return _parse_spdx_json(payload, sbom_path)
    if _is_cyclonedx_json(payload):
        return _parse_cyclonedx_json(payload, sbom_path)
    raise ValueError(f"SBOM file {sbom_path} is not recognized as SPDX JSON or CycloneDX JSON/XML.")


def _parse_spdx_json(payload: dict[str, Any], path: Path) -> SbomResult:
    packages_raw = payload.get("packages")
    if not isinstance(packages_raw, list):
        raise ValueError(f"SPDX SBOM {path} must contain a `packages` list.")
    packages: list[SbomPackage] = []
    for item in packages_raw:
        if not isinstance(item, dict):
            continue
        name = _string(item.get("name"))
        if not name or name.upper() == "SPDXREF-DOCUMENT":
            continue
        licenses = _spdx_licenses(item)
        purls, cpes = _spdx_external_refs(item)
        ecosystem = _ecosystem_from_purls(purls) or _ecosystem_from_cpes(cpes) or "unknown"
        packages.append(
            SbomPackage(
                name=name,
                version=_string(item.get("versionInfo")),
                ecosystem=ecosystem,
                licenses=licenses,
                purls=purls,
                cpes=cpes,
            )
        )
    return _build_result("SPDX", _string(payload.get("spdxVersion")), packages)


def _parse_cyclonedx_json(payload: dict[str, Any], path: Path) -> SbomResult:
    components = payload.get("components")
    if not isinstance(components, list):
        raise ValueError(f"CycloneDX SBOM {path} must contain a `components` list.")
    packages: list[SbomPackage] = []
    for item in components:
        if not isinstance(item, dict):
            continue
        name = _component_name(item)
        if not name:
            continue
        purls = [_string(item.get("purl"))] if _string(item.get("purl")) else []
        cpes = [_string(item.get("cpe"))] if _string(item.get("cpe")) else []
        packages.append(
            SbomPackage(
                name=name,
                version=_string(item.get("version")),
                ecosystem=_ecosystem_from_purls(purls) or _ecosystem_from_cpes(cpes) or _string(item.get("type")) or "unknown",
                licenses=_cyclonedx_licenses(item),
                purls=purls,
                cpes=cpes,
            )
        )
    return _build_result("CycloneDX", _string(payload.get("specVersion")), packages)


def _parse_cyclonedx_xml(raw: str, path: Path) -> SbomResult:
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:
        raise ValueError(f"CycloneDX XML is invalid in {path}: {exc}.") from exc
    if not _local_name(root.tag).lower().endswith("bom"):
        raise ValueError(f"CycloneDX XML {path} must have a BOM root element.")
    namespace = _namespace(root.tag)
    components_root = root.find(f"{namespace}components")
    if components_root is None:
        raise ValueError(f"CycloneDX XML {path} must contain a `components` element.")
    packages: list[SbomPackage] = []
    for component in components_root.findall(f"{namespace}component"):
        name = _xml_text(component, "name", namespace)
        if not name:
            continue
        purl = _xml_text(component, "purl", namespace)
        cpe = _xml_text(component, "cpe", namespace)
        purls = [purl] if purl else []
        cpes = [cpe] if cpe else []
        packages.append(
            SbomPackage(
                name=name,
                version=_xml_text(component, "version", namespace),
                ecosystem=_ecosystem_from_purls(purls) or _ecosystem_from_cpes(cpes) or component.attrib.get("type", "unknown"),
                licenses=_cyclonedx_xml_licenses(component, namespace),
                purls=purls,
                cpes=cpes,
            )
        )
    return _build_result("CycloneDX", _cyclonedx_xml_spec_version(root), packages)


def _build_result(format_name: str, spec_version: str | None, packages: list[SbomPackage]) -> SbomResult:
    package_count_by_ecosystem: dict[str, int] = {}
    license_distribution: dict[str, int] = {}
    purl_evidence: dict[str, list[str]] = {}
    cpe_evidence: dict[str, list[str]] = {}
    dependency_risk_keys: set[str] = set()
    anti_patterns: set[str] = set()

    for package in packages:
        package_count_by_ecosystem[package.ecosystem] = package_count_by_ecosystem.get(package.ecosystem, 0) + 1
        normalized_licenses = package.licenses or ["NOASSERTION"]
        for license_id in normalized_licenses:
            license_distribution[license_id] = license_distribution.get(license_id, 0) + 1
            normalized = _normalize_license(license_id)
            if normalized in _NO_LICENSE_VALUES:
                anti_patterns.add(f"Package `{package.name}` has no declared license")
            elif any(hint in normalized for hint in _COPYLEFT_LICENSE_HINTS):
                anti_patterns.add(f"Package `{package.name}` declares copyleft license `{license_id}`")
        if package.purls:
            purl_evidence[package.name] = package.purls
        if package.cpes:
            cpe_evidence[package.name] = package.cpes
        risk_ecosystem = _risk_ecosystem(package.ecosystem)
        if risk_ecosystem and _dependency_risk_key is not None:
            dependency_risk_keys.add(_dependency_risk_key(risk_ecosystem, package.name))

    patterns = _patterns(format_name, spec_version, packages, package_count_by_ecosystem, purl_evidence, cpe_evidence)
    return SbomResult(
        format=format_name,
        spec_version=spec_version,
        packages=packages,
        package_count=len(packages),
        package_count_by_ecosystem=dict(sorted(package_count_by_ecosystem.items())),
        license_distribution=dict(sorted(license_distribution.items())),
        purl_evidence={key: sorted(value) for key, value in sorted(purl_evidence.items())},
        cpe_evidence={key: sorted(value) for key, value in sorted(cpe_evidence.items())},
        dependency_risk_keys=sorted(dependency_risk_keys),
        patterns=patterns,
        anti_patterns=sorted(anti_patterns),
    )


def _read_non_empty(path: Path, label: str) -> str:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read {label} file {path}: {exc}") from exc
    if not raw.strip():
        raise ValueError(f"{label} file {path} is empty.")
    return raw


def _load_json(raw: str, path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"SBOM JSON is invalid in {path}: {exc.msg} at line {exc.lineno}, column {exc.colno}.") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"SBOM file {path} must contain a JSON object.")
    return payload


def _is_spdx(payload: dict[str, Any]) -> bool:
    return str(payload.get("spdxVersion", "")).upper().startswith("SPDX-")


def _is_cyclonedx_json(payload: dict[str, Any]) -> bool:
    return str(payload.get("bomFormat", "")).lower() == "cyclonedx"


def _spdx_licenses(item: dict[str, Any]) -> list[str]:
    values = [_string(item.get("licenseConcluded")), _string(item.get("licenseDeclared"))]
    return _dedupe_license_values(value for value in values if value)


def _spdx_external_refs(item: dict[str, Any]) -> tuple[list[str], list[str]]:
    purls: list[str] = []
    cpes: list[str] = []
    for ref in item.get("externalRefs", []) or []:
        if not isinstance(ref, dict):
            continue
        locator = _string(ref.get("referenceLocator"))
        if not locator:
            continue
        ref_type = str(ref.get("referenceType", "")).lower()
        if ref_type == "purl" or locator.startswith("pkg:"):
            purls.append(locator)
        elif ref_type.startswith("cpe") or locator.startswith("cpe:"):
            cpes.append(locator)
    return sorted(dict.fromkeys(purls)), sorted(dict.fromkeys(cpes))


def _cyclonedx_licenses(item: dict[str, Any]) -> list[str]:
    licenses: list[str] = []
    for entry in item.get("licenses", []) or []:
        if not isinstance(entry, dict):
            continue
        license_payload = entry.get("license")
        if isinstance(license_payload, dict):
            licenses.extend(
                value
                for value in [
                    _string(license_payload.get("id")),
                    _string(license_payload.get("name")),
                ]
                if value
            )
        expression = _string(entry.get("expression"))
        if expression:
            licenses.append(expression)
    return _dedupe_license_values(licenses)


def _cyclonedx_xml_licenses(component: ElementTree.Element, namespace: str) -> list[str]:
    licenses: list[str] = []
    licenses_root = component.find(f"{namespace}licenses")
    if licenses_root is None:
        return []
    for entry in licenses_root.findall(f"{namespace}license"):
        licenses.extend(value for value in [_xml_text(entry, "id", namespace), _xml_text(entry, "name", namespace)] if value)
    for expression in licenses_root.findall(f"{namespace}expression"):
        if expression.text and expression.text.strip():
            licenses.append(expression.text.strip())
    return _dedupe_license_values(licenses)


def _component_name(item: dict[str, Any]) -> str | None:
    name = _string(item.get("name"))
    group = _string(item.get("group"))
    if name and group and not name.startswith(group):
        return f"{group}/{name}"
    return name


def _ecosystem_from_purls(purls: list[str]) -> str | None:
    for purl in purls:
        match = re.match(r"^pkg:([^/]+)/", purl)
        if match:
            return _PURL_ECOSYSTEM_MAP.get(match.group(1).lower(), match.group(1).lower())
    return None


def _ecosystem_from_cpes(cpes: list[str]) -> str | None:
    if not cpes:
        return None
    return "cpe"


def _risk_ecosystem(ecosystem: str) -> str | None:
    if ecosystem in {"npm", "pip", "cargo", "go"}:
        return ecosystem
    return None


def _patterns(
    format_name: str,
    spec_version: str | None,
    packages: list[SbomPackage],
    ecosystem_counts: dict[str, int],
    purl_evidence: dict[str, list[str]],
    cpe_evidence: dict[str, list[str]],
) -> list[str]:
    patterns = {f"SBOM format: {format_name}{f' {spec_version}' if spec_version else ''}"}
    for ecosystem, count in ecosystem_counts.items():
        patterns.add(f"Package ecosystem `{ecosystem}` contains {count} component(s)")
    if purl_evidence:
        patterns.add(f"Package URL evidence is present for {len(purl_evidence)} component(s)")
    if cpe_evidence:
        patterns.add(f"CPE evidence is present for {len(cpe_evidence)} component(s)")
    if packages:
        patterns.add(f"SBOM inventory contains {len(packages)} package component(s)")
    return sorted(patterns)


def _dedupe_license_values(values: Any) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        stripped = value.strip()
        if stripped:
            cleaned.append(stripped)
    return sorted(dict.fromkeys(cleaned))


def _normalize_license(value: str) -> str:
    return value.lower().replace("license", "").replace(" ", "").replace("_", "-")


def _string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _xml_text(element: ElementTree.Element, child_name: str, namespace: str) -> str | None:
    child = element.find(f"{namespace}{child_name}")
    if child is not None and child.text and child.text.strip():
        return child.text.strip()
    return None


def _namespace(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[0] + "}"
    return ""


def _cyclonedx_xml_spec_version(root: ElementTree.Element) -> str | None:
    namespace_uri = root.tag.split("}", 1)[0].lstrip("{") if root.tag.startswith("{") else ""
    match = re.search(r"/bom/([0-9.]+)$", namespace_uri)
    if match:
        return match.group(1)
    return root.attrib.get("specVersion")


def _local_name(tag: str) -> str:
    return unquote(tag.rsplit("}", 1)[-1])
