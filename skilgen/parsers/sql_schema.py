"""Parse SQL DDL and JSON schema exports into table inventory and quality signals."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class SqlSchemaParseError(ValueError):
    """Raised when SQL or JSON schema input cannot be parsed."""


@dataclass(frozen=True)
class SqlIssue:
    severity: str
    category: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class SqlColumn:
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: str | None = None
    default: str | None = None
    comment: str | None = None


@dataclass(frozen=True)
class SqlIndex:
    name: str
    table: str
    columns: list[str]
    unique: bool = False


@dataclass(frozen=True)
class SqlConstraint:
    name: str | None
    kind: str
    columns: list[str] = field(default_factory=list)
    target_table: str | None = None
    target_columns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SqlTable:
    name: str
    columns: list[SqlColumn]
    primary_key: list[str]
    foreign_keys: list[SqlConstraint]
    indexes: list[SqlIndex]
    constraints: list[SqlConstraint]
    comment: str | None = None


@dataclass(frozen=True)
class SqlSchemaAnalysis:
    source_path: str
    tables: list[SqlTable]
    indexes: list[SqlIndex]
    issues: list[SqlIssue]


CREATE_TABLE_RE = re.compile(
    r"\bcreate\s+table\s+(?:if\s+not\s+exists\s+)?(?P<name>[^\s(]+(?:\s*\.\s*[^\s(]+)*)\s*\(",
    re.IGNORECASE,
)
CREATE_INDEX_RE = re.compile(
    r"\bcreate\s+(?P<unique>unique\s+)?index\s+(?:if\s+not\s+exists\s+)?(?P<name>[^\s]+)\s+on\s+(?P<table>[^\s(]+)\s*\((?P<columns>[^)]+)\)",
    re.IGNORECASE,
)
COMMENT_TABLE_RE = re.compile(r"\bcomment\s+on\s+table\s+([^\s]+)\s+is\s+'([^']*)'", re.IGNORECASE)
COMMENT_COLUMN_RE = re.compile(r"\bcomment\s+on\s+column\s+([^\s]+)\.([^\s.]+)\s+is\s+'([^']*)'", re.IGNORECASE)
CONSTRAINT_PREFIX_RE = re.compile(r"^constraint\s+([^\s]+)\s+(.*)$", re.IGNORECASE | re.DOTALL)
PK_RE = re.compile(r"\bprimary\s+key\s*\(([^)]*)\)", re.IGNORECASE)
FK_RE = re.compile(
    r"\bforeign\s+key\s*\(([^)]*)\)\s+references\s+([^\s(]+)\s*(?:\(([^)]*)\))?",
    re.IGNORECASE,
)
INLINE_REF_RE = re.compile(r"\breferences\s+([^\s(]+)\s*(?:\(([^)]*)\))?", re.IGNORECASE)
DEFAULT_RE = re.compile(r"\bdefault\s+(.+?)(?:\s+not\s+null|\s+null|\s+primary\s+key|\s+references\b|$)", re.IGNORECASE)
SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
CONSTRAINT_KEYWORDS = {
    "check",
    "collate",
    "constraint",
    "default",
    "generated",
    "identity",
    "not",
    "null",
    "primary",
    "references",
    "unique",
}


def parse_sql_schema(path: str | Path) -> SqlSchemaAnalysis:
    """Parse a SQL DDL file or JSON schema export from disk."""

    source = Path(path).resolve()
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise SqlSchemaParseError(f"Could not read schema file {source}: {exc}") from exc
    if not text.strip():
        raise SqlSchemaParseError(f"Schema file is empty: {source}")
    if source.suffix.lower() == ".json":
        return parse_json_schema_export(text, source_path=str(source))
    return parse_sql_schema_text(text, source_path=str(source))


def parse_sql_schema_text(text: str, *, source_path: str = "<memory>") -> SqlSchemaAnalysis:
    """Parse CREATE TABLE DDL text into a schema analysis."""

    if not text.strip():
        raise SqlSchemaParseError(f"SQL schema input is empty: {source_path}")

    raw_tables = _extract_create_tables(text)
    if not raw_tables:
        raise SqlSchemaParseError(f"No CREATE TABLE statements found in SQL schema input: {source_path}")

    all_indexes = _parse_indexes(text)
    table_comments = {_normalize_name(table): comment for table, comment in COMMENT_TABLE_RE.findall(text)}
    column_comments = {
        (_normalize_name(table), _normalize_name(column)): comment
        for table, column, comment in COMMENT_COLUMN_RE.findall(text)
    }
    tables: list[SqlTable] = []
    for raw_name, body in raw_tables:
        table_name = _normalize_name(raw_name)
        columns: list[SqlColumn] = []
        constraints: list[SqlConstraint] = []
        primary_key: list[str] = []
        foreign_keys: list[SqlConstraint] = []

        for definition in _split_top_level(body):
            parsed_constraint = _parse_table_constraint(definition)
            if parsed_constraint is not None:
                constraints.append(parsed_constraint)
                if parsed_constraint.kind == "primary_key":
                    primary_key.extend(parsed_constraint.columns)
                elif parsed_constraint.kind == "foreign_key":
                    foreign_keys.append(parsed_constraint)
                continue
            column = _parse_column(definition, table_name, column_comments)
            columns.append(column)
            if column.primary_key:
                primary_key.append(column.name)
            if column.foreign_key:
                target_table, target_columns = _split_fk_target(column.foreign_key)
                foreign_keys.append(
                    SqlConstraint(
                        name=None,
                        kind="foreign_key",
                        columns=[column.name],
                        target_table=target_table,
                        target_columns=target_columns,
                    )
                )

        table_indexes = [index for index in all_indexes if _normalize_name(index.table) == table_name]
        tables.append(
            SqlTable(
                name=table_name,
                columns=columns,
                primary_key=sorted(dict.fromkeys(primary_key)),
                foreign_keys=foreign_keys,
                indexes=table_indexes,
                constraints=constraints,
                comment=table_comments.get(table_name),
            )
        )

    issues = _audit_schema(tables, all_indexes, source_path)
    return SqlSchemaAnalysis(source_path=source_path, tables=tables, indexes=all_indexes, issues=issues)


def parse_json_schema_export(text: str, *, source_path: str = "<memory>") -> SqlSchemaAnalysis:
    """Parse JSON schema exports into table and column inventory."""

    if not text.strip():
        raise SqlSchemaParseError(f"JSON schema input is empty: {source_path}")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SqlSchemaParseError(f"Could not parse JSON schema export at {source_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SqlSchemaParseError(f"JSON schema export must be an object: {source_path}")

    if isinstance(payload.get("tables"), list):
        tables = [_table_from_export(item) for item in payload["tables"] if isinstance(item, dict)]
    else:
        tables = [_table_from_json_schema(payload, source_path)]
    if not tables:
        raise SqlSchemaParseError(f"JSON schema export did not contain any tables: {source_path}")

    indexes: list[SqlIndex] = []
    for table in tables:
        indexes.extend(table.indexes)
    issues = _audit_schema(tables, indexes, source_path)
    return SqlSchemaAnalysis(source_path=source_path, tables=tables, indexes=indexes, issues=issues)


def _extract_create_tables(text: str) -> list[tuple[str, str]]:
    tables: list[tuple[str, str]] = []
    for match in CREATE_TABLE_RE.finditer(text):
        open_index = text.find("(", match.start())
        if open_index == -1:
            continue
        close_index = _find_matching_paren(text, open_index)
        if close_index == -1:
            raise SqlSchemaParseError(f"Unbalanced CREATE TABLE parentheses near '{match.group('name')}'.")
        tables.append((match.group("name"), text[open_index + 1 : close_index]))
    return tables


def _find_matching_paren(text: str, open_index: int) -> int:
    depth = 0
    quote: str | None = None
    for index in range(open_index, len(text)):
        char = text[index]
        if quote:
            if char == quote and text[index - 1] != "\\":
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return -1


def _split_top_level(value: str) -> list[str]:
    entries: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    for index, char in enumerate(value):
        if quote:
            if char == quote and value[index - 1] != "\\":
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            entry = value[start:index].strip()
            if entry:
                entries.append(entry)
            start = index + 1
    tail = value[start:].strip()
    if tail:
        entries.append(tail)
    return entries


def _parse_indexes(text: str) -> list[SqlIndex]:
    indexes: list[SqlIndex] = []
    for match in CREATE_INDEX_RE.finditer(text):
        indexes.append(
            SqlIndex(
                name=_normalize_name(match.group("name")),
                table=_normalize_name(match.group("table")),
                columns=[_normalize_name(column) for column in _split_identifier_list(match.group("columns"))],
                unique=bool(match.group("unique")),
            )
        )
    return indexes


def _parse_table_constraint(definition: str) -> SqlConstraint | None:
    normalized = definition.strip()
    name: str | None = None
    match = CONSTRAINT_PREFIX_RE.match(normalized)
    if match:
        name = _normalize_name(match.group(1))
        normalized = match.group(2).strip()

    pk = PK_RE.search(normalized)
    if pk:
        return SqlConstraint(name=name, kind="primary_key", columns=[_normalize_name(col) for col in _split_identifier_list(pk.group(1))])

    fk = FK_RE.search(normalized)
    if fk:
        return SqlConstraint(
            name=name,
            kind="foreign_key",
            columns=[_normalize_name(col) for col in _split_identifier_list(fk.group(1))],
            target_table=_normalize_name(fk.group(2)),
            target_columns=[_normalize_name(col) for col in _split_identifier_list(fk.group(3) or "")],
        )

    lowered = normalized.lower()
    if lowered.startswith("unique"):
        columns_match = re.search(r"\(([^)]*)\)", normalized)
        return SqlConstraint(
            name=name,
            kind="unique",
            columns=[_normalize_name(col) for col in _split_identifier_list(columns_match.group(1) if columns_match else "")],
        )
    if lowered.startswith("check"):
        return SqlConstraint(name=name, kind="check")
    return None


def _parse_column(definition: str, table_name: str, comments: dict[tuple[str, str], str]) -> SqlColumn:
    tokens = _tokenize_column_definition(definition)
    if len(tokens) < 2:
        raise SqlSchemaParseError(f"Malformed column definition: {definition}")
    name = _normalize_name(tokens[0])
    type_parts: list[str] = []
    for token in tokens[1:]:
        if token.lower() in CONSTRAINT_KEYWORDS:
            break
        type_parts.append(token)
    data_type = " ".join(type_parts).strip()
    if not data_type:
        raise SqlSchemaParseError(f"Column '{name}' is missing a data type in definition: {definition}")
    lowered = definition.lower()
    inline_ref = INLINE_REF_RE.search(definition)
    default = DEFAULT_RE.search(definition)
    return SqlColumn(
        name=name,
        data_type=data_type.upper(),
        nullable="not null" not in lowered and "primary key" not in lowered,
        primary_key="primary key" in lowered,
        foreign_key=_format_fk_target(inline_ref.group(1), inline_ref.group(2)) if inline_ref else None,
        default=default.group(1).strip() if default else None,
        comment=comments.get((table_name, name)),
    )


def _tokenize_column_definition(definition: str) -> list[str]:
    return re.findall(r'"[^"]+"|`[^`]+`|\[[^\]]+\]|[^\s]+', definition.strip())


def _table_from_export(payload: dict[str, Any]) -> SqlTable:
    name = _normalize_name(str(payload.get("name") or payload.get("table") or "unknown_table"))
    raw_columns = payload.get("columns")
    if not isinstance(raw_columns, list):
        raise SqlSchemaParseError(f"JSON table export for '{name}' must contain a columns array.")
    columns = [
        SqlColumn(
            name=_normalize_name(str(column.get("name"))),
            data_type=str(column.get("type") or column.get("data_type") or "unknown").upper(),
            nullable=bool(column.get("nullable", True)),
            primary_key=bool(column.get("primary_key", False)),
            foreign_key=str(column["foreign_key"]) if column.get("foreign_key") else None,
            comment=str(column["comment"]) if column.get("comment") else None,
        )
        for column in raw_columns
        if isinstance(column, dict) and column.get("name")
    ]
    explicit_primary_key = [_normalize_name(str(column)) for column in payload.get("primary_key", []) if str(column).strip()]
    if explicit_primary_key:
        columns = [
            SqlColumn(
                name=column.name,
                data_type=column.data_type,
                nullable=column.nullable,
                primary_key=column.name in explicit_primary_key or column.primary_key,
                foreign_key=column.foreign_key,
                default=column.default,
                comment=column.comment,
            )
            for column in columns
        ]
    indexes = [
        SqlIndex(
            name=_normalize_name(str(index.get("name") or f"idx_{name}_{'_'.join(index.get('columns', []))}")),
            table=name,
            columns=[_normalize_name(str(column)) for column in index.get("columns", [])],
            unique=bool(index.get("unique", False)),
        )
        for index in payload.get("indexes", [])
        if isinstance(index, dict)
    ]
    foreign_keys = [
        _foreign_key_constraint_from_export(item)
        for item in payload.get("foreign_keys", [])
        if isinstance(item, dict)
    ]
    foreign_keys.extend(
        _column_foreign_key_constraint(column)
        for column in columns
        if column.foreign_key
    )
    constraints = [
        _constraint_from_export(item)
        for item in payload.get("constraints", [])
        if isinstance(item, dict)
    ]
    return SqlTable(
        name=name,
        columns=columns,
        primary_key=explicit_primary_key or [column.name for column in columns if column.primary_key],
        foreign_keys=foreign_keys,
        indexes=indexes,
        constraints=constraints,
        comment=str(payload.get("comment") or payload.get("description") or "") or None,
    )


def _table_from_json_schema(payload: dict[str, Any], source_path: str) -> SqlTable:
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        raise SqlSchemaParseError(f"JSON schema must contain an object properties mapping: {source_path}")
    table_name = _normalize_name(str(payload.get("title") or Path(source_path).stem or "json_schema"))
    required = {str(item) for item in payload.get("required", []) if isinstance(item, str)}
    columns = [
        SqlColumn(
            name=_normalize_name(name),
            data_type=_json_type_to_sql(prop),
            nullable=name not in required,
            primary_key=name in {"id", f"{table_name}_id"} and name in required,
            comment=str(prop["description"]) if isinstance(prop, dict) and prop.get("description") else None,
        )
        for name, prop in properties.items()
    ]
    return SqlTable(
        name=table_name,
        columns=columns,
        primary_key=[column.name for column in columns if column.primary_key],
        foreign_keys=[],
        indexes=[],
        constraints=[],
        comment=str(payload["description"]) if payload.get("description") else None,
    )


def _audit_schema(tables: list[SqlTable], indexes: list[SqlIndex], source_path: str) -> list[SqlIssue]:
    issues: list[SqlIssue] = []
    indexes_by_table = {table.name: table.indexes for table in tables}
    for table in tables:
        if not SNAKE_CASE_RE.fullmatch(_unqualify(table.name)):
            issues.append(SqlIssue("warning", "naming", f"Table '{table.name}' does not follow snake_case naming.", source_path))
        if not table.primary_key:
            issues.append(SqlIssue("error", "no-primary-key", f"Table '{table.name}' has no primary key.", source_path))
        if "updated_at" not in {column.name for column in table.columns}:
            issues.append(SqlIssue("warning", "missing-updated-at", f"Table '{table.name}' is missing an updated_at column.", source_path))

        fk_columns = {column for fk in table.foreign_keys for column in fk.columns}
        indexed_columns = {column for index in indexes_by_table.get(table.name, []) for column in index.columns}
        for column in table.columns:
            if not SNAKE_CASE_RE.fullmatch(column.name):
                issues.append(SqlIssue("warning", "naming", f"Column '{table.name}.{column.name}' does not follow snake_case naming.", source_path))
            if column.name.endswith("_id") and not column.primary_key and column.name not in fk_columns:
                issues.append(SqlIssue("warning", "foreign-key-coverage", f"Column '{table.name}.{column.name}' looks like a foreign key but has no FK constraint.", source_path))
            if column.name in fk_columns and column.name not in indexed_columns and column.name not in table.primary_key:
                issues.append(SqlIssue("warning", "index-strategy", f"Foreign key '{table.name}.{column.name}' is not indexed.", source_path))

        for index in indexes_by_table.get(table.name, []):
            for column_name in index.columns:
                column = next((candidate for candidate in table.columns if candidate.name == column_name), None)
                if column and (column.data_type == "TEXT" or column.data_type.upper().startswith("VARCHAR(MAX)")):
                    issues.append(SqlIssue("warning", "indexed-large-text", f"Index '{index.name}' includes large text column '{table.name}.{column_name}'.", source_path))
    for index in indexes:
        if not SNAKE_CASE_RE.fullmatch(index.name):
            issues.append(SqlIssue("info", "naming", f"Index '{index.name}' does not follow snake_case naming.", source_path))
    return issues


def _split_identifier_list(value: str) -> list[str]:
    return [item.strip() for item in _split_top_level(value or "") if item.strip()]


def _normalize_name(value: str) -> str:
    return value.strip().strip(",").replace(" ", "").strip('"`[]').lower()


def _unqualify(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def _json_type_to_sql(prop: object) -> str:
    if not isinstance(prop, dict):
        return "JSON"
    raw_type = prop.get("type")
    if isinstance(raw_type, list):
        raw_type = next((item for item in raw_type if item != "null"), "object")
    return {
        "array": "JSONB",
        "boolean": "BOOLEAN",
        "integer": "INTEGER",
        "number": "NUMERIC",
        "object": "JSONB",
        "string": "VARCHAR",
    }.get(str(raw_type), "JSONB").upper()


def _format_fk_target(table: str, columns: str | None) -> str:
    normalized_table = _normalize_name(table)
    normalized_columns = [_normalize_name(column) for column in _split_identifier_list(columns or "")]
    if normalized_columns:
        return f"{normalized_table}({', '.join(normalized_columns)})"
    return normalized_table


def _split_fk_target(value: str) -> tuple[str, list[str]]:
    match = re.match(r"([^(]+)(?:\(([^)]*)\))?", value)
    if not match:
        return value, []
    return _normalize_name(match.group(1)), [_normalize_name(column) for column in _split_identifier_list(match.group(2) or "")]


def _column_foreign_key_constraint(column: SqlColumn) -> SqlConstraint:
    target_table, target_columns = _split_fk_target(column.foreign_key or "")
    return SqlConstraint(
        name=None,
        kind="foreign_key",
        columns=[column.name],
        target_table=target_table,
        target_columns=target_columns,
    )


def _foreign_key_constraint_from_export(payload: dict[str, Any]) -> SqlConstraint:
    reference = payload.get("references")
    target_table = payload.get("target_table")
    target_columns = payload.get("target_columns")
    if isinstance(reference, str) and reference.strip():
        parsed_target_table, parsed_target_columns = _split_fk_target(reference)
    else:
        parsed_target_table = _normalize_name(str(target_table or ""))
        parsed_target_columns = [_normalize_name(str(column)) for column in target_columns or [] if str(column).strip()]
    return SqlConstraint(
        name=_optional_name(payload.get("name")),
        kind="foreign_key",
        columns=[_normalize_name(str(column)) for column in payload.get("columns", []) if str(column).strip()],
        target_table=parsed_target_table or None,
        target_columns=parsed_target_columns,
    )


def _constraint_from_export(payload: dict[str, Any]) -> SqlConstraint:
    kind = _normalize_name(str(payload.get("kind") or payload.get("type") or "constraint"))
    return SqlConstraint(
        name=_optional_name(payload.get("name")),
        kind=kind,
        columns=[_normalize_name(str(column)) for column in payload.get("columns", []) if str(column).strip()],
        target_table=_normalize_name(str(payload.get("target_table") or "")) or None,
        target_columns=[_normalize_name(str(column)) for column in payload.get("target_columns", []) if str(column).strip()],
    )


def _optional_name(value: object) -> str | None:
    if value is None:
        return None
    cleaned = _normalize_name(str(value))
    return cleaned or None
