from __future__ import annotations

import os
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.services.standup import send_standup
from packages.db.database import get_db
from packages.db.models import Org


router = APIRouter(prefix="/cron", tags=["cron"])


@router.post("/standup")
async def run_standup_cron(
    db: AsyncSession = Depends(get_db),
    cron_secret: str | None = Header(default=None, alias="CRON_SECRET"),
    x_cron_secret: str | None = Header(default=None, alias="x-cron-secret"),
) -> dict[str, object]:
    expected = os.getenv("CRON_SECRET")
    provided = cron_secret or x_cron_secret
    if expected and provided != expected:
        raise HTTPException(status_code=401, detail="Invalid cron secret")

    current_hour = datetime.utcnow().hour
    orgs = list(
        (
            await db.execute(
                select(Org).where(
                    Org.slack_standup_enabled.is_(True),
                    Org.slack_standup_hour == current_hour,
                )
            )
        )
        .scalars()
        .all()
    )

    sent = 0
    failed: list[str] = []
    today = datetime.utcnow().date().isoformat()
    for org in orgs:
        try:
            await send_standup(str(org.id), today, db)
            sent += 1
        except Exception:
            failed.append(str(org.id))

    return {"ok": True, "matched_orgs": len(orgs), "sent": sent, "failed": failed}
