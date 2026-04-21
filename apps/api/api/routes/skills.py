from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_user
from apps.api.api.routes.orgs import _score_response
from packages.db.database import get_db
from packages.db.models import Skill
from packages.db.schemas import SkillResponse


router = APIRouter(prefix="/skills", tags=["skills"], dependencies=[Depends(get_current_user)])


class UsagePayload(BaseModel):
    agent_runtime: str
    session_id: str


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_db)) -> SkillResponse:
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse(
        id=skill.id,
        domain=skill.domain,
        skill_path=skill.skill_path,
        score=_score_response(skill),  # type: ignore[arg-type]
        is_stale=skill.is_stale,
        load_count_30d=skill.load_count_30d,
        last_loaded_at=skill.last_loaded_at,
    )


@router.post("/{skill_id}/usage")
async def record_skill_usage(skill_id: str, payload: UsagePayload, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill.load_count_30d += 1
    skill.last_loaded_at = datetime.now(timezone.utc)
    return {"recorded": True}
