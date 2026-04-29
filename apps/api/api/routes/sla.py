from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import Repo, Skill
from packages.db.models.sla_policy import SLAPolicy


router = APIRouter(prefix="/orgs/{org_id}/sla", tags=["sla"])


class SLAPolicyPayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    repo_id: str | None = None
    coverage_target_pct: int = Field(ge=60, le=100)
    alert_email: str | None = None


class SLAPolicyResponse(BaseModel):
    id: str
    org_id: str
    repo_id: str | None
    repo_name: str | None = None
    name: str
    coverage_target_pct: int
    alert_email: str | None
    is_active: bool
    created_at: datetime
    last_checked_at: datetime | None
    last_status: str


def _assert_org_scope(org_id: str, current_org_id: str) -> None:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org mismatch")


async def _coverage(db: AsyncSession, org_id: str, repo_id: str | None) -> int:
    if repo_id:
        total = (await db.execute(select(func.count(Skill.id)).where(Skill.repo_id == repo_id))).scalar_one()
        covered = (await db.execute(select(func.count(Skill.id)).where(Skill.repo_id == repo_id, Skill.score_total >= 60))).scalar_one()
    else:
        repo_ids = (await db.execute(select(Repo.id).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        if not repo_ids:
            return 0
        total = (await db.execute(select(func.count(Skill.id)).where(Skill.repo_id.in_(repo_ids)))).scalar_one()
        covered = (await db.execute(select(func.count(Skill.id)).where(Skill.repo_id.in_(repo_ids), Skill.score_total >= 60))).scalar_one()
    return int(round((int(covered or 0) / int(total or 1)) * 100)) if total else 0


async def _response(db: AsyncSession, policy: SLAPolicy) -> SLAPolicyResponse:
    repo_name = None
    if policy.repo_id:
        repo = await db.get(Repo, policy.repo_id)
        repo_name = repo.name if repo else None
    return SLAPolicyResponse(
        id=policy.id,
        org_id=policy.org_id,
        repo_id=policy.repo_id,
        repo_name=repo_name,
        name=policy.name,
        coverage_target_pct=policy.coverage_target_pct,
        alert_email=policy.alert_email,
        is_active=policy.is_active,
        created_at=policy.created_at,
        last_checked_at=policy.last_checked_at,
        last_status=policy.last_status,
    )


@router.get("", response_model=list[SLAPolicyResponse])
async def list_sla(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> list[SLAPolicyResponse]:
    _assert_org_scope(org_id, current_org_id)
    try:
        policies = (await db.execute(select(SLAPolicy).where(SLAPolicy.org_id == org_id, SLAPolicy.is_active.is_(True)).order_by(SLAPolicy.created_at.desc()))).scalars().all()
        return [await _response(db, policy) for policy in policies]
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not list SLA policies") from exc


@router.post("", response_model=SLAPolicyResponse)
async def create_sla(org_id: str, payload: SLAPolicyPayload, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SLAPolicyResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        policy = SLAPolicy(org_id=org_id, repo_id=payload.repo_id, name=payload.name, coverage_target_pct=payload.coverage_target_pct, alert_email=payload.alert_email, created_at=datetime.utcnow())
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return await _response(db, policy)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create SLA policy") from exc


@router.put("/{policy_id}", response_model=SLAPolicyResponse)
async def update_sla(org_id: str, policy_id: str, payload: SLAPolicyPayload, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SLAPolicyResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        policy = await db.get(SLAPolicy, policy_id)
        if policy is None or policy.org_id != org_id:
            raise HTTPException(status_code=404, detail="SLA policy not found")
        policy.name = payload.name
        policy.repo_id = payload.repo_id
        policy.coverage_target_pct = payload.coverage_target_pct
        policy.alert_email = payload.alert_email
        await db.commit()
        return await _response(db, policy)
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not update SLA policy") from exc


@router.delete("/{policy_id}")
async def delete_sla(org_id: str, policy_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict[str, bool]:
    _assert_org_scope(org_id, current_org_id)
    try:
        policy = await db.get(SLAPolicy, policy_id)
        if policy is None or policy.org_id != org_id:
            raise HTTPException(status_code=404, detail="SLA policy not found")
        policy.is_active = False
        await db.commit()
        return {"deactivated": True}
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not deactivate SLA policy") from exc


@router.post("/{policy_id}/check")
async def check_sla(org_id: str, policy_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        policy = await db.get(SLAPolicy, policy_id)
        if policy is None or policy.org_id != org_id:
            raise HTTPException(status_code=404, detail="SLA policy not found")
        current = await _coverage(db, org_id, policy.repo_id)
        policy.last_status = "compliant" if current >= policy.coverage_target_pct else "breaching"
        policy.last_checked_at = datetime.utcnow()
        await db.commit()
        return {"policy_id": policy.id, "status": policy.last_status, "current_coverage": current, "target": policy.coverage_target_pct, "gap": max(0, policy.coverage_target_pct - current)}
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not check SLA policy") from exc
