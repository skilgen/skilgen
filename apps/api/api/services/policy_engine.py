from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import OrgPolicy, PRAttribution


PR_POLICY_RULE_TYPES = {"block_on_red", "require_skill_load", "min_compliance"}
ERROR_SEVERITIES = {"error", "critical", "failure", "fatal"}


async def evaluate_pr_policies(
    org_id: str,
    pr_attribution: PRAttribution,
    db: AsyncSession,
) -> list[dict[str, str]]:
    """Evaluate enabled PR-check policies against one PR attribution."""
    result = await db.execute(
        select(OrgPolicy).where(
            OrgPolicy.org_id == org_id,
            OrgPolicy.enabled.is_(True),
            OrgPolicy.rule_type.in_(PR_POLICY_RULE_TYPES),
        )
    )
    failures: list[dict[str, str]] = []
    for policy in result.scalars().all():
        failure = _evaluate_one(policy, pr_attribution)
        if failure:
            failures.append(failure)
    return failures


def validate_pr_policy_config(rule_type: str, config: dict[str, Any] | None) -> dict[str, Any]:
    cfg = dict(config or {})
    if rule_type == "block_on_red":
        return {}
    if rule_type == "require_skill_load":
        runtimes = cfg.get("agent_runtimes") or []
        if not isinstance(runtimes, list) or any(not isinstance(item, str) for item in runtimes):
            raise ValueError("agent_runtimes must be a list of strings")
        return {"agent_runtimes": runtimes}
    if rule_type == "min_compliance":
        threshold = cfg.get("threshold", 80)
        try:
            threshold_float = float(threshold)
        except (TypeError, ValueError) as exc:
            raise ValueError("threshold must be a number") from exc
        if threshold_float < 0 or threshold_float > 100:
            raise ValueError("threshold must be between 0 and 100")
        return {"threshold": threshold_float}
    raise ValueError("Invalid rule_type")


def _evaluate_one(policy: OrgPolicy, attr: PRAttribution) -> dict[str, str] | None:
    cfg = policy.rule_config or {}
    if policy.rule_type == "block_on_red":
        if attr.risk_tier == "red":
            return _failure(policy, f"Policy '{policy.name}': PR risk tier is RED - merge blocked.")

    elif policy.rule_type == "require_skill_load":
        runtimes = cfg.get("agent_runtimes") or []
        if isinstance(runtimes, list) and runtimes and attr.primary_agent not in runtimes:
            return None
        if not attr.skills_loaded:
            return _failure(policy, f"Policy '{policy.name}': No skills were loaded for this agent session.")

    elif policy.rule_type == "min_compliance":
        threshold = float(cfg.get("threshold") or 80)
        violations = [
            item
            for item in (attr.skills_violated or [])
            if isinstance(item, dict) and str(item.get("severity") or "").lower() in ERROR_SEVERITIES
        ]
        compliance = 0.0 if violations else 100.0
        if compliance < threshold:
            return _failure(policy, f"Policy '{policy.name}': Compliance {compliance:.0f}% is below required {threshold:.0f}%.")

    return None


def _failure(policy: OrgPolicy, message: str) -> dict[str, str]:
    return {
        "policy_id": str(policy.id),
        "name": policy.name,
        "rule_type": policy.rule_type,
        "message": message,
    }
