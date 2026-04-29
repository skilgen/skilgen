from __future__ import annotations

from collections.abc import Sequence
import hashlib
from datetime import datetime
from uuid import uuid4

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.services.github_pr import create_skill_pr
from apps.api.api.services.skill_generator import generate_skill_with_ai
from packages.db.models import AutopilotTask, Org, Repo, Skill, SkillVersion

FRESHNESS_THRESHOLD = 15


def _task_key(task: AutopilotTask) -> tuple[str, str | None, str]:
    return (task.repo_id, task.skill_id, task.task_type)


async def deduplicate_pending_autopilot_tasks(db: AsyncSession, org_id: str) -> int:
    """Resolve older pending tasks that point at the same repo, skill, and action."""
    pending_tasks = (
        await db.execute(
            select(AutopilotTask)
            .where(
                AutopilotTask.org_id == org_id,
                AutopilotTask.status == "pending",
            )
            .order_by(AutopilotTask.created_at.desc())
        )
    ).scalars().all()

    seen: set[tuple[str, str | None, str]] = set()
    deduped = 0
    now = datetime.utcnow()
    for task in pending_tasks:
        key = _task_key(task)
        if key not in seen:
            seen.add(key)
            continue
        task.status = "skipped"
        task.resolved_at = now
        deduped += 1

    if deduped:
        await db.flush()
    return deduped


async def compute_autopilot_queue(
    db: AsyncSession,
    org_id: str,
    repos: Sequence[Repo],
    skills: Sequence[Skill],
) -> list[AutopilotTask]:
    """Create or reuse pending regeneration tasks for stale skills."""
    repo_ids = {repo.id for repo in repos}
    stale_skills = [skill for skill in skills if skill.repo_id in repo_ids and int(skill.score_freshness or 0) < FRESHNESS_THRESHOLD]

    for skill in stale_skills:
        score = int(skill.score_freshness or 0)
        existing = (
            await db.execute(
                select(AutopilotTask).where(
                    AutopilotTask.org_id == org_id,
                    AutopilotTask.repo_id == skill.repo_id,
                    AutopilotTask.skill_id == skill.id,
                    AutopilotTask.task_type == "regenerate",
                    AutopilotTask.status == "pending",
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue
        db.add(
            AutopilotTask(
                org_id=org_id,
                repo_id=skill.repo_id,
                skill_id=skill.id,
                task_type="regenerate",
                trigger_reason=f"Freshness {score}/25 — below 60% threshold",
                freshness_at_trigger=score,
                status="pending",
                created_at=datetime.utcnow(),
            )
        )

    await db.flush()
    await deduplicate_pending_autopilot_tasks(db, org_id)
    tasks = (
        await db.execute(
            select(AutopilotTask)
            .where(AutopilotTask.org_id == org_id)
            .order_by(AutopilotTask.created_at.desc())
        )
    ).scalars().all()
    return list(tasks)


def _score_generated_skill(content: str) -> dict[str, int]:
    word_count = len(content.split())
    has_headings = "## " in content
    has_anti_patterns = "anti-pattern" in content.lower()
    has_file_refs = "/" in content or "`" in content
    groundedness = min(25, 8 + (8 if has_file_refs else 0) + min(9, word_count // 40))
    coverage = min(25, 8 + (8 if has_headings else 0) + min(9, word_count // 35))
    freshness = min(25, 16 + (5 if has_file_refs else 0) + (4 if "last verified" in content.lower() else 0))
    structure = min(25, 10 + (8 if has_headings else 0) + (7 if has_anti_patterns else 0))
    return {
        "groundedness": groundedness,
        "coverage": coverage,
        "freshness": freshness,
        "structure": structure,
        "total": groundedness + coverage + freshness + structure,
    }


async def latest_skill_content(db: AsyncSession, skill: Skill) -> str:
    version = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()
    return str(version.content if version is not None else skill.content or "")


async def generate_autopilot_improvement(db: AsyncSession, task: AutopilotTask, org: Org, repo: Repo, skill: Skill) -> AutopilotTask:
    original_content = await latest_skill_content(db, skill)
    try:
        draft = await generate_skill_with_ai(
            org.settings if isinstance(org.settings, dict) else {},
            domain=skill.domain,
            repo_name=repo.full_name or repo.name,
            context_files=[skill.skill_path],
            enterprise_skills=[],
            user_intent=f"Refresh existing skill because Autopilot found: {task.trigger_reason}\n\nExisting content:\n{original_content[:6000]}",
        )
        task.original_content = original_content
        task.generated_content = str(draft.get("content") or "")
        task.improvement_status = "generated"
        task.generation_error = None
        task.generated_at = datetime.utcnow()
        await db.flush()
        return task
    except Exception as exc:
        task.original_content = original_content
        task.improvement_status = "failed"
        task.generation_error = str(exc)
        task.generated_at = datetime.utcnow()
        await db.flush()
        raise


async def apply_autopilot_improvement(
    db: AsyncSession,
    task: AutopilotTask,
    repo: Repo,
    skill: Skill,
    final_content: str,
    *,
    create_pr: bool = False,
) -> AutopilotTask:
    now = datetime.utcnow()
    content_hash = hashlib.sha256(final_content.encode()).hexdigest()
    latest_version_number = (
        await db.execute(
            select(func.max(SkillVersion.version_number)).where(SkillVersion.skill_id == skill.id)
        )
    ).scalar_one_or_none()

    await db.execute(
        update(SkillVersion)
        .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
        .values(is_latest=False)
    )
    score = _score_generated_skill(final_content)
    skill.content = final_content
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
            repo_id=repo.id,
            domain=skill.domain,
            content=final_content,
            content_hash=content_hash,
            version_number=int(latest_version_number or 0) + 1,
            is_latest=True,
            created_at=now,
        )
    )

    if create_pr:
        branch_slug = "".join(char.lower() if char.isalnum() else "-" for char in skill.domain).strip("-") or "skill"
        pr = await create_skill_pr(
            repo,
            skill.skill_path,
            final_content,
            f"skillayer/autopilot-{branch_slug}-{task.id[:8]}",
            f"Refresh Skillayer skill: {skill.domain}",
            f"Autopilot generated an improvement for `{skill.skill_path}`.\n\nReason: {task.trigger_reason}",
        )
        task.pr_url = str(pr.get("pr_url") or "")
        task.pr_number = int(pr.get("pr_number") or 0)

    task.final_content = final_content
    task.status = "approved"
    task.improvement_status = "approved"
    task.reviewed_at = now
    task.resolved_at = now
    if hasattr(db, "flush"):
        await db.flush()
    return task


async def reject_autopilot_improvement(db: AsyncSession, task: AutopilotTask, reason: str | None = None) -> AutopilotTask:
    now = datetime.utcnow()
    task.status = "rejected"
    task.improvement_status = "rejected"
    task.generation_error = reason or task.generation_error
    task.reviewed_at = now
    task.resolved_at = now
    if hasattr(db, "flush"):
        await db.flush()
    return task
