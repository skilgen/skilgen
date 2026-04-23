"""Detect non-code knowledge sources and render them as generated skills."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
import re
from typing import Callable, Iterable


SOURCE_TYPES = {
    "openapi",
    "graphql",
    "postman",
    "terraform",
    "kubernetes",
    "helm",
    "dbt",
    "sql_schema",
    "kafka",
    "sarif",
    "sbom",
    "security_policy",
    "runbook",
    "runbooks",
    "confluence",
    "notion",
    "incident",
    "incidents",
    "pagerduty",
    "all",
}

SOURCE_ALIASES = {
    "runbooks": "runbook",
    "incidents": "incident",
}


@dataclass(frozen=True)
class SkillSource:
    """Normalized non-code source ready for SKILL.md materialization."""

    domain: str
    title: str
    description: str
    patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    check_paths: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    source_type: str = "code"


@dataclass(frozen=True)
class SourceRunResult:
    """Summary of non-code source analysis and generated skill files."""

    analysed: dict[str, list[str]]
    skill_sources: list[SkillSource]
    written_files: list[Path]
    failures: dict[str, str]


def slugify(value: str) -> str:
    """Return a stable filesystem-safe source domain slug."""
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return slug.strip("_") or "source"


def _field_list(obj: object, *names: str) -> list[str]:
    values: list[str] = []
    for name in names:
        raw = getattr(obj, name, None)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw if item)
        elif isinstance(raw, dict):
            values.extend(f"{key}: {value}" for key, value in raw.items())
        elif raw:
            values.append(str(raw))
    return values


def _description(obj: object, fallback: str) -> str:
    for name in ("description", "summary", "body_summary", "project_name", "kind", "format"):
        value = getattr(obj, name, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _default_domain(obj: object, source_type: str) -> str:
    for name in ("domain", "group", "service_domain", "title", "name", "project_name"):
        value = getattr(obj, name, None)
        if isinstance(value, str) and value.strip():
            return slugify(value)
    defaults = {
        "openapi": "api_spec",
        "graphql": "graphql_api",
        "postman": "postman_collection",
        "terraform": "cloud_infrastructure",
        "kubernetes": "k8s_infrastructure",
        "helm": "helm_chart",
        "dbt": "dbt_data_models",
        "sql_schema": "sql_schema",
        "kafka": "data_streaming",
        "sarif": "security_compliance",
        "sbom": "supply_chain",
        "security_policy": "security_policy",
        "runbook": "operational_runbook",
        "confluence": "confluence_knowledge",
        "notion": "notion_knowledge",
        "incident": "incident_patterns",
        "pagerduty": "incident_patterns",
    }
    return defaults.get(source_type, slugify(source_type))


def _title(obj: object, source_type: str, domain: str) -> str:
    for name in ("title", "name", "project_name", "kind", "format"):
        value = getattr(obj, name, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return domain.replace("_", " ").title()


def normalize_skill_sources(raw: object, source_type: str) -> list[SkillSource]:
    """Coerce parser-specific dataclasses into normalized skill sources."""
    normalized_type = SOURCE_ALIASES.get(source_type, source_type)
    if raw is None:
        return []
    if isinstance(raw, SkillSource):
        return [raw]
    if isinstance(raw, list):
        items: list[SkillSource] = []
        for item in raw:
            items.extend(normalize_skill_sources(item, normalized_type))
        return items
    groups = getattr(raw, "groups", None)
    if isinstance(groups, dict) and groups:
        return _normalize_grouped_api_result(raw, normalized_type, groups)
    domain = _default_domain(raw, normalized_type)
    title = _title(raw, normalized_type, domain)
    patterns = _field_list(raw, "patterns", "success_patterns", "incident_patterns", "root_cause_patterns")
    anti_patterns = _field_list(raw, "anti_patterns", "issues")
    check_paths = _field_list(raw, "check_paths", "outputs")
    evidence = _field_list(
        raw,
        "evidence",
        "source_paths",
        "rule_ids",
        "cwes",
        "file_paths",
        "package_count_by_ecosystem",
        "license_distribution",
        "groups",
        "tables",
        "models",
        "topics",
        "schemas",
        "timeline_evidence",
        "impact_evidence",
    )
    return [
        SkillSource(
            domain=domain,
            title=title,
            description=_description(raw, f"Generated from {normalized_type} source evidence."),
            patterns=_dedupe(patterns),
            anti_patterns=_dedupe(anti_patterns),
            check_paths=_dedupe(check_paths),
            evidence=_dedupe(evidence),
            source_type=normalized_type,
        )
    ]


def _normalize_grouped_api_result(raw: object, source_type: str, groups: dict[str, object]) -> list[SkillSource]:
    """Normalize API-spec parser results into one skill per endpoint group."""
    title = _title(raw, source_type, source_type)
    base_patterns = _finding_messages(getattr(raw, "patterns", []))
    base_anti_patterns = _finding_messages(getattr(raw, "anti_patterns", []))
    global_evidence = _field_list(raw, "auth_schemes", "rate_limits", "error_responses", "examples", "evidence")
    sources: list[SkillSource] = []
    for group, raw_items in groups.items():
        items = raw_items if isinstance(raw_items, list) else []
        item_evidence = []
        for item in items:
            item_evidence.extend(_field_list(item, "operation_id", "name", "path", "method", "url", "type_name", "evidence"))
        sources.append(
            SkillSource(
                domain=slugify(str(group)),
                title=f"{str(group).replace('_', ' ').title()} API",
                description=f"Generated from {title} {source_type} source with {len(items)} parsed operations or fields.",
                patterns=_dedupe(base_patterns + _field_list(raw, "auth_schemes", "rate_limits", "error_responses")),
                anti_patterns=_dedupe(base_anti_patterns),
                check_paths=_dedupe([getattr(item, "path", "") for item in items]),
                evidence=_dedupe(global_evidence + item_evidence),
                source_type=source_type,
            )
        )
    return sources


def _finding_messages(raw_findings: object) -> list[str]:
    """Extract human-readable messages from parser finding objects."""
    if not isinstance(raw_findings, list):
        return []
    messages: list[str] = []
    for finding in raw_findings:
        message = getattr(finding, "message", None)
        if message:
            messages.append(str(message))
        else:
            messages.append(str(finding))
    return messages


def _dedupe(values: Iterable[str], limit: int = 30) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def detect_source_paths(project_root: Path) -> dict[str, list[Path]]:
    """Detect supported non-code source artifacts under a project root."""
    root = project_root.resolve()
    detected: dict[str, list[Path]] = {
        "openapi": _existing(root, ["openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json", "api/openapi.yaml", "docs/openapi.yaml"]),
        "graphql": _glob_existing(root, ["schema.graphql", "src/**/*.graphql", "**/*.gql"]),
        "postman": _glob_existing(root, ["*.collection.json", "**/*.collection.json"]),
        "terraform": _glob_existing(root, ["terraform/*.tf", "*.tf"]),
        "kubernetes": _glob_existing(root, ["k8s/*.yaml", "kubernetes/*.yaml", "manifests/*.yaml", "deploy/**/*.yaml"]),
        "helm": _glob_existing(root, ["Chart.yaml", "helm/*/Chart.yaml"]),
        "dbt": _existing(root, ["dbt_project.yml"]),
        "sql_schema": _glob_existing(root, ["migrations/*.sql", "schema/*.sql", "db/*.sql"]),
        "kafka": _glob_existing(root, ["kafka/*.yaml", "topics/*.yaml", "schemas/*.yaml", "*.avsc"]),
        "sarif": _glob_existing(root, ["*.sarif", ".sarif/*.sarif", "sarif-results/*.sarif"]),
        "sbom": _glob_existing(root, ["sbom.json", "bom.json", "sbom.xml", "bom.xml", "*.spdx.json"]),
        "security_policy": _existing(root, ["SECURITY.md", "security-policy.yml", ".skilgen-security.yml", "approved-dependencies.yml", "blocked-licenses.yml", "allowed-packages.json"]),
        "runbook": _glob_existing(root, ["runbooks/**/*.md", "playbooks/**/*.md", "docs/runbooks/**/*.md", "operations/**/*.md", "on-call/**/*.md"]),
        "confluence": _existing(root, ["confluence-export"]),
        "notion": _existing(root, ["notion-export"]),
        "incident": _glob_existing(root, ["post-mortems/**/*.md", "postmortems/**/*.md", "incident-reports/**/*.md", "docs/incidents/**/*.md", "retros/**/*.md", "PIR*.md", "pagerduty-export.json"]),
    }
    return {key: paths for key, paths in detected.items() if paths}


def _existing(root: Path, patterns: list[str]) -> list[Path]:
    return [root / pattern for pattern in patterns if (root / pattern).exists()]


def _glob_existing(root: Path, patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(path for path in root.glob(pattern) if path.exists())
    return sorted(set(paths))


def run_source_parsers(project_root: Path, source_names: Iterable[str] | None = None) -> SourceRunResult:
    """Run selected source parsers and materialize normalized outputs."""
    root = project_root.resolve()
    detected = detect_source_paths(root)
    selected = _selected_sources(source_names, detected)
    analysed: dict[str, list[str]] = {}
    failures: dict[str, str] = {}
    skill_sources: list[SkillSource] = []
    for source_type in selected:
        paths = detected.get(source_type, [])
        if not paths:
            continue
        for source_path in paths:
            try:
                raw = _call_parser(source_type, source_path)
                sources = normalize_skill_sources(raw, source_type)
                skill_sources.extend(sources)
                analysed.setdefault(source_type, []).extend(source.domain for source in sources)
            except Exception as exc:
                failures[source_type] = f"Failed to parse {source_type} source {source_path}: {exc}"
    written = write_skill_sources(root, skill_sources)
    return SourceRunResult(analysed=analysed, skill_sources=skill_sources, written_files=written, failures=failures)


def _selected_sources(source_names: Iterable[str] | None, detected: dict[str, list[Path]]) -> list[str]:
    requested = [SOURCE_ALIASES.get(source, source) for source in (source_names or []) if source]
    if not requested or "all" in requested:
        return sorted(detected)
    return [source for source in requested if source in SOURCE_TYPES]


def _call_parser(source_type: str, path: Path) -> object:
    candidates: dict[str, tuple[str, tuple[str, ...]]] = {
        "openapi": ("skilgen.parsers.openapi", ("parse_openapi_spec", "parse_openapi")),
        "graphql": ("skilgen.parsers.graphql", ("parse_graphql_schema", "parse_graphql")),
        "postman": ("skilgen.parsers.postman", ("parse_postman_collection", "parse_postman")),
        "terraform": ("skilgen.parsers.terraform", ("parse_terraform_directory", "parse_terraform_dir", "parse_terraform")),
        "kubernetes": ("skilgen.parsers.kubernetes", ("parse_kubernetes_dir", "parse_kubernetes_manifests", "parse_kubernetes")),
        "helm": ("skilgen.parsers.helm", ("parse_helm_chart", "parse_helm")),
        "dbt": ("skilgen.parsers.dbt", ("parse_dbt_project",)),
        "sql_schema": ("skilgen.parsers.sql_schema", ("parse_sql_schema",)),
        "kafka": ("skilgen.parsers.kafka", ("parse_kafka_artifact",)),
        "sarif": ("skilgen.parsers.sarif", ("parse_sarif_file", "parse_sarif")),
        "sbom": ("skilgen.parsers.sbom", ("parse_sbom_file", "parse_sbom")),
        "security_policy": ("skilgen.parsers.security_policy", ("parse_security_policy_file", "parse_security_policy")),
        "runbook": ("skilgen.parsers.runbook", ("parse_runbook_dir", "parse_runbook_source", "parse_runbook_file")),
        "confluence": ("skilgen.parsers.confluence", ("parse_confluence_export", "parse_confluence_source", "parse_confluence_file")),
        "notion": ("skilgen.parsers.notion", ("parse_notion_export", "parse_notion_source", "parse_notion_file")),
        "incident": ("skilgen.parsers.incident", ("parse_incident_dir", "parse_incident_source", "parse_incident_sources", "parse_incident_file")),
        "pagerduty": ("skilgen.parsers.incident", ("parse_pagerduty_export", "parse_incident_source")),
    }
    module_name, function_names = candidates[source_type]
    module = import_module(module_name)
    parser = _first_callable(module, function_names)
    if getattr(parser, "__name__", "") == "parse_incident_sources":
        return parser([path])
    return parser(path.parent if source_type in {"terraform", "kubernetes", "dbt"} and path.is_file() else path)


def _first_callable(module: object, names: tuple[str, ...]) -> Callable[[Path], object]:
    for name in names:
        parser = getattr(module, name, None)
        if callable(parser):
            return parser
    raise AttributeError(f"None of {', '.join(names)} exist in parser module")


def write_skill_sources(project_root: Path, sources: list[SkillSource]) -> list[Path]:
    """Write normalized source skills under skills/<source-domain>/SKILL.md."""
    written: list[Path] = []
    for source in sources:
        skill_dir = project_root / "skills" / source.domain
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(render_skill_source(source), encoding="utf-8")
        written.append(skill_file)
    return written


def render_skill_source(source: SkillSource) -> str:
    """Render a normalized non-code source as an agent-readable SKILL.md."""
    sections = [
        f"# {source.title}",
        "",
        "## Domain summary",
        source.description,
    ]
    _append_section(sections, "Detected patterns", source.patterns)
    _append_section(sections, "Anti-patterns", source.anti_patterns)
    _append_section(sections, "Check paths", source.check_paths)
    _append_section(sections, "Evidence", source.evidence)
    sections.extend(["", f"_Source type: {source.source_type}_", ""])
    return "\n".join(sections)


def _append_section(sections: list[str], title: str, values: list[str]) -> None:
    if not values:
        return
    sections.extend(["", f"## {title}"])
    sections.extend(f"- {value}" for value in values[:20])
