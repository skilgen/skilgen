from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from packages.db.config import settings
from packages.db.database import AsyncSessionLocal


router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    db_status = "ok"
    if not settings.DATABASE_URL:
        db_status = "error"
    else:
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("select 1"))
        except Exception:
            db_status = "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": "1.0.0",
        "deployment_mode": settings.DEPLOYMENT_MODE,
        "db": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
