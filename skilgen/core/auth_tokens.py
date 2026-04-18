from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import socket
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class SignedTokenError(ValueError):
    pass


_REMOTE_CACHE_LOCK = threading.Lock()
_REMOTE_JSON_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding_bytes = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(value + padding_bytes)
    except (ValueError, TypeError) as exc:
        raise SignedTokenError("invalid token encoding") from exc


def _normalize_timestamp(raw_value: float | int | None, *, default: float | None = None) -> int:
    if raw_value is None:
        if default is None:
            raise SignedTokenError("missing required timestamp")
        raw_value = default
    return int(raw_value)


def _parse_token(token: str) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
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
    return header, payload, _base64url_decode(encoded_signature), f"{encoded_header}.{encoded_payload}".encode("ascii")


def _audiences(payload: dict[str, Any]) -> list[str]:
    raw_audience = payload.get("aud")
    if isinstance(raw_audience, str):
        return [raw_audience]
    if isinstance(raw_audience, list):
        return [str(item) for item in raw_audience]
    return []


def _validate_registered_claims(
    payload: dict[str, Any],
    *,
    issuer: str | None = None,
    audience: str | None = None,
    leeway_seconds: float = 0,
) -> None:
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
    if "iat" in payload:
        try:
            issued_at = float(payload["iat"])
        except (TypeError, ValueError) as exc:
            raise SignedTokenError("invalid token issued-at") from exc
        if issued_at > now + leeway:
            raise SignedTokenError("token issued-at is in the future")
    if issuer is not None and payload.get("iss") != issuer:
        raise SignedTokenError("token issuer mismatch")
    if audience is not None and audience not in _audiences(payload):
        raise SignedTokenError("token audience mismatch")
    if not isinstance(payload.get("sub"), str) or not payload["sub"].strip():
        raise SignedTokenError("missing token principal")


def _assert_scope_claim(payload: dict[str, Any]) -> None:
    scope = payload.get("scope")
    if isinstance(scope, str) and scope.strip():
        return
    scp = payload.get("scp")
    if isinstance(scp, str) and scp.strip():
        return
    if isinstance(scp, list) and any(str(item).strip() for item in scp):
        return
    raise SignedTokenError("missing token scope")


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
    header, payload, actual_signature, signing_input = _parse_token(token)
    if header.get("alg") != "HS256":
        raise SignedTokenError("unsupported token algorithm")
    expected_signature = hmac.new(signing_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise SignedTokenError("invalid token signature")
    _validate_registered_claims(payload, issuer=issuer, audience=audience, leeway_seconds=leeway_seconds)
    _assert_scope_claim(payload)
    return payload


def _base64url_to_int(value: str) -> int:
    return int.from_bytes(_base64url_decode(value), "big")


def _rsa_public_key_from_jwk(jwk: dict[str, Any]) -> rsa.RSAPublicKey:
    try:
        modulus = _base64url_to_int(str(jwk["n"]))
        exponent = _base64url_to_int(str(jwk["e"]))
    except (KeyError, ValueError, TypeError) as exc:
        raise SignedTokenError("invalid jwk parameters") from exc
    return rsa.RSAPublicNumbers(exponent, modulus).public_key()


def _matching_jwk(header: dict[str, Any], jwks: dict[str, Any]) -> dict[str, Any]:
    keys = jwks.get("keys")
    if not isinstance(keys, list):
        raise SignedTokenError("invalid jwks document")
    algorithm = str(header.get("alg", "")).strip()
    key_id = str(header.get("kid", "")).strip()
    matches: list[dict[str, Any]] = []
    for item in keys:
        if not isinstance(item, dict) or item.get("kty") != "RSA":
            continue
        if item.get("use") not in {None, "sig"}:
            continue
        if item.get("alg") not in {None, algorithm}:
            continue
        if key_id and str(item.get("kid", "")).strip() != key_id:
            continue
        matches.append(item)
    if not matches:
        raise SignedTokenError("no matching jwk for token")
    if len(matches) > 1 and not key_id:
        raise SignedTokenError("token missing key id")
    return matches[0]


def verify_jwks_token(
    token: str,
    jwks: dict[str, Any],
    *,
    issuer: str | None = None,
    audience: str | None = None,
    leeway_seconds: float = 0,
) -> dict[str, Any]:
    header, payload, signature, signing_input = _parse_token(token)
    if header.get("alg") != "RS256":
        raise SignedTokenError("unsupported token algorithm")
    public_key = _rsa_public_key_from_jwk(_matching_jwk(header, jwks))
    try:
        public_key.verify(signature, signing_input, padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature as exc:
        raise SignedTokenError("invalid token signature") from exc
    _validate_registered_claims(payload, issuer=issuer, audience=audience, leeway_seconds=leeway_seconds)
    _assert_scope_claim(payload)
    return payload


def _is_loopback_host(hostname: str) -> bool:
    normalized = hostname.strip().lower().rstrip(".")
    if normalized in {"localhost"}:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        try:
            addresses = socket.getaddrinfo(normalized, None)
        except socket.gaierror:
            return False
        resolved = []
        for item in addresses:
            raw_address = item[4][0].split("%", 1)[0]
            try:
                resolved.append(ipaddress.ip_address(raw_address))
            except ValueError:
                continue
        return bool(resolved) and all(address.is_loopback for address in resolved)


def _assert_secure_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return
    if parsed.scheme != "http":
        raise SignedTokenError("OIDC endpoints must use http or https")
    if not parsed.hostname or not _is_loopback_host(parsed.hostname):
        raise SignedTokenError("OIDC endpoints must use https unless the host is loopback")


def _load_remote_json(url: str, *, timeout_seconds: float, cache_ttl_seconds: float) -> dict[str, Any]:
    _assert_secure_url(url)
    now = time.monotonic()
    if cache_ttl_seconds > 0:
        with _REMOTE_CACHE_LOCK:
            cached = _REMOTE_JSON_CACHE.get(url)
            if cached is not None and cached[0] > now:
                return dict(cached[1])
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "skilgen-auth/1.0"})
    try:
        with urlopen(request, timeout=max(0.5, timeout_seconds)) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SignedTokenError(f"unable to load OIDC metadata from `{url}`") from exc
    if not isinstance(payload, dict):
        raise SignedTokenError("OIDC metadata must be a JSON object")
    if cache_ttl_seconds > 0:
        with _REMOTE_CACHE_LOCK:
            _REMOTE_JSON_CACHE[url] = (now + cache_ttl_seconds, payload)
    return dict(payload)


def clear_remote_verifier_caches() -> None:
    with _REMOTE_CACHE_LOCK:
        _REMOTE_JSON_CACHE.clear()


def _issuer_discovery_url(issuer: str) -> str:
    return issuer.rstrip("/") + "/.well-known/openid-configuration"


def verify_oidc_token(
    token: str,
    *,
    issuer: str | None = None,
    audience: str | None = None,
    jwks_url: str | None = None,
    timeout_seconds: float = 5.0,
    cache_ttl_seconds: float = 300.0,
    leeway_seconds: float = 0,
) -> dict[str, Any]:
    resolved_jwks_url = (jwks_url or "").strip() or None
    if resolved_jwks_url is None:
        if issuer is None or not issuer.strip():
            raise SignedTokenError("OIDC issuer or jwks_url is required")
        discovery = _load_remote_json(
            _issuer_discovery_url(issuer),
            timeout_seconds=timeout_seconds,
            cache_ttl_seconds=cache_ttl_seconds,
        )
        resolved_issuer = str(discovery.get("issuer", "")).strip()
        if resolved_issuer and issuer.rstrip("/") != resolved_issuer.rstrip("/"):
            raise SignedTokenError("OIDC discovery issuer mismatch")
        resolved_jwks_url = str(discovery.get("jwks_uri", "")).strip()
        if not resolved_jwks_url:
            raise SignedTokenError("OIDC discovery metadata is missing jwks_uri")
    jwks = _load_remote_json(
        resolved_jwks_url,
        timeout_seconds=timeout_seconds,
        cache_ttl_seconds=cache_ttl_seconds,
    )
    return verify_jwks_token(
        token,
        jwks,
        issuer=issuer,
        audience=audience,
        leeway_seconds=leeway_seconds,
    )
