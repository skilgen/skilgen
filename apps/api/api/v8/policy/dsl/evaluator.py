from __future__ import annotations

import fnmatch
import re
import time
from collections.abc import Iterable
from typing import Any

from apps.api.api.v8.policy.dsl.models import EvaluationContext, PolicyDecision, PolicyRule, RESTRICTIVENESS


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
    files_raw = payload.get("files") or payload.get("file_scope") or []
    files = [str(item) for item in files_raw] if isinstance(files_raw, list) else [str(files_raw)]
    return EvaluationContext(
        repo=_string_or_none(payload.get("repo")),
        agent=_string_or_none(payload.get("agent")),
        action_class=_string_or_none(payload.get("action_class")),
        command=_string_or_none(payload.get("command")),
        files=files,
        metadata={key: value for key, value in payload.items() if key not in {"repo", "agent", "action_class", "command", "files", "file_scope"}},
    )


def _rule_matches(rule: PolicyRule, context: EvaluationContext) -> bool:
    return _mapping_matches(rule.scope, context, scope=True) and _mapping_matches(rule.match, context, scope=False)


def _mapping_matches(mapping: dict[str, Any], context: EvaluationContext, *, scope: bool) -> bool:
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
        if not scope and key not in {"repo", "agent", "action_class", "command_regex", "file_glob", "files_glob", "metadata"}:
            value = context.metadata.get(key)
            if not _value_matches(_string_or_none(value), expected):
                return False
    return True


def _value_matches(actual: str | None, expected: object) -> bool:
    if isinstance(expected, list):
        return any(_value_matches(actual, item) for item in expected)
    if not isinstance(expected, str):
        return actual == str(expected)
    if actual is None:
        return False
    return fnmatch.fnmatchcase(actual, expected)


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
    return all(_value_matches(_string_or_none(metadata.get(key)), value) for key, value in expected.items())


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

