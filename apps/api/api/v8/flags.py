from __future__ import annotations

import os
from contextvars import ContextVar
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import AsyncSessionLocal, get_db
from packages.db.models import Org


router = APIRouter(prefix="/v8/orgs/{org_id}/flags", tags=["v8-flags"])

_request_cache: ContextVar[dict[str, bool] | None] = ContextVar("ia_v8_request_cache", default=None)


class IAV8FlagResponse(BaseModel):
    IA_V8: bool


def _parse_bool(value: str | None) -> bool | None:
    if value is None or not value.strip():
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return None


def _env_default() -> bool:
    return _parse_bool(os.getenv("IA_V8_DEFAULT")) or False


def _tenant_override(settings: dict[str, Any] | None) -> bool | None:
    if not isinstance(settings, dict):
        return None
    feature_flags = settings.get("feature_flags")
    if not isinstance(feature_flags, dict):
        return None
    value = feature_flags.get("IA_V8")
    return value if isinstance(value, bool) else None


async def _compute_is_v8(org_id: str, db: AsyncSession) -> bool:
    org = await db.get(Org, org_id)
    if org is None:
        return _env_default()
    override = _tenant_override(org.settings if isinstance(org.settings, dict) else None)
    if override is not None:
        return override
    return _env_default()


async def is_v8(org_id: str, db: AsyncSession | None = None) -> bool:
    """Return the effective IA_V8 value for an org.

    Read order: tenant override at orgs.settings.feature_flags.IA_V8,
    then IA_V8_DEFAULT, then false. Results are cached in a request
    ContextVar so repeated checks during one request do not re-query.
    """
    cache = _request_cache.get()
    if cache is None:
        cache = {}
        _request_cache.set(cache)
    if org_id in cache:
        return cache[org_id]

    if db is None:
        async with AsyncSessionLocal() as session:
            value = await _compute_is_v8(org_id, session)
    else:
        value = await _compute_is_v8(org_id, db)

    cache[org_id] = value
    return value


async def request_flag_cache() -> AsyncGenerator[None, None]:
    token = _request_cache.set({})
    try:
        yield
    finally:
        _request_cache.reset(token)


@router.get("/ia-v8", response_model=IAV8FlagResponse, dependencies=[Depends(request_flag_cache)])
async def get_ia_v8_flag(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> IAV8FlagResponse:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    return IAV8FlagResponse(IA_V8=await is_v8(org_id, db))
