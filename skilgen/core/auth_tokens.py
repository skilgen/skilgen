from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from pathlib import Path
from typing import Any


class SignedTokenError(ValueError):
    pass


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(value + padding)
    except (ValueError, TypeError) as exc:
        raise SignedTokenError("invalid token encoding") from exc


def _normalize_timestamp(raw_value: float | int | None, *, default: float | None = None) -> int:
    if raw_value is None:
        if default is None:
            raise SignedTokenError("missing required timestamp")
        raw_value = default
    return int(raw_value)


def mint_signed_token(
    signing_key: str,
    *,
    principal: str,
    scope: str,
    ttl_seconds: float = 900,
    expires_at: float | int | None = None,
    issued_at: float | int | None = None,
    not_before: float | int | None = None,
    allowed_project_roots: list[str | Path] | None = None,
    tenant: str | None = None,
    issuer: str | None = None,
    audience: str | list[str] | None = None,
    allow_insecure_transport: bool = False,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    issued_at_value = _normalize_timestamp(issued_at, default=time.time())
    expires_at_value = _normalize_timestamp(expires_at, default=issued_at_value + ttl_seconds)
    payload: dict[str, Any] = {
        "sub": principal,
        "scope": scope,
        "iat": issued_at_value,
        "exp": expires_at_value,
    }
    if not_before is not None:
        payload["nbf"] = _normalize_timestamp(not_before)
    if allowed_project_roots:
        payload["roots"] = [str(Path(item).resolve()) for item in allowed_project_roots]
    if tenant:
        payload["tenant"] = tenant
    if issuer:
        payload["iss"] = issuer
    if audience:
        payload["aud"] = audience
    if allow_insecure_transport:
        payload["allow_insecure_transport"] = True
    if extra_claims:
        payload.update(extra_claims)
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(signing_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def verify_signed_token(
    token: str,
    signing_key: str,
    *,
    issuer: str | None = None,
    audience: str | None = None,
    leeway_seconds: float = 0,
) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise SignedTokenError("invalid token structure")
    encoded_header, encoded_payload, encoded_signature = parts
    try:
        header = json.loads(_base64url_decode(encoded_header).decode("utf-8"))
        payload = json.loads(_base64url_decode(encoded_payload).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SignedTokenError("invalid token payload") from exc
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise SignedTokenError("invalid token content")
    if header.get("alg") != "HS256":
        raise SignedTokenError("unsupported token algorithm")
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    expected_signature = hmac.new(signing_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual_signature = _base64url_decode(encoded_signature)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise SignedTokenError("invalid token signature")

    now = time.time()
    leeway = max(0.0, float(leeway_seconds))
    try:
        expires_at = float(payload["exp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SignedTokenError("invalid token expiry") from exc
    if now > expires_at + leeway:
        raise SignedTokenError("token expired")
    if "nbf" in payload:
        try:
            not_before = float(payload["nbf"])
        except (TypeError, ValueError) as exc:
            raise SignedTokenError("invalid token not-before") from exc
        if now + leeway < not_before:
            raise SignedTokenError("token not yet valid")
    if issuer is not None and payload.get("iss") != issuer:
        raise SignedTokenError("token issuer mismatch")
    if audience is not None:
        raw_audience = payload.get("aud")
        if isinstance(raw_audience, str):
            audiences = [raw_audience]
        elif isinstance(raw_audience, list):
            audiences = [str(item) for item in raw_audience]
        else:
            audiences = []
        if audience not in audiences:
            raise SignedTokenError("token audience mismatch")
    if not isinstance(payload.get("sub"), str) or not payload["sub"].strip():
        raise SignedTokenError("missing token principal")
    if not isinstance(payload.get("scope"), str) or not payload["scope"].strip():
        raise SignedTokenError("missing token scope")
    return payload
