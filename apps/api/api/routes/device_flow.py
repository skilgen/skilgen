from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import DeviceAuthorization, Org


router = APIRouter(prefix="/v1/device", tags=["device-flow"])

DEVICE_CODE_TTL_MINUTES = 15
DEVICE_POLL_INTERVAL_SECONDS = 5


class DeviceCodeRequest(BaseModel):
    project_root: str | None = Field(default=None, max_length=1024)
    repo_id: str | None = Field(default=None, max_length=128)
    repo_full_name: str | None = Field(default=None, max_length=255)


class DeviceCodeResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    interval: int
    expires_in: int


class DeviceApproveRequest(BaseModel):
    user_code: str = Field(min_length=4, max_length=32)


class DeviceTokenRequest(BaseModel):
    device_code: str = Field(min_length=16, max_length=256)


class DeviceTokenResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "skillayer_api_key"
    org_id: str | None = None
    api_url: str | None = None
    project_root: str | None = None
    repo_id: str | None = None
    repo_full_name: str | None = None
    error: str | None = None
    error_description: str | None = None
    interval: int = DEVICE_POLL_INTERVAL_SECONDS


def _user_code() -> str:
    raw = secrets.token_hex(4).upper()
    return f"{raw[:4]}-{raw[4:]}"


def _verification_base() -> str:
    return "https://app.skillayer.com/device"


@router.post("/code", response_model=DeviceCodeResponse)
async def create_device_code(payload: DeviceCodeRequest, db: AsyncSession = Depends(get_db)) -> DeviceCodeResponse:
    now = datetime.now(UTC)
    authorization = DeviceAuthorization(
        device_code=secrets.token_urlsafe(48),
        user_code=_user_code(),
        project_root=payload.project_root,
        repo_id=payload.repo_id,
        repo_full_name=payload.repo_full_name,
        expires_at=(now + timedelta(minutes=DEVICE_CODE_TTL_MINUTES)).replace(tzinfo=None),
    )
    db.add(authorization)
    await db.commit()
    verification_uri = _verification_base()
    return DeviceCodeResponse(
        device_code=authorization.device_code,
        user_code=authorization.user_code,
        verification_uri=verification_uri,
        verification_uri_complete=f"{verification_uri}?user_code={authorization.user_code}",
        interval=DEVICE_POLL_INTERVAL_SECONDS,
        expires_in=DEVICE_CODE_TTL_MINUTES * 60,
    )


@router.post("/approve")
async def approve_device_code(
    payload: DeviceApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    now = datetime.now(UTC).replace(tzinfo=None)
    authorization = (
        await db.execute(select(DeviceAuthorization).where(DeviceAuthorization.user_code == payload.user_code.upper()))
    ).scalar_one_or_none()
    if authorization is None:
        raise HTTPException(status_code=404, detail="Device code not found")
    if authorization.expires_at < now:
        authorization.status = "expired"
        await db.commit()
        raise HTTPException(status_code=400, detail="Device code expired")
    org = await db.get(Org, current_org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    if not org.api_key:
        org.api_key = f"sk-{secrets.token_urlsafe(32)}"
    authorization.org_id = current_org_id
    authorization.api_key = org.api_key
    authorization.status = "approved"
    authorization.approved_at = now
    await db.commit()
    return {"ok": True, "status": "approved", "org_id": current_org_id}


@router.post("/token", response_model=DeviceTokenResponse)
async def poll_device_token(payload: DeviceTokenRequest, db: AsyncSession = Depends(get_db)) -> DeviceTokenResponse:
    now = datetime.now(UTC).replace(tzinfo=None)
    authorization = (
        await db.execute(select(DeviceAuthorization).where(DeviceAuthorization.device_code == payload.device_code))
    ).scalar_one_or_none()
    if authorization is None:
        return DeviceTokenResponse(error="invalid_request", error_description="Device code not found")
    authorization.last_polled_at = now
    if authorization.expires_at < now:
        authorization.status = "expired"
        await db.commit()
        return DeviceTokenResponse(error="expired_token", error_description="Device code expired")
    if authorization.status != "approved" or not authorization.api_key or not authorization.org_id:
        await db.commit()
        return DeviceTokenResponse(error="authorization_pending", error_description="Waiting for browser approval")
    await db.commit()
    return DeviceTokenResponse(
        access_token=authorization.api_key,
        org_id=authorization.org_id,
        api_url="https://api.skillayer.com",
        project_root=authorization.project_root,
        repo_id=authorization.repo_id,
        repo_full_name=authorization.repo_full_name,
    )
