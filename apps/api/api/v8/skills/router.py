from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_org_id_optional
from apps.api.api.routes import orgs as org_routes
from apps.api.api.v8.flags import is_v8, request_flag_cache
from packages.db.database import get_db
from packages.db.models import OrgPolicy, Repo, Skill, SkillHalfLife, SkillUsageEvent, SkillVersion


router = APIRouter(
    prefix="/v8/orgs/{org_id}/skills",
    tags=["v8-skills"],
    dependencies=[Depends(request_flag_cache)],
)


class V8SkillScore(BaseModel):
    total: int
    groundedness: int
    coverage: int
    freshness: int
    structure: int


class V8SkillRegistryItem(BaseModel):
    skill_id: str
    name: str
    version: str
    signature_status: str
    score: V8SkillScore
    drift_status: str
    last_code_grounded_at: datetime | None
    owning_team: str
    dependent_agents: list[str]
    policy_bindings: list[str]
    repo_id: str
    repo_name: str
    repo_full_name: str
    sensitivity_tier: str = "internal"


class V8RegistryResponse(BaseModel):
    items: list[V8SkillRegistryItem]
    total: int


class V8ScoreResponse(BaseModel):
    subscores: list[str]
    items: list[V8SkillRegistryItem]
    total: int
    average_score: float
    rubric_path: str = "docs/v8-refactor/skills/score-rubric.md"


class V8DriftEvent(BaseModel):
    skill_id: str
    name: str
    repo_id: str
    repo_name: str
    predicted_decay_date: datetime | None
    predicted_decay_days: float
    decay_confidence: float
    commits_30d: int
    file_churn_30d: int
    regen_queued: bool
    computed_at: datetime


class V8DriftResponse(BaseModel):
    events: list[V8DriftEvent]
    total: int


class V8ProvenanceVersion(BaseModel):
    skill_id: str
    version_id: str
    version_number: int
    content_hash: str
    signature_status: str
    git_commit: str | None
    generation_run_id: str
    scoring_run_id: str
    approver: str | None
    created_at: datetime


class V8ProvenanceResponse(BaseModel):
    versions: list[V8ProvenanceVersion]
    transparency_log: list[dict[str, Any]] = Field(default_factory=list)
    total: int


class V8RepoItem(BaseModel):
    id: str
    full_name: str
    name: str
    language: str | None
    sensitivity_tier: str
    indexing_status: str
    generated_skill_count: int
    drift_count: int
    policy_bindings: list[str]
    last_analysed_at: datetime | None


class V8ReposResponse(BaseModel):
    repos: list[V8RepoItem]
    total: int


async def _require_v8(org_id: str, current_org_id: str | None, db: AsyncSession) -> None:
    if current_org_id is not None and org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="v8 Skills surface is disabled")


def _score(skill: Skill) -> V8SkillScore:
    return V8SkillScore(
        total=int(skill.score_total or 0),
        groundedness=int(skill.score_groundedness or 0),
        coverage=int(skill.score_coverage or 0),
        freshness=int(skill.score_freshness or 0),
        structure=int(skill.score_structure or 0),
    )


def _sensitivity_tier(repo: Repo) -> str:
    value = getattr(repo, "sensitivity_tier", None)
    return value if isinstance(value, str) and value else "internal"


def _signature_status(skill: Skill, latest_version: SkillVersion | None) -> str:
    if latest_version is not None and latest_version.content_hash:
        return "verified"
    if skill.content_hash:
        return "verified"
    return "unsigned"


def _policy_names(policies: Iterable[OrgPolicy]) -> list[str]:
    return sorted({policy.name for policy in policies if policy.enabled})


def _version_label(latest_version: SkillVersion | None) -> str:
    if latest_version is None:
        return "v1"
    return f"v{latest_version.version_number}"


def _registry_item(
    skill: Skill,
    repo: Repo,
    latest_version: SkillVersion | None,
    dependent_agents: Iterable[str],
    policies: Iterable[OrgPolicy],
) -> V8SkillRegistryItem:
    return V8SkillRegistryItem(
        skill_id=skill.id,
        name=skill.skill_path or skill.domain,
        version=_version_label(latest_version),
        signature_status=_signature_status(skill, latest_version),
        score=_score(skill),
        drift_status="drifted" if skill.is_stale else "healthy",
        last_code_grounded_at=getattr(skill, "updated_at", None),
        owning_team=repo.full_name.split("/", 1)[0] if "/" in repo.full_name else repo.full_name,
        dependent_agents=sorted({agent for agent in dependent_agents if agent}),
        policy_bindings=_policy_names(policies),
        repo_id=repo.id,
        repo_name=repo.name,
        repo_full_name=repo.full_name,
        sensitivity_tier=_sensitivity_tier(repo),
    )


async def _org_policies(db: AsyncSession, org_id: str) -> list[OrgPolicy]:
    result = await db.execute(
        select(OrgPolicy).where(OrgPolicy.org_id == org_id, OrgPolicy.enabled.is_(True))
    )
    return list(result.scalars().all())


async def _latest_version(db: AsyncSession, skill_id: str) -> SkillVersion | None:
    result = await db.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill_id, SkillVersion.is_latest.is_(True))
        .order_by(desc(SkillVersion.version_number))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _dependent_agents(db: AsyncSession, skill_id: str) -> list[str]:
    result = await db.execute(
        select(distinct(SkillUsageEvent.agent_runtime)).where(SkillUsageEvent.skill_id == skill_id)
    )
    return [str(agent) for agent in result.scalars().all() if agent]


async def _registry_items(db: AsyncSession, org_id: str, limit: int, offset: int) -> list[V8SkillRegistryItem]:
    rows = (
        await db.execute(
            select(Skill, Repo)
            .join(Repo, Repo.id == Skill.repo_id)
            .where(Repo.org_id == org_id, Repo.is_active.is_(True))
            .order_by(desc(Skill.score_total), Skill.domain)
            .offset(offset)
            .limit(limit)
        )
    ).all()
    policies = await _org_policies(db, org_id)
    items: list[V8SkillRegistryItem] = []
    for skill, repo in rows:
        latest_version = await _latest_version(db, skill.id)
        agents = await _dependent_agents(db, skill.id)
        items.append(_registry_item(skill, repo, latest_version, agents, policies))
    return items


async def _registry_total(db: AsyncSession, org_id: str) -> int:
    result = await db.execute(
        select(func.count(Skill.id))
        .join(Repo, Repo.id == Skill.repo_id)
        .where(Repo.org_id == org_id, Repo.is_active.is_(True))
    )
    return int(result.scalar() or 0)


@router.get("/registry", response_model=V8RegistryResponse)
async def registry(
    org_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> V8RegistryResponse:
    await _require_v8(org_id, current_org_id, db)
    items = await _registry_items(db, org_id, limit, offset)
    return V8RegistryResponse(items=items, total=await _registry_total(db, org_id))


@router.get("/score", response_model=V8ScoreResponse)
async def score(
    org_id: str,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> V8ScoreResponse:
    await _require_v8(org_id, current_org_id, db)
    items = await _registry_items(db, org_id, limit, offset)
    average = round(sum(item.score.total for item in items) / len(items), 2) if items else 0.0
    return V8ScoreResponse(
        subscores=["Groundedness", "Coverage", "Freshness", "Structure"],
        items=items,
        total=await _registry_total(db, org_id),
        average_score=average,
    )


@router.get("/drift", response_model=V8DriftResponse)
async def drift(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> V8DriftResponse:
    await _require_v8(org_id, current_org_id, db)
    rows = (
        await db.execute(
            select(SkillHalfLife, Skill, Repo)
            .join(Skill, Skill.id == SkillHalfLife.skill_id)
            .join(Repo, Repo.id == SkillHalfLife.repo_id)
            .where(SkillHalfLife.org_id == org_id)
            .order_by(SkillHalfLife.predicted_decay_date)
        )
    ).all()
    events = [
        V8DriftEvent(
            skill_id=skill.id,
            name=skill.skill_path,
            repo_id=repo.id,
            repo_name=repo.name,
            predicted_decay_date=half_life.predicted_decay_date,
            predicted_decay_days=float(half_life.predicted_decay_days or 0),
            decay_confidence=float(half_life.decay_confidence or 0),
            commits_30d=int(half_life.commits_30d or 0),
            file_churn_30d=int(half_life.file_churn_30d or 0),
            regen_queued=bool(half_life.regen_queued),
            computed_at=half_life.computed_at,
        )
        for half_life, skill, repo in rows
    ]
    return V8DriftResponse(events=events, total=len(events))


@router.get("/provenance", response_model=V8ProvenanceResponse)
async def provenance(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> V8ProvenanceResponse:
    await _require_v8(org_id, current_org_id, db)
    rows = (
        await db.execute(
            select(SkillVersion, Skill)
            .join(Skill, Skill.id == SkillVersion.skill_id)
            .join(Repo, Repo.id == Skill.repo_id)
            .where(Repo.org_id == org_id)
            .order_by(desc(SkillVersion.created_at))
            .limit(200)
        )
    ).all()
    versions = [
        V8ProvenanceVersion(
            skill_id=skill.id,
            version_id=version.id,
            version_number=int(version.version_number or 1),
            content_hash=version.content_hash,
            signature_status="verified" if version.content_hash else "unsigned",
            git_commit=None,
            generation_run_id=version.run_id,
            scoring_run_id=version.run_id,
            approver=None,
            created_at=version.created_at,
        )
        for version, skill in rows
    ]
    return V8ProvenanceResponse(versions=versions, transparency_log=[], total=len(versions))


@router.post("/skillql", response_model=None)
async def skillql(
    org_id: str,
    payload: org_routes.SkillQLRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any] | JSONResponse:
    await _require_v8(org_id, current_org_id, db)
    return await org_routes.run_skillql(org_id, payload, db, current_org_id)


@router.get("/skillql/suggestions")
async def skillql_suggestions(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, list[str]]:
    await _require_v8(org_id, current_org_id, db)
    return await org_routes.get_skillql_suggestions(org_id, current_org_id)


@router.get("/repos", response_model=V8ReposResponse)
async def repos(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> V8ReposResponse:
    await _require_v8(org_id, current_org_id, db)
    repo_rows = (
        await db.execute(
            select(
                Repo,
                func.count(Skill.id).label("skill_count"),
                func.count(SkillHalfLife.id).label("drift_count"),
            )
            .outerjoin(Skill, Skill.repo_id == Repo.id)
            .outerjoin(SkillHalfLife, SkillHalfLife.skill_id == Skill.id)
            .where(Repo.org_id == org_id, Repo.is_active.is_(True))
            .group_by(Repo.id)
            .order_by(Repo.full_name)
        )
    ).all()
    policies = _policy_names(await _org_policies(db, org_id))
    items = [
        V8RepoItem(
            id=repo.id,
            full_name=repo.full_name,
            name=repo.name,
            language=repo.language,
            sensitivity_tier=_sensitivity_tier(repo),
            indexing_status="indexed" if repo.last_analysed_at else "pending",
            generated_skill_count=int(skill_count or 0),
            drift_count=int(drift_count or 0),
            policy_bindings=policies,
            last_analysed_at=repo.last_analysed_at,
        )
        for repo, skill_count, drift_count in repo_rows
    ]
    return V8ReposResponse(repos=items, total=len(items))
