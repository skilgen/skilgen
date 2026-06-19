"""Parse Helm chart metadata, values shape, and template evidence."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEPRECATED_API_VERSIONS = {
    "apps/v1beta1",
    "apps/v1beta2",
    "batch/v1beta1",
    "extensions/v1beta1",
    "networking.k8s.io/v1beta1",
    "policy/v1beta1",
    "rbac.authorization.k8s.io/v1beta1",
}
KIND_RE = re.compile(r"(?m)^\s*kind:\s*([A-Za-z0-9_.-]+)\s*$")
API_VERSION_RE = re.compile(r"(?m)^\s*apiVersion:\s*([A-Za-z0-9_./-]+)\s*$")
HELPER_RE = re.compile(r'{{-?\s*define\s+"([^"]+)"')
HOOK_RE = re.compile(r"helm\.sh/hook:\s*['\"]?([^'\"\n]+)")


class HelmParserError(ValueError):
    """Raised when a Helm chart cannot be parsed."""


@dataclass(frozen=True)
class HelmTemplateSummary:
    """Safe evidence extracted from a Helm template file."""

    file: str
    kinds: list[str] = field(default_factory=list)
    api_versions: list[str] = field(default_factory=list)
    helpers: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)
    uses_values: bool = False


@dataclass(frozen=True)
class HelmChartParseResult:
    """Helm chart summary that avoids exposing values data."""

    root: str
    chart_metadata: dict[str, object]
    dependencies: list[dict[str, object]]
    values_schema: dict[str, str]
    template_kinds: dict[str, int]
    templates: list[HelmTemplateSummary] = field(default_factory=list)
    helpers: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)


def parse_helm_chart(path: str | Path) -> HelmChartParseResult:
    """Parse Helm chart files from ``path`` and summarize metadata and templates."""

    root = Path(path).resolve()
    if not root.exists():
        raise HelmParserError(f"Helm parser expected an existing chart path: {root}")
    if not root.is_dir():
        raise HelmParserError(f"Helm parser expected a chart directory, got file: {root}")

    chart_payload = _load_yaml_file(root / "Chart.yaml", required=False)
    values_payload = _load_yaml_file(root / "values.yaml", required=False)
    chart = chart_payload if isinstance(chart_payload, dict) else {}
    values = values_payload if isinstance(values_payload, dict) else {}

    templates = _template_summaries(root)
    all_helpers = sorted({helper for template in templates for helper in template.helpers})
    all_hooks = sorted({hook for template in templates for hook in template.hooks})
    kind_counts = Counter(kind for template in templates for kind in template.kinds)
    patterns: set[str] = set()
    anti_patterns: set[str] = set()

    if values:
        patterns.add("values_configurability")
    if any(template.uses_values for template in templates):
        patterns.add("template_values_configurability")
    if all_hooks:
        patterns.add("helm_hooks")

    for template in templates:
        for api_version in template.api_versions:
            if api_version in DEPRECATED_API_VERSIONS:
                anti_patterns.add(f"deprecated_api_version:{template.file}:{api_version}")

    return HelmChartParseResult(
        root=root.as_posix(),
        chart_metadata=_chart_metadata(chart),
        dependencies=_dependencies(chart),
        values_schema=_values_schema(values),
        template_kinds=dict(sorted(kind_counts.items())),
        templates=templates,
        helpers=all_helpers,
        hooks=all_hooks,
        patterns=sorted(patterns),
        anti_patterns=sorted(anti_patterns),
    )


def _load_yaml_file(path: Path, *, required: bool) -> object:
    if not path.exists():
        if required:
            raise HelmParserError(f"Helm parser expected required file: {path}")
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HelmParserError(f"Helm parser could not read {path}: {exc}") from exc
    if not text.strip():
        return {}
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise HelmParserError(f"Helm parser failed to parse {path}: {exc}") from exc


def _chart_metadata(chart: dict[str, Any]) -> dict[str, object]:
    allowed_keys = ("apiVersion", "name", "version", "appVersion", "description", "type", "kubeVersion")
    return {key: chart[key] for key in allowed_keys if key in chart}


def _dependencies(chart: dict[str, Any]) -> list[dict[str, object]]:
    dependencies = chart.get("dependencies")
    if not isinstance(dependencies, list):
        return []
    cleaned: list[dict[str, object]] = []
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        cleaned.append(
            {
                key: dependency[key]
                for key in ("name", "version", "repository", "condition", "alias")
                if key in dependency
            }
        )
    return cleaned


def _values_schema(values: dict[str, Any]) -> dict[str, str]:
    schema: dict[str, str] = {}

    def visit(prefix: str, value: object) -> None:
        if isinstance(value, dict):
            if prefix:
                schema[prefix] = "object"
            for key, nested in value.items():
                child = f"{prefix}.{key}" if prefix else str(key)
                visit(child, nested)
        elif isinstance(value, list):
            schema[prefix] = "list"
            if value:
                schema[f"{prefix}[]"] = _type_name(value[0])
        else:
            schema[prefix] = _type_name(value)

    for key, value in values.items():
        visit(str(key), value)
    return dict(sorted(schema.items()))


def _type_name(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "list"
    return type(value).__name__


def _template_summaries(root: Path) -> list[HelmTemplateSummary]:
    templates_dir = root / "templates"
    if not templates_dir.exists():
        return []
    summaries: list[HelmTemplateSummary] = []
    for path in sorted(templates_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".tpl"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise HelmParserError(f"Helm parser could not read template {path}: {exc}") from exc
        relative = path.relative_to(root).as_posix()
        summaries.append(
            HelmTemplateSummary(
                file=relative,
                kinds=sorted(dict.fromkeys(KIND_RE.findall(text))),
                api_versions=sorted(dict.fromkeys(API_VERSION_RE.findall(text))),
                helpers=sorted(dict.fromkeys(HELPER_RE.findall(text))),
                hooks=sorted(dict.fromkeys(hook.strip() for hook in HOOK_RE.findall(text))),
                uses_values=".Values" in text,
            )
        )
    return summaries
