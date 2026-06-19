from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.services.jit_provisioning import ensure_from_login
from packages.db.database import get_db
from packages.db.models import Org, User


router = APIRouter(prefix="/me", tags=["me"])


class ProvisionPayload(BaseModel):
    source: str = Field(default="workos", max_length=32)
    authentication_method: str | None = Field(default=None, max_length=128)
    email: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=255)


@router.post("/provision")
async def provision_me(
    payload: ProvisionPayload,
    request: Request,
    user: dict[str, object] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    email = str(user.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if payload.email and str(payload.email).strip().lower() != email:
        raise HTTPException(status_code=403, detail="Email mismatch")

    source = str(payload.source or "workos").strip().lower()
    if source not in {"workos", "magic_link", "github_oauth"}:
        raise HTTPException(status_code=422, detail="Invalid source")

    prior_user_id = (
        await db.execute(select(User.id).where(User.email == email).limit(1))
    ).scalar_one_or_none()

    org, jit_user, created_org = await ensure_from_login(
        db,
        email=email,
        name=payload.name,
        source=source,  # type: ignore[arg-type]
        request=request,
    )

    workos_org_id = user.get("org_id") or user.get("organization_id")
    if workos_org_id and not org.workos_org_id:
        org.workos_org_id = str(workos_org_id)
        await db.flush()

    await db.commit()
    return {
        "org": {"id": org.id, "login": org.login, "name": org.name, "plan": org.plan},
        "user": {"id": jit_user.id, "email": jit_user.email, "role": jit_user.role, "source": jit_user.source},
        "created": {"org": created_org, "user": prior_user_id is None},
    }


@router.get("/org")
async def get_my_org(
    org_id: str = Depends(get_current_org_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {"id": org.id, "login": org.login, "name": org.name, "plan": org.plan}
