"""Parse SARIF 2.1 security results into skill-ready compliance signals."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any


@dataclass(frozen=True)
class SarifTool:
    """Tool metadata extracted from a SARIF run."""

    name: str
    version: str | None = None
    information_uri: str | None = None


@dataclass(frozen=True)
class SarifFinding:
    """A SARIF finding with code content intentionally excluded."""

    rule_id: str
    severity: str
    file_paths: list[str]
    cwes: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SarifResult:
    """Aggregated SARIF security posture suitable for generated skills."""

    tools: list[SarifTool]
    findings: list[SarifFinding]
    rule_ids: list[str]
    severities: dict[str, int]
    cwes: list[str]
    file_paths: list[str]
    categories: dict[str, list[str]]
    tags: dict[str, list[str]]
    patterns: list[str]
    anti_patterns: list[str]


_CWE_PATTERN = re.compile(r"\bCWE[-_/ ]?(\d{1,5})\b", re.IGNORECASE)
_ANTI_PATTERN_HINTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bsql\s+injection\b|\binjection\b", re.IGNORECASE), "Injection-prone input handling"),
    (re.compile(r"\bxss\b|cross[- ]site scripting", re.IGNORECASE), "Cross-site scripting exposure"),
    (re.compile(r"hardcoded|secret|credential|password|token", re.IGNORECASE), "Hardcoded secret handling"),
    (re.compile(r"weak crypto|md5|sha1|des\b|insecure random", re.IGNORECASE), "Weak cryptography"),
    (re.compile(r"path traversal|directory traversal", re.IGNORECASE), "Path traversal exposure"),
    (re.compile(r"deseriali[sz]ation|pickle|yaml\.load", re.IGNORECASE), "Unsafe deserialization"),
    (re.compile(r"\bdebug\b|stack trace", re.IGNORECASE), "Debug information disclosure"),
)
_CWE_CATEGORY_NAMES = {
    "CWE-22": "path-traversal",
    "CWE-79": "cross-site-scripting",
    "CWE-89": "injection",
    "CWE-200": "information-exposure",
    "CWE-295": "certificate-validation",
    "CWE-327": "weak-cryptography",
    "CWE-352": "cross-site-request-forgery",
    "CWE-502": "unsafe-deserialization",
    "CWE-798": "hardcoded-credentials",
}


def parse_sarif(path: str | Path) -> SarifResult:
    """Parse a SARIF 2.1 JSON file and return security evidence without code snippets."""
    sarif_path = Path(path)
    payload = _load_sarif_json(sarif_path)
    version = payload.get("version")
    if version != "2.1.0":
        raise ValueError(f"SARIF parser expected version 2.1.0 in {sarif_path}; found {version!r}.")
    runs = payload.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError(f"SARIF file {sarif_path} must contain a non-empty `runs` list.")

    tools: list[SarifTool] = []
    findings: list[SarifFinding] = []
    rule_metadata_by_run: list[dict[str, dict[str, object]]] = []
    all_rule_ids: set[str] = set()
    severities: dict[str, int] = {}
    cwes: set[str] = set()
    file_paths: set[str] = set()
    category_map: dict[str, set[str]] = {}
    tag_map: dict[str, set[str]] = {}
    anti_patterns: set[str] = set()

    for run_index, run in enumerate(runs):
        if not isinstance(run, dict):
            raise ValueError(f"SARIF run {run_index} in {sarif_path} must be a mapping.")
        tool = _tool_from_run(run, sarif_path, run_index)
        tools.append(tool)
        rules = _rules_from_run(run)
        rule_metadata_by_run.append(rules)
        results = run.get("results", [])
        if results is None:
            results = []
        if not isinstance(results, list):
            raise ValueError(f"SARIF run {run_index} in {sarif_path} has a non-list `results` value.")

        for rule_id, rule in rules.items():
            all_rule_ids.add(rule_id)
            rule_cwes = _extract_cwes(rule)
            rule_tags = _extract_tags(rule)
            rule_categories = _categories_for(rule_cwes, rule_tags)
            for cwe in rule_cwes:
                cwes.add(cwe)
            for tag in rule_tags:
                tag_map.setdefault(tag, set()).add(rule_id)
            for category in rule_categories:
                category_map.setdefault(category, set()).add(rule_id)
            anti_patterns.update(_anti_patterns_from_rule(rule))

        for result in results:
            if not isinstance(result, dict):
                continue
            rule_id = _string_value(result.get("ruleId")) or _rule_id_from_index(result, rules)
            if rule_id is None:
                rule_id = "unknown-rule"
            all_rule_ids.add(rule_id)
            rule = rules.get(rule_id, {})
            severity = _result_severity(result, rule)
            severities[severity] = severities.get(severity, 0) + 1
            paths = _file_paths_from_result(result)
            file_paths.update(paths)
            rule_cwes = _extract_cwes(rule)
            rule_tags = _extract_tags(rule)
            rule_categories = _categories_for(rule_cwes, rule_tags)
            findings.append(
                SarifFinding(
                    rule_id=rule_id,
                    severity=severity,
                    file_paths=paths,
                    cwes=rule_cwes,
                    tags=rule_tags,
                    categories=rule_categories,
                )
            )

    patterns = _patterns(tools, category_map, tag_map, severities)
    return SarifResult(
        tools=_dedupe_tools(tools),
        findings=findings,
        rule_ids=sorted(all_rule_ids),
        severities=dict(sorted(severities.items())),
        cwes=sorted(cwes),
        file_paths=sorted(file_paths),
        categories={key: sorted(value) for key, value in sorted(category_map.items())},
        tags={key: sorted(value) for key, value in sorted(tag_map.items())},
        patterns=patterns,
        anti_patterns=sorted(anti_patterns),
    )


def _load_sarif_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read SARIF file {path}: {exc}") from exc
    if not raw.strip():
        raise ValueError(f"SARIF file {path} is empty.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"SARIF JSON is invalid in {path}: {exc.msg} at line {exc.lineno}, column {exc.colno}.") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"SARIF file {path} must contain a JSON object.")
    return payload


def _tool_from_run(run: dict[str, Any], path: Path, run_index: int) -> SarifTool:
    tool = run.get("tool")
    if not isinstance(tool, dict):
        raise ValueError(f"SARIF run {run_index} in {path} is missing `tool` metadata.")
    driver = tool.get("driver")
    if not isinstance(driver, dict):
        raise ValueError(f"SARIF run {run_index} in {path} is missing `tool.driver` metadata.")
    name = _string_value(driver.get("name"))
    if not name:
        raise ValueError(f"SARIF run {run_index} in {path} is missing `tool.driver.name`.")
    return SarifTool(
        name=name,
        version=_string_value(driver.get("semanticVersion")) or _string_value(driver.get("version")),
        information_uri=_string_value(driver.get("informationUri")),
    )


def _rules_from_run(run: dict[str, Any]) -> dict[str, dict[str, object]]:
    rules: dict[str, dict[str, object]] = {}
    tool = run.get("tool") if isinstance(run.get("tool"), dict) else {}
    components: list[object] = []
    if isinstance(tool, dict):
        components.append(tool.get("driver"))
        extensions = tool.get("extensions")
        if isinstance(extensions, list):
            components.extend(extensions)
    for component in components:
        if not isinstance(component, dict):
            continue
        for rule in component.get("rules", []) or []:
            if not isinstance(rule, dict):
                continue
            rule_id = _string_value(rule.get("id"))
            if rule_id:
                rules[rule_id] = rule
    return rules


def _rule_id_from_index(result: dict[str, Any], rules: dict[str, dict[str, object]]) -> str | None:
    rule_index = result.get("ruleIndex")
    if not isinstance(rule_index, int):
        return None
    rule_ids = list(rules)
    if 0 <= rule_index < len(rule_ids):
        return rule_ids[rule_index]
    return None


def _result_severity(result: dict[str, Any], rule: dict[str, object]) -> str:
    level = _string_value(result.get("level"))
    if level:
        return level.lower()
    default_configuration = rule.get("defaultConfiguration")
    if isinstance(default_configuration, dict):
        default_level = _string_value(default_configuration.get("level"))
        if default_level:
            return default_level.lower()
    properties = rule.get("properties")
    if isinstance(properties, dict):
        severity = _string_value(properties.get("problem.severity")) or _string_value(properties.get("security-severity"))
        if severity:
            return severity.lower()
    return "warning"


def _file_paths_from_result(result: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for location in result.get("locations", []) or []:
        if not isinstance(location, dict):
            continue
        physical = location.get("physicalLocation")
        if not isinstance(physical, dict):
            continue
        artifact = physical.get("artifactLocation")
        if not isinstance(artifact, dict):
            continue
        uri = _string_value(artifact.get("uri"))
        if uri:
            paths.add(uri.split("#", 1)[0])
    return sorted(paths)


def _extract_cwes(rule: dict[str, object]) -> list[str]:
    values: list[str] = []
    for candidate in _flatten_rule_metadata(rule):
        values.extend(f"CWE-{int(match.group(1))}" for match in _CWE_PATTERN.finditer(candidate))
    return sorted(dict.fromkeys(values))


def _extract_tags(rule: dict[str, object]) -> list[str]:
    properties = rule.get("properties")
    tags: list[str] = []
    if isinstance(properties, dict):
        raw_tags = properties.get("tags")
        if isinstance(raw_tags, list):
            tags.extend(str(tag) for tag in raw_tags if str(tag).strip())
        category = properties.get("category")
        if category:
            tags.append(str(category))
    return sorted(dict.fromkeys(tag for tag in tags if not _CWE_PATTERN.search(tag)))


def _categories_for(cwes: list[str], tags: list[str]) -> list[str]:
    categories: set[str] = set()
    for cwe in cwes:
        categories.add(_CWE_CATEGORY_NAMES.get(cwe, cwe.lower()))
    for tag in tags:
        normalized = _normalize_label(tag)
        if normalized.startswith(("owasp", "security", "injection", "xss")):
            categories.add(normalized)
    return sorted(categories)


def _anti_patterns_from_rule(rule: dict[str, object]) -> list[str]:
    text = " ".join(_flatten_rule_metadata(rule))
    return sorted({label for pattern, label in _ANTI_PATTERN_HINTS if pattern.search(text)})


def _flatten_rule_metadata(rule: dict[str, object]) -> list[str]:
    values: list[str] = []
    for key in ("id", "name"):
        value = _string_value(rule.get(key))
        if value:
            values.append(value)
    for key in ("shortDescription", "fullDescription", "help"):
        section = rule.get(key)
        if isinstance(section, dict):
            value = _string_value(section.get("text")) or _string_value(section.get("markdown"))
            if value:
                values.append(value)
    properties = rule.get("properties")
    if isinstance(properties, dict):
        for value in properties.values():
            if isinstance(value, list):
                values.extend(str(item) for item in value if str(item).strip())
            elif isinstance(value, str):
                values.append(value)
    return values


def _patterns(
    tools: list[SarifTool],
    category_map: dict[str, set[str]],
    tag_map: dict[str, set[str]],
    severities: dict[str, int],
) -> list[str]:
    patterns: set[str] = set()
    for tool in tools:
        label = f"Configured SARIF tool: {tool.name}"
        if tool.version:
            label = f"{label} {tool.version}"
        patterns.add(label)
    for category, rule_ids in category_map.items():
        patterns.add(f"CWE/security category `{category}` covers {len(rule_ids)} rule(s)")
    for tag, rule_ids in tag_map.items():
        if tag.lower() in {"security", "audit", "correctness"} or tag.lower().startswith("owasp"):
            patterns.add(f"SARIF rule tag `{tag}` covers {len(rule_ids)} rule(s)")
    for severity, count in severities.items():
        patterns.add(f"SARIF severity `{severity}` reported {count} finding(s)")
    return sorted(patterns)


def _dedupe_tools(tools: list[SarifTool]) -> list[SarifTool]:
    seen: set[tuple[str, str | None, str | None]] = set()
    deduped: list[SarifTool] = []
    for tool in tools:
        key = (tool.name, tool.version, tool.information_uri)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(tool)
    return deduped


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
