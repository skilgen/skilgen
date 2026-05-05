from __future__ import annotations

from fnmatch import fnmatchcase
from typing import Any


ScopeContext = dict[str, Any]
ScopeExpression = dict[str, Any] | str | None


def _string_value(value: Any) -> str:
    return "" if value is None else str(value)


def _match_pattern(actual: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_match_pattern(actual, item) for item in expected)
    if expected is None:
        return actual is None
    pattern = _string_value(expected)
    if pattern == "*":
        return True
    return fnmatchcase(_string_value(actual), pattern)


def _eval_atom(expression: dict[str, Any], context: ScopeContext) -> bool:
    if "all" in expression:
        clauses = expression.get("all")
        return isinstance(clauses, list) and all(matches_scope_expression(clause, context) for clause in clauses)
    if "any" in expression:
        clauses = expression.get("any")
        return isinstance(clauses, list) and any(matches_scope_expression(clause, context) for clause in clauses)
    if "not" in expression:
        return not matches_scope_expression(expression.get("not"), context)

    for field, expected in expression.items():
        if field in {"all", "any", "not"}:
            continue
        if not _match_pattern(context.get(field), expected):
            return False
    return True


def _parse_string_expression(expression: str) -> dict[str, Any]:
    if expression.strip() in {"", "*"}:
        return {}
    clauses: list[dict[str, str]] = []
    for raw_clause in expression.split("&&"):
        clause = raw_clause.strip()
        if not clause:
            continue
        if ":" not in clause:
            return {"__invalid__": clause}
        field, pattern = clause.split(":", 1)
        clauses.append({field.strip(): pattern.strip()})
    if len(clauses) == 1:
        return clauses[0]
    return {"all": clauses}


def matches_scope_expression(expression: ScopeExpression, context: ScopeContext) -> bool:
    """Evaluate the constrained RBAC scope expression.

    Supported forms:
    - None, {}, or "*" means all scopes.
    - {"repo": "payments/*"} uses shell-style globs.
    - {"all": [{"surface": "policy"}, {"repo": "payments/*"}]}.
    - {"any": [...]}, {"not": {...}}.
    - "surface:policy && repo:payments/*" for compact seed/test data.
    """
    if expression is None or expression == {}:
        return True
    if isinstance(expression, str):
        expression = _parse_string_expression(expression)
    if not isinstance(expression, dict) or "__invalid__" in expression:
        return False
    return _eval_atom(expression, context)


def permission_matches(granted: str, requested: str) -> bool:
    if granted in {"*", requested}:
        return True
    if granted.endswith("*"):
        return requested.startswith(granted[:-1])
    return False
