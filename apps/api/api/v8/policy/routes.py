from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

import yaml
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.services.policy import evaluate_policies
from apps.api.api.v8.flags import is_v8, request_flag_cache
from apps.api.api.v8.policy.dsl import context_from_mapping, evaluate_rules, parse_policy_mapping, parse_policy_yaml
from apps.api.api.v8.policy.dsl.models import FLAGGED_DECISIONS, DecisionVerb, PolicyRule
from apps.api.api.v8.policy.dsl.parser import PolicyDSLParseError, policy_to_rule_config
from apps.api.api.v8.policy.packs import load_starter_packs
from apps.api.api.v8.policy.rbac import report_policy_rbac_status, require_policy_permission
from packages.db.database import get_db
from packages.db.models import OrgPolicy, SkillRegistryEntry


router = APIRouter(
    prefix="/v8/orgs/{org_id}/policy",
    tags=["v8-policy"],
    dependencies=[Depends(request_flag_cache)],
)


class PolicyRuleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    rule_type: str
    rule_config: dict[str, object]
    decision: DecisionVerb
    deprecated_decision: str | None
    dsl_yaml: str | None
    dsl_version: int
    policy_pack: str | None
    enabled: bool
    created_at: datetime
    violation_count: int = 0


class PolicyRuleMutation(BaseModel):
    yaml: str | None = Field(default=None, min_length=1)
    policy: dict[str, object] | None = None
    enabled: bool | None = None
    policy_pack: str | None = None


class EvaluationRequest(BaseModel):
    event: dict[str, object]
    policies: list[dict[str, object]] | None = None


class EvaluationResponse(BaseModel):
    decision: DecisionVerb
    matched_rule_ids: list[str]
    reasons: list[str]
    notifications: list[str]
    compliance_tags: list[str]
    elapsed_ms: float


class ViolationResponse(BaseModel):
    id: str
    policy_id: str
    policy_name: str
    decision: DecisionVerb
    severity: str
    repo_id: str | None
    repo_name: str | None
    skill_id: str | None
    skill_domain: str | None
    description: str
    flagged: bool
    sla_started_at: datetime
    sla_due_at: datetime
    sla_minutes_remaining: int


class ViolationsResponse(BaseModel):
    items: list[ViolationResponse]
    checked_at: datetime


class ApprovalQueueResponse(BaseModel):
    items: list[ViolationResponse]
    rbac: dict[str, str | bool]


class ApprovalDecisionPayload(BaseModel):
    decision: Literal["approve", "deny", "request_info"]
    note: str | None = Field(default=None, max_length=512)


class QuarantineItem(BaseModel):
    id: str
    name: str
    domain: str
    version: str
    disposition: Literal["quarantined", "retired"]
    score_total: float
    updated_at: datetime


class QuarantineDecisionPayload(BaseModel):
    action: Literal["promote", "retire"]
    note: str | None = Field(default=None, max_length=512)


async def _ensure_v8(org_id: str, current_org_id: str, db: AsyncSession) -> None:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="v8 Policy is disabled")


@router.get("/rules", response_model=list[PolicyRuleResponse])
async def list_rules(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[PolicyRuleResponse]:
    await _ensure_v8(org_id, current_org_id, db)
    rows = (await db.execute(select(OrgPolicy).where(OrgPolicy.org_id == org_id).order_by(desc(OrgPolicy.created_at)))).scalars().all()
    violations = await _policy_violation_counts(org_id, db)
    return [_policy_response(row, violations.get(row.id, 0)) for row in rows]


@router.post("/rules", response_model=PolicyRuleResponse)
async def create_rule(
    org_id: str,
    payload: PolicyRuleMutation,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PolicyRuleResponse:
    await _ensure_v8(org_id, current_org_id, db)
    rule, source = _parse_mutation(payload)
    row = OrgPolicy(
        org_id=org_id,
        name=rule.title,
        description=", ".join(rule.compliance_tags) or None,
        rule_type="v8_yaml_dsl",
        rule_config=policy_to_rule_config(rule),
        decision=rule.decision,
        deprecated_decision=rule.deprecated_decision,
        dsl_yaml=source,
        dsl_version=1,
        policy_pack=payload.policy_pack or rule.source_pack,
        severity="error" if rule.decision == "deny" else "warning",
        enabled=True if payload.enabled is None else payload.enabled,
    )
    row.id = rule.id
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _policy_response(row)


@router.patch("/rules/{policy_id}", response_model=PolicyRuleResponse)
async def update_rule(
    org_id: str,
    policy_id: str,
    payload: PolicyRuleMutation,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PolicyRuleResponse:
    await _ensure_v8(org_id, current_org_id, db)
    row = await db.get(OrgPolicy, policy_id)
    if row is None or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Policy rule not found")
    if payload.yaml is not None or payload.policy is not None:
        rule, source = _parse_mutation(payload)
        row.name = rule.title
        row.description = ", ".join(rule.compliance_tags) or None
        row.rule_type = "v8_yaml_dsl"
        row.rule_config = policy_to_rule_config(rule)
        row.decision = rule.decision
        row.deprecated_decision = rule.deprecated_decision
        row.dsl_yaml = source
        row.dsl_version = 1
        row.policy_pack = payload.policy_pack or rule.source_pack
        row.severity = "error" if rule.decision == "deny" else "warning"
    if payload.enabled is not None:
        row.enabled = payload.enabled
    await db.commit()
    await db.refresh(row)
    return _policy_response(row)


@router.delete("/rules/{policy_id}")
async def delete_rule(
    org_id: str,
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, bool]:
    await _ensure_v8(org_id, current_org_id, db)
    row = await db.get(OrgPolicy, policy_id)
    if row is None or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Policy rule not found")
    await db.delete(row)
    await db.commit()
    return {"deleted": True}


@router.get("/rules/starter-packs")
async def starter_packs(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[dict[str, object]]:
    await _ensure_v8(org_id, current_org_id, db)
    return load_starter_packs()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_policy_event(
    org_id: str,
    payload: EvaluationRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> EvaluationResponse:
    await _ensure_v8(org_id, current_org_id, db)
    rules = [_rule_from_policy(row) for row in await _load_enabled_rules(org_id, db)]
    if payload.policies is not None:
        rules = [parse_policy_mapping(item) for item in payload.policies]
    decision = evaluate_rules(rules, context_from_mapping(payload.event))
    return EvaluationResponse(
        decision=decision.decision,
        matched_rule_ids=list(decision.matched_rule_ids),
        reasons=list(decision.reasons),
        notifications=list(decision.notifications),
        compliance_tags=list(decision.compliance_tags),
        elapsed_ms=decision.elapsed_ms,
    )


@router.get("/violations", response_model=ViolationsResponse)
async def list_violations(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ViolationsResponse:
    await _ensure_v8(org_id, current_org_id, db)
    return ViolationsResponse(items=await _violations(org_id, db), checked_at=datetime.utcnow())


@router.get("/approvals", response_model=ApprovalQueueResponse)
async def list_approvals(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ApprovalQueueResponse:
    await _ensure_v8(org_id, current_org_id, db)
    approvals = [item for item in await _violations(org_id, db) if item.decision == "require_approval"]
    return ApprovalQueueResponse(items=approvals, rbac=await report_policy_rbac_status())


@router.post("/approvals/{approval_id}/decision", dependencies=[Depends(require_policy_permission("policy.approvals.approve"))])
async def decide_approval(
    org_id: str,
    approval_id: str,
    payload: ApprovalDecisionPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, str | bool]:
    await _ensure_v8(org_id, current_org_id, db)
    return {"recorded": True, "approval_id": approval_id, "decision": payload.decision}


@router.get("/quarantine", response_model=list[QuarantineItem])
async def list_quarantine(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[QuarantineItem]:
    await _ensure_v8(org_id, current_org_id, db)
    rows = (
        await db.execute(
            select(SkillRegistryEntry)
            .where(SkillRegistryEntry.org_id == org_id)
            .order_by(desc(SkillRegistryEntry.updated_at))
        )
    ).scalars().all()
    items: list[QuarantineItem] = []
    for row in rows:
        tags = {str(tag) for tag in (row.tags or [])}
        if "quarantined" not in tags and not row.is_deprecated:
            continue
        items.append(
            QuarantineItem(
                id=row.id,
                name=row.name,
                domain=row.domain,
                version=row.version,
                disposition="retired" if row.is_deprecated else "quarantined",
                score_total=float(row.score_total or 0),
                updated_at=row.updated_at,
            )
        )
    return items


@router.post("/quarantine/{skill_id}/decision", response_model=QuarantineItem)
async def decide_quarantine(
    org_id: str,
    skill_id: str,
    payload: QuarantineDecisionPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> QuarantineItem:
    await _ensure_v8(org_id, current_org_id, db)
    row = await db.get(SkillRegistryEntry, skill_id)
    if row is None or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Skill registry entry not found")
    tags = [str(tag) for tag in (row.tags or []) if str(tag) != "quarantined"]
    if payload.action == "promote":
        row.tags = tags
        row.is_deprecated = False
        row.deprecation_message = None
    else:
        row.tags = tags
        row.is_deprecated = True
        row.deprecation_message = payload.note or "Retired from Policy quarantine review"
    await db.commit()
    await db.refresh(row)
    return QuarantineItem(
        id=row.id,
        name=row.name,
        domain=row.domain,
        version=row.version,
        disposition="retired" if row.is_deprecated else "quarantined",
        score_total=float(row.score_total or 0),
        updated_at=row.updated_at,
    )


def _parse_mutation(payload: PolicyRuleMutation) -> tuple[PolicyRule, str]:
    try:
        if payload.yaml is not None:
            return parse_policy_yaml(payload.yaml, source_pack=payload.policy_pack), payload.yaml
        if payload.policy is not None:
            rule = parse_policy_mapping(payload.policy, source_pack=payload.policy_pack)
            return rule, yaml.safe_dump(payload.policy, sort_keys=False)
    except PolicyDSLParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise HTTPException(status_code=400, detail="yaml or policy is required")


async def _load_enabled_rules(org_id: str, db: AsyncSession) -> list[OrgPolicy]:
    return (
        await db.execute(
            select(OrgPolicy)
            .where(OrgPolicy.org_id == org_id, OrgPolicy.enabled.is_(True))
            .order_by(OrgPolicy.created_at)
        )
    ).scalars().all()


async def _policy_violation_counts(org_id: str, db: AsyncSession) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in await _violations(org_id, db):
        counts[item.policy_id] = counts.get(item.policy_id, 0) + 1
    return counts


async def _violations(org_id: str, db: AsyncSession) -> list[ViolationResponse]:
    rows = {row.id: row for row in (await db.execute(select(OrgPolicy).where(OrgPolicy.org_id == org_id))).scalars().all()}
    now = datetime.utcnow()
    items: list[ViolationResponse] = []
    for index, violation in enumerate(await evaluate_policies(org_id, db)):
        row = rows.get(violation.policy_id)
        decision = _canonical_decision(getattr(row, "decision", "log_only") if row else "log_only")
        if decision not in FLAGGED_DECISIONS:
            continue
        started = row.created_at if row and row.created_at else now
        due = started.replace() + _sla_delta_minutes(decision)
        remaining = int((due - now).total_seconds() // 60)
        items.append(
            ViolationResponse(
                id=f"{violation.policy_id}:{violation.repo_id or 'org'}:{violation.skill_id or index}",
                policy_id=violation.policy_id,
                policy_name=violation.policy_name,
                decision=decision,
                severity=violation.severity,
                repo_id=violation.repo_id,
                repo_name=violation.repo_name,
                skill_id=violation.skill_id,
                skill_domain=violation.skill_domain,
                description=violation.description,
                flagged=True,
                sla_started_at=started,
                sla_due_at=due,
                sla_minutes_remaining=remaining,
            )
        )
    return items


def _policy_response(policy: OrgPolicy, violation_count: int = 0) -> PolicyRuleResponse:
    return PolicyRuleResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        rule_type=policy.rule_type,
        rule_config=policy.rule_config or {},
        decision=_canonical_decision(getattr(policy, "decision", "log_only")),
        deprecated_decision=getattr(policy, "deprecated_decision", None),
        dsl_yaml=getattr(policy, "dsl_yaml", None),
        dsl_version=int(getattr(policy, "dsl_version", 1) or 1),
        policy_pack=getattr(policy, "policy_pack", None),
        enabled=bool(policy.enabled),
        created_at=policy.created_at,
        violation_count=violation_count,
    )


def _rule_from_policy(policy: OrgPolicy) -> PolicyRule:
    if policy.dsl_yaml:
        return parse_policy_yaml(policy.dsl_yaml, source_pack=policy.policy_pack)
    config = policy.rule_config or {}
    return PolicyRule(
        id=policy.id,
        title=policy.name,
        scope=dict(config.get("scope") or {}),
        match=dict(config.get("match") or config),
        decision=_canonical_decision(getattr(policy, "decision", "log_only")),
        notify=tuple(str(item) for item in config.get("notify", []) if isinstance(item, str)) if isinstance(config.get("notify"), list) else (),
        compliance_tags=tuple(str(item) for item in config.get("compliance_tags", []) if isinstance(item, str)) if isinstance(config.get("compliance_tags"), list) else (),
        priority=int(config.get("priority") or 0),
        source_pack=getattr(policy, "policy_pack", None),
        deprecated_decision=getattr(policy, "deprecated_decision", None),
    )


def _canonical_decision(value: object) -> DecisionVerb:
    from apps.api.api.v8.policy.dsl.parser import canonicalize_decision

    return canonicalize_decision(value)[0]


def _sla_delta_minutes(decision: DecisionVerb):
    from datetime import timedelta

    if decision == "deny":
        return timedelta(hours=4)
    if decision == "require_approval":
        return timedelta(hours=2)
    return timedelta(hours=24)
