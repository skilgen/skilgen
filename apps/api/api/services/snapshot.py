from __future__ import annotations

from datetime import datetime
import hashlib

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import Skill, SkillSnapshot


SCORE_FIELDS = ("score_total", "score_groundedness", "score_coverage", "score_freshness", "score_structure")


def _minute_floor(value: datetime) -> datetime:
    return value.replace(second=0, microsecond=0)


def _snapshot_from_skill(
    skill: Skill,
    *,
    snapshot_type: str,
    label: str | None = None,
    created_by: str | None = None,
) -> SkillSnapshot:
    return SkillSnapshot(
        skill_id=skill.id,
        repo_id=skill.repo_id,
        snapshot_type=snapshot_type,
        label=label,
        content=skill.content or "",
        score_total=skill.score_total,
        score_groundedness=skill.score_groundedness,
        score_coverage=skill.score_coverage,
        score_freshness=skill.score_freshness,
        score_structure=skill.score_structure,
        created_by=created_by,
    )


def snapshot_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def auto_snapshot_skill(
    skill: Skill,
    db: AsyncSession,
    snapshot_type: str = "auto",
    *,
    label: str | None = None,
    created_by: str | None = None,
    idempotent: bool = True,
) -> SkillSnapshot:
    """Capture the current skill state, reusing a same-minute identical snapshot when present."""
    if idempotent:
        now = datetime.utcnow()
        minute_start = _minute_floor(now)
        existing = (
            await db.execute(
                select(SkillSnapshot)
                .where(
                    SkillSnapshot.skill_id == skill.id,
                    SkillSnapshot.snapshot_type == snapshot_type,
                    SkillSnapshot.created_at >= minute_start,
                )
                .order_by(desc(SkillSnapshot.created_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing is not None and existing.content == (skill.content or ""):
            return existing

    snapshot = _snapshot_from_skill(skill, snapshot_type=snapshot_type, label=label, created_by=created_by)
    db.add(snapshot)
    await db.flush()
    return snapshot


async def snapshot_repo_skills(repo_id: str, db: AsyncSession, snapshot_type: str = "auto") -> list[SkillSnapshot]:
    skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
    snapshots: list[SkillSnapshot] = []
    for skill in skills:
        snapshots.append(await auto_snapshot_skill(skill, db, snapshot_type=snapshot_type))
    return snapshots


async def rollback_skill(skill_id: str, snapshot_id: str, db: AsyncSession, actor: str | None = None) -> tuple[Skill, SkillSnapshot]:
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise ValueError("Skill not found")
    snapshot = await db.get(SkillSnapshot, snapshot_id)
    if snapshot is None or snapshot.skill_id != skill_id:
        raise ValueError("Snapshot not found")

    pre_edit = _snapshot_from_skill(
        skill,
        snapshot_type="pre_edit",
        label=f"Before rollback to {snapshot_id}",
        created_by=actor,
    )
    db.add(pre_edit)
    await db.flush()

    skill.content = snapshot.content
    skill.content_hash = snapshot_content_hash(snapshot.content)
    for field in SCORE_FIELDS:
        setattr(skill, field, getattr(snapshot, field))
    skill.updated_at = datetime.utcnow()
    await db.flush()
    return skill, pre_edit
