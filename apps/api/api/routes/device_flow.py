from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, optional_bearer
from apps.api.api.services.jit_provisioning import ensure_from_login
from packages.db.config import settings
from packages.db.database import get_db
from packages.db.models import DeviceAuthorization, Org


router = APIRouter(prefix="/v1/device", tags=["device-flow"])

DEVICE_CODE_TTL_MINUTES = 15
DEVICE_POLL_INTERVAL_SECONDS = 5
DEVICE_CODE_IP_LIMIT = 10
DEVICE_CODE_RATE_LIMIT_MINUTES = 5


class DeviceCodeRequest(BaseModel):
    project_root: str | None = Field(default=None, max_length=1024)
    repo_id: str | None = Field(default=None, max_length=128)
    repo_full_name: str | None = Field(default=None, max_length=255)
    machine_id: str | None = Field(default=None, max_length=128)
    machine_label: str | None = Field(default=None, max_length=255)


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
    token_type: str = "skillayer_device_key"
    org_id: str | None = None
    api_url: str | None = None
    project_root: str | None = None
    repo_id: str | None = None
    repo_full_name: str | None = None
    machine_id: str | None = None
    machine_label: str | None = None
    error: str | None = None
    error_description: str | None = None
    interval: int = DEVICE_POLL_INTERVAL_SECONDS


class DeviceAuthorizationRecord(BaseModel):
    id: str
    machine_id: str | None = None
    machine_label: str | None = None
    repo_full_name: str | None = None
    project_root: str | None = None
    status: str
    api_key_hint: str | None = None
    client_ip: str | None = None
    approved_at: str | None = None
    last_polled_at: str | None = None
    revoked_at: str | None = None


def _user_code() -> str:
    raw = secrets.token_hex(4).upper()
    return f"{raw[:4]}-{raw[4:]}"


def _verification_base() -> str:
    return "https://app.skillayer.com/device"


def _generate_device_api_key() -> str:
    return f"sk-device-{secrets.token_urlsafe(32)}"


def _api_key_hint(value: str | None) -> str | None:
    if not value:
        return None
    return f"...{value[-4:]}" if len(value) >= 4 else "****"


def _timestamp(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _authorization_record(authorization: DeviceAuthorization) -> DeviceAuthorizationRecord:
    return DeviceAuthorizationRecord(
        id=str(authorization.id),
        machine_id=authorization.machine_id,
        machine_label=authorization.machine_label,
        repo_full_name=authorization.repo_full_name,
        project_root=authorization.project_root,
        status=authorization.status,
        api_key_hint=_api_key_hint(authorization.api_key),
        client_ip=authorization.client_ip,
        approved_at=_timestamp(authorization.approved_at),
        last_polled_at=_timestamp(authorization.last_polled_at),
        revoked_at=_timestamp(authorization.revoked_at),
    )


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if forwarded_for:
        return forwarded_for[:64]
    if request.client and request.client.host:
        return request.client.host[:64]
    return "unknown"


async def _enforce_device_code_rate_limit(db: AsyncSession, *, client_ip: str, now: datetime) -> None:
    cutoff = (now - timedelta(minutes=DEVICE_CODE_RATE_LIMIT_MINUTES)).replace(tzinfo=None)
    active = (
        (
            await db.execute(
                select(DeviceAuthorization).where(
                    DeviceAuthorization.client_ip == client_ip,
                    DeviceAuthorization.status == "pending",
                    DeviceAuthorization.created_at >= cutoff,
                    DeviceAuthorization.expires_at > now.replace(tzinfo=None),
                )
            )
        )
        .scalars()
        .all()
    )
    if len(active) >= DEVICE_CODE_IP_LIMIT:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "slow_down",
                "error_description": "Too many pending device authorizations from this network. Try again in a few minutes.",
            },
        )


def _admin_secret_valid(value: str) -> bool:
    secret = os.getenv("ADMIN_SECRET", "") or settings.ADMIN_SECRET
    return bool(secret and value and hmac.compare_digest(value, secret))


async def _approval_org_id(
    *,
    db: AsyncSession,
    credentials: HTTPAuthorizationCredentials | None,
    x_admin_secret: str,
    x_skillayer_actor_email: str,
) -> str:
    if _admin_secret_valid(x_admin_secret):
        email = x_skillayer_actor_email.strip().lower()
        if not email:
            raise HTTPException(status_code=401, detail="Missing actor email")
        org, _, _ = await ensure_from_login(db, email=email, name=None, source="workos")
        await db.flush()
        return org.id
    return await get_current_org_id(credentials, db)


@router.post("/code", response_model=DeviceCodeResponse)
async def create_device_code(
    payload: DeviceCodeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> DeviceCodeResponse:
    now = datetime.now(UTC)
    client_ip = _client_ip(request)
    await _enforce_device_code_rate_limit(db, client_ip=client_ip, now=now)
    authorization = DeviceAuthorization(
        device_code=secrets.token_urlsafe(48),
        user_code=_user_code(),
        project_root=payload.project_root,
        repo_id=payload.repo_id,
        repo_full_name=payload.repo_full_name,
        machine_id=payload.machine_id,
        machine_label=payload.machine_label,
        client_ip=client_ip,
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
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
    x_admin_secret: str = Header(default=""),
    x_skillayer_actor_email: str = Header(default=""),
) -> dict[str, object]:
    now = datetime.now(UTC).replace(tzinfo=None)
    current_org_id = await _approval_org_id(
        db=db,
        credentials=credentials,
        x_admin_secret=x_admin_secret,
        x_skillayer_actor_email=x_skillayer_actor_email,
    )
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
    authorization.org_id = current_org_id
    authorization.api_key = authorization.api_key or _generate_device_api_key()
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
    if authorization.revoked_at is not None:
        await db.commit()
        return DeviceTokenResponse(error="access_denied", error_description="Device authorization was revoked")
    await db.commit()
    return DeviceTokenResponse(
        access_token=authorization.api_key,
        org_id=authorization.org_id,
        api_url="https://api.skillayer.com",
        project_root=authorization.project_root,
        repo_id=authorization.repo_id,
        repo_full_name=authorization.repo_full_name,
        machine_id=authorization.machine_id,
        machine_label=authorization.machine_label,
    )


@router.get("/authorizations", response_model=list[DeviceAuthorizationRecord])
async def list_device_authorizations(
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[DeviceAuthorizationRecord]:
    rows = (
        (
            await db.execute(
                select(DeviceAuthorization).where(
                    DeviceAuthorization.org_id == current_org_id,
                    DeviceAuthorization.status.in_(("approved", "revoked")),
                )
            )
        )
        .scalars()
        .all()
    )
    rows.sort(key=lambda item: (item.revoked_at is not None, item.machine_label or "", item.approved_at or datetime.min), reverse=False)
    return [_authorization_record(row) for row in rows]


@router.post("/authorizations/{authorization_id}/revoke", response_model=DeviceAuthorizationRecord)
async def revoke_device_authorization(
    authorization_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> DeviceAuthorizationRecord:
    authorization = (
        await db.execute(
            select(DeviceAuthorization).where(
                DeviceAuthorization.id == authorization_id,
                DeviceAuthorization.org_id == current_org_id,
            )
        )
    ).scalar_one_or_none()
    if authorization is None:
        raise HTTPException(status_code=404, detail="Device authorization not found")
    now = datetime.now(UTC).replace(tzinfo=None)
    authorization.revoked_at = authorization.revoked_at or now
    authorization.status = "revoked"
    await db.commit()
    return _authorization_record(authorization)
