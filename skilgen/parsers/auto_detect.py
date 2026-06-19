"""Config-aware auto-detection for non-code source artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from skilgen.core.config import load_config
from skilgen.core.models import SourceConfigValue
from skilgen.parsers.sources import SOURCE_ALIASES, SOURCE_TYPES


DEFAULT_SOURCE_PATTERNS: dict[str, tuple[str, ...]] = {
    "openapi": (
        "openapi.yaml",
        "openapi.json",
        "openapi*.yaml",
        "openapi*.json",
        "swagger.yaml",
        "swagger.json",
        "swagger*.yaml",
        "swagger*.json",
        "api/openapi.yaml",
        "docs/api.yaml",
        "docs/openapi.yaml",
    ),
    "graphql": ("schema.graphql", "src/**/*.graphql", "**/*.gql"),
    "postman": ("*.collection.json", "**/*.collection.json"),
    "terraform": ("terraform/*.tf", "*.tf"),
    "kubernetes": ("k8s/*.yaml", "kubernetes/*.yaml", "manifests/*.yaml", "deploy/**/*.yaml"),
    "helm": ("Chart.yaml", "helm/*/Chart.yaml"),
    "dbt": ("dbt_project.yml",),
    "sql_schema": ("migrations/*.sql", "schema/*.sql", "db/*.sql"),
    "kafka": ("kafka/*.yaml", "topics/*.yaml", "schemas/*.yaml", "*.avsc"),
    "sarif": ("*.sarif", ".sarif/*.sarif", "sarif-results/*.sarif"),
    "sbom": ("sbom.json", "bom.json", "sbom.xml", "bom.xml", "*.spdx.json"),
    "security_policy": ("SECURITY.md", "security-policy.yml", ".skilgen-security.yml", "approved-dependencies.yml", "blocked-licenses.yml", "allowed-packages.json"),
    "runbook": ("runbooks/**/*.md", "playbooks/**/*.md", "docs/runbooks/**/*.md", "operations/**/*.md", "on-call/**/*.md"),
    "confluence": ("confluence-export",),
    "notion": ("notion-export",),
    "incident": ("post-mortems/**/*.md", "postmortems/**/*.md", "incident-reports/**/*.md", "docs/incidents/**/*.md", "retros/**/*.md", "PIR*.md", "pagerduty-export.json"),
    "pagerduty": ("pagerduty-export.json",),
}


def normalize_source_name(source_name: str) -> str:
    """Return the canonical name for a configured or requested source."""
    return SOURCE_ALIASES.get(source_name, source_name)


def load_source_config(project_root: Path, raw_sources: dict[str, SourceConfigValue] | None = None) -> dict[str, SourceConfigValue]:
    """Load and normalize the optional sources block from config."""
    source_payload = raw_sources if raw_sources is not None else load_config(project_root).sources
    normalized: dict[str, SourceConfigValue] = {}
    for key, value in source_payload.items():
        canonical = normalize_source_name(str(key))
        if canonical not in SOURCE_TYPES:
            continue
        if isinstance(value, list):
            entries = [str(item).strip() for item in value if isinstance(item, str) and item.strip()]
            normalized[canonical] = entries
        elif isinstance(value, (bool, str)):
            normalized[canonical] = value.strip() if isinstance(value, str) else value
    return normalized


def detect_source_paths(
    project_root: Path,
    source_names: Iterable[str] | None = None,
    raw_sources: dict[str, SourceConfigValue] | None = None,
) -> dict[str, list[Path]]:
    """Detect supported source artifacts, honoring sparse config and aliases."""
    root = project_root.resolve()
    configured = load_source_config(root, raw_sources)
    selected = _selected_sources(source_names)
    detected: dict[str, list[Path]] = {}
    for source_type in _candidate_sources(selected, configured):
        configured_value = configured.get(source_type)
        if selected and configured_value is False:
            configured_value = None
        explicit = _configured_paths(root, configured_value)
        if explicit is not None:
            if explicit:
                detected[source_type] = explicit
            continue
        paths = _detect_with_defaults(root, source_type)
        if paths:
            detected[source_type] = paths
    return detected


def resolve_source_paths(project_root: Path, source_type: str, configured_value: SourceConfigValue) -> list[Path]:
    """Resolve configured source paths for one source type."""
    canonical = normalize_source_name(source_type)
    if canonical not in DEFAULT_SOURCE_PATTERNS:
        return []
    explicit = _configured_paths(project_root.resolve(), configured_value)
    return explicit or []


def _candidate_sources(selected: list[str], configured: dict[str, SourceConfigValue]) -> list[str]:
    if selected:
        return selected
    if configured:
        enabled: list[str] = []
        for source, value in configured.items():
            if value is False:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, list) and not value:
                continue
            enabled.append(source)
        return sorted(enabled)
    return sorted(DEFAULT_SOURCE_PATTERNS)


def _selected_sources(source_names: Iterable[str] | None) -> list[str]:
    selected = [normalize_source_name(str(source)) for source in (source_names or []) if str(source).strip()]
    if not selected or "all" in selected:
        return []
    return [source for source in selected if source in DEFAULT_SOURCE_PATTERNS]


def _configured_paths(root: Path, configured_value: SourceConfigValue | None) -> list[Path] | None:
    if configured_value is None:
        return None
    if configured_value is False:
        return []
    if configured_value is True:
        return None
    if isinstance(configured_value, str):
        return _resolve_entries(root, [configured_value])
    if isinstance(configured_value, list):
        return _resolve_entries(root, configured_value)
    return None


def _resolve_entries(root: Path, entries: list[str]) -> list[Path]:
    paths: list[Path] = []
    for entry in entries:
        resolved = (root / entry).resolve() if not Path(entry).is_absolute() else Path(entry).resolve()
        if any(marker in entry for marker in ("*", "?", "[")):
            paths.extend(path.resolve() for path in root.glob(entry) if path.exists())
            continue
        if resolved.exists():
            paths.append(resolved)
    return sorted(dict.fromkeys(paths))


def _detect_with_defaults(root: Path, source_type: str) -> list[Path]:
    patterns = DEFAULT_SOURCE_PATTERNS.get(source_type, ())
    paths: list[Path] = []
    for pattern in patterns:
        if any(marker in pattern for marker in ("*", "?", "[")):
            paths.extend(path.resolve() for path in root.glob(pattern) if path.exists())
        else:
            candidate = root / pattern
            if candidate.exists():
                paths.append(candidate.resolve())
    return sorted(dict.fromkeys(paths))
