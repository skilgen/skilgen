from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime, timedelta
from difflib import unified_diff
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from apps.api.api.auth import get_current_org_id, get_current_org_id_optional, get_current_user
from apps.api.api.routes.orgs import (
    _criticality_score,
    _last_30_dates,
    _repo_language_metadata,
    _repo_response,
    _score_response,
    _skill_alert,
)

from apps.api.api.analysis import _skill_category_for_domain
from apps.api.api.routes.webhook import _queue_analysis
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
from apps.api.api.services.agent_connection import detect_runtime_from_headers, normalize_runtime
from apps.api.api.services.commit_check import run_commit_check
from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError, call_llm
from apps.api.api.services.memory import run_session_knowledge_extraction
from apps.api.api.services.pr_attribution import attribute_pr
from apps.api.api.services.pr_risk import compute_risk_score
from apps.api.api.services.snapshot import auto_snapshot_skill, rollback_skill
from packages.db.database import get_db
from packages.db.models import AgentSession, AnalysisRun, Dependency, Org, PRAttribution, PullRequest, Repo, ScoreHistory, Skill, SkillMemoryStub, SkillSnapshot, SkillUsageEvent, SkillVersion
from packages.db.models.skill import skill_category_for_source_type
from packages.db.schemas import (
    AnalysisRunResponse,
    AnalyzeSourceResponse,
    DependencyReportResponse,
    DailyLoadPointResponse,
    DependencyResponse,
    RepoSkillSourceSummary,
    RepoSkillSourcesResponse,
    RepoSkillUsageStatsResponse,
    SkillCategoryCoverage,
    SkillSourceSkillSummary,
)
from skilgen.core.score import render_repo_score_badge_svg


router = APIRouter(prefix="/repos", tags=["repos"])

SKILL_CATEGORIES = [
    "codebase_architecture",
    "code_style",
    "testing_conventions",
    "internal_tools",
    "security_compliance",
    "design_system",
    "data_schema",
    "operational_knowledge",
]

SOURCE_TYPES = [
    "code",
    "openapi",
    "graphql",
    "postman",
    "terraform",
    "kubernetes",
    "helm",
    "dbt",
    "sql_schema",
    "kafka",
    "sarif",
    "sbom",
    "security_policy",
    "runbook",
    "confluence",
    "notion",
    "incident",
    "pagerduty",
]


class ManualAnalysisRequest(BaseModel):
    installation_id: int | None = None


class AnalyzeSourceRequest(BaseModel):
    """Request body for source-specific analysis jobs."""

    source_type: Literal[
        "openapi",
        "graphql",
        "postman",
        "terraform",
        "kubernetes",
        "helm",
        "dbt",
        "sql_schema",
        "kafka",
        "sarif",
        "sbom",
        "security_policy",
        "runbook",
        "confluence",
        "notion",
        "incident",
        "pagerduty",
    ]
    path: str | None = Field(default=None, max_length=512)


class SkillContentUpdate(BaseModel):
    """Request body for manual skill content updates."""

    content: str = Field(min_length=1, max_length=200_000)


class CommitCheckRequest(BaseModel):
    base_sha: str | None = Field(default=None, max_length=255)
    branch: str | None = Field(default=None, max_length=255)
    diff: str | None = Field(default=None, max_length=500_000)


class RepoDiffCheckRequest(BaseModel):
    diff: str = Field(min_length=1, max_length=500_000)


class SkillSnapshotCreateRequest(BaseModel):
    label: str | None = Field(default=None, max_length=255)


def _serialize_pr_attribution(attribution: PRAttribution) -> dict[str, object]:
    return {
        "id": attribution.id,
        "pr_id": attribution.pr_id,
        "primary_agent": attribution.primary_agent,
        "confidence": attribution.confidence,
        "lines_by_agent": attribution.lines_by_agent or {},
        "lines_by_human": attribution.lines_by_human,
        "sessions": attribution.sessions or [],
        "skills_loaded": attribution.skills_loaded or [],
        "skills_violated": attribution.skills_violated or [],
        "risk_score": attribution.risk_score,
        "risk_tier": attribution.risk_tier,
        "risk_breakdown": attribution.risk_breakdown or {},
        "computed_at": attribution.computed_at.isoformat() if attribution.computed_at else None,
    }


class SkillImproveRequest(BaseModel):
    """Request body for the skill improvement loop."""

    mode: Literal["regenerate", "enhance"] = "enhance"
    section: Literal["anti_patterns"] | None = None
    content_to_append: str | None = None
    review_comment: str | None = None


class SkillImprovementIssue(BaseModel):
    dimension: str
    score: int
    max: int
    reason: str
    fix: str
    impact: Literal["high", "medium"]
    points_available: int


class ImprovementPlanResponse(BaseModel):
    skill_id: str
    current_score: int
    potential_score: int
    score_gap: int
    issues: list[SkillImprovementIssue]
    word_count: int
    code_block_count: int
    is_improvable: bool
    quick_win: SkillImprovementIssue | None


class SkillImproveResponse(BaseModel):
    improved: bool
    queued: bool | None = None
    task_id: str | None = None
    reason: str | None = None
    new_score: float | None = None
    score_delta: float | None = None
    new_version: int | None = None
    content: str | None = None


class SkillSnapshotItem(BaseModel):
    skill_id: str
    domain: str
    version_number: int
    content: str
    score_total: int
    score_freshness: int
    created_at: datetime


class SnapshotResponse(BaseModel):
    at: datetime
    repo_id: str
    skill_count: int
    skills: list[SkillSnapshotItem]


class SessionMessage(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str


class SessionIngestionPayload(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()), max_length=128)
    agent_runtime: Literal["claude_code", "codex", "cursor", "copilot", "gemini", "other"]
    task_description: str | None = Field(default=None, max_length=1000)
    engineer_login: str | None = Field(default=None, max_length=128)
    duration_minutes: int | None = None
    files_touched: list[str] = Field(default_factory=list, max_length=500)
    skill_paths_loaded: list[str] = Field(default_factory=list, max_length=200)
    skills_loaded: list[str] = Field(default_factory=list, max_length=200)
    code_produced: str | None = None
    outcome: str | None = None
    notes: str | None = None
    messages: list[SessionMessage] = Field(default_factory=list, max_length=500)


class SessionIngestionResponse(BaseModel):
    session_db_id: str
    session_id: str | None = None
    status: Literal["created", "duplicate"]
    extraction_queued: bool


class AgentSessionResponse(BaseModel):
    id: str
    session_id: str
    agent_runtime: str
    task_description: str | None
    engineer_login: str | None
    duration_minutes: int | None
    files_touched: list[str]
    skill_paths_loaded: list[str]
    extraction_status: str
    discoveries_found: int
    created_at: datetime


class KnowledgeVelocityPoint(BaseModel):
    week_start: str
    discoveries: int


async def _repo_in_scope(db: AsyncSession, repo_id: str, org_id: str) -> Repo:
    repo_result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = repo_result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return repo


async def _snapshot_actor(request: Request, db: AsyncSession, current_org_id: str | None) -> tuple[str, str]:
    api_key = (
        request.headers.get("x-api-key")
        or request.headers.get("X-API-Key")
        or request.headers.get("api-key")
        or request.headers.get("API-Key")
    )
    if api_key:
        org = (await db.execute(select(Org).where(Org.api_key == api_key))).scalar_one_or_none()
        if org is None:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return str(org.id), f"api_key:{getattr(org, 'login', None) or org.id}"
    if current_org_id:
        return current_org_id, get_actor_login(request)
    raise HTTPException(status_code=401, detail="API key required")


def _snapshot_metadata(snapshot: SkillSnapshot) -> dict[str, object]:
    return {
        "id": snapshot.id,
        "skill_id": snapshot.skill_id,
        "repo_id": snapshot.repo_id,
        "snapshot_type": snapshot.snapshot_type,
        "label": snapshot.label,
        "score_total": snapshot.score_total,
        "score_groundedness": snapshot.score_groundedness,
        "score_coverage": snapshot.score_coverage,
        "score_freshness": snapshot.score_freshness,
        "score_structure": snapshot.score_structure,
        "created_by": snapshot.created_by,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
    }


async def _skill_in_repo(db: AsyncSession, repo_id: str, skill_id: str) -> Skill:
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


def _normalized_source_type(skill: Skill) -> str:
    """Return the persisted source type or the backwards-compatible default."""
    return str(skill.source_type or "code")


def _normalized_skill_category(skill: Skill) -> str:
    """Return the persisted skill category or derive one from source type."""
    return str(skill.skill_category or skill_category_for_source_type(_normalized_source_type(skill)))


def _coverage_score(coverage_map: dict[str, SkillCategoryCoverage]) -> int:
    """Compute the 0-100 category coverage score."""
    covered = sum(1 for item in coverage_map.values() if item.covered)
    return round((covered / len(SKILL_CATEGORIES)) * 100)


def _compute_skill_score(content: str) -> dict[str, int]:
    """Compute the lightweight 0-100 score used for manual content edits."""
    word_count = len(content.split())
    has_headings = bool(re.search(r"^#{1,3}\s", content, re.MULTILINE))
    heading_count = len(re.findall(r"^#{1,3}\s", content, re.MULTILINE))
    has_code_blocks = "```" in content
    file_ref_count = len(re.findall(r"`[^`]+\.(py|ts|tsx|js|go|rs|java|cs|rb|php)`", content))
    has_patterns_section = bool(re.search(r"pattern|example|usage|how.to", content, re.IGNORECASE))
    has_version_hint = bool(re.search(r"v\d+\.\d+|version|last.verified|updated", content, re.IGNORECASE))
    bullet_count = len(re.findall(r"^\s*[-*]\s", content, re.MULTILINE))

    groundedness = min(25, file_ref_count * 4 + (8 if has_code_blocks else 0) + (5 if has_patterns_section else 0))
    coverage = min(25, max(0, (word_count // 20)) + (heading_count * 3) + (bullet_count // 2))
    freshness = min(25, 10 + (15 if has_version_hint else 0))
    structure = min(25, (10 if has_headings else 0) + (heading_count * 3) + (5 if bullet_count >= 3 else 0))

    return {
        "total": groundedness + coverage + freshness + structure,
        "groundedness": groundedness,
        "coverage": coverage,
        "freshness": freshness,
        "structure": structure,
    }


def _score_dict(skill: Skill) -> dict[str, int]:
    return {
        "total": int(skill.score_total or 0),
        "groundedness": int(skill.score_groundedness or 0),
        "coverage": int(skill.score_coverage or 0),
        "freshness": int(skill.score_freshness or 0),
        "structure": int(skill.score_structure or 0),
    }


def _skill_word_count(content: str | None) -> int:
    return len((content or "").split())


def _skill_code_block_count(content: str | None) -> int:
    return len(re.findall(r"```", content or "")) // 2


def _skill_improvement_issues(skill: Skill, content: str) -> list[SkillImprovementIssue]:
    """Build the requested quality diagnosis from persisted skill health and content."""
    issues: list[SkillImprovementIssue] = []
    lines = content.splitlines()
    words = len(content.split())
    code_block_count = content.count("```")
    file_ref_count = len([line for line in lines if "/" in line and "." in line])
    groundedness = int(skill.score_groundedness or 0)
    coverage = int(skill.score_coverage or 0)
    freshness = int(skill.score_freshness or 0)
    structure = int(skill.score_structure or 0)
    if groundedness < 15:
        issues.append(
            SkillImprovementIssue(
                dimension="Groundedness",
                score=groundedness,
                max=25,
                reason=f"Only {code_block_count // 2} code examples found. Skills need concrete examples from your actual codebase.",
                fix="Add 3-5 real code snippets from your repo showing how this domain is actually used.",
                impact="high",
                points_available=25 - groundedness,
            )
        )
    elif groundedness < 20:
        issues.append(
            SkillImprovementIssue(
                dimension="Groundedness",
                score=groundedness,
                max=25,
                reason=f"Only {file_ref_count} file path references found. More specific file references help agents navigate.",
                fix="Add specific file paths (e.g. src/payments/checkout.py) where key logic lives.",
                impact="medium",
                points_available=25 - groundedness,
            )
        )

    has_antipatterns = "anti-pattern" in content.lower() or "avoid" in content.lower() or "don't" in content.lower()
    if coverage < 15:
        issues.append(
            SkillImprovementIssue(
                dimension="Coverage",
                score=coverage,
                max=25,
                reason="Missing patterns and anti-patterns. Agents need to know both what TO do and what NOT to do.",
                fix="Add a 'Key Patterns' section (3-5 patterns) and a 'Common Mistakes' or 'Anti-patterns' section.",
                impact="high",
                points_available=25 - coverage,
            )
        )
    elif not has_antipatterns:
        issues.append(
            SkillImprovementIssue(
                dimension="Coverage",
                score=coverage,
                max=25,
                reason="No anti-patterns documented. Agents frequently make mistakes that could be prevented.",
                fix="Add an 'Anti-patterns' or 'Common Mistakes' section with 2-3 things to avoid.",
                impact="medium",
                points_available=25 - coverage,
            )
        )

    updated_at = getattr(skill, "updated_at", None) or getattr(skill, "created_at", None)
    days_since_update = (datetime.utcnow() - updated_at).days if updated_at else 999
    if freshness < 15:
        issues.append(
            SkillImprovementIssue(
                dimension="Freshness",
                score=freshness,
                max=25,
                reason=f"Skill content is {days_since_update} days old. Stale skills mislead agents about current code structure.",
                fix="Run `skilgen deliver --project-root .` to regenerate from current source, then review and save.",
                impact="high",
                points_available=25 - freshness,
            )
        )

    header_count = len([line for line in lines if line.startswith("#")])
    if structure < 15:
        issues.append(
            SkillImprovementIssue(
                dimension="Structure",
                score=structure,
                max=25,
                reason=f"Only {header_count} sections found, {words} words total. Skills need clear sections and sufficient depth.",
                fix="Organise with headers: Overview, Key Patterns, Anti-patterns, File Map, Check Paths. Target 300-800 words.",
                impact="medium" if words > 100 else "high",
                points_available=25 - structure,
            )
        )
    issues.sort(key=lambda item: (0 if item.impact == "high" else 1, -item.points_available))
    return issues


def _improvement_plan(skill: Skill, version: SkillVersion | None) -> dict[str, object]:
    content = (version.content if version else skill.content) or ""
    issues = _skill_improvement_issues(skill, content)
    current_score = int(skill.score_total or 0)
    potential_score = min(100, current_score + sum(issue.points_available for issue in issues))
    return {
        "skill_id": str(skill.id),
        "current_score": current_score,
        "potential_score": potential_score,
        "score_gap": potential_score - current_score,
        "issues": issues,
        "word_count": len(content.split()),
        "code_block_count": content.count("```") // 2,
        "is_improvable": len(issues) > 0,
        "quick_win": issues[0] if issues else None,
    }


def _skill_improvement_plan(skill: Skill, version: SkillVersion | None = None) -> ImprovementPlanResponse:
    plan = _improvement_plan(skill, version)
    return ImprovementPlanResponse(
        skill_id=str(plan["skill_id"]),
        current_score=int(plan["current_score"]),
        potential_score=int(plan["potential_score"]),
        score_gap=int(plan["score_gap"]),
        issues=plan["issues"],  # type: ignore[arg-type]
        word_count=int(plan["word_count"]),
        code_block_count=int(plan["code_block_count"]),
        is_improvable=bool(plan["is_improvable"]),
        quick_win=plan["quick_win"],  # type: ignore[arg-type]
    )


def _append_to_anti_patterns(content: str, addition: str) -> str:
    heading = re.search(r"(^##\s+Anti[- ]patterns.*$)", content, flags=re.IGNORECASE | re.MULTILINE)
    addition = addition.strip()
    if not addition:
        return content
    if not heading:
        suffix = "\n\n" if content.strip() else ""
        return f"{content.rstrip()}{suffix}## Anti-patterns\n\n{addition}\n"
    insert_at = heading.end()
    next_heading = re.search(r"^##\s+", content[insert_at:], flags=re.MULTILINE)
    if next_heading:
        position = insert_at + next_heading.start()
        return f"{content[:position].rstrip()}\n\n{addition}\n\n{content[position:].lstrip()}"
    return f"{content.rstrip()}\n\n{addition}\n"


async def _llm_skill_improvement(
    *,
    settings: dict[str, object],
    content: str,
    issues: list[SkillImprovementIssue],
    score: int,
) -> str | None:
    """Return AI-improved content through the central LLM service."""
    issues_summary = ", ".join(f"{issue.dimension} ({issue.score}/{issue.max})" for issue in issues) or "none"
    specific_fixes = "\n".join(f"- {issue.fix}" for issue in issues) or "- Preserve and clarify the existing guidance."
    user_prompt = f"""The current skill scored
{score}/100. The weakest areas are: {issues_summary}.

Current content:
{content or ""}

Improve this skill by:
{specific_fixes}

Rules:
- Keep all existing correct information
- Add code examples if missing (use realistic placeholder syntax matching the domain)
- Add anti-patterns section if missing
- Improve structure with clear headers
- Target 400-600 words
- Return ONLY the improved skill content, no explanation
"""
    return await call_llm(
        settings,
        "You are improving a software skill document for AI agents. Return only the improved markdown content.",
        user_prompt,
        max_tokens=2000,
    )


async def _latest_repo_skills(db: AsyncSession, repo_id: str) -> list[Skill]:
    """Return latest skills by domain for a repository."""
    rows = (
        await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(desc(Skill.created_at)))
    ).scalars().all()
    latest_by_domain: dict[str, Skill] = {}
    for skill in rows:
        latest_by_domain.setdefault(skill.domain, skill)
    return list(latest_by_domain.values())


def _build_coverage_map(skills: list[Skill]) -> dict[str, SkillCategoryCoverage]:
    """Build the eight-category coverage map used by API and dashboard."""
    grouped: dict[str, list[Skill]] = {category: [] for category in SKILL_CATEGORIES}
    for skill in skills:
        category = _normalized_skill_category(skill)
        if category in grouped:
            grouped[category].append(skill)
    coverage_map: dict[str, SkillCategoryCoverage] = {}
    for category, category_skills in grouped.items():
        avg = 0
        if category_skills:
            avg = round(sum(int(skill.score_total or 0) for skill in category_skills) / len(category_skills))
        coverage_map[category] = SkillCategoryCoverage(
            covered=bool(category_skills),
            skill_count=len(category_skills),
            avg_score=avg,
        )
    return coverage_map

async def _latest_repo_score_total(db: AsyncSession, repo_id: str) -> int:
    """Return the most recent stored score total for a repository."""
    latest_run = (
        await db.execute(
            select(AnalysisRun.score_total)
            .where(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "complete")
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    if latest_run is not None:
        return int(latest_run or 0)
    latest_history = (
        await db.execute(
            select(ScoreHistory.score_total)
            .where(ScoreHistory.repo_id == repo_id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    return int(latest_history or 0)


async def _repo_score_history_rows(db: AsyncSession, repo_id: str, limit: int = 30) -> list[ScoreHistory]:
    """Load recent score history in ascending order for charting and projections."""
    rows = (
        await db.execute(
            select(ScoreHistory)
            .where(ScoreHistory.repo_id == repo_id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(limit)
        )
    ).scalars().all()
    return list(reversed(rows))


def _dependency_upgrade_command(dependency: Dependency) -> str | None:
    """Return the safest package-manager upgrade command for a dependency."""
    ecosystem = str(dependency.ecosystem or "").lower()
    if ecosystem == "pip":
        return f"python -m pip install --upgrade {dependency.name}"
    if ecosystem == "npm":
        return f"npm update {dependency.name}"
    if ecosystem == "cargo":
        return f"cargo update -p {dependency.name}"
    if ecosystem == "go":
        return f"go get {dependency.name}@latest"
    return None


def _dependency_response(dependency: Dependency) -> DependencyResponse:
    """Serialize a stored dependency row for API responses."""
    raw_cves = dependency.cves or []
    cves = [str(item) for item in raw_cves] if isinstance(raw_cves, list) else []
    return DependencyResponse(
        id=str(dependency.id),
        name=str(dependency.name),
        version=dependency.version,
        ecosystem=str(dependency.ecosystem),
        risk_level=str(dependency.risk_level),
        cves=cves,
        latest_version=dependency.latest_version,
        license=dependency.license,
        created_at=dependency.created_at,
        upgrade_command=_dependency_upgrade_command(dependency),
    )


def _dependency_risk_score(dependencies: list[Dependency]) -> int:
    """Compute a 0-100 dependency risk score where lower means safer."""
    weights = {"high": 30, "medium": 15, "low": 5, "healthy": 0}
    return min(100, sum(weights.get(str(item.risk_level), 0) for item in dependencies))


@router.get("/{repo_id}")
async def get_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    response = (await _repo_response(db, repo)).model_dump()
    latest_skills = await _latest_repo_skills(db, repo.id)
    languages, derived_display_language = _repo_language_metadata(latest_skills, repo.language)
    response["default_branch"] = repo.default_branch
    response["installation_id"] = repo.github_installation_id
    response["languages"] = languages
    response["display_language"] = repo.language or derived_display_language
    return response


@router.get("/{repo_id}/score-badge")
async def get_repo_score_badge(
    repo_id: str,
    style: Literal["flat", "flat-square", "for-the-badge"] = Query(default="flat"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return an SVG Skilgen Score badge for the repository."""
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    score_total = await _latest_repo_score_total(db, repo_id)
    svg = render_repo_score_badge_svg(score_total, style=style)
    return Response(content=svg, media_type="image/svg+xml")


def _cert_badge_svg(score: int | None, grade: str | None = None) -> str:
    configured = score is not None
    safe_score = max(0, min(100, int(score or 0)))
    color = "#6b7280"
    right_text = "not configured"
    if configured:
        color = "#16a34a" if safe_score >= 80 else "#ca8a04" if safe_score >= 60 else "#dc2626"
        right_text = f"AI Ready &#183; {safe_score}/100" if not grade else f"Grade {grade} &#183; {safe_score}/100"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="180" height="20" role="img" aria-label="Skillayer: {right_text}">
  <linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-opacity=".08"/></linearGradient>
  <clipPath id="r"><rect width="180" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)"><rect width="78" height="20" fill="#111827"/><rect x="78" width="102" height="20" fill="{color}"/><rect width="180" height="20" fill="url(#s)"/></g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="39" y="15" fill="#010101" fill-opacity=".3">Skillayer</text><text x="39" y="14">Skillayer</text>
    <text x="129" y="15" fill="#010101" fill-opacity=".3">{right_text}</text><text x="129" y="14">{right_text}</text>
  </g>
</svg>"""


def _grade_for_score(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


@router.get("/{repo_id}/badge.svg")
async def get_repo_certification_badge(repo_id: str, db: AsyncSession = Depends(get_db)) -> Response:
    """Return a public dynamic AI-readiness badge for README embeds."""
    try:
        repo = await db.get(Repo, repo_id)
        if repo is None:
            svg = _cert_badge_svg(None)
        else:
            try:
                skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
            except Exception:
                skills = []
            if not skills:
                score = await _latest_repo_score_total(db, repo_id)
            else:
                categories = {str(skill.skill_category or skill_category_for_source_type(skill.source_type)) for skill in skills}
                coverage = min(1.0, len(categories) / len(SKILL_CATEGORIES))
                loads = min(1.0, sum(int(skill.load_count_30d or 0) for skill in skills) / 1000)
                quality = sum(int(skill.score_total or 0) for skill in skills) / len(skills) / 100
                freshness = sum(1 for skill in skills if int(skill.score_freshness or 0) >= 15) / len(skills)
                score = round((coverage * 30) + (loads * 30) + (quality * 25) + (freshness * 15))
            svg = _cert_badge_svg(score)
        return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "no-cache, max-age=300"})
    except Exception:
        return Response(content=_cert_badge_svg(None), media_type="image/svg+xml", headers={"Cache-Control": "no-cache, max-age=300"})


@router.get("/{repo_id}/skills")
async def get_repo_skills(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    skills = sorted(await _latest_repo_skills(db, repo_id), key=lambda item: (-int(item.score_total or 0), item.domain))
    responses: list[dict[str, object]] = []
    for skill in skills:
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
        score = _score_response(skill)  # type: ignore[arg-type]
        responses.append({
            "id": skill.id,
            "repo_id": repo.id,
            "repo_name": repo.name,
            "domain": skill.domain,
            "skill_path": skill.skill_path,
            "score": score.model_dump() if score else None,
            "content": (skill.content[:500] if skill.content else None),
            "content_hash": skill.content_hash,
            "source_type": _normalized_source_type(skill),
            "skill_category": _normalized_skill_category(skill),
            "is_enterprise": bool(getattr(skill, "is_enterprise", False)),
            "is_stale": skill.is_stale,
            "load_count_30d": skill.load_count_30d,
            "last_loaded_at": skill.last_loaded_at,
            "version_count": int(version_count or 0),
            "latest_version_number": (latest_version.version_number if latest_version else None),
            "last_updated_at": latest_version.created_at if latest_version else skill.created_at,
        })
    return responses


@router.get("/{repo_id}/skills/{skill_id}/snapshots")
async def list_skill_snapshots(
    repo_id: str,
    skill_id: str,
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[dict[str, object]]:
    org_id, _actor = await _snapshot_actor(request, db, current_org_id)
    await _repo_in_scope(db, repo_id, org_id)
    await _skill_in_repo(db, repo_id, skill_id)
    statement = select(SkillSnapshot).where(SkillSnapshot.repo_id == repo_id, SkillSnapshot.skill_id == skill_id)
    if cursor:
        try:
            cursor_at = datetime.fromisoformat(cursor.replace("Z", "+00:00")).replace(tzinfo=None)
            statement = statement.where(SkillSnapshot.created_at < cursor_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid cursor") from None
    snapshots = (
        await db.execute(statement.order_by(desc(SkillSnapshot.created_at)).limit(limit))
    ).scalars().all()
    return [_snapshot_metadata(snapshot) for snapshot in snapshots]


@router.get("/{repo_id}/skills/{skill_id}/snapshots/{snapshot_id}")
async def get_skill_snapshot(
    repo_id: str,
    skill_id: str,
    snapshot_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict[str, object]:
    org_id, _actor = await _snapshot_actor(request, db, current_org_id)
    await _repo_in_scope(db, repo_id, org_id)
    await _skill_in_repo(db, repo_id, skill_id)
    snapshot = await db.get(SkillSnapshot, snapshot_id)
    if snapshot is None or snapshot.skill_id != skill_id or snapshot.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return {**_snapshot_metadata(snapshot), "content": snapshot.content}


@router.get("/{repo_id}/skills/{skill_id}/snapshots/{snapshot_id}/diff")
async def get_skill_snapshot_diff(
    repo_id: str,
    skill_id: str,
    snapshot_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> Response:
    org_id, _actor = await _snapshot_actor(request, db, current_org_id)
    await _repo_in_scope(db, repo_id, org_id)
    skill = await _skill_in_repo(db, repo_id, skill_id)
    snapshot = await db.get(SkillSnapshot, snapshot_id)
    if snapshot is None or snapshot.skill_id != skill_id or snapshot.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    diff = "".join(
        unified_diff(
            (snapshot.content or "").splitlines(keepends=True),
            (skill.content or "").splitlines(keepends=True),
            fromfile=f"snapshot/{snapshot.id}",
            tofile="current",
        )
    )
    return Response(content=diff, media_type="text/plain")


@router.post("/{repo_id}/skills/{skill_id}/snapshots")
async def create_skill_snapshot(
    repo_id: str,
    skill_id: str,
    payload: SkillSnapshotCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict[str, object]:
    org_id, actor = await _snapshot_actor(request, db, current_org_id)
    await _repo_in_scope(db, repo_id, org_id)
    skill = await _skill_in_repo(db, repo_id, skill_id)
    try:
        snapshot = await auto_snapshot_skill(
            skill,
            db,
            snapshot_type="manual",
            label=(payload.label or "").strip() or None,
            created_by=actor,
            idempotent=False,
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to create snapshot") from exc
    return _snapshot_metadata(snapshot)


@router.post("/{repo_id}/skills/{skill_id}/rollback/{snapshot_id}")
async def rollback_repo_skill(
    repo_id: str,
    skill_id: str,
    snapshot_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict[str, object]:
    org_id, actor = await _snapshot_actor(request, db, current_org_id)
    await _repo_in_scope(db, repo_id, org_id)
    await _skill_in_repo(db, repo_id, skill_id)
    try:
        _skill, pre_edit = await rollback_skill(skill_id, snapshot_id, db, actor)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to rollback skill") from exc
    return {"ok": True, "snapshot_id": snapshot_id, "pre_edit_snapshot_id": pre_edit.id}


@router.get("/{repo_id}/skills/{skill_id}/usage-stats", response_model=RepoSkillUsageStatsResponse)
async def get_repo_skill_usage_stats(
    repo_id: str,
    skill_id: str,
    db: AsyncSession = Depends(get_db),
) -> RepoSkillUsageStatsResponse:
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    now = datetime.now(UTC).replace(tzinfo=None)
    cutoff_30d = now - timedelta(days=30)
    cutoff_7d = now - timedelta(days=7)
    daily_label = func.date(SkillUsageEvent.loaded_at).label("day")

    try:
        usage = (
            await db.execute(
                select(
                    func.count(SkillUsageEvent.id).label("loads_30d"),
                    func.count(SkillUsageEvent.id).filter(SkillUsageEvent.loaded_at >= cutoff_7d).label("loads_7d"),
                    func.max(SkillUsageEvent.loaded_at).label("last_loaded_at"),
                )
                .where(SkillUsageEvent.skill_id == skill_id, SkillUsageEvent.loaded_at >= cutoff_30d)
            )
        ).one()
        daily_rows = (
            await db.execute(
                select(daily_label, func.count(SkillUsageEvent.id).label("loads"))
                .where(SkillUsageEvent.skill_id == skill_id, SkillUsageEvent.loaded_at >= cutoff_30d)
                .group_by(daily_label)
                .order_by(daily_label)
            )
        ).all()
        repo_max_loads = (
            await db.execute(select(func.max(Skill.load_count_30d)).where(Skill.repo_id == repo_id))
        ).scalar_one_or_none()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to load skill usage stats") from exc

    try:
        runtime_rows = (
            await db.execute(
                select(SkillUsageEvent.agent_runtime, func.count(SkillUsageEvent.id).label("loads"))
                .where(SkillUsageEvent.skill_id == skill_id, SkillUsageEvent.loaded_at >= cutoff_30d)
                .group_by(SkillUsageEvent.agent_runtime)
                .order_by(desc(func.count(SkillUsageEvent.id)))
            )
        ).all()
        runtime_counts = {str(row.agent_runtime or "unknown"): int(row.loads or 0) for row in runtime_rows}
    except Exception:
        await db.rollback()
        runtime_counts = {"unknown": int(usage.loads_30d or 0)}

    daily_map = {str(row.day): int(row.loads or 0) for row in daily_rows}
    loads_30d = int(usage.loads_30d or 0)
    loads_7d = int(usage.loads_7d or 0)
    last_loaded_at = usage.last_loaded_at

    return RepoSkillUsageStatsResponse(
        criticality_score=_criticality_score(loads_30d, last_loaded_at, bool(skill.is_stale), int(repo_max_loads or 1)),
        loads_30d=loads_30d,
        loads_7d=loads_7d,
        last_loaded_at=last_loaded_at,
        alert=_skill_alert(skill, loads_30d, now),
        daily_loads=[DailyLoadPointResponse(date=day, loads=daily_map.get(day, 0)) for day in _last_30_dates(now)],
        agent_runtimes=runtime_counts,
    )


def _parse_snapshot_at(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed.replace(tzinfo=None)


@router.get("/{repo_id}/skills/snapshot", response_model=SnapshotResponse)
async def get_skills_snapshot(
    repo_id: str,
    at: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SnapshotResponse:
    await _repo_in_scope(db, repo_id, current_org_id)
    at_datetime = _parse_snapshot_at(at)
    try:
        skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
        items: list[SkillSnapshotItem] = []
        for skill in skills:
            version = (
                await db.execute(
                    select(SkillVersion)
                    .where(SkillVersion.skill_id == skill.id, SkillVersion.created_at <= at_datetime)
                    .order_by(desc(SkillVersion.version_number))
                    .limit(1)
                )
            ).scalar_one_or_none()
            if version is None:
                continue
            items.append(
                SkillSnapshotItem(
                    skill_id=skill.id,
                    domain=skill.domain,
                    version_number=int(version.version_number or 1),
                    content=version.content,
                    score_total=int(skill.score_total or 0),
                    score_freshness=int(skill.score_freshness or 0),
                    created_at=version.created_at,
                )
            )
        return SnapshotResponse(at=at_datetime, repo_id=repo_id, skill_count=len(items), skills=items)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to load skill snapshot") from exc


@router.get("/{repo_id}/skills/timeline")
async def get_skills_timeline(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[dict[str, object]]:
    await _repo_in_scope(db, repo_id, current_org_id)
    cutoff = datetime.utcnow() - timedelta(days=90)
    try:
        versions = (
            await db.execute(
                select(SkillVersion)
                .where(SkillVersion.repo_id == repo_id, SkillVersion.created_at >= cutoff)
                .order_by(desc(SkillVersion.created_at))
                .limit(200)
            )
        ).scalars().all()
        rows: list[dict[str, object]] = []
        previous_by_skill: dict[str, int] = {}
        for version in reversed(list(versions)):
            skill = await db.get(Skill, version.skill_id)
            score_after = int(skill.score_total or 0) if skill else 0
            score_before = previous_by_skill.get(version.skill_id)
            event = "new" if score_before is None else "improved" if score_after >= score_before else "dropped"
            previous_by_skill[version.skill_id] = score_after
            rows.append({"date": version.created_at.date().isoformat(), "event": event, "skill_domain": version.domain, "version_number": int(version.version_number or 1), "score_before": score_before, "score_after": score_after})
        return list(reversed(rows))
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to load skill timeline") from exc


@router.get("/{repo_id}/skills/{skill_id}/improvement-plan", response_model=ImprovementPlanResponse)
async def get_skill_improvement_plan(
    repo_id: str,
    skill_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ImprovementPlanResponse:
    """Return a deterministic plan for improving a skill."""
    await _repo_in_scope(db, repo_id, current_org_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")
    latest_version = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()
    return _skill_improvement_plan(skill, latest_version)


@router.post("/{repo_id}/skills/{skill_id}/improve", response_model=SkillImproveResponse)
async def improve_skill(
    repo_id: str,
    skill_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    payload: SkillImproveRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SkillImproveResponse:
    """Improve stored skill content and create a new version."""
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    body = payload
    latest_version = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()
    plan = _skill_improvement_plan(skill, latest_version)
    if body.section == "anti_patterns":
        addition = (body.content_to_append or "").strip()
        if not addition:
            raise HTTPException(status_code=400, detail="content_to_append is required")
        current_content = skill.content or ""
        new_content = _append_to_anti_patterns(current_content, addition)
        content_hash = hashlib.sha256(new_content.encode()).hexdigest()
        try:
            await db.execute(
                update(SkillVersion)
                .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
                .values(is_latest=False)
            )
            count_result = await db.execute(select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id))
            version_number = int(count_result.scalar() or 0) + 1
            skill.content = new_content
            skill.content_hash = content_hash
            skill.score_freshness = min(25, int(skill.score_freshness or 0) + 5)
            if hasattr(skill, "updated_at"):
                setattr(skill, "updated_at", datetime.utcnow())
            db.add(
                SkillVersion(
                    skill_id=skill.id,
                    run_id=skill.run_id or str(uuid4()),
                    repo_id=repo_id,
                    domain=skill.domain,
                    content=new_content,
                    content_hash=content_hash,
                    version_number=version_number,
                    is_latest=True,
                )
            )
            await db.commit()
        except SQLAlchemyError as exc:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Unable to update skill anti-patterns") from exc
        return SkillImproveResponse(
            improved=True,
            reason="Anti-pattern appended from code review",
            new_version=version_number,
            new_score=float(skill.score_total or 0),
            score_delta=0,
            content=new_content[:1000],
        )
    if body.mode == "regenerate":
        installation_id = repo.github_installation_id
        if not installation_id:
            raise HTTPException(status_code=400, detail="Repo installation id is not available")
        run = AnalysisRun(
            repo_id=repo_id,
            trigger="manual",
            status="queued",
            branch=repo.default_branch,
            created_at=datetime.utcnow(),
        )
        db.add(run)
        await db.flush()
        await db.commit()
        await _queue_analysis(
            request,
            background_tasks,
            {
                "run_id": run.id,
                "repo_id": repo.id,
                "installation_id": int(installation_id),
                "full_name": repo.full_name,
                "ref": repo.default_branch,
                "domain": skill.domain,
            },
        )
        return SkillImproveResponse(improved=False, queued=True, task_id=str(run.id))

    current_content = skill.content or ""
    org = await db.get(Org, repo.org_id)
    org_settings = org.settings if org is not None and isinstance(org.settings, dict) else {}
    try:
        new_content = await _llm_skill_improvement(
            settings=org_settings,
            content=current_content,
            issues=plan.issues,
            score=plan.current_score,
        )
    except LLMNotConfiguredError as exc:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "llm_not_configured",
                "message": "Configure an AI model in Settings to use this feature",
                "settings_url": "/dashboard/settings",
            },
        ) from exc
    except LLMCallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not new_content:
        return SkillImproveResponse(
            improved=False,
            reason="AI model did not return improved content",
        )

    content_hash = hashlib.sha256(new_content.encode()).hexdigest()
    latest_version_number = (
        await db.execute(
            select(SkillVersion.version_number)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()
    if content_hash == skill.content_hash:
        return SkillImproveResponse(
            improved=False,
            reason="Skill content is already up to date.",
            new_version=int(latest_version_number or 1),
            new_score=float(plan.current_score),
            score_delta=0,
        )

    score = _compute_skill_score(new_content)
    try:
        await db.execute(
            update(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .values(is_latest=False)
        )
        count_result = await db.execute(select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id))
        version_number = int(count_result.scalar() or 0) + 1

        skill.content = new_content
        skill.content_hash = content_hash
        skill.score_total = score["total"]
        skill.score_groundedness = score["groundedness"]
        skill.score_coverage = score["coverage"]
        skill.score_freshness = score["freshness"]
        skill.score_structure = score["structure"]
        skill.is_stale = False

        db.add(
            SkillVersion(
                skill_id=skill.id,
                run_id=skill.run_id or str(uuid4()),
                repo_id=repo_id,
                domain=skill.domain,
                content=new_content,
                content_hash=content_hash,
                version_number=version_number,
                is_latest=True,
            )
        )
        await audit.emit(
            db,
            current_org_id,
            "skill.improved",
            "updated",
            f"Improved skill content for {skill.domain}",
            actor_login=get_actor_login(request),
            repo_id=repo_id,
            repo_name=repo.name,
            skill_id=skill.id,
            skill_domain=skill.domain,
            resource_type="skill",
            resource_id=skill.id,
            metadata={"version_number": version_number, "score_total": score["total"], "mode": body.mode},
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to improve skill") from exc

    return SkillImproveResponse(
        improved=True,
        reason=None,
        new_version=version_number,
        new_score=float(skill.score_total or 0),
        score_delta=float(int(skill.score_total or 0) - plan.current_score),
        content=new_content,
    )


@router.patch("/{repo_id}/skills/{skill_id}/content")
async def update_repo_skill_content(
    repo_id: str,
    skill_id: str,
    payload: SkillContentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Update stored skill content and create a new version for the edit."""
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    content_hash = hashlib.sha256(payload.content.encode()).hexdigest()
    score = _compute_skill_score(payload.content)

    latest_version_number = (
        await db.execute(
            select(SkillVersion.version_number)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()

    if content_hash == skill.content_hash:
        return {
            "updated": False,
            "version_number": int(latest_version_number or 1),
            "score": _score_response(skill).model_dump(),
        }

    try:
        await db.execute(
            update(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .values(is_latest=False)
        )
        count_result = await db.execute(
            select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id)
        )
        version_number = int(count_result.scalar() or 0) + 1

        skill.content = payload.content
        skill.content_hash = content_hash
        skill.score_total = score["total"]
        skill.score_groundedness = score["groundedness"]
        skill.score_coverage = score["coverage"]
        skill.score_freshness = score["freshness"]
        skill.score_structure = score["structure"]
        skill.is_stale = False

        db.add(
            SkillVersion(
                skill_id=skill.id,
                run_id=skill.run_id or str(uuid4()),
                repo_id=repo_id,
                domain=skill.domain,
                content=payload.content,
                content_hash=content_hash,
                version_number=version_number,
                is_latest=True,
            )
        )
        await audit.emit(
            db,
            current_org_id,
            "skill.content_edited",
            "updated",
            f"Edited skill content for {skill.domain}",
            actor_login=get_actor_login(request),
            repo_id=repo_id,
            repo_name=repo.name,
            skill_id=skill.id,
            skill_domain=skill.domain,
            resource_type="skill",
            resource_id=skill.id,
            metadata={"version_number": version_number, "score_total": score["total"]},
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to update skill content") from exc

    return {
        "updated": True,
        "version_number": version_number,
        "score": _score_response(skill).model_dump(),
    }


def _week_start(value: datetime) -> datetime:
    return (value - timedelta(days=value.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


@router.post("/{repo_id}/sessions", response_model=SessionIngestionResponse, status_code=201)
async def ingest_agent_session(
    repo_id: str,
    payload: SessionIngestionPayload,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SessionIngestionResponse:
    """Capture a coding-agent session for asynchronous knowledge extraction."""
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    existing = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.repo_id == repo_id,
                AgentSession.session_id == payload.session_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return SessionIngestionResponse(session_db_id=existing.id, session_id=existing.id, status="duplicate", extraction_queued=False)

    session = AgentSession(
        repo_id=repo_id,
        org_id=repo.org_id,
        session_id=payload.session_id,
        agent_runtime=payload.agent_runtime,
        task_description=payload.task_description,
        engineer_login=payload.engineer_login,
        duration_minutes=payload.duration_minutes,
        files_touched=list(payload.files_touched),
        skill_paths_loaded=list(payload.skill_paths_loaded or payload.skills_loaded),
        skills_loaded=list(payload.skills_loaded or payload.skill_paths_loaded),
        code_produced=payload.code_produced,
        outcome=payload.outcome,
        notes=payload.notes,
        raw_message_count=len(payload.messages),
        extraction_status="pending",
        discoveries_found=0,
    )
    db.add(session)
    await audit.emit(
        db,
        repo.org_id,
        "memory.session_uploaded",
        "created",
        f"Uploaded {payload.agent_runtime} session {payload.session_id}",
        actor_login=get_actor_login(request),
        repo_id=repo_id,
        repo_name=repo.name,
        resource_type="session",
        resource_id=session.id,
        metadata={"agent_runtime": payload.agent_runtime, "message_count": len(payload.messages)},
    )
    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to capture session") from exc

    background_tasks.add_task(run_session_knowledge_extraction, session.id, payload.messages, repo_id)
    return SessionIngestionResponse(session_db_id=session.id, session_id=session.id, status="created", extraction_queued=True)


@router.get("/{repo_id}/sessions", response_model=list[AgentSessionResponse])
async def list_agent_sessions(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[AgentSessionResponse]:
    await _repo_in_scope(db, repo_id, current_org_id)
    sessions = (
        await db.execute(
            select(AgentSession)
            .where(AgentSession.repo_id == repo_id)
            .order_by(desc(AgentSession.created_at))
            .limit(20)
        )
    ).scalars().all()
    return [
        AgentSessionResponse(
            id=session.id,
            session_id=session.session_id,
            agent_runtime=session.agent_runtime,
            task_description=session.task_description,
            engineer_login=session.engineer_login,
            duration_minutes=session.duration_minutes,
            files_touched=list(session.files_touched or []),
            skill_paths_loaded=list(session.skill_paths_loaded or []),
            extraction_status=session.extraction_status,
            discoveries_found=int(session.discoveries_found or 0),
            created_at=session.created_at,
        )
        for session in sessions
    ]


@router.get("/{repo_id}/knowledge-velocity", response_model=list[KnowledgeVelocityPoint])
async def repo_knowledge_velocity(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[KnowledgeVelocityPoint]:
    await _repo_in_scope(db, repo_id, current_org_id)
    now = datetime.now(UTC).replace(tzinfo=None)
    this_week = _week_start(now)
    week_starts = [this_week - timedelta(weeks=offset) for offset in range(8)]
    oldest = week_starts[-1]
    rows = (
        await db.execute(
            select(SkillMemoryStub.created_at)
            .where(
                SkillMemoryStub.repo_id == repo_id,
                SkillMemoryStub.status != "rejected",
                SkillMemoryStub.created_at >= oldest,
            )
        )
    ).all()
    counts = {week.date().isoformat(): 0 for week in week_starts}
    for row in rows:
        created_at = getattr(row, "created_at", None) or row[0]
        if isinstance(created_at, datetime):
            key = _week_start(created_at).date().isoformat()
            if key in counts:
                counts[key] += 1
    return [KnowledgeVelocityPoint(week_start=week.date().isoformat(), discoveries=counts[week.date().isoformat()]) for week in week_starts]


@router.get("/{repo_id}/score-history")
async def get_score_history(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    rows = await _repo_score_history_rows(db, repo_id, limit=10)
    return [
        {
            "date": row.recorded_at.date().isoformat(),
            "score_total": row.score_total,
            "groundedness": row.score_groundedness,
            "coverage": row.score_coverage,
            "freshness": row.score_freshness,
            "structure": row.score_structure,
        }
        for row in rows
    ]


@router.get("/{repo_id}/score-forecast")
async def get_score_forecast(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Return a simple linear forecast for 30/90-day score based on score history."""
    import statistics

    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    history = await _repo_score_history_rows(db, repo_id, limit=30)
    if len(history) < 2:
        return {
            "has_forecast": False,
            "reason": "Not enough history — analyse more frequently to enable forecasting.",
            "current_score": int(history[-1].score_total) if history else None,
            "forecast_30d": None,
            "forecast_90d": None,
            "trend": "stable",
        }

    scores = [int(point.score_total or 0) for point in history]
    n = len(scores)
    x_vals = list(range(n))
    x_mean = statistics.mean(x_vals)
    y_mean = statistics.mean(scores)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, scores))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)
    slope = numerator / denominator if denominator != 0 else 0

    total_days = max(1, (history[-1].recorded_at - history[0].recorded_at).days)
    days_per_point = total_days / (n - 1) if n > 1 else 7

    slope_per_day = slope / max(days_per_point, 1)
    current = scores[-1]
    forecast_30 = max(0, min(100, round(current + slope_per_day * 30)))
    forecast_90 = max(0, min(100, round(current + slope_per_day * 90)))
    trend = "improving" if slope_per_day > 0.1 else "declining" if slope_per_day < -0.1 else "stable"

    return {
        "has_forecast": True,
        "current_score": current,
        "forecast_30d": forecast_30,
        "forecast_90d": forecast_90,
        "trend": trend,
        "slope_per_day": round(slope_per_day, 3),
        "data_points": n,
        "reason": None,
    }


@router.get("/{repo_id}/skills/{skill_id}/versions/{version_id}/diff")
async def get_skill_version_diff(
    repo_id: str,
    skill_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Return line-level diff between a skill version and its predecessor."""
    from difflib import unified_diff

    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    version = await db.get(SkillVersion, version_id)
    if version is None or version.skill_id != skill_id:
        raise HTTPException(status_code=404, detail="Skill version not found")

    previous_version = (
        await db.execute(
            select(SkillVersion)
            .where(
                SkillVersion.skill_id == skill_id,
                SkillVersion.version_number < version.version_number,
            )
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()

    old_content = previous_version.content if previous_version else ""
    new_content = version.content or ""
    old_lines = (old_content or "").splitlines(keepends=True)
    new_lines = (new_content or "").splitlines(keepends=True)
    diff = list(
        unified_diff(
            old_lines,
            new_lines,
            fromfile=f"v{previous_version.version_number if previous_version else 0}",
            tofile=f"v{version.version_number}",
            lineterm="",
        )
    )

    lines: list[dict[str, str]] = []
    if previous_version is None:
        for line in (version.content or "").splitlines():
            lines.append({"type": "added", "text": line})
    else:
        for line in diff:
            if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                lines.append({"type": "meta", "text": line})
            elif line.startswith("+"):
                lines.append({"type": "added", "text": line[1:]})
            elif line.startswith("-"):
                lines.append({"type": "removed", "text": line[1:]})
            else:
                lines.append({"type": "context", "text": line[1:] if line.startswith(" ") else line})

    return {
        "skill_id": skill_id,
        "repo_id": repo_id,
        "domain": skill.domain,
        "version_id": version_id,
        "version_number": version.version_number,
        "prev_version_number": previous_version.version_number if previous_version else None,
        "is_first_version": previous_version is None,
        "lines": lines,
        "added_count": sum(1 for line in lines if line["type"] == "added"),
        "removed_count": sum(1 for line in lines if line["type"] == "removed"),
    }


@router.get("/{repo_id}/skill-sources", response_model=RepoSkillSourcesResponse)
async def get_repo_skill_sources(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RepoSkillSourcesResponse:
    """Return source-type and category coverage for a repository."""
    await _repo_in_scope(db, repo_id, current_org_id)
    try:
        skills = await _latest_repo_skills(db, repo_id)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Unable to load skill source coverage", "code": "SKILL_SOURCES_FAILED"},
        ) from exc

    sources: list[RepoSkillSourceSummary] = []
    for source_type in SOURCE_TYPES:
        source_skills = [skill for skill in skills if _normalized_source_type(skill) == source_type]
        if not source_skills and source_type != "code":
            continue
        source_skills.sort(key=lambda skill: (-int(skill.score_total or 0), skill.domain))
        sources.append(
            RepoSkillSourceSummary(
                source_type=source_type,
                detected=bool(source_skills),
                skill_count=len(source_skills),
                last_analysed_at=max((skill.created_at for skill in source_skills), default=None),
                skills=[
                    SkillSourceSkillSummary(id=skill.id, domain=skill.domain, score=int(skill.score_total or 0))
                    for skill in source_skills
                ],
            )
        )
    coverage_map = _build_coverage_map(skills)
    return RepoSkillSourcesResponse(
        sources=sources,
        coverage_map=coverage_map,
        coverage_score=_coverage_score(coverage_map),
    )


@router.get("/{repo_id}/dependencies", response_model=DependencyReportResponse)
async def get_dependencies(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> DependencyReportResponse:
    """Return the latest dependency risk report for a repo in the current org."""
    await _repo_in_scope(db, repo_id, current_org_id)
    try:
        latest_run_result = await db.execute(
            select(AnalysisRun.id)
            .join(Dependency, Dependency.run_id == AnalysisRun.id)
            .where(AnalysisRun.repo_id == repo_id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
        latest_run_id = latest_run_result.scalar_one_or_none()
        if latest_run_id is None:
            return DependencyReportResponse(high_risk=[], medium_risk=[], healthy=[], total_count=0, risk_score=0)

        dependencies = (
            await db.execute(
                select(Dependency)
                .where(Dependency.repo_id == repo_id, Dependency.run_id == latest_run_id)
                .order_by(Dependency.risk_level, Dependency.ecosystem, Dependency.name)
            )
        ).scalars().all()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Unable to load dependency risk report", "code": "DEPENDENCY_REPORT_FAILED"},
        ) from exc

    high_risk = [_dependency_response(item) for item in dependencies if item.risk_level == "high"]
    medium_risk = [_dependency_response(item) for item in dependencies if item.risk_level == "medium"]
    healthy = [_dependency_response(item) for item in dependencies if item.risk_level == "healthy"]
    return DependencyReportResponse(
        high_risk=high_risk,
        medium_risk=medium_risk,
        healthy=healthy,
        total_count=len(dependencies),
        risk_score=_dependency_risk_score(list(dependencies)),
    )


@router.get("/{repo_id}/runs", response_model=list[AnalysisRunResponse])
async def get_runs(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[AnalysisRunResponse]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    runs = (
        await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.repo_id == repo_id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(10)
        )
    ).scalars().all()
    return [
        AnalysisRunResponse(
            id=run.id,
            status=run.status,
            trigger=run.trigger,
            commit_sha=run.commit_sha,
            score=_score_response(run),
            domain_count=run.domain_count,
            skill_count=run.skill_count,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )
        for run in runs
    ]


@router.get("/{repo_id}/prs/{pr_number}/attribution")
async def get_pr_attribution(
    repo_id: str,
    pr_number: int,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    pr = (
        await db.execute(
            select(PullRequest).where(PullRequest.repo_id == repo_id, PullRequest.github_pr_number == pr_number)
        )
    ).scalar_one_or_none()
    if pr is None:
        raise HTTPException(status_code=404, detail="Pull request not found")

    attribution = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id == pr.id))).scalar_one_or_none()
    if attribution is None:
        attribution = await attribute_pr(pr.id, db)
    return _serialize_pr_attribution(attribution)


@router.get("/{repo_id}/prs/{pr_number}/risk")
async def get_pr_risk(
    repo_id: str,
    pr_number: int,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    pr = (
        await db.execute(
            select(PullRequest).where(PullRequest.repo_id == repo_id, PullRequest.github_pr_number == pr_number)
        )
    ).scalar_one_or_none()
    if pr is None:
        raise HTTPException(status_code=404, detail="Pull request not found")

    try:
        return await compute_risk_score(pr.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{repo_id}/commits/{sha}/check")
async def check_commit(
    repo_id: str,
    sha: str,
    body: CommitCheckRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    payload = body or CommitCheckRequest()
    try:
        result = await run_commit_check(
            repo,
            sha,
            db,
            base_sha=payload.base_sha,
            branch=payload.branch,
            diff=payload.diff,
        )
        return result.as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{repo_id}/check")
async def check_repo_diff(
    repo_id: str,
    body: RepoDiffCheckRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    api_key = (
        request.headers.get("x-api-key")
        or request.headers.get("X-API-Key")
        or request.headers.get("api-key")
        or request.headers.get("API-Key")
    )
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    org = (await db.execute(select(Org).where(Org.api_key == api_key))).scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    repo = await _repo_in_scope(db, repo_id, org.id)
    try:
        result = await run_commit_check(repo, "working-tree", db, diff=body.diff)
        return result.as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{repo_id}/analyse")
async def trigger_analysis(
    repo_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    payload: ManualAnalysisRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> dict[str, str]:
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    installation_id = (payload.installation_id if payload else None) or repo.github_installation_id
    if not installation_id:
        raise HTTPException(status_code=400, detail="Repo installation id is not available")
    run = AnalysisRun(
        repo_id=repo_id,
        trigger="manual",
        status="queued",
        branch=repo.default_branch,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    await db.flush()
    await db.commit()
    await _queue_analysis(
        request,
        background_tasks,
        {
            "run_id": run.id,
            "repo_id": repo.id,
            "installation_id": int(installation_id),
            "full_name": repo.full_name,
            "ref": repo.default_branch,
        },
    )
    return {"queued": run.id}


@router.post("/{repo_id}/analyze-source", response_model=AnalyzeSourceResponse)
async def trigger_source_analysis(
    repo_id: str,
    payload: AnalyzeSourceRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> AnalyzeSourceResponse:
    """Queue a source-specific analysis run for a repository."""
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    if not repo.github_installation_id:
        raise HTTPException(
            status_code=400,
            detail={"detail": "Repo installation id is not available", "code": "INSTALLATION_ID_MISSING"},
        )
    run = AnalysisRun(
        repo_id=repo_id,
        trigger=f"source:{payload.source_type}",
        status="queued",
        branch=repo.default_branch,
        created_at=datetime.utcnow(),
    )
    try:
        db.add(run)
        await db.flush()
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Could not queue source analysis", "code": "SOURCE_ANALYSIS_QUEUE_FAILED"},
        ) from exc

    await _queue_analysis(
        request,
        background_tasks,
        {
            "run_id": run.id,
            "repo_id": repo.id,
            "installation_id": int(repo.github_installation_id),
            "full_name": repo.full_name,
            "ref": repo.default_branch,
            "source_type": payload.source_type,
            "source_path": payload.path,
        },
    )
    return AnalyzeSourceResponse(job_id=run.id, status="queued")


@router.post("/{repo_id}/backfill-categories")
async def backfill_skill_categories(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, int]:
    """Re-infer skill_category for all existing skills in a repo without re-running analysis.

    Uses the same domain/path keyword mapping as analysis.py so the categories
    are consistent with future analysis runs.
    """
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != current_org_id:
        raise HTTPException(status_code=404, detail="Repo not found")

    skills_result = await db.execute(select(Skill).where(Skill.repo_id == repo_id))
    skills = skills_result.scalars().all()

    updated = 0
    for skill in skills:
        source_type = str(skill.source_type or "code")
        if source_type != "code":
            new_category = skill_category_for_source_type(source_type)
        else:
            new_category = _skill_category_for_domain(
                str(skill.domain or ""),
                str(skill.skill_path or ""),
            )
        if skill.skill_category != new_category:
            skill.skill_category = new_category
            updated += 1

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to backfill categories") from exc

    return {"updated": updated, "total": len(skills)}


class _LocalUsageEvent(BaseModel):
    skill_path: str
    agent_runtime: str = "unknown"
    session_id: str = ""
    timestamp: str = ""


class _SyncAnalyticsPayload(BaseModel):
    repo_id: str
    events: list[_LocalUsageEvent]


@router.post("/{repo_id}/sync-analytics")
async def sync_repo_analytics(
    repo_id: str,
    payload: _SyncAnalyticsPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, int]:
    """Sync local ``.skilgen/analytics/usage.jsonl`` events to the API database.

    Maps skill paths to DB skill records and increments ``load_count_30d``
    so the dashboard heatmap reflects real agent usage data.
    """
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != current_org_id:
        raise HTTPException(status_code=404, detail="Repo not found")

    skills_result = await db.execute(select(Skill).where(Skill.repo_id == repo_id))
    skills_by_path: dict[str, Skill] = {
        str(skill.skill_path or "").strip("/"): skill
        for skill in skills_result.scalars().all()
    }

    now = datetime.now(UTC).replace(tzinfo=None)
    synced = 0
    skipped = 0

    for event in payload.events:
        normalized = event.skill_path.strip("/").removeprefix(".skilgen/").removeprefix("skilgen/")
        skill = skills_by_path.get(event.skill_path.strip("/")) or skills_by_path.get(normalized)
        if skill is None:
            skipped += 1
            continue

        try:
            loaded_at = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
        except (ValueError, AttributeError):
            loaded_at = now

        skill.load_count_30d = int(skill.load_count_30d or 0) + 1
        if skill.last_loaded_at is None or loaded_at > skill.last_loaded_at:
            skill.last_loaded_at = loaded_at

        db.add(
            SkillUsageEvent(
                org_id=current_org_id,
                repo_id=repo_id,
                skill_id=skill.id,
                agent_runtime=normalize_runtime(event.agent_runtime)[:100],
                session_id=event.session_id[:255] or str(uuid4()),
                loaded_at=loaded_at,
            )
        )
        synced += 1

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to sync analytics") from exc

    return {"synced": synced, "skipped": skipped}


# ---------------------------------------------------------------------------
# GET /{repo_id}/skills/load  — agent skill loader
# Called by Claude Code, Codex, Cursor via the API-Key header.
# Returns all skill content concatenated for the repo, and records a load event.
# ---------------------------------------------------------------------------

@router.get("/{repo_id}/skills/load")
async def load_skills_for_agent(
    repo_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict:
    """
    Primary endpoint called by AI agents (Claude Code, Codex, Cursor).
    Returns all skills for the repo as structured text the agent can read.
    Records a SkillUsageEvent for every skill returned so analytics populate.
    Accepts auth via:
      - Authorization: Bearer sk-...
      - API-Key: sk-...   (header used in CLAUDE.md / AGENTS.md snippets)
    This endpoint MUST never return 500. Skills are always returned if they exist.
    """
    # Resolve org from API-Key header (used in CLAUDE.md / AGENTS.md)
    # Wrapped in try/except so a missing api_key column never crashes the endpoint.
    if not current_org_id:
        try:
            api_key_header = request.headers.get("api-key") or request.headers.get("API-Key")
            if api_key_header:
                from packages.db.models import Org
                org_row = (await db.execute(select(Org).where(Org.api_key == api_key_header))).scalar_one_or_none()
                if org_row:
                    current_org_id = str(org_row.id)
        except Exception:
            pass  # Degrade gracefully — org_id will be inferred from repo below

    # Load repo — 404 if not found, that's intentional
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Load latest skill versions. If version rows are temporarily unavailable,
    # fall back to the current Skill content so connected agents still receive
    # useful guidance instead of an empty "no skills" response.
    try:
        skills_result = await db.execute(
            select(Skill, SkillVersion)
            .join(SkillVersion, Skill.id == SkillVersion.skill_id)
            .where(Skill.repo_id == repo_id, SkillVersion.is_latest.is_(True))
            .order_by(Skill.domain)
        )
        rows: list[tuple[Skill, SkillVersion | None]] = list(skills_result.all())
    except Exception:
        try:
            await db.rollback()
        except Exception:
            pass
        fallback_skills = sorted(await _latest_repo_skills(db, repo_id), key=lambda item: item.domain)
        rows = [(skill, None) for skill in fallback_skills]

    if not rows:
        return {
            "repo": repo.name,
            "skills": [],
            "content": f"# {repo.name} — No skills generated yet\nRun `skilgen deliver --project-root .` to generate skills.",
        }

    # Build agent-readable content
    agent = _detect_agent_runtime(request)
    session_id = request.headers.get("x-session-id") or str(uuid4())
    now = datetime.utcnow()  # naive UTC — required by asyncpg for TIMESTAMP WITHOUT TIME ZONE
    effective_org_id = current_org_id or str(repo.org_id)

    skill_blocks: list[str] = []
    skill_summaries: list[dict] = []

    for skill, version in rows:
        content = (version.content if version is not None else skill.content) or ""
        skill_blocks.append(
            f"## {skill.domain}\n"
            f"Score: {skill.score_total or 0:.0f}/100 | "
            f"Freshness: {skill.score_freshness or 0:.0f}/25\n\n"
            f"{content}\n"
        )
        skill_summaries.append({
            "id": str(skill.id),
            "domain": skill.domain,
            "score": skill.score_total,
            "version": version.version_number if version is not None else None,
            "is_enterprise": bool(getattr(skill, "is_enterprise", False)),
        })

    # Record load events — completely non-fatal, never affects the response
    try:
        for skill, _version in rows:
            skill.load_count_30d = int(skill.load_count_30d or 0) + 1
            skill.last_loaded_at = now
            db.add(SkillUsageEvent(
                org_id=effective_org_id,
                repo_id=repo_id,
                skill_id=str(skill.id),
                agent_runtime=agent,
                session_id=session_id,
                loaded_at=now,
            ))
        await db.commit()
    except Exception:
        try:
            await db.rollback()
        except Exception:
            pass

    full_content = (
        f"# {repo.name} — Skillayer Skills\n"
        f"{len(rows)} skills loaded. Use these as authoritative guidance for this codebase.\n\n"
        + "\n---\n\n".join(skill_blocks)
    )

    return {
        "repo": repo.name,
        "skill_count": len(rows),
        "skills": skill_summaries,
        "content": full_content,
    }


def _detect_agent_runtime(request: Request) -> str:
    """Infer which agent is calling based on headers / user-agent."""
    return detect_runtime_from_headers(request.headers)
