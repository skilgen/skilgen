from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes.orgs import _score_response
from packages.db.database import get_db
from packages.db.models import Repo, Skill, SkillUsageEvent, SkillVersion
from packages.db.schemas import SkillResponse, SkillVersionResponse, SkillVersionSummaryResponse


router = APIRouter(prefix="/skills", tags=["skills"])


class UsagePayload(BaseModel):
    """Validated payload for skill usage telemetry."""

    agent_runtime: str = Field(min_length=1, max_length=100)
    session_id: str = Field(min_length=1, max_length=255)


class UsageResponse(BaseModel):
    """Response returned after recording a skill usage event."""

    recorded: bool
    load_count_30d_incremented: bool


async def _build_skill_response(db: AsyncSession, skill: Skill, repo: Repo) -> SkillResponse:
    """Build the dashboard-facing skill payload with version and repo metadata."""
    version_count = (
        await db.execute(select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id))
    ).scalar_one()
    latest_version = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()
    return SkillResponse(
        id=skill.id,
        repo_id=repo.id,
        repo_name=repo.name,
        domain=skill.domain,
        skill_path=skill.skill_path,
        score=_score_response(skill),  # type: ignore[arg-type]
        content=skill.content,
        content_hash=skill.content_hash,
        is_stale=skill.is_stale,
        load_count_30d=skill.load_count_30d,
        last_loaded_at=skill.last_loaded_at,
        version_count=int(version_count or 0),
        latest_version_number=(latest_version.version_number if latest_version else None),
    )


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
) -> SkillResponse:
    # TODO: restore org-scoped auth before GA. Read-only skill browsing is public during dashboard bootstrap.
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    repo = await db.get(Repo, skill.repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    return await _build_skill_response(db, skill, repo)


@router.get("/{skill_id}/versions", response_model=list[SkillVersionSummaryResponse])
async def list_skill_versions(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[SkillVersionSummaryResponse]:
    # TODO: restore org-scoped auth before GA. Read-only skill browsing is public during dashboard bootstrap.
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    repo = await db.get(Repo, skill.repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    versions = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill_id)
            .order_by(desc(SkillVersion.version_number))
        )
    ).scalars().all()
    return [
        SkillVersionSummaryResponse(
            id=version.id,
            version_number=version.version_number,
            is_latest=version.is_latest,
            content_hash=version.content_hash,
            created_at=version.created_at,
            run_id=version.run_id,
        )
        for version in versions
    ]


@router.get("/{skill_id}/versions/{version_id}", response_model=SkillVersionResponse)
async def get_skill_version(
    skill_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
) -> SkillVersionResponse:
    # TODO: restore org-scoped auth before GA. Read-only skill browsing is public during dashboard bootstrap.
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    repo = await db.get(Repo, skill.repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    version = await db.get(SkillVersion, version_id)
    if version is None or version.skill_id != skill_id:
        raise HTTPException(status_code=404, detail="Skill version not found")
    return SkillVersionResponse(
        id=version.id,
        version_number=version.version_number,
        content=version.content,
        content_hash=version.content_hash,
        created_at=version.created_at,
        is_latest=version.is_latest,
    )


@router.post("/{skill_id}/usage")
async def record_skill_usage(
    skill_id: str,
    payload: UsagePayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> UsageResponse:
    """Atomically increment usage counters and persist the raw load event."""
    now = datetime.now(UTC).replace(tzinfo=None)
    try:
        scoped_skill = (
            await db.execute(
                select(Skill.id, Skill.repo_id)
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Skill.id == skill_id, Repo.org_id == current_org_id)
                .limit(1)
            )
        ).first()
        if scoped_skill is None:
            skill_exists = await db.get(Skill, skill_id)
            if skill_exists is None:
                raise HTTPException(status_code=404, detail="Skill not found")
            raise HTTPException(status_code=403, detail="Forbidden")

        await db.execute(
            update(Skill)
            .where(Skill.id == skill_id)
            .values(load_count_30d=Skill.load_count_30d + 1, last_loaded_at=now)
        )
        db.add(
            SkillUsageEvent(
                org_id=current_org_id,
                repo_id=str(scoped_skill.repo_id),
                skill_id=skill_id,
                agent_runtime=payload.agent_runtime,
                session_id=payload.session_id,
                loaded_at=now,
            )
        )
        await db.flush()
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to record skill usage") from exc
    return UsageResponse(recorded=True, load_count_30d_incremented=True)
