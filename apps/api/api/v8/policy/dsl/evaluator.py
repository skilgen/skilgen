from __future__ import annotations

import fnmatch
import re
import time
from collections.abc import Iterable
from typing import Any

from apps.api.api.v8.policy.dsl.models import EvaluationContext, PolicyDecision, PolicyRule, RESTRICTIVENESS

AGENT_COMPLIANCE_ALIASES: dict[str, tuple[str, ...]] = {
    "provider": ("provider", "agent_provider", "source_provider"),
    "model": ("model", "model_name", "model_id"),
    "intelligence_tier": ("intelligence_tier", "model_tier", "reasoning_tier"),
    "access_scope": ("access_scope", "permission_scope", "grant_scope"),
    "full_access": ("full_access", "is_full_access", "has_full_access", "access_scope", "permission_scope", "grant_scope"),
    "tool_permissions": ("tool_permissions", "tools", "tool_calls", "mcp_tools"),
    "mcp_server": ("mcp_server", "mcp_server_name", "mcp_server_id"),
    "mcp_tool": ("mcp_tool", "mcp_tool_name", "tool_name", "mcp_tools", "tool_permissions", "tools", "tool_calls"),
    "mcp_tools": ("mcp_tools", "tool_permissions", "tools", "tool_calls"),
    "repo_sensitivity": ("repo_sensitivity", "repo_sensitivity_tier", "sensitivity_tier"),
    "policy_decision": ("policy_decision", "decision", "outcome"),
    "source_envelope_hash": ("source_envelope_hash", "envelope_hash", "event_hash"),
}


def evaluate_rules(rules: Iterable[PolicyRule], context: EvaluationContext) -> PolicyDecision:
    started = time.perf_counter()
    matched = [rule for rule in rules if _rule_matches(rule, context)]
    matched.sort(key=lambda rule: (-RESTRICTIVENESS[rule.decision], -rule.priority, rule.id))
    if not matched:
        return PolicyDecision(decision="allow", elapsed_ms=_elapsed_ms(started))

    winner = matched[0]
    return PolicyDecision(
        decision=winner.decision,
        matched_rule_ids=tuple(rule.id for rule in matched),
        reasons=tuple(rule.title for rule in matched),
        notifications=_unique(item for rule in matched for item in rule.notify),
        compliance_tags=_unique(item for rule in matched for item in rule.compliance_tags),
        redactions=_unique(_redaction_targets(rule) for rule in matched),
        dlp_routes=_unique(_dlp_targets(rule) for rule in matched),
        elapsed_ms=_elapsed_ms(started),
    )


def context_from_mapping(payload: dict[str, Any]) -> EvaluationContext:
    files_raw = payload.get("files") or payload.get("file_scope") or payload.get("file_paths") or []
    files = [str(item) for item in files_raw] if isinstance(files_raw, list) else [str(files_raw)]
    reserved = {"repo", "agent", "action_class", "command", "files", "file_scope", "file_paths", "metadata"}
    metadata = dict(payload.get("metadata") or {}) if isinstance(payload.get("metadata"), dict) else {}
    metadata.update({key: value for key, value in payload.items() if key not in reserved})
    return EvaluationContext(
        repo=_string_or_none(payload.get("repo")),
        agent=_string_or_none(payload.get("agent")),
        action_class=_string_or_none(payload.get("action_class")),
        command=_string_or_none(payload.get("command")),
        files=files,
        metadata=metadata,
    )


def _rule_matches(rule: PolicyRule, context: EvaluationContext) -> bool:
    return _mapping_matches(rule.scope, context, scope=True) and _mapping_matches(rule.match, context, scope=False)


def _mapping_matches(mapping: dict[str, Any], context: EvaluationContext, *, scope: bool) -> bool:
    recognized = {"repo", "agent", "action_class", "command_regex", "file_glob", "files_glob", "metadata"} | set(AGENT_COMPLIANCE_ALIASES)
    for key, expected in mapping.items():
        if key == "repo" and not _value_matches(context.repo, expected):
            return False
        if key == "agent" and not _value_matches(context.agent, expected):
            return False
        if key == "action_class" and not _value_matches(context.action_class, expected):
            return False
        if key == "command_regex" and not _regex_matches(context.command or "", expected):
            return False
        if key in {"file_glob", "files_glob"} and not _any_file_matches(context.files, expected):
            return False
        if key == "metadata" and not _metadata_matches(context.metadata, expected):
            return False
        if key in AGENT_COMPLIANCE_ALIASES and not _value_matches(_metadata_lookup(context.metadata, key), expected):
            return False
        if not scope and key not in recognized:
            if not _value_matches(_metadata_lookup(context.metadata, key), expected):
                return False
    return True


def _value_matches(actual: object, expected: object) -> bool:
    if isinstance(expected, list):
        return any(_value_matches(actual, item) for item in expected)
    if isinstance(actual, (list, tuple, set)):
        return any(_value_matches(item, expected) for item in actual)
    if isinstance(expected, bool):
        if isinstance(actual, bool):
            return actual is expected
        if actual is None:
            return False
        normalized = str(actual).strip().lower()
        return normalized in {"true", "1", "yes", "full-access"} if expected else normalized in {"false", "0", "no", ""}
    if not isinstance(expected, str):
        return actual == str(expected)
    if actual is None:
        return False
    return fnmatch.fnmatchcase(str(actual), expected)


def _regex_matches(actual: str, expected: object) -> bool:
    if not isinstance(expected, str):
        return False
    return re.search(expected, actual) is not None


def _any_file_matches(files: list[str], expected: object) -> bool:
    patterns = expected if isinstance(expected, list) else [expected]
    return any(isinstance(pattern, str) and fnmatch.fnmatchcase(file_name, pattern) for file_name in files for pattern in patterns)


def _metadata_matches(metadata: dict[str, Any], expected: object) -> bool:
    if not isinstance(expected, dict):
        return False
    return all(_value_matches(_metadata_lookup(metadata, key), value) for key, value in expected.items())


def _metadata_lookup(metadata: dict[str, Any], key: str) -> object:
    aliases = AGENT_COMPLIANCE_ALIASES.get(key, (key,))
    for alias in aliases:
        value = metadata.get(alias)
        if value is not None and value != "":
            return value
    return None


def _redaction_targets(rule: PolicyRule) -> str:
    return str(rule.match.get("redact") or rule.match.get("data_class") or "matched_payload") if rule.decision == "redact" else ""


def _dlp_targets(rule: PolicyRule) -> str:
    return str(rule.match.get("dlp_route") or rule.match.get("data_class") or "default") if rule.decision == "route_to_dlp" else ""


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 4)
