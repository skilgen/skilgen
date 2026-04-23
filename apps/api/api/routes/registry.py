from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import String, and_, cast, desc, func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from packages.db.database import get_db
from packages.db.models import RegistrySkill, Repo, Skill, SkillVersion
from packages.db.schemas import RegistryListResponse, RegistrySkillDetailResponse, RegistrySkillSummaryResponse


router = APIRouter(prefix="/registry", tags=["registry"])
logger = logging.getLogger(__name__)


class PublishRegistrySkillRequest(BaseModel):
    """Validated request body for publishing a generated skill."""

    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2000)
    is_public: bool = True
    tags: list[str] = Field(default_factory=list, max_length=10)


def _error(status_code: int, message: str, code: str) -> HTTPException:
    """Build a structured API error response."""
    return HTTPException(status_code=status_code, detail={"detail": message, "code": code})


def _normalized_tags(tags: list[str]) -> list[str]:
    """Normalize tags for registry storage and filtering."""
    normalized: list[str] = []
    for tag in tags:
        clean = tag.strip().lower()
        if clean and clean not in normalized:
            normalized.append(clean[:50])
    return normalized


async def _latest_content(db: AsyncSession, skill: Skill) -> tuple[str | None, str | None]:
    """Return the best available full skill content and content hash."""
    if skill.content:
        return skill.content, skill.content_hash
    version = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()
    if version is None:
        return None, skill.content_hash
    return version.content, version.content_hash


def _summary(listing: RegistrySkill, skill: Skill) -> RegistrySkillSummaryResponse:
    """Serialize a registry listing without raw skill content."""
    return RegistrySkillSummaryResponse(
        id=listing.id,
        org_id=listing.org_id,
        repo_id=listing.repo_id,
        skill_id=listing.skill_id,
        domain=listing.domain,
        name=listing.name,
        description=listing.description,
        is_public=listing.is_public,
        is_official=listing.is_official,
        import_count=int(listing.import_count or 0),
        tags=list(listing.tags or []),
        created_at=listing.created_at,
        score_total=int(skill.score_total or 0),
    )


async def _detail(db: AsyncSession, listing: RegistrySkill, skill: Skill, repo: Repo) -> RegistrySkillDetailResponse:
    """Serialize a registry listing with raw skill content."""
    content, content_hash = await _latest_content(db, skill)
    if not content:
        raise _error(422, "Published skill has no content", "SKILL_CONTENT_MISSING")
    summary = _summary(listing, skill).model_dump()
    return RegistrySkillDetailResponse(
        **summary,
        content=content,
        content_hash=content_hash,
        skill_path=skill.skill_path,
        repo_name=repo.name,
        repo_full_name=repo.full_name,
    )


def _registry_filters(search: str | None, tag: str | None, org_id: str | None) -> list[object]:
    """Build public registry filters from query params."""
    filters: list[object] = [RegistrySkill.is_public.is_(True)]
    if org_id:
        filters.append(RegistrySkill.org_id == org_id)
    if search:
        term = f"%{search.strip()}%"
        filters.append(
            or_(
                RegistrySkill.name.ilike(term),
                RegistrySkill.domain.ilike(term),
                RegistrySkill.description.ilike(term),
            )
        )
    if tag:
        filters.append(cast(RegistrySkill.tags, String).ilike(f'%"{tag.strip().lower()}"%'))
    return filters


async def _public_listing(db: AsyncSession, registry_id: str) -> tuple[RegistrySkill, Skill, Repo]:
    """Load a public registry listing and its backing skill/repo."""
    row = (
        await db.execute(
            select(RegistrySkill, Skill, Repo)
            .join(Skill, Skill.id == RegistrySkill.skill_id)
            .join(Repo, Repo.id == RegistrySkill.repo_id)
            .where(RegistrySkill.id == registry_id, RegistrySkill.is_public.is_(True))
        )
    ).first()
    if row is None:
        raise _error(404, "Registry skill not found", "REGISTRY_SKILL_NOT_FOUND")
    return row[0], row[1], row[2]


@router.get("", response_model=RegistryListResponse)
async def list_registry_skills(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=100),
    tag: str | None = Query(default=None, max_length=50),
    sort: str = Query(default="imports", pattern="^(imports|score|newest)$"),
    org_id: str | None = Query(default=None, max_length=255),
    db: AsyncSession = Depends(get_db),
) -> RegistryListResponse:
    """List public registry skills with pagination, search, tag filtering, and sorting."""
    try:
        filters = _registry_filters(search, tag, org_id)
        order_by = desc(RegistrySkill.import_count)
        if sort == "score":
            order_by = desc(Skill.score_total)
        elif sort == "newest":
            order_by = desc(RegistrySkill.created_at)
        total = (
            await db.execute(select(func.count(RegistrySkill.id)).where(and_(*filters)))
        ).scalar_one()
        rows = (
            await db.execute(
                select(RegistrySkill, Skill)
                .join(Skill, Skill.id == RegistrySkill.skill_id)
                .where(and_(*filters))
                .order_by(order_by, RegistrySkill.name)
                .offset(offset)
                .limit(limit)
            )
        ).all()
        return RegistryListResponse(
            skills=[_summary(row[0], row[1]) for row in rows],
            total=int(total or 0),
            limit=limit,
            offset=offset,
        )
    except SQLAlchemyError as exc:
        logger.exception("Registry list query failed")
        await db.rollback()
        raise _error(400, "Unable to list registry skills", "REGISTRY_LIST_FAILED") from exc


@router.post("/publish", response_model=RegistrySkillSummaryResponse)
async def publish_registry_skill(
    payload: PublishRegistrySkillRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> RegistrySkillSummaryResponse:
    """Publish a skill owned by the authenticated org to the Skillayer registry."""
    try:
        row = (
            await db.execute(
                select(Skill, Repo)
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Skill.id == payload.skill_id)
            )
        ).first()
        if row is None:
            raise _error(404, "Skill not found", "SKILL_NOT_FOUND")
        skill, repo = row[0], row[1]
        if repo.org_id != current_org_id:
            raise _error(403, "Skill does not belong to this org", "SKILL_FORBIDDEN")
        content, _content_hash = await _latest_content(db, skill)
        if not content:
            raise _error(422, "Skill has no publishable content", "SKILL_CONTENT_MISSING")
        existing = (
            await db.execute(
                select(RegistrySkill).where(
                    RegistrySkill.org_id == current_org_id,
                    RegistrySkill.skill_id == skill.id,
                )
            )
        ).scalar_one_or_none()
        listing = existing or RegistrySkill(org_id=current_org_id, repo_id=repo.id, skill_id=skill.id)
        listing.domain = skill.domain
        listing.name = payload.name.strip()
        listing.description = payload.description.strip()
        listing.is_public = payload.is_public
        listing.tags = _normalized_tags(payload.tags)
        if existing is None:
            db.add(listing)
        await db.flush()
        return _summary(listing, skill)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Registry publish failed for skill %s", payload.skill_id)
        await db.rollback()
        raise _error(400, "Unable to publish registry skill", "REGISTRY_PUBLISH_FAILED") from exc


@router.get("/{registry_id}", response_model=RegistrySkillDetailResponse)
async def get_registry_skill(
    registry_id: str,
    db: AsyncSession = Depends(get_db),
) -> RegistrySkillDetailResponse:
    """Read a public registry skill with full raw SKILL.md content."""
    try:
        listing, skill, repo = await _public_listing(db, registry_id)
        return await _detail(db, listing, skill, repo)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Registry detail query failed for %s", registry_id)
        await db.rollback()
        raise _error(400, "Unable to load registry skill", "REGISTRY_DETAIL_FAILED") from exc


@router.post("/{registry_id}/import", response_model=RegistrySkillDetailResponse)
async def import_registry_skill(
    registry_id: str,
    db: AsyncSession = Depends(get_db),
    _current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> RegistrySkillDetailResponse:
    """Atomically increment import count and return a public registry skill's content."""
    try:
        listing, skill, repo = await _public_listing(db, registry_id)
        await db.execute(
            update(RegistrySkill)
            .where(RegistrySkill.id == registry_id)
            .values(import_count=RegistrySkill.import_count + 1)
        )
        await db.flush()
        listing.import_count = int(listing.import_count or 0) + 1
        return await _detail(db, listing, skill, repo)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Registry import failed for %s", registry_id)
        await db.rollback()
        raise _error(400, "Unable to import registry skill", "REGISTRY_IMPORT_FAILED") from exc
