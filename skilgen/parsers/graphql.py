"""Parser for GraphQL SDL, .gql files, and introspection schema JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError


TYPE_BLOCK_RE = re.compile(
    r"\b(?P<kind>type|interface|input|enum)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s+implements\s+[^{]+)?\s*(?P<directives>(?:@[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?\s*)*)\{(?P<body>.*?)\}",
    re.DOTALL,
)
DIRECTIVE_RE = re.compile(r"@([A-Za-z_][A-Za-z0-9_]*)")
FIELD_RE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*:\s*(?P<type>[^@#=]+)"
    r"(?P<directives>(?:\s+@[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?)*)"
)
ROOT_GROUPS = {"Query", "Mutation", "Subscription"}


def parse_graphql_schema(path: str | Path) -> ApiSpecParseResult:
    """Parse a GraphQL SDL or introspection JSON schema file."""

    schema_path = Path(path)
    raw = _read_non_empty(schema_path)
    if schema_path.suffix.lower() == ".json":
        return _parse_introspection(schema_path, raw)
    return _parse_sdl(schema_path, raw)


def parse_graphql(path: str | Path) -> ApiSpecParseResult:
    """Alias for :func:`parse_graphql_schema`."""

    return parse_graphql_schema(path)


def parse(path: str | Path) -> ApiSpecParseResult:
    """Parse a GraphQL schema file."""

    return parse_graphql_schema(path)


def _parse_sdl(path: Path, raw: str) -> ApiSpecParseResult:
    groups: dict[str, list[ApiSpecItem]] = {}
    evidence: list[str] = []
    directives: set[str] = set(DIRECTIVE_RE.findall(raw))
    type_names: set[str] = set()
    key_types: set[str] = set()
    deprecated_fields: list[str] = []
    n_plus_one_fields: list[str] = []
    required_count = 0
    paginated_fields: list[str] = []
    field_names: list[str] = []

    for match in TYPE_BLOCK_RE.finditer(raw):
        parent_kind = match.group("kind")
        parent_name = match.group("name")
        parent_directives = sorted(set(DIRECTIVE_RE.findall(match.group("directives"))))
        body = match.group("body")
        type_names.add(parent_name)
        if parent_name in ROOT_GROUPS or "key" in parent_directives or re.search(r"\bid\s*:\s*ID!?\b", body):
            key_types.add(parent_name)
        evidence.append(f"type:{parent_name}")
        for directive in parent_directives:
            evidence.append(f"directive:{directive}")

        if parent_kind == "enum":
            continue
        for raw_line in body.splitlines():
            line = raw_line.strip().rstrip(",")
            if not line or line.startswith("#"):
                continue
            field_match = FIELD_RE.match(line)
            if not field_match:
                continue
            field_name = field_match.group("name")
            type_name = " ".join(field_match.group("type").split())
            field_directives = sorted(set(DIRECTIVE_RE.findall(line)))
            path_name = f"{parent_name}.{field_name}"
            group = parent_name if parent_name in ROOT_GROUPS else "types"
            field_names.append(field_name)
            evidence.extend([f"field:{path_name}", f"type:{type_name}"])
            evidence.extend(f"directive:{directive}" for directive in field_directives)
            if type_name.endswith("!"):
                required_count += 1
            if "deprecated" in field_directives:
                deprecated_fields.append(path_name)
            if _is_paginated(field_name, type_name, line):
                paginated_fields.append(path_name)
            if parent_name not in ROOT_GROUPS and _looks_like_list_object(type_name):
                n_plus_one_fields.append(path_name)

            groups.setdefault(group, []).append(
                ApiSpecItem(
                    group=group,
                    name=field_name,
                    kind="field",
                    path=path_name,
                    deprecated="deprecated" in field_directives,
                    directives=field_directives,
                    type_name=type_name,
                    evidence=[f"field:{path_name}", f"type:{type_name}", *[f"directive:{item}" for item in field_directives]],
                )
            )

    if not groups:
        raise ApiSpecParserError(f"GraphQL parser found no object fields in {path}")
    return _graphql_result(
        title=path.stem,
        version=None,
        groups=groups,
        directives=directives,
        key_types=key_types,
        deprecated_fields=deprecated_fields,
        n_plus_one_fields=n_plus_one_fields,
        required_count=required_count,
        paginated_fields=paginated_fields,
        field_names=field_names,
        evidence=evidence,
    )


def _parse_introspection(path: Path, raw: str) -> ApiSpecParseResult:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiSpecParserError(f"GraphQL parser could not decode introspection JSON {path}: {exc}") from exc
    schema = payload.get("data", {}).get("__schema") if isinstance(payload, dict) else None
    if schema is None and isinstance(payload, dict):
        schema = payload.get("__schema", payload)
    if not isinstance(schema, dict):
        raise ApiSpecParserError(f"GraphQL parser expected an introspection '__schema' object in {path}")

    groups: dict[str, list[ApiSpecItem]] = {}
    evidence: list[str] = []
    directives = {str(item.get("name")) for item in schema.get("directives", []) if isinstance(item, dict) and item.get("name")}
    key_types: set[str] = set()
    deprecated_fields: list[str] = []
    n_plus_one_fields: list[str] = []
    required_count = 0
    paginated_fields: list[str] = []
    field_names: list[str] = []

    query_name = _named_type(schema.get("queryType")) or "Query"
    mutation_name = _named_type(schema.get("mutationType")) or "Mutation"
    subscription_name = _named_type(schema.get("subscriptionType")) or "Subscription"
    root_names = {query_name: "Query", mutation_name: "Mutation", subscription_name: "Subscription"}

    types = schema.get("types")
    if not isinstance(types, list):
        raise ApiSpecParserError(f"GraphQL parser expected schema.types to be a list in {path}")
    for type_entry in types:
        if not isinstance(type_entry, dict):
            continue
        parent_name = type_entry.get("name")
        if not isinstance(parent_name, str) or parent_name.startswith("__"):
            continue
        fields = type_entry.get("fields")
        if not isinstance(fields, list):
            continue
        evidence.append(f"type:{parent_name}")
        if parent_name in root_names:
            key_types.add(root_names[parent_name])
        for field in fields:
            if not isinstance(field, dict) or not isinstance(field.get("name"), str):
                continue
            field_name = field["name"]
            type_name = _render_type(field.get("type"))
            field_path = f"{parent_name}.{field_name}"
            group = root_names.get(parent_name, "types")
            directives_for_field = ["deprecated"] if field.get("isDeprecated") else []
            args = field.get("args") if isinstance(field.get("args"), list) else []
            arg_names = [str(arg.get("name")) for arg in args if isinstance(arg, dict) and arg.get("name")]
            field_names.append(field_name)
            evidence.extend([f"field:{field_path}", f"type:{type_name}"])
            if type_name.endswith("!"):
                required_count += 1
            if field.get("isDeprecated"):
                deprecated_fields.append(field_path)
                reason = field.get("deprecationReason")
                if isinstance(reason, str) and reason:
                    evidence.append(f"deprecated:{field_path}:{reason}")
            if _is_paginated(field_name, type_name, " ".join(arg_names)):
                paginated_fields.append(field_path)
            if parent_name not in root_names and _looks_like_list_object(type_name):
                n_plus_one_fields.append(field_path)
            if field_name == "id" and "ID" in type_name:
                key_types.add(parent_name)

            groups.setdefault(group, []).append(
                ApiSpecItem(
                    group=group,
                    name=field_name,
                    kind="field",
                    path=field_path,
                    deprecated=bool(field.get("isDeprecated")),
                    directives=directives_for_field,
                    type_name=type_name,
                    evidence=[f"field:{field_path}", f"type:{type_name}"],
                )
            )

    if not groups:
        raise ApiSpecParserError(f"GraphQL parser found no introspection fields in {path}")
    return _graphql_result(
        title=path.stem,
        version=None,
        groups=groups,
        directives=directives,
        key_types=key_types,
        deprecated_fields=deprecated_fields,
        n_plus_one_fields=n_plus_one_fields,
        required_count=required_count,
        paginated_fields=paginated_fields,
        field_names=field_names,
        evidence=evidence,
    )


def _graphql_result(
    *,
    title: str,
    version: str | None,
    groups: dict[str, list[ApiSpecItem]],
    directives: set[str],
    key_types: set[str],
    deprecated_fields: list[str],
    n_plus_one_fields: list[str],
    required_count: int,
    paginated_fields: list[str],
    field_names: list[str],
    evidence: list[str],
) -> ApiSpecParseResult:
    patterns = [
        ApiSpecFinding(
            category="key-types",
            message=f"Key/root types detected: {', '.join(sorted(key_types)) or 'none'}.",
            evidence=[f"type:{name}" for name in sorted(key_types)],
        ),
        ApiSpecFinding(
            category="directives",
            message=f"Directives detected: {', '.join(sorted(directives)) or 'none'}.",
            evidence=[f"directive:{name}" for name in sorted(directives)],
        ),
        ApiSpecFinding(
            category="nullability",
            message=f"{required_count} fields are explicitly non-null.",
            evidence=[f"non_null_fields:{required_count}"],
        ),
    ]
    if _mostly_lower_camel(field_names):
        patterns.append(
            ApiSpecFinding(
                category="naming",
                message="Field naming mostly follows lowerCamelCase.",
                evidence=field_names[:8],
            )
        )
    if paginated_fields:
        patterns.append(
            ApiSpecFinding(
                category="pagination",
                message="Pagination fields or connection types are present.",
                evidence=paginated_fields[:8],
            )
        )

    anti_patterns: list[ApiSpecFinding] = []
    if n_plus_one_fields:
        anti_patterns.append(
            ApiSpecFinding(
                category="n-plus-one-risk",
                message="Nested list fields can create resolver N+1 risk without batching or DataLoader use.",
                evidence=n_plus_one_fields[:8],
            )
        )
    if deprecated_fields:
        anti_patterns.append(
            ApiSpecFinding(
                category="deprecated-field",
                message="Deprecated GraphQL fields are still present in the schema.",
                evidence=deprecated_fields[:8],
            )
        )

    return ApiSpecParseResult(
        source_type="graphql",
        title=title,
        version=version,
        groups=groups,
        patterns=patterns,
        anti_patterns=anti_patterns,
        evidence=_unique(evidence),
    )


def _read_non_empty(path: Path) -> str:
    if not path.exists():
        raise ApiSpecParserError(f"GraphQL parser could not find file: {path}")
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if not raw.strip():
        raise ApiSpecParserError(f"GraphQL parser cannot parse empty input: {path}")
    return raw


def _looks_like_list_object(type_name: str) -> bool:
    return "[" in type_name and bool(re.search(r"\b[A-Z][A-Za-z0-9_]*\b", type_name.replace("ID", "")))


def _is_paginated(field_name: str, type_name: str, context: str) -> bool:
    lowered = f"{field_name} {type_name} {context}".lower()
    return "connection" in lowered or "pageinfo" in lowered or bool({"first", "after", "limit", "offset"} & set(lowered.split()))


def _mostly_lower_camel(names: list[str]) -> bool:
    if not names:
        return False
    matching = [name for name in names if re.match(r"^[a-z][A-Za-z0-9]*$", name)]
    return len(matching) / len(names) >= 0.8


def _render_type(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    kind = value.get("kind")
    name = value.get("name")
    nested = value.get("ofType")
    if kind == "NON_NULL":
        return f"{_render_type(nested)}!"
    if kind == "LIST":
        return f"[{_render_type(nested)}]"
    return str(name or kind or "unknown")


def _named_type(value: object) -> str | None:
    if isinstance(value, dict) and isinstance(value.get("name"), str):
        return value["name"]
    return None


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
