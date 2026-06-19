from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


DecisionVerb = Literal["allow", "deny", "require_approval", "log_only", "redact", "route_to_dlp"]
LegacyDecisionVerb = Literal["block", "warn", "log"]

CANONICAL_DECISIONS: tuple[DecisionVerb, ...] = (
    "allow",
    "deny",
    "require_approval",
    "log_only",
    "redact",
    "route_to_dlp",
)
LEGACY_DECISIONS: tuple[LegacyDecisionVerb, ...] = ("block", "warn", "log")
LEGACY_DECISION_MAP: dict[str, DecisionVerb] = {
    "block": "deny",
    "warn": "require_approval",
    "log": "log_only",
}
DOWNGRADE_DECISION_MAP: dict[str, str] = {
    "allow": "log",
    "deny": "block",
    "require_approval": "warn",
    "log_only": "log",
    "redact": "warn",
    "route_to_dlp": "warn",
}
FLAGGED_DECISIONS: frozenset[DecisionVerb] = frozenset({"deny", "require_approval", "log_only"})
RESTRICTIVENESS: dict[DecisionVerb, int] = {
    "allow": 0,
    "log_only": 10,
    "redact": 20,
    "route_to_dlp": 30,
    "require_approval": 40,
    "deny": 50,
}


@dataclass(frozen=True)
class PolicyRule:
    id: str
    title: str
    scope: dict[str, Any]
    match: dict[str, Any]
    decision: DecisionVerb
    notify: tuple[str, ...] = ()
    compliance_tags: tuple[str, ...] = ()
    priority: int = 0
    source_pack: str | None = None
    deprecated_decision: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    decision: DecisionVerb
    matched_rule_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    notifications: tuple[str, ...] = ()
    compliance_tags: tuple[str, ...] = ()
    redactions: tuple[str, ...] = ()
    dlp_routes: tuple[str, ...] = ()
    elapsed_ms: float = 0.0


@dataclass
class EvaluationContext:
    repo: str | None = None
    agent: str | None = None
    action_class: str | None = None
    command: str | None = None
    files: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

