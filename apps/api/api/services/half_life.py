from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import Repo, Skill, SkillHalfLife, SkillVersion


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


async def get_commit_velocity(skill_id: str, db: AsyncSession) -> dict[str, int]:
    now = _now()
    cut_30 = now - timedelta(days=30)
    cut_60 = now - timedelta(days=60)
    cut_90 = now - timedelta(days=90)
    versions = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == str(skill_id), SkillVersion.created_at >= cut_90)
            .order_by(desc(SkillVersion.created_at))
        )
    ).scalars().all()
    commits_30d = sum(1 for version in versions if version.created_at >= cut_30)
    commits_60d = sum(1 for version in versions if version.created_at >= cut_60)
    commits_90d = len(versions)
    recent = [version for version in versions if version.created_at >= cut_30]
    churn = 0
    for previous, current in zip(recent[1:], recent):
        churn += abs(len(current.content or "") - len(previous.content or ""))
    return {
        "commits_30d": commits_30d,
        "commits_60d": commits_60d,
        "commits_90d": commits_90d,
        "file_churn_30d": churn,
    }


async def compute_half_life(skill_id: str, db: AsyncSession) -> SkillHalfLife:
    skill = await db.get(Skill, str(skill_id))
    if skill is None:
        raise ValueError(f"Skill not found: {skill_id}")
    repo = await db.get(Repo, skill.repo_id)
    if repo is None:
        raise ValueError(f"Repo not found for skill: {skill_id}")
    velocity = await get_commit_velocity(skill.id, db)
    daily_commit_rate = velocity["commits_30d"] / 30
    freshness = float(skill.score_freshness or 0)
    if freshness < 20:
        days_to_stale = 0.0
    elif daily_commit_rate > 2.0:
        days_to_stale = (freshness - 20) / 5
    elif daily_commit_rate > 0.5:
        days_to_stale = (freshness - 20) / 2
    else:
        days_to_stale = (freshness - 20) / 0.5
    days_to_stale = max(0.0 if freshness < 20 else 1.0, min(90.0, days_to_stale))
    version_count = int(
        (await db.execute(select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id))).scalar() or 0
    )
    confidence = 0.9 if version_count >= 5 else 0.6 if version_count >= 2 else 0.3
    now = _now()
    existing = (
        await db.execute(select(SkillHalfLife).where(SkillHalfLife.skill_id == skill.id))
    ).scalar_one_or_none()
    row = existing or SkillHalfLife(skill_id=skill.id, org_id=repo.org_id, repo_id=repo.id)
    row.org_id = repo.org_id
    row.repo_id = repo.id
    row.commits_30d = velocity["commits_30d"]
    row.commits_60d = velocity["commits_60d"]
    row.commits_90d = velocity["commits_90d"]
    row.file_churn_30d = velocity["file_churn_30d"]
    row.predicted_decay_days = days_to_stale
    row.predicted_decay_date = now + timedelta(days=days_to_stale) if days_to_stale > 0 else now
    row.decay_confidence = confidence
    row.computed_at = now
    row.updated_at = now
    if existing is None:
        db.add(row)
    await db.flush()
    return row


async def check_and_queue_regenerations(org_id: str, db: AsyncSession) -> list[dict[str, object]]:
    now = _now()
    rows = (
        await db.execute(
            select(SkillHalfLife, Skill, Repo)
            .join(Skill, Skill.id == SkillHalfLife.skill_id)
            .join(Repo, Repo.id == SkillHalfLife.repo_id)
            .where(
                SkillHalfLife.org_id == str(org_id),
                SkillHalfLife.regen_queued.is_(False),
                Skill.score_freshness > 20,
            )
        )
    ).all()
    queued: list[dict[str, object]] = []
    for half_life, skill, repo in rows:
        threshold = now + timedelta(hours=int(half_life.regeneration_buffer_hours or 24))
        if half_life.predicted_decay_date and half_life.predicted_decay_date <= threshold:
            half_life.regen_queued = True
            half_life.regen_queued_at = now
            queued.append({
                "skill_id": skill.id,
                "skill_name": skill.domain,
                "predicted_decay_date": half_life.predicted_decay_date,
                "repo_id": repo.id,
            })
    await db.flush()
    return queued


async def calibrate_predictions(org_id: str, db: AsyncSession) -> int:
    rows = (
        await db.execute(
            select(SkillHalfLife).where(
                SkillHalfLife.org_id == str(org_id),
                SkillHalfLife.last_actual_decay_date.is_not(None),
                SkillHalfLife.prediction_error_days.is_(None),
            )
        )
    ).scalars().all()
    count = 0
    for row in rows:
        if row.predicted_decay_date and row.last_actual_decay_date:
            row.prediction_error_days = abs((row.predicted_decay_date - row.last_actual_decay_date).days)
            row.updated_at = _now()
            count += 1
    await db.flush()
    return count
