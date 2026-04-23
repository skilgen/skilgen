from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.config import settings
from packages.db.database import get_db
from packages.db.models import Skill


router = APIRouter(prefix="/admin", tags=["admin"])


def _error(status_code: int, detail: str, code: str) -> JSONResponse:
    """Build the structured error response used by admin endpoints."""
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})


@router.post("/rollup-usage", response_model=None)
async def rollup_usage(
    x_admin_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object] | JSONResponse:
    """Reset stale 30-day usage counters for skills not loaded in the current window."""
    if not settings.ADMIN_SECRET:
        return _error(503, "ADMIN_SECRET is not configured", "ADMIN_SECRET_MISSING")
    if x_admin_secret != settings.ADMIN_SECRET:
        return _error(401, "Invalid admin secret", "ADMIN_SECRET_INVALID")

    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=30)
    try:
        result = await db.execute(
            update(Skill)
            .where(Skill.load_count_30d > 0, Skill.last_loaded_at.is_not(None), Skill.last_loaded_at < cutoff)
            .values(load_count_30d=0)
        )
        await db.flush()
    except SQLAlchemyError:
        await db.rollback()
        return _error(400, "Unable to roll up usage counters", "ROLLUP_FAILED")
    return {"rolled_up": True, "reset_count": int(result.rowcount or 0)}
