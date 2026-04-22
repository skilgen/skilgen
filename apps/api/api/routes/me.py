from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import Org


router = APIRouter(prefix="/me", tags=["me"])


@router.get("/org")
async def get_my_org(
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {"id": org.id, "login": org.login, "name": org.name, "plan": org.plan}
