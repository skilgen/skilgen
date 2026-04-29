from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import String, and_, cast, desc, func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes.repos import _compute_skill_score
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
from apps.api.api.services.github_pr import create_skill_pr
from apps.api.api.services.half_life import check_and_queue_regenerations, compute_half_life
from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError, call_llm
from apps.api.api.services.skill_generator import chat_create_skill
from apps.api.api.services.dependency_analyzer import compute_cross_repo_dependencies, compute_repo_dependencies
from packages.db.database import AsyncSessionLocal, get_db
from packages.db.models import (
    MarketplaceInstall,
    DependencyGraphCache,
    Org,
    RegistrySkill,
    Repo,
    Skill,
    SkillDependency,
    SkillHalfLife,
    SkillRegistryEntry,
    SkillVersion,
)
from packages.db.schemas import RegistryListResponse, RegistrySkillDetailResponse, RegistrySkillSummaryResponse


router = APIRouter(prefix="/registry", tags=["registry"])
logger = logging.getLogger(__name__)
RUNTIMES = ["claude-code", "codex", "cursor", "copilot", "gemini-cli"]


class PublishRegistrySkillRequest(BaseModel):
    skill_id: str = Field(min_length=1)
    name: str | None = Field(default=None, max_length=255)
    version: str = "1.0.0"
    visibility: Literal["private", "org", "public"] = "private"
    tags: list[str] = Field(default_factory=list, max_length=20)
    description: str = Field(min_length=1, max_length=2000)
    compatible_runtimes: list[str] = Field(default_factory=lambda: list(RUNTIMES), max_length=10)
    is_public: bool | None = None


class ImportSkillFileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    domain: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=10, max_length=200_000)
    source_type: str = "custom"
    source: str | None = None
    repo_id: str | None = None
    is_public: bool = False
    tags: list[str] = Field(default_factory=list, max_length=20)


class InstallPayload(BaseModel):
    repo_id: str | None = None
    org_id: str | None = None


class DeprecatePayload(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    successor_entry_id: str | None = None


class DependencyScanPayload(BaseModel):
    repo_id: str


class SkillRegistryEntryResponse(BaseModel):
    id: str
    name: str
    domain: str
    version: str
    visibility: str
    tags: list[str]
    description: str
    publisher_login: str
    compatible_runtimes: list[str]
    install_count: int
    score_total: float
    score_groundedness: float
    score_coverage: float
    score_freshness: float
    score_structure: float
    is_verified: bool
    is_deprecated: bool
    deprecation_message: str | None
    successor_entry_id: str | None
    content_preview: str | None
    predicted_decay_date: datetime | None
    predicted_decay_days: float | None
    decay_confidence: float | None
    regen_queued: bool
    created_at: datetime
    updated_at: datetime


class RegistryEntriesResponse(BaseModel):
    entries: list[SkillRegistryEntryResponse]
    total: int
    page: int
    page_size: int


class DependencyGraphResponse(BaseModel):
    nodes: list[dict[str, object]]
    edges: list[dict[str, object]]
    stale_upstream_count: int


class HalfLifeSummaryResponse(BaseModel):
    critical: list[dict[str, object]]
    warning: list[dict[str, object]]
    healthy: list[dict[str, object]]
    total_skills: int
    regen_queued_count: int


class ImportRegistryResponse(BaseModel):
    entry: SkillRegistryEntryResponse
    score: dict[str, int]
    improvement_suggestions: list[str]


class CompatibilityMatrixResponse(BaseModel):
    skills: list[dict[str, str]]
    runtimes: list[str]
    matrix: dict[str, dict[str, str]]


class SkillMapResponse(BaseModel):
    nodes: list[dict[str, object]]
    edges: list[dict[str, object]]
    domains: list[dict[str, object]]
    repo_count: int
    skill_count: int


class SkillTreeResponse(BaseModel):
    name: str
    type: str
    children: list[dict[str, object]]


class DependencyGraphCacheResponse(BaseModel):
    nodes: list[dict[str, object]]
    edges: list[dict[str, object]]
    opportunities: list[dict[str, object]] = []
    computed_at: datetime | None = None


class ChatCreateMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatCreatePayload(BaseModel):
    messages: list[ChatCreateMessage] = Field(min_length=1, max_length=30)
    repo_id: str | None = None


class ChatCreateResponse(BaseModel):
    assistant_reply: str
    ready_to_create: bool
    draft_skill: dict[str, object] | None = None


class ChatCreatePushPayload(BaseModel):
    repo_id: str = Field(min_length=1)
    domain: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=10, max_length=200_000)
    skill_path: str | None = Field(default=None, max_length=512)


class ChatCreatePushResponse(BaseModel):
    pushed: bool
    pr_url: str
    pr_number: int
    branch: str


class RegistrySearchPayload(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=25)
    ai: bool = True


class RegistrySearchResponse(BaseModel):
    query: str
    answer: str | None
    results: list[dict[str, object]]


def _error(status_code: int, message: str, code: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"detail": message, "code": code})


def _normalized_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    for tag in tags:
        clean = tag.strip().lower()
        if clean and clean not in normalized:
            normalized.append(clean[:50])
    return normalized


def _entry_response(entry: SkillRegistryEntry, half_life: SkillHalfLife | None = None, *, preview_chars: int | None = 500) -> SkillRegistryEntryResponse:
    return SkillRegistryEntryResponse(
        id=entry.id,
        name=entry.name,
        domain=entry.domain,
        version=entry.version,
        visibility=entry.visibility,
        tags=list(entry.tags or []),
        description=entry.description,
        publisher_login=entry.publisher_login,
        compatible_runtimes=list(entry.compatible_runtimes or []),
        install_count=int(entry.install_count or 0),
        score_total=float(entry.score_total or 0),
        score_groundedness=float(entry.score_groundedness or 0),
        score_coverage=float(entry.score_coverage or 0),
        score_freshness=float(entry.score_freshness or 0),
        score_structure=float(entry.score_structure or 0),
        is_verified=bool(entry.is_verified),
        is_deprecated=bool(entry.is_deprecated),
        deprecation_message=entry.deprecation_message,
        successor_entry_id=entry.successor_entry_id,
        content_preview=(entry.content[:preview_chars] if preview_chars else None),
        predicted_decay_date=half_life.predicted_decay_date if half_life else None,
        predicted_decay_days=half_life.predicted_decay_days if half_life else None,
        decay_confidence=half_life.decay_confidence if half_life else None,
        regen_queued=bool(half_life.regen_queued) if half_life else False,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


async def _latest_content(db: AsyncSession, skill: Skill) -> tuple[str | None, str | None]:
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
    return (version.content, version.content_hash) if version else (None, skill.content_hash)


async def _compute_half_life_background(skill_id: str) -> None:
    async with AsyncSessionLocal() as db:
        try:
            await compute_half_life(skill_id, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Half-life background compute failed for %s", skill_id)


async def _refresh_half_lives_background(org_id: str) -> None:
    async with AsyncSessionLocal() as db:
        try:
            skills = (
                await db.execute(select(Skill).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id))
            ).scalars().all()
            for skill in skills:
                await compute_half_life(skill.id, db)
            await check_and_queue_regenerations(org_id, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Half-life refresh failed for org %s", org_id)


async def _scan_dependencies_background(org_id: str, repo_id: str) -> None:
    async with AsyncSessionLocal() as db:
        try:
            source_skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
            entries = (
                await db.execute(
                    select(SkillRegistryEntry).where(
                        SkillRegistryEntry.publisher_org_id == org_id,
                        SkillRegistryEntry.skill_id.is_not(None),
                    )
                )
            ).scalars().all()
            for skill in source_skills:
                content = (skill.content or "").lower()
                for entry in entries:
                    if entry.skill_id == skill.id:
                        continue
                    if entry.domain.lower() in content or entry.name.lower() in content:
                        existing = (
                            await db.execute(
                                select(SkillDependency).where(
                                    SkillDependency.source_skill_id == skill.id,
                                    SkillDependency.target_registry_entry_id == entry.id,
                                )
                            )
                        ).scalar_one_or_none()
                        if existing is None:
                            db.add(SkillDependency(source_skill_id=skill.id, target_registry_entry_id=entry.id, org_id=org_id))
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Dependency scan failed for repo %s", repo_id)


async def _enterprise_skill_examples(db: AsyncSession, org_id: str, limit: int = 5) -> list[dict[str, object]]:
    rows = (
        await db.execute(
            select(Skill, Repo)
            .join(Repo, Repo.id == Skill.repo_id)
            .where(Repo.org_id == org_id, Skill.is_enterprise.is_(True))
            .order_by(desc(Skill.created_at))
            .limit(limit)
        )
    ).all()
    return [
        {
            "id": skill.id,
            "domain": skill.domain,
            "repo_name": repo.name,
            "content": skill.content or "",
            "skill_path": skill.skill_path,
        }
        for skill, repo in rows
    ]


async def _repo_context(db: AsyncSession, org_id: str, repo_id: str | None) -> tuple[Repo | None, dict[str, object] | None]:
    if not repo_id:
        return None, None
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != org_id:
        raise _error(404, "Repo not found", "REPO_NOT_FOUND")
    skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(desc(Skill.created_at)).limit(20))).scalars().all()
    file_tree_sample = "\n".join(skill.skill_path for skill in skills if skill.skill_path)
    return repo, {"repo_id": repo.id, "repo_name": repo.name, "full_name": repo.full_name, "file_tree_sample": file_tree_sample}


def _skill_path_for_domain(domain: str, provided: str | None = None) -> str:
    if provided:
        return provided.strip().lstrip("/")
    slug = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-") or "generated-skill"
    return f"skills/{slug}/SKILL.md"


@router.post("/orgs/{org_id}/publish", response_model=SkillRegistryEntryResponse)
async def publish_org_skill(
    org_id: str,
    payload: PublishRegistrySkillRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> SkillRegistryEntryResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    row = (
        await db.execute(select(Skill, Repo, Org).join(Repo, Repo.id == Skill.repo_id).join(Org, Org.id == Repo.org_id).where(Skill.id == payload.skill_id))
    ).first()
    if row is None:
        raise _error(404, "Skill not found", "SKILL_NOT_FOUND")
    skill, repo, org = row
    if repo.org_id != org_id:
        raise _error(403, "Skill does not belong to this org", "SKILL_FORBIDDEN")
    content, content_hash = await _latest_content(db, skill)
    if not content:
        raise _error(422, "Skill has no publishable content", "SKILL_CONTENT_MISSING")
    scores = _compute_skill_score(content)
    visibility = "public" if payload.is_public is True else payload.visibility
    entry = SkillRegistryEntry(
        org_id=None if visibility == "public" else org_id,
        skill_id=skill.id,
        name=payload.name or f"{skill.domain}/SKILL.md",
        domain=skill.domain,
        version=payload.version,
        publisher_org_id=org_id,
        publisher_login=org.login,
        visibility=visibility,
        tags=_normalized_tags(payload.tags),
        description=payload.description,
        content_hash=content_hash or hashlib.sha256(content.encode()).hexdigest(),
        content=content,
        compatible_runtimes=[runtime for runtime in payload.compatible_runtimes if runtime in RUNTIMES] or list(RUNTIMES),
        score_groundedness=float(skill.score_groundedness or scores["groundedness"]),
        score_coverage=float(skill.score_coverage or scores["coverage"]),
        score_freshness=float(skill.score_freshness or scores["freshness"]),
        score_structure=float(skill.score_structure or scores["structure"]),
        score_total=float(skill.score_total or scores["total"]),
        is_verified=False,
    )
    db.add(entry)
    await db.flush()
    await audit.emit(db, org_id, "skill.published", "published", f"Published {entry.name} v{entry.version}", actor_login=get_actor_login(request), repo_id=repo.id, repo_name=repo.name, skill_id=skill.id, skill_domain=skill.domain, resource_type="skill", resource_id=skill.id)
    background_tasks.add_task(_compute_half_life_background, skill.id)
    half_life = (await db.execute(select(SkillHalfLife).where(SkillHalfLife.skill_id == skill.id))).scalar_one_or_none()
    return _entry_response(entry, half_life)


@router.get("/orgs/{org_id}/entries", response_model=RegistryEntriesResponse)
async def list_org_entries(
    org_id: str,
    visibility: str | None = None,
    tag: str | None = None,
    min_score: float | None = None,
    search: str | None = None,
    runtime: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RegistryEntriesResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    filters = [or_(SkillRegistryEntry.org_id == org_id, SkillRegistryEntry.publisher_org_id == org_id)]
    if visibility:
        filters.append(SkillRegistryEntry.visibility == visibility)
    if min_score is not None:
        filters.append(SkillRegistryEntry.score_total >= min_score)
    if tag:
        filters.append(cast(SkillRegistryEntry.tags, String).ilike(f'%"{tag.strip().lower()}"%'))
    if runtime:
        filters.append(cast(SkillRegistryEntry.compatible_runtimes, String).ilike(f'%"{runtime.strip()}"%'))
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(SkillRegistryEntry.name.ilike(term), SkillRegistryEntry.domain.ilike(term), SkillRegistryEntry.description.ilike(term)))
    total = int((await db.execute(select(func.count(SkillRegistryEntry.id)).where(and_(*filters)))).scalar() or 0)
    rows = (
        await db.execute(
            select(SkillRegistryEntry, SkillHalfLife)
            .outerjoin(SkillHalfLife, SkillHalfLife.skill_id == SkillRegistryEntry.skill_id)
            .where(and_(*filters))
            .order_by(desc(SkillRegistryEntry.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).all()
    return RegistryEntriesResponse(entries=[_entry_response(row[0], row[1]) for row in rows], total=total, page=page, page_size=page_size)


@router.get("/orgs/{org_id}/skill-map", response_model=SkillMapResponse)
async def org_skill_map(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SkillMapResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    rows = (
        await db.execute(
            select(Skill, Repo)
            .join(Repo, Repo.id == Skill.repo_id)
            .where(Repo.org_id == org_id)
            .order_by(Repo.name, Skill.domain)
        )
    ).all()
    nodes: list[dict[str, object]] = []
    domain_counts: dict[str, int] = {}
    repo_ids: set[str] = set()
    for skill, repo in rows:
        repo_ids.add(repo.id)
        domain = str(skill.domain or "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        nodes.append(
            {
                "id": skill.id,
                "type": "skill",
                "label": domain,
                "repo_id": repo.id,
                "repo_name": repo.name,
                "skill_path": skill.skill_path,
                "score_total": int(skill.score_total or 0),
                "is_enterprise": bool(skill.is_enterprise),
                "is_stale": bool(skill.is_stale),
                "load_count_30d": int(skill.load_count_30d or 0),
            }
        )
    deps = (
        await db.execute(
            select(SkillDependency, SkillRegistryEntry)
            .join(SkillRegistryEntry, SkillRegistryEntry.id == SkillDependency.target_registry_entry_id)
            .where(SkillDependency.org_id == org_id)
        )
    ).all()
    edges = [
        {
            "source": dep.source_skill_id,
            "target": dep.target_registry_entry_id,
            "target_name": entry.name,
            "relationship": "depends_on",
        }
        for dep, entry in deps
    ]
    return SkillMapResponse(
        nodes=nodes,
        edges=edges,
        domains=[{"domain": domain, "skill_count": count} for domain, count in sorted(domain_counts.items(), key=lambda item: item[1], reverse=True)],
        repo_count=len(repo_ids),
        skill_count=len(nodes),
    )


def _tree_status(skill: Skill) -> str:
    if int(skill.load_count_30d or 0) == 0:
        return "never_loaded"
    if bool(skill.is_stale) or int(skill.score_freshness or 0) < 10:
        return "stale"
    if int(skill.score_total or 0) < 50:
        return "low_score"
    return "healthy"


@router.get("/orgs/{org_id}/skill-tree", response_model=SkillTreeResponse)
async def org_skill_tree(org_id: str, repo_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SkillTreeResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != org_id:
        raise _error(404, "Repo not found", "REPO_NOT_FOUND")
    skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(Skill.domain, Skill.skill_path))).scalars().all()
    grouped: dict[str, list[Skill]] = {}
    for skill in skills:
        grouped.setdefault(skill.skill_category or skill.domain or "unknown", []).append(skill)
    children: list[dict[str, object]] = []
    for domain, domain_skills in sorted(grouped.items()):
        avg = round(sum(int(skill.score_total or 0) for skill in domain_skills) / max(1, len(domain_skills)))
        children.append(
            {
                "name": domain,
                "type": "domain",
                "skill_count": len(domain_skills),
                "avg_score": avg,
                "children": [
                    {
                        "name": skill.domain,
                        "type": "skill",
                        "skill_id": skill.id,
                        "score": int(skill.score_total or 0),
                        "path": skill.skill_path,
                        "load_count": int(skill.load_count_30d or 0),
                        "last_updated": skill.created_at.date().isoformat() if skill.created_at else None,
                        "status": _tree_status(skill),
                        "content_preview": (skill.content or "")[:800],
                    }
                    for skill in domain_skills
                ],
            }
        )
    return SkillTreeResponse(name=repo.name, type="repo", children=children)


@router.post("/orgs/{org_id}/chat-create", response_model=ChatCreateResponse)
async def registry_chat_create(org_id: str, payload: ChatCreatePayload, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> ChatCreateResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    org = await db.get(Org, org_id)
    if org is None:
        raise _error(404, "Org not found", "ORG_NOT_FOUND")
    _repo, repo_context = await _repo_context(db, org_id, payload.repo_id)
    enterprise_skills = await _enterprise_skill_examples(db, org_id)
    try:
        result = await chat_create_skill(
            dict(org.settings or {}),
            [message.model_dump() for message in payload.messages],
            repo_context,
            enterprise_skills,
        )
    except LLMNotConfiguredError as exc:
        raise HTTPException(status_code=402, detail={"error": "llm_not_configured", "detail": str(exc), "settings_url": "/dashboard/settings"}) from exc
    except (LLMCallError, ValueError) as exc:
        raise _error(502, str(exc), "LLM_CALL_FAILED") from exc
    return ChatCreateResponse(**result)


@router.post("/orgs/{org_id}/chat-create/push", response_model=ChatCreatePushResponse)
async def registry_chat_create_push(
    org_id: str,
    payload: ChatCreatePushPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ChatCreatePushResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    repo = await db.get(Repo, payload.repo_id)
    if repo is None or repo.org_id != org_id:
        raise _error(404, "Repo not found", "REPO_NOT_FOUND")
    skill_path = _skill_path_for_domain(payload.domain, payload.skill_path)
    slug = re.sub(r"[^a-z0-9]+", "-", payload.domain.lower()).strip("-") or "skill"
    branch_name = f"skillayer/ai-skill-{slug}"
    try:
        pr = await create_skill_pr(
            repo,
            skill_path,
            payload.content,
            branch_name,
            f"Add Skillayer skill for {payload.domain}",
            f"Adds an AI-generated Skillayer skill at `{skill_path}`.\n\nGenerated from the registry Create skill with AI flow.",
        )
    except ValueError as exc:
        raise _error(400, str(exc), "GITHUB_PR_FAILED") from exc
    except Exception as exc:
        raise _error(502, "Could not create GitHub PR", "GITHUB_PR_FAILED") from exc
    return ChatCreatePushResponse(pushed=True, pr_url=str(pr["pr_url"]), pr_number=int(pr["pr_number"]), branch=str(pr["branch"]))


@router.post("/orgs/{org_id}/search", response_model=RegistrySearchResponse)
async def registry_search(org_id: str, payload: RegistrySearchPayload, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> RegistrySearchResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    term = f"%{payload.query.strip()}%"
    rows = (
        await db.execute(
            select(SkillRegistryEntry)
            .where(
                or_(SkillRegistryEntry.org_id == org_id, SkillRegistryEntry.publisher_org_id == org_id),
                or_(
                    SkillRegistryEntry.name.ilike(term),
                    SkillRegistryEntry.domain.ilike(term),
                    SkillRegistryEntry.description.ilike(term),
                    SkillRegistryEntry.content.ilike(term),
                ),
            )
            .order_by(desc(SkillRegistryEntry.score_total), desc(SkillRegistryEntry.updated_at))
            .limit(payload.limit)
        )
    ).scalars().all()
    results = [
        {
            "id": entry.id,
            "name": entry.name,
            "domain": entry.domain,
            "description": entry.description,
            "score_total": float(entry.score_total or 0),
            "visibility": entry.visibility,
            "snippet": entry.content[:500],
        }
        for entry in rows
    ]
    answer: str | None = None
    if payload.ai and results:
        org = await db.get(Org, org_id)
        try:
            answer = await call_llm(
                dict(org.settings or {}) if org else {},
                "You summarize Skillayer registry search results. Be concise and mention the most relevant skill names.",
                f"Query: {payload.query}\nResults JSON:\n{results}",
                max_tokens=300,
            )
        except (LLMNotConfiguredError, LLMCallError):
            answer = None
    return RegistrySearchResponse(query=payload.query, answer=answer, results=results)


@router.get("/orgs/{org_id}/entries/{entry_id}", response_model=SkillRegistryEntryResponse)
async def get_org_entry(org_id: str, entry_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SkillRegistryEntryResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    row = (
        await db.execute(
            select(SkillRegistryEntry, SkillHalfLife)
            .outerjoin(SkillHalfLife, SkillHalfLife.skill_id == SkillRegistryEntry.skill_id)
            .where(SkillRegistryEntry.id == entry_id, or_(SkillRegistryEntry.org_id == org_id, SkillRegistryEntry.publisher_org_id == org_id))
        )
    ).first()
    if row is None:
        raise _error(404, "Registry entry not found", "ENTRY_NOT_FOUND")
    return _entry_response(row[0], row[1], preview_chars=800)


@router.post("/orgs/{org_id}/entries/{entry_id}/install")
async def install_org_entry(
    org_id: str,
    entry_id: str,
    payload: InstallPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    entry = await db.get(SkillRegistryEntry, entry_id)
    if entry is None or (entry.visibility != "public" and entry.publisher_org_id != org_id and entry.org_id != org_id):
        raise _error(404, "Registry entry not found", "ENTRY_NOT_FOUND")
    install = MarketplaceInstall(registry_entry_id=entry.id, org_id=org_id, repo_id=payload.repo_id, installed_by=get_actor_login(request) or "unknown")
    db.add(install)
    entry.install_count = int(entry.install_count or 0) + 1
    await audit.emit(db, org_id, "skill.installed", "created", f"Installed {entry.name}", actor_login=get_actor_login(request), resource_type="skill", resource_id=entry.id)
    await db.flush()
    return {"installed": True, "install_id": install.id}


@router.patch("/orgs/{org_id}/entries/{entry_id}/deprecate", response_model=SkillRegistryEntryResponse)
async def deprecate_org_entry(org_id: str, entry_id: str, payload: DeprecatePayload, request: Request, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SkillRegistryEntryResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    entry = await db.get(SkillRegistryEntry, entry_id)
    if entry is None or entry.publisher_org_id != org_id:
        raise _error(404, "Registry entry not found", "ENTRY_NOT_FOUND")
    entry.is_deprecated = True
    entry.deprecation_message = payload.message
    entry.successor_entry_id = payload.successor_entry_id
    await audit.emit(db, org_id, "skill.deprecated", "updated", f"Deprecated {entry.name}", actor_login=get_actor_login(request), resource_type="skill", resource_id=entry.id)
    return _entry_response(entry)


@router.get("/orgs/{org_id}/dependency-graph", response_model=DependencyGraphResponse)
async def dependency_graph(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> DependencyGraphResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    deps = (
        await db.execute(
            select(SkillDependency, Skill, Repo, SkillRegistryEntry)
            .join(Skill, Skill.id == SkillDependency.source_skill_id)
            .join(Repo, Repo.id == Skill.repo_id)
            .join(SkillRegistryEntry, SkillRegistryEntry.id == SkillDependency.target_registry_entry_id)
            .where(SkillDependency.org_id == org_id)
        )
    ).all()
    nodes_by_id: dict[str, dict[str, object]] = {}
    edges: list[dict[str, object]] = []
    stale = 0
    for dep, skill, repo, target in deps:
        nodes_by_id[skill.id] = {"skill_id": skill.id, "name": skill.skill_path, "domain": skill.domain, "repo_id": repo.id, "repo_name": repo.name, "score_total": int(skill.score_total or 0)}
        edges.append({"source_skill_id": dep.source_skill_id, "target_entry_id": dep.target_registry_entry_id, "target_name": target.name})
        if float(target.score_freshness or 0) < 20:
            stale += 1
    return DependencyGraphResponse(nodes=list(nodes_by_id.values()), edges=edges, stale_upstream_count=stale)


@router.post("/orgs/{org_id}/dependency-scan")
async def dependency_scan(org_id: str, payload: DependencyScanPayload, background_tasks: BackgroundTasks, current_org_id: str = Depends(get_current_org_id)) -> dict[str, bool]:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    background_tasks.add_task(_scan_dependencies_background, org_id, payload.repo_id)
    return {"queued": True}


@router.get("/marketplace", response_model=RegistryEntriesResponse)
async def list_marketplace(tag: str | None = None, min_score: float | None = None, search: str | None = None, runtime: str | None = None, page: int = Query(default=1, ge=1), page_size: int = Query(default=24, ge=1, le=100), db: AsyncSession = Depends(get_db)) -> RegistryEntriesResponse:
    filters = [SkillRegistryEntry.visibility == "public"]
    if min_score is not None:
        filters.append(SkillRegistryEntry.score_total >= min_score)
    if tag:
        filters.append(cast(SkillRegistryEntry.tags, String).ilike(f'%"{tag.strip().lower()}"%'))
    if runtime:
        filters.append(cast(SkillRegistryEntry.compatible_runtimes, String).ilike(f'%"{runtime.strip()}"%'))
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(SkillRegistryEntry.name.ilike(term), SkillRegistryEntry.domain.ilike(term), SkillRegistryEntry.description.ilike(term)))
    total = int((await db.execute(select(func.count(SkillRegistryEntry.id)).where(and_(*filters)))).scalar() or 0)
    rows = (
        await db.execute(select(SkillRegistryEntry).where(and_(*filters)).order_by(desc(SkillRegistryEntry.install_count), desc(SkillRegistryEntry.score_total)).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return RegistryEntriesResponse(entries=[_entry_response(entry, preview_chars=500) for entry in rows], total=total, page=page, page_size=page_size)


@router.get("/marketplace/{entry_id}", response_model=SkillRegistryEntryResponse)
async def marketplace_detail(entry_id: str, db: AsyncSession = Depends(get_db)) -> SkillRegistryEntryResponse:
    entry = await db.get(SkillRegistryEntry, entry_id)
    if entry is None or entry.visibility != "public":
        raise _error(404, "Marketplace entry not found", "ENTRY_NOT_FOUND")
    return _entry_response(entry, preview_chars=800)


@router.post("/marketplace/{entry_id}/install")
async def install_marketplace_entry(entry_id: str, payload: InstallPayload, request: Request, db: AsyncSession = Depends(get_db), _current_org_id: str = Depends(get_current_org_id)) -> dict[str, object]:
    if not payload.org_id:
        raise _error(400, "org_id is required", "ORG_REQUIRED")
    return await install_org_entry(payload.org_id, entry_id, payload, request, db, payload.org_id)


@router.get("/orgs/{org_id}/half-life", response_model=HalfLifeSummaryResponse)
async def org_half_life(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> HalfLifeSummaryResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    rows = (
        await db.execute(select(SkillHalfLife, Skill, Repo).join(Skill, Skill.id == SkillHalfLife.skill_id).join(Repo, Repo.id == SkillHalfLife.repo_id).where(SkillHalfLife.org_id == org_id).order_by(SkillHalfLife.predicted_decay_date))
    ).all()
    buckets = {"critical": [], "warning": [], "healthy": []}
    for half_life, skill, repo in rows:
        item = {"skill_id": skill.id, "name": skill.skill_path, "domain": skill.domain, "repo_id": repo.id, "repo_name": repo.name, "freshness": int(skill.score_freshness or 0), "commits_30d": int(half_life.commits_30d or 0), "predicted_decay_date": half_life.predicted_decay_date, "predicted_decay_days": float(half_life.predicted_decay_days or 0), "decay_confidence": float(half_life.decay_confidence or 0), "regen_queued": bool(half_life.regen_queued)}
        days = float(half_life.predicted_decay_days or 0)
        buckets["critical" if days < 3 else "warning" if days <= 7 else "healthy"].append(item)
    return HalfLifeSummaryResponse(critical=buckets["critical"], warning=buckets["warning"], healthy=buckets["healthy"], total_skills=len(rows), regen_queued_count=sum(1 for row in rows if row[0].regen_queued))


@router.post("/orgs/{org_id}/half-life/refresh")
async def refresh_org_half_life(org_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict[str, object]:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    count = int((await db.execute(select(func.count(Skill.id)).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id))).scalar() or 0)
    background_tasks.add_task(_refresh_half_lives_background, org_id)
    return {"queued": True, "skill_count": count}


@router.get("/skills/{skill_id}/half-life")
async def skill_half_life(skill_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    row = (await db.execute(select(SkillHalfLife).where(SkillHalfLife.skill_id == skill_id))).scalar_one_or_none()
    if row is None:
        row = await compute_half_life(skill_id, db)
    return {"skill_id": skill_id, "predicted_decay_date": row.predicted_decay_date, "predicted_decay_days": row.predicted_decay_days, "decay_confidence": row.decay_confidence, "prediction_error_days": row.prediction_error_days, "history": [{"computed_at": row.computed_at, "predicted_decay_days": row.predicted_decay_days, "actual_decay_occurred": row.last_actual_decay_date is not None}]}


@router.get("/orgs/{org_id}/compatibility-matrix", response_model=CompatibilityMatrixResponse)
async def compatibility_matrix(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> CompatibilityMatrixResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    skills = (await db.execute(select(Skill).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id))).scalars().all()
    entries = (await db.execute(select(SkillRegistryEntry).where(SkillRegistryEntry.publisher_org_id == org_id, SkillRegistryEntry.skill_id.is_not(None)).order_by(desc(SkillRegistryEntry.created_at)))).scalars().all()
    latest_by_skill: dict[str, SkillRegistryEntry] = {}
    for entry in entries:
        if entry.skill_id:
            latest_by_skill.setdefault(entry.skill_id, entry)
    matrix: dict[str, dict[str, str]] = {}
    for skill in skills:
        entry = latest_by_skill.get(skill.id)
        compatible = set(entry.compatible_runtimes or []) if entry else set()
        matrix[skill.id] = {runtime: ("compatible" if runtime in compatible else "untested") for runtime in RUNTIMES}
    return CompatibilityMatrixResponse(skills=[{"skill_id": skill.id, "name": skill.skill_path, "domain": skill.domain} for skill in skills], runtimes=RUNTIMES, matrix=matrix)


@router.post("/orgs/{org_id}/import", response_model=ImportRegistryResponse)
async def import_org_skill(org_id: str, payload: ImportSkillFileRequest, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> ImportRegistryResponse:
    if org_id != current_org_id:
        raise _error(403, "Forbidden", "ORG_FORBIDDEN")
    if not payload.repo_id:
        raise _error(400, "repo_id is required", "REPO_REQUIRED")
    repo = await db.get(Repo, payload.repo_id)
    if repo is None or repo.org_id != org_id:
        raise _error(404, "Repo not found", "REPO_NOT_FOUND")
    domain = payload.domain or re.sub(r"[^a-z0-9]+", "-", payload.name.lower()).strip("-") or "imported-skill"
    score = _compute_skill_score(payload.content)
    entry = SkillRegistryEntry(
        org_id=org_id,
        skill_id=None,
        name=payload.name,
        domain=domain,
        version="1.0.0",
        publisher_org_id=org_id,
        publisher_login=org.name,
        visibility="private",
        tags=_normalized_tags(payload.tags),
        description=f"Imported from {payload.source or payload.source_type}",
        content_hash=hashlib.sha256(payload.content.encode()).hexdigest(),
        content=payload.content,
        compatible_runtimes=list(RUNTIMES),
        score_total=score["total"],
        score_groundedness=score["groundedness"],
        score_coverage=score["coverage"],
        score_freshness=score["freshness"],
        score_structure=score["structure"],
    )
    db.add(entry)
    await db.flush()
    suggestions = []
    if score["groundedness"] <= 12:
        suggestions.append("Add concrete file paths and code examples.")
    if score["coverage"] <= 12:
        suggestions.append("Expand testing, edge cases, and related files.")
    if score["freshness"] <= 12:
        suggestions.append("Add version constraints or a last-verified note.")
    if score["structure"] <= 12:
        suggestions.append("Add clear markdown headings and sections.")
    return ImportRegistryResponse(entry=_entry_response(entry), score=score, improvement_suggestions=suggestions)


# Legacy public registry endpoints retained for CLI/backwards compatibility.
def _legacy_summary(listing: RegistrySkill, skill: Skill) -> RegistrySkillSummaryResponse:
    return RegistrySkillSummaryResponse(id=listing.id, org_id=listing.org_id, repo_id=listing.repo_id, skill_id=listing.skill_id, domain=listing.domain, name=listing.name, description=listing.description, is_public=listing.is_public, is_official=listing.is_official, import_count=int(listing.import_count or 0), tags=list(listing.tags or []), created_at=listing.created_at, score_total=int(skill.score_total or 0))


@router.get("", response_model=RegistryListResponse)
async def list_registry_skills(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), search: str | None = None, tag: str | None = None, sort: str = Query(default="imports", pattern="^(imports|score|newest)$"), org_id: str | None = None, db: AsyncSession = Depends(get_db)) -> RegistryListResponse:
    filters = [RegistrySkill.is_public.is_(True)]
    if org_id:
        filters.append(RegistrySkill.org_id == org_id)
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(RegistrySkill.name.ilike(term), RegistrySkill.domain.ilike(term), RegistrySkill.description.ilike(term)))
    if tag:
        filters.append(cast(RegistrySkill.tags, String).ilike(f'%"{tag.strip().lower()}"%'))
    order_by = desc(RegistrySkill.import_count) if sort == "imports" else desc(Skill.score_total) if sort == "score" else desc(RegistrySkill.created_at)
    total = int((await db.execute(select(func.count(RegistrySkill.id)).where(and_(*filters)))).scalar_one() or 0)
    rows = (await db.execute(select(RegistrySkill, Skill).join(Skill, Skill.id == RegistrySkill.skill_id).where(and_(*filters)).order_by(order_by, RegistrySkill.name).offset(offset).limit(limit))).all()
    return RegistryListResponse(skills=[_legacy_summary(row[0], row[1]) for row in rows], total=total, limit=limit, offset=offset)


@router.post("/publish", response_model=RegistrySkillSummaryResponse)
async def publish_registry_skill(payload: PublishRegistrySkillRequest, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id), _current_user: dict[str, object] = Depends(get_current_user)) -> RegistrySkillSummaryResponse:
    row = (
        await db.execute(select(Skill, Repo).join(Repo, Repo.id == Skill.repo_id).where(Skill.id == payload.skill_id))
    ).first()
    if row is None:
        raise _error(404, "Skill not found", "SKILL_NOT_FOUND")
    skill, repo = row
    if repo.org_id != current_org_id:
        raise _error(403, "Skill does not belong to this org", "SKILL_FORBIDDEN")
    listing = (
        await db.execute(select(RegistrySkill).where(RegistrySkill.skill_id == skill.id, RegistrySkill.org_id == current_org_id))
    ).scalar_one_or_none()
    if listing is None:
        listing = RegistrySkill(
            org_id=current_org_id,
            repo_id=repo.id,
            skill_id=skill.id,
            domain=skill.domain,
            name=payload.name or f"{skill.domain}/SKILL.md",
            description=payload.description,
            is_public=payload.is_public if payload.is_public is not None else payload.visibility == "public",
            tags=_normalized_tags(payload.tags),
        )
        db.add(listing)
    else:
        listing.name = payload.name or listing.name
        listing.description = payload.description
        listing.is_public = payload.is_public if payload.is_public is not None else payload.visibility == "public"
        listing.tags = _normalized_tags(payload.tags)
    await db.flush()
    return _legacy_summary(listing, skill)


@router.post("/import-skill-file", response_model=ImportRegistryResponse)
async def import_skill_file(payload: ImportSkillFileRequest, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id), _current_user: dict[str, object] = Depends(get_current_user)) -> ImportRegistryResponse:
    if payload.repo_id:
        return await import_org_skill(current_org_id, payload, db, current_org_id)
    repo = (await db.execute(select(Repo).where(Repo.org_id == current_org_id).limit(1))).scalar_one_or_none()
    if repo is None:
        raise _error(404, "Repo not found", "REPO_NOT_FOUND")
    payload.repo_id = repo.id
    return await import_org_skill(current_org_id, payload, db, current_org_id)


@router.get("/{registry_id}")
async def get_registry_skill(registry_id: str, db: AsyncSession = Depends(get_db)):
    if hasattr(db, "get"):
        entry = await db.get(SkillRegistryEntry, registry_id)
        if entry is not None and entry.visibility == "public":
            return _entry_response(entry, preview_chars=800).model_dump(mode="json") | {"content": entry.content, "content_hash": entry.content_hash, "skill_path": None, "repo_name": "", "repo_full_name": ""}
    row = (await db.execute(select(RegistrySkill, Skill, Repo).join(Skill, Skill.id == RegistrySkill.skill_id).join(Repo, Repo.id == RegistrySkill.repo_id).where(RegistrySkill.id == registry_id, RegistrySkill.is_public.is_(True)))).first()
    if row is None:
        raise _error(404, "Registry skill not found", "REGISTRY_SKILL_NOT_FOUND")
    listing, skill, repo = row
    content, content_hash = await _latest_content(db, skill)
    return RegistrySkillDetailResponse(**_legacy_summary(listing, skill).model_dump(), content=content or "", content_hash=content_hash, skill_path=skill.skill_path, repo_name=repo.name, repo_full_name=repo.full_name)


@router.post("/{registry_id}/import")
async def import_registry_skill(registry_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id), _current_user: dict[str, object] = Depends(get_current_user)):
    if hasattr(db, "get"):
        entry = await db.get(SkillRegistryEntry, registry_id)
        if entry is not None and entry.visibility == "public":
            entry.install_count = int(entry.install_count or 0) + 1
            db.add(MarketplaceInstall(registry_entry_id=entry.id, org_id=current_org_id, installed_by="cli"))
            return _entry_response(entry, preview_chars=800).model_dump(mode="json") | {"content": entry.content, "content_hash": entry.content_hash}
    row = (await db.execute(select(RegistrySkill, Skill, Repo).join(Skill, Skill.id == RegistrySkill.skill_id).join(Repo, Repo.id == RegistrySkill.repo_id).where(RegistrySkill.id == registry_id, RegistrySkill.is_public.is_(True)))).first()
    if row is None:
        raise _error(404, "Registry skill not found", "REGISTRY_SKILL_NOT_FOUND")
    listing, skill, repo = row
    listing.import_count = int(listing.import_count or 0) + 1
    await db.execute(update(RegistrySkill).where(RegistrySkill.id == registry_id).values(import_count=RegistrySkill.import_count + 1))
    await db.flush()
    content, content_hash = await _latest_content(db, skill)
    return RegistrySkillDetailResponse(**_legacy_summary(listing, skill).model_dump(), content=content or "", content_hash=content_hash, skill_path=skill.skill_path, repo_name=repo.name, repo_full_name=repo.full_name)
