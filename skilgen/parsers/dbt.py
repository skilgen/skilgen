"""Parse dbt projects into model lineage, documentation, and quality signals."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class DbtProjectParseError(ValueError):
    """Raised when a dbt project artifact cannot be parsed."""


@dataclass(frozen=True)
class DbtIssue:
    severity: str
    category: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class DbtColumn:
    name: str
    description: str | None
    tests: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DbtModel:
    name: str
    path: str
    group: str
    description: str | None
    columns: list[DbtColumn]
    tests: list[str]
    refs: list[str]
    sources: list[str]
    ctes: list[str]
    macros: list[str]
    hardcoded_relations: list[str]


@dataclass(frozen=True)
class DbtSourceTable:
    source_name: str
    table_name: str
    description: str | None
    columns: list[DbtColumn] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DbtMacro:
    name: str
    path: str | None = None
    description: str | None = None
    arguments: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DbtProjectAnalysis:
    project_name: str
    project_path: str
    models: list[DbtModel]
    sources: list[DbtSourceTable]
    macros: list[DbtMacro]
    groups: dict[str, list[str]]
    test_coverage: dict[str, bool]
    circular_refs: list[list[str]]
    issues: list[DbtIssue]


REF_RE = re.compile(r"\bref\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", re.IGNORECASE)
SOURCE_RE = re.compile(r"\bsource\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)", re.IGNORECASE)
CTE_RE = re.compile(r"(?:\bwith|,)\s+([A-Za-z_][A-Za-z0-9_]*)\s+as\s*\(", re.IGNORECASE)
JINJA_CALL_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.IGNORECASE)
MACRO_DEF_RE = re.compile(r"\{%-?\s*macro\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", re.IGNORECASE)
FROM_JOIN_RE = re.compile(r"\b(?:from|join)\s+([`\"A-Za-z_][A-Za-z0-9_`\".\-]*)", re.IGNORECASE)
DBT_BUILTINS = {"config", "doc", "env_var", "exceptions", "log", "ref", "return", "source", "var"}


def parse_dbt_project(project_root: str | Path) -> DbtProjectAnalysis:
    """Parse a dbt project directory and return lineage, docs, tests, and audit issues."""

    root = Path(project_root).resolve()
    if not root.exists() or not root.is_dir():
        raise DbtProjectParseError(f"dbt project root does not exist or is not a directory: {root}")

    project_path = root / "dbt_project.yml"
    project = _load_yaml_mapping(project_path, artifact="dbt_project.yml")
    project_name = str(project.get("name") or root.name)
    model_roots = _configured_paths(project, "model-paths", default=["models"])
    macro_roots = _configured_paths(project, "macro-paths", default=["macros"])

    schema_docs = _collect_schema_docs(root, model_roots)
    macros = _collect_macros(root, macro_roots, schema_docs["macros"])
    models: list[DbtModel] = []
    issues: list[DbtIssue] = []

    for sql_path in _iter_sql_models(root, model_roots):
        model = parse_dbt_model_sql(root, sql_path, schema_docs["models"])
        models.append(model)
        if not model.description:
            issues.append(
                DbtIssue(
                    severity="warning",
                    category="missing-description",
                    message=f"Model '{model.name}' is missing a schema.yml description.",
                    path=model.path,
                )
            )
        for column in model.columns:
            if not column.description:
                issues.append(
                    DbtIssue(
                        severity="warning",
                        category="missing-description",
                        message=f"Column '{model.name}.{column.name}' is missing a description.",
                        path=model.path,
                    )
                )
        if not (model.tests or any(column.tests for column in model.columns)):
            issues.append(
                DbtIssue(
                    severity="warning",
                    category="test-coverage",
                    message=f"Model '{model.name}' has no model or column tests.",
                    path=model.path,
                )
            )
        for relation in model.hardcoded_relations:
            issues.append(
                DbtIssue(
                    severity="warning",
                    category="hardcoded-schema",
                    message=f"Model '{model.name}' references hardcoded relation '{relation}' instead of ref/source.",
                    path=model.path,
                )
            )

    model_names = {model.name for model in models}
    for model in models:
        for ref in model.refs:
            if ref not in model_names:
                issues.append(
                    DbtIssue(
                        severity="info",
                        category="unresolved-ref",
                        message=f"Model '{model.name}' references '{ref}', which was not found in parsed model paths.",
                        path=model.path,
                    )
                )

    circular_refs = _find_cycles({model.name: [ref for ref in model.refs if ref in model_names] for model in models})
    for cycle in circular_refs:
        issues.append(
            DbtIssue(
                severity="error",
                category="circular-ref",
                message=f"Circular dbt model reference detected: {' -> '.join(cycle)}.",
                path=None,
            )
        )

    groups: dict[str, list[str]] = {}
    for model in models:
        groups.setdefault(model.group, []).append(model.name)

    return DbtProjectAnalysis(
        project_name=project_name,
        project_path=str(project_path),
        models=sorted(models, key=lambda item: item.path),
        sources=schema_docs["sources"],
        macros=sorted(macros, key=lambda item: item.name),
        groups={name: sorted(values) for name, values in sorted(groups.items())},
        test_coverage={model.name: bool(model.tests or any(column.tests for column in model.columns)) for model in models},
        circular_refs=circular_refs,
        issues=issues,
    )


def parse_dbt_model_sql(root: Path, sql_path: Path, model_docs: dict[str, dict[str, Any]]) -> DbtModel:
    """Parse a single dbt model SQL file with optional schema.yml documentation."""

    try:
        text = sql_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DbtProjectParseError(f"Could not read dbt model SQL file {sql_path}: {exc}") from exc
    if not text.strip():
        raise DbtProjectParseError(f"dbt model SQL file is empty: {sql_path}")

    name = sql_path.stem
    relative = sql_path.relative_to(root).as_posix()
    docs = model_docs.get(name, {})
    columns = [
        DbtColumn(
            name=str(column.get("name", "")),
            description=_optional_string(column.get("description")),
            tests=_normalize_tests(column.get("tests")),
        )
        for column in docs.get("columns", [])
        if isinstance(column, dict) and column.get("name")
    ]
    return DbtModel(
        name=name,
        path=relative,
        group=_infer_model_group(relative),
        description=_optional_string(docs.get("description")),
        columns=columns,
        tests=_normalize_tests(docs.get("tests")),
        refs=sorted(dict.fromkeys(REF_RE.findall(text))),
        sources=sorted(dict.fromkeys(f"{source}.{table}" for source, table in SOURCE_RE.findall(text))),
        ctes=sorted(dict.fromkeys(CTE_RE.findall(text))),
        macros=sorted(
            name
            for name in dict.fromkeys(JINJA_CALL_RE.findall(text))
            if name.lower() not in DBT_BUILTINS
        ),
        hardcoded_relations=_hardcoded_relations(text),
    )


def _load_yaml_mapping(path: Path, *, artifact: str) -> dict[str, Any]:
    if not path.exists():
        raise DbtProjectParseError(f"Missing required {artifact}: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DbtProjectParseError(f"Could not read {artifact} at {path}: {exc}") from exc
    if not text.strip():
        raise DbtProjectParseError(f"{artifact} is empty: {path}")
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise DbtProjectParseError(f"Could not parse {artifact} at {path}: {exc}") from exc
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise DbtProjectParseError(f"{artifact} must contain a YAML mapping at {path}")
    return payload


def _configured_paths(project: dict[str, Any], key: str, *, default: list[str]) -> list[str]:
    value = project.get(key, default)
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return default


def _iter_sql_models(root: Path, model_roots: list[str]) -> list[Path]:
    paths: list[Path] = []
    for model_root in model_roots:
        base = root / model_root
        if not base.exists():
            continue
        paths.extend(path for path in base.rglob("*.sql") if path.is_file() and "target" not in path.parts)
    return sorted(paths)


def _collect_schema_docs(root: Path, model_roots: list[str]) -> dict[str, Any]:
    model_docs: dict[str, dict[str, Any]] = {}
    sources: list[DbtSourceTable] = []
    macros: dict[str, DbtMacro] = {}
    candidates: set[Path] = set()
    for model_root in model_roots:
        base = root / model_root
        if base.exists():
            candidates.update(path for path in base.rglob("*.yml") if path.is_file())
            candidates.update(path for path in base.rglob("*.yaml") if path.is_file())
    candidates.update(path for path in root.glob("*.yml") if path.name != "dbt_project.yml")
    candidates.update(path for path in root.glob("*.yaml") if path.name != "dbt_project.yaml")

    for path in sorted(candidates):
        payload = _load_yaml_mapping(path, artifact="dbt schema YAML")
        for model in _as_list(payload.get("models")):
            if not isinstance(model, dict) or not model.get("name"):
                continue
            model_docs[str(model["name"])] = model
        for source in _as_list(payload.get("sources")):
            if not isinstance(source, dict) or not source.get("name"):
                continue
            source_name = str(source["name"])
            for table in _as_list(source.get("tables")):
                if not isinstance(table, dict) or not table.get("name"):
                    continue
                sources.append(
                    DbtSourceTable(
                        source_name=source_name,
                        table_name=str(table["name"]),
                        description=_optional_string(table.get("description") or source.get("description")),
                        columns=_parse_columns(table.get("columns")),
                        tests=_normalize_tests(table.get("tests")),
                    )
                )
        for macro in _as_list(payload.get("macros")):
            if not isinstance(macro, dict) or not macro.get("name"):
                continue
            name = str(macro["name"])
            macros[name] = DbtMacro(
                name=name,
                path=path.relative_to(root).as_posix(),
                description=_optional_string(macro.get("description")),
                arguments=[str(arg.get("name")) for arg in _as_list(macro.get("arguments")) if isinstance(arg, dict) and arg.get("name")],
            )
    return {"models": model_docs, "sources": sources, "macros": macros}


def _collect_macros(root: Path, macro_roots: list[str], documented: dict[str, DbtMacro]) -> list[DbtMacro]:
    macros = dict(documented)
    for macro_root in macro_roots:
        base = root / macro_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.sql")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise DbtProjectParseError(f"Could not read dbt macro SQL file {path}: {exc}") from exc
            for name, raw_args in MACRO_DEF_RE.findall(text):
                args = [arg.split("=", 1)[0].strip() for arg in raw_args.split(",") if arg.strip()]
                existing = macros.get(name)
                macros[name] = DbtMacro(
                    name=name,
                    path=path.relative_to(root).as_posix(),
                    description=existing.description if existing else None,
                    arguments=args or (existing.arguments if existing else []),
                )
    return list(macros.values())


def _parse_columns(value: object) -> list[DbtColumn]:
    columns: list[DbtColumn] = []
    for column in _as_list(value):
        if isinstance(column, dict) and column.get("name"):
            columns.append(
                DbtColumn(
                    name=str(column["name"]),
                    description=_optional_string(column.get("description")),
                    tests=_normalize_tests(column.get("tests")),
                )
            )
    return columns


def _normalize_tests(value: object) -> list[str]:
    tests: list[str] = []
    for item in _as_list(value):
        if isinstance(item, str):
            tests.append(item)
        elif isinstance(item, dict):
            tests.extend(str(key) for key in item.keys())
    return sorted(dict.fromkeys(tests))


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _infer_model_group(relative: str) -> str:
    parts = Path(relative).parts
    lowered = [part.lower() for part in parts]
    for known in ("staging", "intermediate", "marts"):
        if known in lowered:
            return known
    if len(parts) > 2 and parts[0] == "models":
        return parts[1]
    return "root"


def _hardcoded_relations(text: str) -> list[str]:
    relations: list[str] = []
    for relation in FROM_JOIN_RE.findall(text):
        cleaned = relation.strip("`\"")
        if "." not in cleaned or "{{" in cleaned or cleaned.startswith("("):
            continue
        relations.append(cleaned)
    return sorted(dict.fromkeys(relations))


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    seen: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        if node in visiting:
            start = stack.index(node)
            cycle = [*stack[start:], node]
            key = tuple(cycle)
            if key not in seen:
                seen.add(key)
                cycles.append(cycle)
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for target in graph.get(node, []):
            visit(target)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return cycles
