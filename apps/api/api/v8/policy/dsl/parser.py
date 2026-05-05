from __future__ import annotations

from typing import Any

import yaml

from apps.api.api.v8.policy.dsl.models import (
    CANONICAL_DECISIONS,
    LEGACY_DECISION_MAP,
    LEGACY_DECISIONS,
    DecisionVerb,
    PolicyRule,
)


class PolicyDSLParseError(ValueError):
    """Raised when policy YAML falls outside the constrained PRD DSL."""


def canonicalize_decision(value: object) -> tuple[DecisionVerb, str | None]:
    raw = str(value or "").strip()
    if raw in CANONICAL_DECISIONS:
        return raw, None  # type: ignore[return-value]
    if raw in LEGACY_DECISIONS:
        return LEGACY_DECISION_MAP[raw], raw
    raise PolicyDSLParseError(f"Unsupported decision verb: {raw or '<empty>'}")


def parse_policy_yaml(source: str, *, source_pack: str | None = None) -> PolicyRule:
    try:
        loaded = yaml.safe_load(source)
    except yaml.YAMLError as exc:
        raise PolicyDSLParseError(f"Invalid YAML: {exc}") from exc
    return parse_policy_mapping(loaded, source_pack=source_pack)


def parse_policy_mapping(loaded: object, *, source_pack: str | None = None) -> PolicyRule:
    if not isinstance(loaded, dict):
        raise PolicyDSLParseError("Policy must be a YAML mapping")
    if "rego" in loaded or "rego_module" in loaded:
        raise PolicyDSLParseError("Rego policies are not supported in PR-3")

    policy_id = _required_string(loaded, "id")
    title = _required_string(loaded, "title")
    scope = _optional_mapping(loaded, "scope")
    match = _required_mapping(loaded, "match")
    decision, deprecated = canonicalize_decision(loaded.get("decision"))
    notify = _string_tuple(loaded.get("notify"), "notify")
    tags = _string_tuple(loaded.get("compliance_tags"), "compliance_tags")
    priority = _integer(loaded.get("priority"), "priority", default=0)

    if not scope and not match:
        raise PolicyDSLParseError("Policy must define scope or match")

    return PolicyRule(
        id=policy_id,
        title=title,
        scope=scope,
        match=match,
        decision=decision,
        notify=notify,
        compliance_tags=tags,
        priority=priority,
        source_pack=source_pack,
        deprecated_decision=deprecated,
    )


def policy_to_rule_config(rule: PolicyRule) -> dict[str, object]:
    return {
        "scope": rule.scope,
        "match": rule.match,
        "notify": list(rule.notify),
        "compliance_tags": list(rule.compliance_tags),
        "priority": rule.priority,
    }


def _required_string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PolicyDSLParseError(f"{key} must be a non-empty string")
    return value.strip()


def _required_mapping(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key)
    if not isinstance(value, dict) or not value:
        raise PolicyDSLParseError(f"{key} must be a non-empty mapping")
    return dict(value)


def _optional_mapping(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key) or {}
    if not isinstance(value, dict):
        raise PolicyDSLParseError(f"{key} must be a mapping")
    return dict(value)


def _string_tuple(value: object, key: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise PolicyDSLParseError(f"{key} must be a list of strings")
    return tuple(item.strip() for item in value)


def _integer(value: object, key: str, *, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        raise PolicyDSLParseError(f"{key} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise PolicyDSLParseError(f"{key} must be an integer") from exc

