from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AutopilotTask, Repo, Skill

FRESHNESS_THRESHOLD = 15


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
    tasks = (
        await db.execute(
            select(AutopilotTask)
            .where(AutopilotTask.org_id == org_id)
            .order_by(AutopilotTask.created_at.desc())
        )
    ).scalars().all()
    return list(tasks)
