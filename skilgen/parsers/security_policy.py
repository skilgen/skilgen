"""Parse security disclosure documents and structured compliance policies."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any

import yaml


@dataclass(frozen=True)
class SecurityPolicyResult:
    """Normalized security policy controls and process evidence."""

    kind: str
    blocked_licenses: list[str] = field(default_factory=list)
    approved_packages: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)
    required_headers: list[str] = field(default_factory=list)
    allowed_origins: list[str] = field(default_factory=list)
    process: dict[str, list[str]] = field(default_factory=dict)
    patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)


_STRUCTURED_KEYS = {
    "allowed_origins",
    "approved_packages",
    "blocked_licenses",
    "forbidden_patterns",
    "required_headers",
}
_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
_URL_PATTERN = re.compile(r"https?://[^\s)>\]]+")
_TIMELINE_PATTERN = re.compile(r"\b\d+\s+(?:business\s+)?(?:hour|hours|day|days|week|weeks)\b", re.IGNORECASE)


def parse_security_policy(path: str | Path) -> SecurityPolicyResult:
    """Parse SECURITY.md or a YAML/JSON security policy into compliance signals."""
    policy_path = Path(path)
    raw = _read_non_empty(policy_path)
    lower_name = policy_path.name.lower()
    if lower_name in {"security.md", "security"} or policy_path.suffix.lower() in {".md", ".markdown"}:
        return _parse_security_markdown(raw, policy_path)
    if policy_path.suffix.lower() == ".json":
        return _parse_structured_json(raw, policy_path)
    return _parse_structured_yaml(raw, policy_path)


def _parse_structured_yaml(raw: str, path: Path) -> SecurityPolicyResult:
    try:
        payload = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"Security policy YAML is invalid in {path}: {exc}") from exc
    return _parse_structured_payload(payload, path)


def _parse_structured_json(raw: str, path: Path) -> SecurityPolicyResult:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Security policy JSON is invalid in {path}: {exc.msg} at line {exc.lineno}, column {exc.colno}.") from exc
    return _parse_structured_payload(payload, path)


def _parse_structured_payload(payload: Any, path: Path) -> SecurityPolicyResult:
    if not isinstance(payload, dict):
        raise ValueError(f"Security policy {path} must contain a mapping/object.")
    unknown = sorted(set(payload) - _STRUCTURED_KEYS)
    if unknown:
        raise ValueError(f"Security policy {path} contains unsupported keys: {', '.join(unknown)}.")
    blocked_licenses = _string_list(payload.get("blocked_licenses"), "blocked_licenses", path)
    approved_packages = _string_list_or_mapping(payload.get("approved_packages"), "approved_packages", path)
    forbidden_patterns = _string_list(payload.get("forbidden_patterns"), "forbidden_patterns", path)
    required_headers = _string_list_or_mapping(payload.get("required_headers"), "required_headers", path)
    allowed_origins = _string_list(payload.get("allowed_origins"), "allowed_origins", path)

    patterns: set[str] = set()
    anti_patterns: set[str] = set()
    for value in approved_packages:
        patterns.add(f"Approved package policy includes `{value}`")
    for value in required_headers:
        patterns.add(f"Required header policy includes `{value}`")
    for value in allowed_origins:
        patterns.add(f"Allowed origin policy includes `{value}`")
    for value in blocked_licenses:
        anti_patterns.add(f"Blocked license policy includes `{value}`")
    for value in forbidden_patterns:
        anti_patterns.add(f"Forbidden pattern policy includes `{value}`")

    return SecurityPolicyResult(
        kind="structured-policy",
        blocked_licenses=blocked_licenses,
        approved_packages=approved_packages,
        forbidden_patterns=forbidden_patterns,
        required_headers=required_headers,
        allowed_origins=allowed_origins,
        process={},
        patterns=sorted(patterns),
        anti_patterns=sorted(anti_patterns),
    )


def _parse_security_markdown(raw: str, path: Path) -> SecurityPolicyResult:
    lines = [line.rstrip() for line in raw.splitlines()]
    if not any(line.strip() for line in lines):
        raise ValueError(f"Security policy {path} is empty.")

    contacts = _dedupe([*(_EMAIL_PATTERN.findall(raw)), *(_URL_PATTERN.findall(raw))])
    timelines = _dedupe(match.group(0).lower() for match in _TIMELINE_PATTERN.finditer(raw))
    supported_versions = _supported_version_lines(lines)
    reporting_channels = _reporting_lines(lines)
    disclosure_terms = _disclosure_terms(raw)
    process = {
        "contacts": contacts,
        "disclosure_terms": disclosure_terms,
        "reporting_channels": reporting_channels,
        "response_timelines": timelines,
        "supported_versions": supported_versions,
    }

    patterns: set[str] = set()
    anti_patterns: set[str] = set()
    if contacts:
        patterns.add(f"Security disclosure contact configured: {contacts[0]}")
    else:
        anti_patterns.add("SECURITY.md does not publish a reporting contact")
    if timelines:
        patterns.add(f"Security response timeline documented: {timelines[0]}")
    else:
        anti_patterns.add("SECURITY.md does not document a response timeline")
    if supported_versions:
        patterns.add("Supported versions are documented in SECURITY.md")
    else:
        anti_patterns.add("SECURITY.md does not document supported versions")
    if disclosure_terms:
        patterns.add("Coordinated disclosure process is documented in SECURITY.md")

    return SecurityPolicyResult(
        kind="security-md",
        process=process,
        patterns=sorted(patterns),
        anti_patterns=sorted(anti_patterns),
    )


def _read_non_empty(path: Path) -> str:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read security policy {path}: {exc}") from exc
    if not raw.strip():
        raise ValueError(f"Security policy {path} is empty.")
    return raw


def _string_list(value: object, field_name: str, path: Path) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"`{field_name}` in {path} must be a list of strings.")
    cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(cleaned) != len(value):
        raise ValueError(f"`{field_name}` in {path} must contain only non-empty strings.")
    return sorted(dict.fromkeys(cleaned))


def _string_list_or_mapping(value: object, field_name: str, path: Path) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return _string_list(value, field_name, path)
    if isinstance(value, dict):
        flattened: list[str] = []
        for key, entry in value.items():
            if isinstance(entry, list):
                for item in entry:
                    if not isinstance(item, str) or not item.strip():
                        raise ValueError(f"`{field_name}` in {path} must contain only non-empty strings.")
                    flattened.append(f"{key}:{item.strip()}")
            elif isinstance(entry, str) and entry.strip():
                flattened.append(f"{key}:{entry.strip()}")
            else:
                raise ValueError(f"`{field_name}` in {path} mapping values must be strings or string lists.")
        return sorted(dict.fromkeys(flattened))
    raise ValueError(f"`{field_name}` in {path} must be a list or mapping.")


def _supported_version_lines(lines: list[str]) -> list[str]:
    supported: list[str] = []
    in_supported_section = False
    for line in lines:
        stripped = line.strip()
        heading = stripped.lstrip("#").strip().lower() if stripped.startswith("#") else ""
        if heading:
            in_supported_section = "supported" in heading and "version" in heading
            continue
        if in_supported_section and stripped.startswith("|") and "version" not in stripped.lower():
            supported.append(stripped)
    return _dedupe(supported)


def _reporting_lines(lines: list[str]) -> list[str]:
    report_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(marker in lowered for marker in ("report", "vulnerability", "security advisory")) and not stripped.startswith("#"):
            report_lines.append(stripped)
    return _dedupe(report_lines[:5])


def _disclosure_terms(raw: str) -> list[str]:
    lowered = raw.lower()
    terms = []
    if "coordinated disclosure" in lowered:
        terms.append("coordinated disclosure")
    if "private" in lowered and "disclos" in lowered:
        terms.append("private disclosure")
    if "security advisory" in lowered:
        terms.append("security advisory")
    return _dedupe(terms)


def _dedupe(values: Any) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        if isinstance(value, str) and value.strip():
            cleaned.append(value.strip())
    return sorted(dict.fromkeys(cleaned))
