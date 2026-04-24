from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.database import get_db
from packages.db.config import settings
from packages.db.models import Org


bearer_scheme = HTTPBearer(auto_error=True)
_JWKS_CACHE: dict[str, dict[str, Any]] = {}
_JWKS_TTL_SECONDS = 3600


def _deployment_mode() -> str:
    return settings.DEPLOYMENT_MODE.strip().lower()


def _oidc_issuer() -> str:
    issuer = settings.OIDC_ISSUER_URL.strip().rstrip("/")
    if not issuer:
        raise HTTPException(status_code=500, detail="OIDC_ISSUER_URL is not configured")
    return issuer


def _oidc_audience() -> str:
    audience = settings.OIDC_AUDIENCE.strip()
    if not audience:
        raise HTTPException(status_code=500, detail="OIDC_AUDIENCE is not configured")
    return audience


def _oidc_jwks_uri() -> str:
    if settings.OIDC_JWKS_URI.strip():
        return settings.OIDC_JWKS_URI.strip()
    return f"{_oidc_issuer()}/.well-known/jwks.json"


async def _fetch_jwks(url: str) -> list[dict[str, Any]]:
    now = time.time()
    cached = _JWKS_CACHE.get(url)
    if cached is not None and now < float(cached["expires_at"]):
        return list(cached["keys"])
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(url)
    response.raise_for_status()
    keys = response.json().get("keys", [])
    _JWKS_CACHE[url] = {"expires_at": now + _JWKS_TTL_SECONDS, "keys": keys}
    return list(keys)


async def _workos_jwks() -> list[dict[str, Any]]:
    if not settings.WORKOS_CLIENT_ID:
        raise HTTPException(status_code=500, detail="WORKOS_CLIENT_ID is not configured")
    return await _fetch_jwks(f"https://api.workos.com/sso/jwks/{settings.WORKOS_CLIENT_ID}")


async def _oidc_jwks() -> list[dict[str, Any]]:
    return await _fetch_jwks(_oidc_jwks_uri())


def _signing_key(keys: list[dict[str, Any]], kid: str | None) -> dict[str, Any]:
    signing_key = next((key for key in keys if key.get("kid") == kid), None)
    if signing_key is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return signing_key


def _verify_signature(token: str, signing_key: dict[str, Any]) -> None:
    public_key = jwk.construct(signing_key)
    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise HTTPException(status_code=401, detail="Invalid token")


async def _verify_workos_token(token: str) -> dict[str, Any]:
    header = jwt.get_unverified_header(token)
    signing_key = _signing_key(await _workos_jwks(), header.get("kid"))
    _verify_signature(token, signing_key)
    payload = jwt.decode(
        token,
        signing_key,
        algorithms=[header.get("alg", "RS256")],
        audience=settings.WORKOS_CLIENT_ID,
        issuer="https://api.workos.com/",
    )
    return dict(payload)


async def _verify_oidc_token(token: str) -> dict[str, Any]:
    header = jwt.get_unverified_header(token)
    signing_key = _signing_key(await _oidc_jwks(), header.get("kid"))
    _verify_signature(token, signing_key)
    payload = jwt.decode(
        token,
        signing_key,
        algorithms=[header.get("alg", "RS256")],
        audience=_oidc_audience(),
        issuer=_oidc_issuer(),
    )
    return dict(payload)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict[str, Any]:
    if _deployment_mode() == "bootstrap":
        return {
            "email": "bootstrap@skillayer.com",
            "sub": "bootstrap",
            "org_id": None,
        }
    token = credentials.credentials
    try:
        if _deployment_mode() == "selfhosted":
            return await _verify_oidc_token(token)
        return await _verify_workos_token(token)
    except HTTPException:
        raise
    except (JWTError, ValueError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


async def get_current_org_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> str:
    user = await get_current_user(credentials)
    workos_org_id = user.get("org_id") or user.get("organization_id")

    if workos_org_id:
        result = await db.execute(select(Org).where(Org.workos_org_id == str(workos_org_id)))
        org = result.scalar_one_or_none()
        if org is not None:
            return org.id

    # Temporary bootstrap fallback until WorkOS organization membership is fully mapped.
    email = str(user.get("email", ""))
    result = await db.execute(select(Org).limit(1))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=403, detail="No org found")
    return org.id
