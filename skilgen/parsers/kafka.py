"""Parse Kafka topic configs and schema files into operational audit signals."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class KafkaParseError(ValueError):
    """Raised when Kafka topic or schema artifacts cannot be parsed."""


@dataclass(frozen=True)
class KafkaIssue:
    severity: str
    category: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class KafkaTopic:
    name: str
    partitions: int | None
    replication_factor: int | None
    retention_ms: int | None
    cleanup_policy: str | None
    configs: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class KafkaField:
    name: str
    field_type: str
    required: bool = False
    default: object | None = None
    doc: str | None = None


@dataclass(frozen=True)
class KafkaSchema:
    name: str
    schema_type: str
    namespace: str | None
    fields: list[KafkaField]
    compatibility: str | None = None


@dataclass(frozen=True)
class KafkaAnalysis:
    source_path: str
    topics: list[KafkaTopic]
    schemas: list[KafkaSchema]
    patterns: list[str]
    issues: list[KafkaIssue]


def parse_kafka_artifact(path: str | Path) -> KafkaAnalysis:
    """Parse a Kafka YAML topic config, Avro schema, JSON schema, or directory."""

    source = Path(path).resolve()
    if source.is_dir():
        analyses: list[KafkaAnalysis] = []
        skipped_errors: list[str] = []
        for child in sorted(source.rglob("*")):
            if not child.is_file() or not _is_kafka_candidate(child):
                continue
            try:
                analyses.append(parse_kafka_artifact(child))
            except KafkaParseError as exc:
                skipped_errors.append(str(exc))
        topics = [topic for analysis in analyses for topic in analysis.topics]
        schemas = [schema for analysis in analyses for schema in analysis.schemas]
        issues = [issue for analysis in analyses for issue in analysis.issues]
        patterns = sorted(dict.fromkeys(pattern for analysis in analyses for pattern in analysis.patterns))
        if not analyses:
            suffix = f" Skipped candidates: {'; '.join(skipped_errors[:3])}" if skipped_errors else ""
            raise KafkaParseError(f"No Kafka topic or schema artifacts found in directory: {source}.{suffix}")
        return KafkaAnalysis(str(source), topics, schemas, patterns, issues)

    if not source.exists():
        raise KafkaParseError(f"Kafka artifact does not exist: {source}")
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise KafkaParseError(f"Could not read Kafka artifact {source}: {exc}") from exc
    if not text.strip():
        raise KafkaParseError(f"Kafka artifact is empty: {source}")

    suffix = source.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        return parse_kafka_topic(text, source_path=str(source))
    if suffix == ".avsc":
        schema = _parse_avro_schema(text, source_path=str(source))
        issues, patterns = _audit_schemas([schema], str(source))
        return KafkaAnalysis(str(source), [], [schema], patterns, issues)
    if suffix == ".json":
        schema = _parse_json_schema(text, source_path=str(source))
        issues, patterns = _audit_schemas([schema], str(source))
        return KafkaAnalysis(str(source), [], [schema], patterns, issues)
    raise KafkaParseError(f"Unsupported Kafka artifact type for {source}; expected YAML, .avsc, or JSON schema.")


def parse_kafka_topic(text: str, *, source_path: str = "<memory>") -> KafkaAnalysis:
    """Parse a Kafka topic YAML config string."""

    if not text.strip():
        raise KafkaParseError(f"Kafka topic YAML is empty: {source_path}")
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise KafkaParseError(f"Could not parse Kafka topic YAML at {source_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KafkaParseError(f"Kafka topic YAML must contain a mapping: {source_path}")

    topic_payload = payload.get("topic") if isinstance(payload.get("topic"), dict) else payload
    topic = _topic_from_payload(topic_payload, source_path)
    schemas: list[KafkaSchema] = []
    if isinstance(payload.get("schema"), dict):
        schemas.append(_schema_from_mapping(payload["schema"], source_path=source_path))
    issues, patterns = _audit_topics([topic], source_path)
    schema_issues, schema_patterns = _audit_schemas(schemas, source_path)
    return KafkaAnalysis(source_path, [topic], schemas, sorted(dict.fromkeys([*patterns, *schema_patterns])), [*issues, *schema_issues])


def parse_kafka_schema(path: str | Path) -> KafkaSchema:
    """Parse an Avro .avsc or JSON schema file from disk."""

    analysis = parse_kafka_artifact(path)
    if not analysis.schemas:
        raise KafkaParseError(f"No schema found in Kafka artifact: {path}")
    return analysis.schemas[0]


def _topic_from_payload(payload: object, source_path: str) -> KafkaTopic:
    if not isinstance(payload, dict):
        raise KafkaParseError(f"Kafka topic config must be a mapping: {source_path}")
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    configs = _collect_configs(payload)
    name = str(payload.get("name") or metadata.get("name") or payload.get("topic_name") or "").strip()
    if not name:
        raise KafkaParseError(f"Kafka topic config is missing a topic name: {source_path}")
    return KafkaTopic(
        name=name,
        partitions=_int_or_none(payload.get("partitions") or payload.get("num_partitions") or configs.get("partitions")),
        replication_factor=_int_or_none(
            payload.get("replication_factor") or payload.get("replicationFactor") or configs.get("replication.factor")
        ),
        retention_ms=_int_or_none(configs.get("retention.ms") or payload.get("retention_ms") or payload.get("retentionMs")),
        cleanup_policy=_string_or_none(configs.get("cleanup.policy") or payload.get("cleanup_policy") or payload.get("cleanupPolicy")),
        configs=configs,
    )


def _collect_configs(payload: dict[str, Any]) -> dict[str, object]:
    configs: dict[str, object] = {}
    raw_configs = payload.get("configs") or payload.get("config")
    if isinstance(raw_configs, dict):
        configs.update(raw_configs)
    spec = payload.get("spec")
    if isinstance(spec, dict):
        if isinstance(spec.get("config"), dict):
            configs.update(spec["config"])
        if isinstance(spec.get("configs"), dict):
            configs.update(spec["configs"])
        for key in ("partitions", "replicationFactor", "replication_factor"):
            if key in spec and key not in configs:
                configs[key] = spec[key]
    return configs


def _parse_avro_schema(text: str, *, source_path: str) -> KafkaSchema:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KafkaParseError(f"Could not parse Avro schema JSON at {source_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KafkaParseError(f"Avro schema must be a JSON object: {source_path}")
    return _schema_from_mapping(payload, source_path=source_path, default_schema_type="avro")


def _parse_json_schema(text: str, *, source_path: str) -> KafkaSchema:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KafkaParseError(f"Could not parse Kafka JSON schema at {source_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KafkaParseError(f"Kafka JSON schema must be a JSON object: {source_path}")
    return _schema_from_mapping(payload, source_path=source_path, default_schema_type="json_schema")


def _schema_from_mapping(payload: dict[str, Any], *, source_path: str, default_schema_type: str | None = None) -> KafkaSchema:
    schema_type = default_schema_type or str(payload.get("schemaType") or payload.get("schema_type") or payload.get("type") or "json_schema")
    if schema_type == "record" or "fields" in payload:
        return _avro_schema_from_mapping(payload, source_path=source_path)
    return _json_schema_from_mapping(payload, source_path=source_path)


def _avro_schema_from_mapping(payload: dict[str, Any], *, source_path: str) -> KafkaSchema:
    name = str(payload.get("name") or "").strip()
    if not name:
        raise KafkaParseError(f"Avro schema is missing a name: {source_path}")
    raw_fields = payload.get("fields")
    if not isinstance(raw_fields, list):
        raise KafkaParseError(f"Avro schema '{name}' must contain a fields array: {source_path}")
    fields: list[KafkaField] = []
    for field in raw_fields:
        if not isinstance(field, dict) or not field.get("name"):
            raise KafkaParseError(f"Avro schema '{name}' contains a malformed field: {source_path}")
        fields.append(
            KafkaField(
                name=str(field["name"]),
                field_type=_avro_type_name(field.get("type")),
                required=not _avro_type_allows_null(field.get("type")),
                default=field.get("default"),
                doc=str(field["doc"]) if field.get("doc") else None,
            )
        )
    return KafkaSchema(
        name=name,
        schema_type="avro",
        namespace=str(payload["namespace"]) if payload.get("namespace") else None,
        fields=fields,
        compatibility=_string_or_none(payload.get("compatibility") or payload.get("schemaCompatibility")),
    )


def _json_schema_from_mapping(payload: dict[str, Any], *, source_path: str) -> KafkaSchema:
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        raise KafkaParseError(f"JSON schema must contain a properties mapping: {source_path}")
    name = str(payload.get("title") or payload.get("$id") or Path(source_path).stem or "json_schema")
    required = {str(item) for item in payload.get("required", []) if isinstance(item, str)}
    fields = [
        KafkaField(
            name=str(name),
            field_type=_json_type_name(prop),
            required=str(name) in required,
            default=prop.get("default") if isinstance(prop, dict) else None,
            doc=str(prop["description"]) if isinstance(prop, dict) and prop.get("description") else None,
        )
        for name, prop in properties.items()
    ]
    return KafkaSchema(
        name=name,
        schema_type="json_schema",
        namespace=None,
        fields=fields,
        compatibility=_string_or_none(payload.get("compatibility") or payload.get("schemaCompatibility")),
    )


def _audit_topics(topics: list[KafkaTopic], source_path: str) -> tuple[list[KafkaIssue], list[str]]:
    issues: list[KafkaIssue] = []
    patterns: list[str] = []
    for topic in topics:
        if topic.retention_ms is not None:
            patterns.append("retention-configured")
        else:
            issues.append(KafkaIssue("warning", "retention", f"Topic '{topic.name}' does not define retention.ms.", source_path))
        if topic.cleanup_policy:
            policies = {part.strip() for part in topic.cleanup_policy.split(",")}
            if "compact" in policies:
                patterns.append("compacted-topic")
            if "delete" in policies:
                issues.append(
                    KafkaIssue(
                        "warning",
                        "delete-policy-audit",
                        f"Topic '{topic.name}' uses delete cleanup policy; verify retention/audit requirements.",
                        source_path,
                    )
                )
        if topic.replication_factor is not None and topic.replication_factor < 3:
            issues.append(
                KafkaIssue(
                    "warning",
                    "replication-factor",
                    f"Topic '{topic.name}' replication factor is below the common production minimum of 3.",
                    source_path,
                )
            )
        throughput_hint = str(topic.configs.get("throughput") or topic.configs.get("throughput.tier") or topic.configs.get("expected_throughput") or "").lower()
        if topic.partitions == 1 and throughput_hint in {"high", "heavy", "critical"}:
            issues.append(
                KafkaIssue(
                    "error",
                    "single-partition-high-throughput",
                    f"Topic '{topic.name}' is single-partition but marked as high throughput.",
                    source_path,
                )
            )
    return issues, patterns


def _audit_schemas(schemas: list[KafkaSchema], source_path: str) -> tuple[list[KafkaIssue], list[str]]:
    issues: list[KafkaIssue] = []
    patterns: list[str] = []
    for schema in schemas:
        if schema.compatibility:
            patterns.append("schema-compatibility-configured")
        else:
            issues.append(KafkaIssue("info", "schema-evolution", f"Schema '{schema.name}' does not declare compatibility mode.", source_path))
        if schema.schema_type == "avro" and not schema.namespace:
            issues.append(KafkaIssue("warning", "schema-namespace", f"Avro schema '{schema.name}' is missing a namespace.", source_path))
        for field in schema.fields:
            if schema.schema_type == "avro" and field.required and field.default is None:
                issues.append(
                    KafkaIssue(
                        "info",
                        "schema-evolution",
                        f"Required Avro field '{schema.name}.{field.name}' has no default, which can limit backward compatibility.",
                        source_path,
                    )
                )
    if schemas:
        patterns.append("schema-defined")
    return issues, patterns


def _is_kafka_candidate(path: Path) -> bool:
    return path.suffix.lower() in {".avsc", ".json", ".yaml", ".yml"}


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _avro_type_name(value: object) -> str:
    if isinstance(value, list):
        return "|".join(_avro_type_name(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("type") or "record")
    return str(value)


def _avro_type_allows_null(value: object) -> bool:
    if isinstance(value, list):
        return any(item == "null" or (isinstance(item, dict) and item.get("type") == "null") for item in value)
    return value == "null" or (isinstance(value, dict) and value.get("type") == "null")


def _json_type_name(value: object) -> str:
    if not isinstance(value, dict):
        return "object"
    raw_type = value.get("type")
    if isinstance(raw_type, list):
        return "|".join(str(item) for item in raw_type)
    return str(raw_type or "object")
