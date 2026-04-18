from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import hmac
import hashlib
import ipaddress
import json
import logging
import math
import os
import socket
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from skilgen.api.service import (
    analytics_payload,
    analyze_payload,
    architecture_payload,
    dashboard_payload,
    cancel_job_payload,
    connectors_activate_payload,
    connectors_active_payload,
    connectors_deactivate_payload,
    connectors_list_payload,
    connectors_recommend_payload,
    create_deliver_job,
    decision_payload,
    deliver_payload,
    diff_payload,
    doctor_payload,
    enterprise_generate_payload,
    enterprise_ingest_payload,
    enterprise_list_payload,
    features_payload,
    fingerprint_payload,
    health_payload,
    intent_payload,
    jobs_payload,
    job_status_payload,
    map_payload,
    plan_payload,
    preview_payload,
    report_payload,
    resume_job_payload,
    score_badge_payload,
    score_payload,
    skills_activate_payload,
    skills_active_payload,
    skills_deactivate_payload,
    skills_detect_payload,
    skills_import_payload,
    skills_install_payload,
    skills_list_payload,
    skills_lock_export_payload,
    skills_lock_import_payload,
    skills_lock_payload,
    skills_policy_payload,
    skills_rank_payload,
    skills_remove_payload,
    skills_show_payload,
    skills_sync_payload,
    status_payload,
    validate_payload,
)
from skilgen.core.auth_tokens import SignedTokenError, verify_oidc_token, verify_signed_token
from skilgen.core.audit import append_audit_event, append_central_audit_event
from skilgen.core.runtime_data import prune_runtime_data


LOGGER = logging.getLogger("skilgen.api")
_LOGGING_READY = False
_METRICS_LOCK = threading.Lock()
_RATE_LIMIT_LOCK = threading.Lock()
_METRICS = {
    "requests_total": 0,
    "requests_by_status": {},
    "durations_ms": [],
}
_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = {}
_SCOPE_LEVELS = {"read": 1, "write": 2, "admin": 3}


@dataclass(frozen=True)
class ApiPrincipal:
    principal: str
    scope: str
    token: str
    allowed_roots: tuple[Path, ...] = ()
    tenant: str | None = None
    allow_insecure_transport: bool = False
    auth_method: str = "static"


@dataclass(frozen=True)
class OidcClaimMapping:
    provider: str
    principal_claims: tuple[str, ...]
    scope_claims: tuple[str, ...]
    group_claims: tuple[str, ...]
    root_claims: tuple[str, ...]
    tenant_claims: tuple[str, ...]


def _ensure_logging() -> None:
    global _LOGGING_READY
    if _LOGGING_READY:
        return
    handler = logging.StreamHandler()

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                "level": record.levelname.lower(),
                "logger": record.name,
                "message": record.getMessage(),
            }
            if hasattr(record, "event"):
                payload["event"] = record.event
            if hasattr(record, "request_id"):
                payload["request_id"] = record.request_id
            if hasattr(record, "method"):
                payload["method"] = record.method
            if hasattr(record, "path"):
                payload["path"] = record.path
            if hasattr(record, "status"):
                payload["status"] = record.status
            if hasattr(record, "duration_ms"):
                payload["duration_ms"] = record.duration_ms
            if hasattr(record, "remote_addr"):
                payload["remote_addr"] = record.remote_addr
            if hasattr(record, "principal"):
                payload["principal"] = record.principal
            if hasattr(record, "scope"):
                payload["scope"] = record.scope
            if hasattr(record, "tenant"):
                payload["tenant"] = record.tenant
            if hasattr(record, "secure_transport"):
                payload["secure_transport"] = record.secure_transport
            if hasattr(record, "auth_method"):
                payload["auth_method"] = record.auth_method
            return json.dumps(payload, sort_keys=True)

    handler.setFormatter(JsonFormatter())
    LOGGER.setLevel(logging.INFO)
    LOGGER.handlers[:] = [handler]
    LOGGER.propagate = False
    _LOGGING_READY = True


def _record_metrics(status_code: int, duration_ms: float) -> None:
    with _METRICS_LOCK:
        _METRICS["requests_total"] += 1
        _METRICS["requests_by_status"][status_code] = _METRICS["requests_by_status"].get(status_code, 0) + 1
        durations = _METRICS["durations_ms"]
        durations.append(duration_ms)
        if len(durations) > 256:
            del durations[:-256]


def _metrics_payload() -> str:
    with _METRICS_LOCK:
        requests_total = int(_METRICS["requests_total"])
        requests_by_status = dict(_METRICS["requests_by_status"])
        durations = list(_METRICS["durations_ms"])
    avg_duration = (sum(durations) / len(durations)) if durations else 0.0
    lines = [
        "# HELP skilgen_http_requests_total Total HTTP requests handled by the API server.",
        "# TYPE skilgen_http_requests_total counter",
        f"skilgen_http_requests_total {requests_total}",
        "# HELP skilgen_http_request_duration_average_ms Average request duration in milliseconds.",
        "# TYPE skilgen_http_request_duration_average_ms gauge",
        f"skilgen_http_request_duration_average_ms {avg_duration:.2f}",
    ]
    for status_code, count in sorted(requests_by_status.items()):
        lines.append(f'skilgen_http_requests_by_status_total{{status="{status_code}"}} {count}')
    return "\n".join(lines) + "\n"


def _json_response(handler: BaseHTTPRequestHandler, status_code: int, payload: dict[str, object], *, request_id: str) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("X-Request-Id", request_id)
    handler.end_headers()
    handler.wfile.write(body)


def _svg_response(handler: BaseHTTPRequestHandler, status_code: int, body: str, *, request_id: str) -> None:
    payload = body.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "image/svg+xml")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("X-Request-Id", request_id)
    handler.end_headers()
    handler.wfile.write(payload)


def _text_response(handler: BaseHTTPRequestHandler, status_code: int, body: str, *, content_type: str, request_id: str) -> None:
    payload = body.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("X-Request-Id", request_id)
    handler.end_headers()
    handler.wfile.write(payload)


def _configured_api_token() -> str | None:
    return os.getenv("SKILGEN_API_TOKEN")


def _configured_api_signing_key() -> str | None:
    value = os.getenv("SKILGEN_API_SIGNING_KEY", "").strip()
    return value or None


def _signed_token_issuer() -> str | None:
    value = os.getenv("SKILGEN_API_TOKEN_ISSUER", "").strip()
    return value or None


def _signed_token_audience() -> str | None:
    value = os.getenv("SKILGEN_API_TOKEN_AUDIENCE", "").strip()
    return value or None


def _signed_token_leeway_seconds() -> float:
    try:
        return max(0.0, float(os.getenv("SKILGEN_API_TOKEN_LEEWAY_SECONDS", "5")))
    except ValueError:
        return 5.0


def _configured_oidc_issuer() -> str | None:
    value = os.getenv("SKILGEN_API_OIDC_ISSUER", "").strip()
    return value or None


def _configured_oidc_audience() -> str | None:
    value = os.getenv("SKILGEN_API_OIDC_AUDIENCE", "").strip()
    return value or None


def _configured_oidc_jwks_url() -> str | None:
    value = os.getenv("SKILGEN_API_JWKS_URL", "").strip()
    return value or None


def _configured_oidc_timeout_seconds() -> float:
    try:
        return max(0.5, float(os.getenv("SKILGEN_API_OIDC_TIMEOUT_SECONDS", "5")))
    except ValueError:
        return 5.0


def _configured_oidc_cache_ttl_seconds() -> float:
    try:
        return max(0.0, float(os.getenv("SKILGEN_API_OIDC_CACHE_TTL_SECONDS", "300")))
    except ValueError:
        return 300.0


def _configured_oidc_provider() -> str:
    value = os.getenv("SKILGEN_API_OIDC_PROVIDER", "generic").strip().lower()
    return value or "generic"


def _configured_oidc_auth0_namespace() -> str | None:
    value = os.getenv("SKILGEN_API_OIDC_AUTH0_NAMESPACE", "").strip().rstrip("/")
    return value or None


def _csv_env(name: str) -> tuple[str, ...]:
    value = os.getenv(name, "").strip()
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _json_object_env(name: str) -> dict[str, object]:
    value = os.getenv(name, "").strip()
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _namespaced_claim(namespace: str | None, claim: str) -> tuple[str, ...]:
    if namespace is None:
        return ()
    return (f"{namespace}/{claim.lstrip('/')}",)


def _provider_claim_mapping() -> OidcClaimMapping:
    provider = _configured_oidc_provider()
    auth0_namespace = _configured_oidc_auth0_namespace()
    presets: dict[str, OidcClaimMapping] = {
        "generic": OidcClaimMapping(
            provider="generic",
            principal_claims=("preferred_username", "email", "sub", "principal"),
            scope_claims=("scope", "scp", "roles", "role"),
            group_claims=("groups", "group", "roles", "role"),
            root_claims=("roots", "allowed_project_roots", "project_roots"),
            tenant_claims=("tenant", "tid"),
        ),
        "okta": OidcClaimMapping(
            provider="okta",
            principal_claims=("preferred_username", "email", "sub"),
            scope_claims=("scope", "scp", "groups", "roles", "role"),
            group_claims=("groups", "roles", "role"),
            root_claims=("skilgen_roots", "roots", "allowed_project_roots", "project_roots"),
            tenant_claims=("tenant", "org_id", "tid"),
        ),
        "entra": OidcClaimMapping(
            provider="entra",
            principal_claims=("preferred_username", "upn", "email", "oid", "sub"),
            scope_claims=("scp", "roles", "groups", "scope"),
            group_claims=("groups", "roles", "wids"),
            root_claims=("extension_skilgen_roots", "skilgen_roots", "roots", "allowed_project_roots", "project_roots"),
            tenant_claims=("tid", "tenant"),
        ),
        "auth0": OidcClaimMapping(
            provider="auth0",
            principal_claims=("email", "nickname", "name", "sub") + _namespaced_claim(auth0_namespace, "principal"),
            scope_claims=("scope", "permissions", "roles", "groups")
            + _namespaced_claim(auth0_namespace, "scope")
            + _namespaced_claim(auth0_namespace, "permissions")
            + _namespaced_claim(auth0_namespace, "roles")
            + _namespaced_claim(auth0_namespace, "groups"),
            group_claims=("permissions", "roles", "groups")
            + _namespaced_claim(auth0_namespace, "permissions")
            + _namespaced_claim(auth0_namespace, "roles")
            + _namespaced_claim(auth0_namespace, "groups"),
            root_claims=("roots", "allowed_project_roots", "project_roots")
            + _namespaced_claim(auth0_namespace, "roots")
            + _namespaced_claim(auth0_namespace, "allowed_project_roots")
            + _namespaced_claim(auth0_namespace, "project_roots"),
            tenant_claims=("tenant", "org_id")
            + _namespaced_claim(auth0_namespace, "tenant")
            + _namespaced_claim(auth0_namespace, "org_id"),
        ),
    }
    base_mapping = presets.get(provider, presets["generic"])
    return OidcClaimMapping(
        provider=base_mapping.provider,
        principal_claims=_csv_env("SKILGEN_API_OIDC_PRINCIPAL_CLAIMS") or base_mapping.principal_claims,
        scope_claims=_csv_env("SKILGEN_API_OIDC_SCOPE_CLAIMS") or base_mapping.scope_claims,
        group_claims=_csv_env("SKILGEN_API_OIDC_GROUP_CLAIMS") or base_mapping.group_claims,
        root_claims=_csv_env("SKILGEN_API_OIDC_ROOTS_CLAIMS") or base_mapping.root_claims,
        tenant_claims=_csv_env("SKILGEN_API_OIDC_TENANT_CLAIMS") or base_mapping.tenant_claims,
    )


def _policy_roots(raw_roots: object) -> tuple[Path, ...]:
    if raw_roots is None or raw_roots == "":
        return ()
    if isinstance(raw_roots, str):
        raw_roots = [item.strip() for item in raw_roots.split(",") if item.strip()]
    if not isinstance(raw_roots, list):
        raise ValueError("allowed_project_roots must be a list or comma-separated string")
    roots: list[Path] = []
    for item in raw_roots:
        candidate = str(item).strip()
        if candidate:
            roots.append(Path(candidate).resolve())
    return tuple(roots)


def _configured_api_principals() -> list[ApiPrincipal]:
    principals: list[ApiPrincipal] = []
    if _configured_api_token():
        principals.append(ApiPrincipal(principal="legacy-admin", scope="admin", token=str(_configured_api_token())))
    for env_name, scope in (
        ("SKILGEN_API_READ_TOKEN", "read"),
        ("SKILGEN_API_WRITE_TOKEN", "write"),
        ("SKILGEN_API_ADMIN_TOKEN", "admin"),
    ):
        value = os.getenv(env_name)
        if value:
            principals.append(
                ApiPrincipal(
                    principal=env_name.removeprefix("SKILGEN_API_").removesuffix("_TOKEN").lower(),
                    scope=scope,
                    token=value,
                )
            )
    raw_pairs = os.getenv("SKILGEN_API_TOKENS", "")
    for item in raw_pairs.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            continue
        scope, token = stripped.split(":", 1)
        normalized_scope = scope.strip().lower()
        normalized_token = token.strip()
        if normalized_scope in _SCOPE_LEVELS and normalized_token:
            principals.append(
                ApiPrincipal(
                    principal=f"{normalized_scope}-token-{len(principals) + 1}",
                    scope=normalized_scope,
                    token=normalized_token,
                )
            )
    raw_policies = os.getenv("SKILGEN_API_TOKEN_POLICIES", "").strip()
    if raw_policies:
        try:
            parsed = json.loads(raw_policies)
        except json.JSONDecodeError:
            parsed = []
        if isinstance(parsed, dict):
            parsed = parsed.get("tokens", [])
        if isinstance(parsed, list):
            for index, item in enumerate(parsed, start=1):
                if not isinstance(item, dict):
                    continue
                token = str(item.get("token", "")).strip()
                scope = str(item.get("scope", "read")).strip().lower()
                if not token or scope not in _SCOPE_LEVELS:
                    continue
                try:
                    allowed_roots = _policy_roots(item.get("allowed_project_roots", item.get("project_roots", [])))
                except ValueError:
                    continue
                principals.append(
                    ApiPrincipal(
                        principal=str(item.get("principal") or item.get("name") or f"principal-{index}"),
                        scope=scope,
                        token=token,
                        allowed_roots=allowed_roots,
                        tenant=str(item.get("tenant")).strip() if item.get("tenant") not in {None, ""} else None,
                        allow_insecure_transport=bool(item.get("allow_insecure_transport", False)),
                        auth_method="static",
                    )
                )
    return principals


def _auth_is_configured() -> bool:
    return bool(
        _configured_api_principals()
        or _configured_api_signing_key()
        or _configured_oidc_issuer()
        or _configured_oidc_jwks_url()
    )


def _max_body_bytes() -> int:
    raw = os.getenv("SKILGEN_API_MAX_BODY_BYTES", "10485760")
    try:
        return max(1024, int(raw))
    except ValueError:
        return 10 * 1024 * 1024


def _allowed_project_roots() -> list[Path]:
    raw = os.getenv("SKILGEN_ALLOWED_PROJECT_ROOTS")
    if not raw:
        return [Path.cwd().resolve()]
    roots: list[Path] = []
    for value in raw.split(","):
        stripped = value.strip()
        if stripped:
            roots.append(Path(stripped).resolve())
    return roots or [Path.cwd().resolve()]


def _principal_contains_root(principal: ApiPrincipal, candidate: Path) -> bool:
    if not principal.allowed_roots:
        return True
    return any(_contains_path(root, candidate) for root in principal.allowed_roots)


def _resolve_project_root(raw_value: str | None, *, principal: ApiPrincipal | None = None) -> Path:
    candidate = Path(raw_value or ".").resolve()
    for allowed_root in _allowed_project_roots():
        if candidate == allowed_root or allowed_root in candidate.parents:
            if principal is not None and not _principal_contains_root(principal, candidate):
                raise PermissionError(f"project_root `{candidate}` is outside the allowed scope for principal `{principal.principal}`")
            return candidate
    raise PermissionError(f"project_root `{candidate}` is outside the configured allowlist")


def _contains_path(base: Path, candidate: Path) -> bool:
    return candidate == base or base in candidate.parents


def _resolve_scoped_path(
    raw_value: str,
    *,
    project_root: Path | None,
    must_exist: bool = False,
) -> Path:
    candidate = Path(raw_value)
    if not candidate.is_absolute():
        candidate = ((project_root or Path.cwd()) / candidate).resolve()
    else:
        candidate = candidate.resolve()

    allowed_bases = [project_root] if project_root is not None else _allowed_project_roots()
    for base in allowed_bases:
        if _contains_path(base.resolve(), candidate):
            if must_exist and not candidate.exists():
                raise FileNotFoundError(f"path `{candidate}` does not exist")
            return candidate
    scope_label = str(project_root) if project_root is not None else "configured allowlist"
    raise PermissionError(f"path `{candidate}` is outside the allowed scope `{scope_label}`")


def _rate_limit_config() -> tuple[int, float]:
    try:
        count = max(0, int(os.getenv("SKILGEN_API_RATE_LIMIT_COUNT", "240")))
    except ValueError:
        count = 240
    try:
        window_seconds = max(1.0, float(os.getenv("SKILGEN_API_RATE_LIMIT_WINDOW_SECONDS", "60")))
    except ValueError:
        window_seconds = 60.0
    return count, window_seconds


def _bucket_key(remote_addr: str, token: str | None) -> str:
    digest = hashlib.sha256((token or "anonymous").encode("utf-8")).hexdigest()[:16]
    return f"{remote_addr}:{digest}"


def _enforce_rate_limit(handler: BaseHTTPRequestHandler, *, request_id: str) -> tuple[bool, int]:
    max_count, window_seconds = _rate_limit_config()
    if max_count <= 0:
        return True, 200
    header = handler.headers.get("Authorization", "")
    token = header.removeprefix("Bearer ").strip() if header.startswith("Bearer ") else None
    key = _bucket_key(handler.client_address[0], token)
    now = time.monotonic()
    with _RATE_LIMIT_LOCK:
        bucket = _RATE_LIMIT_BUCKETS.setdefault(key, deque())
        cutoff = now - window_seconds
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= max_count:
            retry_after = max(1, math.ceil(window_seconds - (now - bucket[0])))
            _json_response(handler, 429, {"error": "rate_limited", "retry_after_seconds": retry_after}, request_id=request_id)
            return False, 429
        bucket.append(now)
        if len(_RATE_LIMIT_BUCKETS) > 2048:
            expired = [item for item, timestamps in _RATE_LIMIT_BUCKETS.items() if not timestamps or timestamps[-1] < cutoff]
            for item in expired[:512]:
                _RATE_LIMIT_BUCKETS.pop(item, None)
    return True, 200


def _claim_values(claims: dict[str, object], *names: str) -> list[str]:
    values: list[str] = []
    for name in names:
        raw_value = claims.get(name)
        if isinstance(raw_value, str):
            values.extend(part for part in raw_value.replace(",", " ").split() if part.strip())
        elif isinstance(raw_value, list):
            values.extend(str(item).strip() for item in raw_value if str(item).strip())
    return values


def _claim_first(claims: dict[str, object], names: tuple[str, ...]) -> str | None:
    for name in names:
        raw_value = claims.get(name)
        if isinstance(raw_value, str) and raw_value.strip():
            return raw_value.strip()
    return None


def _group_scope_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw_name, raw_scope in _json_object_env("SKILGEN_API_OIDC_GROUP_SCOPE_MAP").items():
        normalized_scope = _normalize_scope_value(str(raw_scope))
        if normalized_scope is None:
            continue
        group_name = str(raw_name).strip()
        if group_name:
            mapping[group_name.lower()] = normalized_scope
    return mapping


def _group_roots_map() -> dict[str, tuple[Path, ...]]:
    mapping: dict[str, tuple[Path, ...]] = {}
    for raw_name, raw_roots in _json_object_env("SKILGEN_API_OIDC_GROUP_ROOTS_MAP").items():
        group_name = str(raw_name).strip()
        if not group_name:
            continue
        try:
            mapping[group_name.lower()] = _policy_roots(raw_roots)
        except ValueError:
            continue
    return mapping


def _normalize_scope_value(candidate: str) -> str | None:
    normalized = candidate.strip().lower()
    if normalized in _SCOPE_LEVELS:
        return normalized
    for separator in (":", ".", "/"):
        if separator in normalized:
            suffix = normalized.rsplit(separator, 1)[-1]
            if suffix in _SCOPE_LEVELS:
                return suffix
    return None


def _claims_scope(claims: dict[str, object], mapping: OidcClaimMapping) -> str | None:
    best_scope: str | None = None
    for candidate in _claim_values(claims, *mapping.scope_claims):
        normalized = _normalize_scope_value(candidate)
        if normalized is None:
            continue
        if best_scope is None or _SCOPE_LEVELS[normalized] > _SCOPE_LEVELS[best_scope]:
            best_scope = normalized
    scoped_groups = _group_scope_map()
    if scoped_groups:
        for candidate in _claim_values(claims, *mapping.group_claims):
            normalized = scoped_groups.get(candidate.strip().lower())
            if normalized is None:
                continue
            if best_scope is None or _SCOPE_LEVELS[normalized] > _SCOPE_LEVELS[best_scope]:
                best_scope = normalized
    return best_scope


def _claims_allowed_roots(claims: dict[str, object], mapping: OidcClaimMapping) -> tuple[Path, ...] | None:
    resolved_roots: list[Path] = []
    seen_roots: set[Path] = set()
    for name in mapping.root_claims:
        if name not in claims:
            continue
        try:
            roots = _policy_roots(claims.get(name))
        except ValueError:
            return None
        for root in roots:
            if root not in seen_roots:
                seen_roots.add(root)
                resolved_roots.append(root)
    mapped_roots = _group_roots_map()
    if mapped_roots:
        for candidate in _claim_values(claims, *mapping.group_claims):
            for root in mapped_roots.get(candidate.strip().lower(), ()):
                if root not in seen_roots:
                    seen_roots.add(root)
                    resolved_roots.append(root)
    return tuple(resolved_roots)


def _claims_tenant(claims: dict[str, object], mapping: OidcClaimMapping) -> str | None:
    return _claim_first(claims, mapping.tenant_claims)


def _claims_principal(claims: dict[str, object], mapping: OidcClaimMapping) -> str:
    principal = _claim_first(claims, mapping.principal_claims)
    if principal:
        return principal
    return str(claims.get("sub", claims.get("principal", ""))).strip() or "oidc-principal"


def _oidc_principal(token: str) -> ApiPrincipal | None:
    issuer = _configured_oidc_issuer()
    jwks_url = _configured_oidc_jwks_url()
    if issuer is None and jwks_url is None:
        return None
    mapping = _provider_claim_mapping()
    try:
        claims = verify_oidc_token(
            token,
            issuer=issuer,
            audience=_configured_oidc_audience(),
            jwks_url=jwks_url,
            timeout_seconds=_configured_oidc_timeout_seconds(),
            cache_ttl_seconds=_configured_oidc_cache_ttl_seconds(),
            leeway_seconds=_signed_token_leeway_seconds(),
        )
    except SignedTokenError:
        return None
    scope = _claims_scope(claims, mapping)
    if scope is None:
        return None
    allowed_roots = _claims_allowed_roots(claims, mapping)
    if allowed_roots is None:
        return None
    tenant = _claims_tenant(claims, mapping)
    return ApiPrincipal(
        principal=_claims_principal(claims, mapping),
        scope=scope,
        token=token,
        allowed_roots=allowed_roots,
        tenant=tenant,
        allow_insecure_transport=bool(claims.get("allow_insecure_transport", False)),
        auth_method="oidc",
    )


def _token_principal(token: str | None) -> ApiPrincipal | None:
    if not token:
        return None
    for principal in _configured_api_principals():
        if hmac.compare_digest(token, principal.token):
            return principal
    signing_key = _configured_api_signing_key()
    if signing_key is not None:
        try:
            claims = verify_signed_token(
                token,
                signing_key,
                issuer=_signed_token_issuer(),
                audience=_signed_token_audience(),
                leeway_seconds=_signed_token_leeway_seconds(),
            )
        except SignedTokenError:
            claims = None
        if claims is not None:
            mapping = _provider_claim_mapping()
            scope = _claims_scope(claims, mapping)
            if scope is None:
                return None
            allowed_roots = _claims_allowed_roots(claims, mapping)
            if allowed_roots is None:
                return None
            tenant = _claims_tenant(claims, mapping)
            return ApiPrincipal(
                principal=_claims_principal(claims, mapping),
                scope=scope,
                token=token,
                allowed_roots=allowed_roots,
                tenant=tenant,
                allow_insecure_transport=bool(claims.get("allow_insecure_transport", False)),
                auth_method="signed",
            )
    return _oidc_principal(token)


def _scope_satisfies(actual_scope: str, required_scope: str) -> bool:
    return _SCOPE_LEVELS[actual_scope] >= _SCOPE_LEVELS[required_scope]


def _required_scope_for_get(path: str, query: dict[str, list[str]]) -> str:
    if path in {"/doctor", "/metrics"}:
        return "admin"
    if path == "/skills/lock/export":
        return "write"
    if path == "/score" and query.get("badge_file", [None])[0]:
        return "write"
    return "read"


def _required_scope_for_post(path: str) -> str:
    if path in {"/deliver", "/jobs/deliver"} or path.endswith("/cancel") or path.endswith("/resume"):
        return "write"
    if path.startswith("/skills/") or path.startswith("/enterprise/") or path.startswith("/connectors/"):
        return "admin"
    return "read"


def _remote_host_allowed(hostname: str) -> bool:
    allowed_hosts = [item.strip().lower() for item in os.getenv("SKILGEN_REMOTE_SOURCE_ALLOWED_HOSTS", "").split(",") if item.strip()]
    normalized = hostname.lower().rstrip(".")
    if allowed_hosts:
        return any(normalized == host or normalized.endswith(f".{host}") for host in allowed_hosts)
    return True


def _assert_public_remote_host(hostname: str) -> None:
    normalized = hostname.lower().rstrip(".")
    if normalized in {"localhost"} or normalized.endswith(".local"):
        raise PermissionError(f"remote host `{hostname}` is not allowed")
    if not _remote_host_allowed(normalized):
        raise PermissionError(f"remote host `{hostname}` is outside the configured allowlist")

    def classify_address(raw_address: str) -> ipaddress._BaseAddress:
        return ipaddress.ip_address(raw_address.split("%", 1)[0])

    try:
        literal = classify_address(normalized)
        addresses = [literal]
    except ValueError:
        try:
            resolved = socket.getaddrinfo(normalized, None)
        except socket.gaierror as exc:
            raise PermissionError(f"remote host `{hostname}` could not be resolved safely") from exc
        addresses = []
        for item in resolved:
            raw_address = item[4][0]
            try:
                addresses.append(classify_address(raw_address))
            except ValueError:
                continue

    for address in addresses:
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        ):
            raise PermissionError(f"remote host `{hostname}` resolved to a non-public address")


def _normalize_remote_source(
    raw_value: str,
    *,
    project_root: Path | None,
    allow_local: bool = True,
) -> str:
    parsed = urlparse(raw_value)
    if parsed.scheme in {"", "file"}:
        if not allow_local:
            raise PermissionError("local remote sources are disabled for this endpoint")
        local_value = parsed.path if parsed.scheme == "file" else raw_value
        return str(_resolve_scoped_path(local_value, project_root=project_root, must_exist=True))
    if parsed.scheme not in {"http", "https"}:
        raise PermissionError("remote sources must use http or https")
    if parsed.username or parsed.password:
        raise PermissionError("remote sources must not embed credentials in the URL")
    hostname = parsed.hostname
    if not hostname:
        raise PermissionError("remote source URL must include a hostname")
    _assert_public_remote_host(hostname)
    return raw_value


def _tls_required() -> bool:
    return os.getenv("SKILGEN_API_REQUIRE_TLS", "1").strip().lower() not in {"0", "false", "no"}


def _allow_insecure_loopback() -> bool:
    return os.getenv("SKILGEN_API_ALLOW_INSECURE_LOOPBACK", "1").strip().lower() not in {"0", "false", "no"}


def _is_loopback_address(raw_address: str) -> bool:
    try:
        return ipaddress.ip_address(raw_address.split("%", 1)[0]).is_loopback
    except ValueError:
        return raw_address in {"localhost", "::1"}


def _forwarded_proto(handler: BaseHTTPRequestHandler) -> str | None:
    forwarded = handler.headers.get("Forwarded", "")
    for part in forwarded.split(";"):
        stripped = part.strip()
        if stripped.lower().startswith("proto="):
            return stripped.split("=", 1)[1].strip().strip('"').lower()
    x_forwarded_proto = handler.headers.get("X-Forwarded-Proto", "").split(",", 1)[0].strip().lower()
    if x_forwarded_proto:
        return x_forwarded_proto
    if handler.headers.get("X-Forwarded-Ssl", "").strip().lower() == "on":
        return "https"
    return None


def _request_is_secure(handler: BaseHTTPRequestHandler) -> bool:
    forwarded_proto = _forwarded_proto(handler)
    if forwarded_proto == "https":
        return True
    connection = getattr(handler, "connection", None)
    cipher = getattr(connection, "cipher", None)
    if callable(cipher):
        try:
            return cipher() is not None
        except OSError:
            return False
    return False


def _enforce_transport_security(
    handler: BaseHTTPRequestHandler,
    *,
    request_id: str,
    principal: ApiPrincipal | None,
) -> tuple[bool, int]:
    if not _tls_required():
        return True, 200
    if principal is not None and principal.allow_insecure_transport:
        return True, 200
    if _request_is_secure(handler):
        return True, 200
    if _allow_insecure_loopback() and _is_loopback_address(handler.client_address[0]):
        return True, 200
    _json_response(
        handler,
        426,
        {
            "error": "tls_required",
            "message": "HTTPS is required. Terminate TLS upstream and forward `X-Forwarded-Proto: https`.",
        },
        request_id=request_id,
    )
    return False, 426


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    if length > _max_body_bytes():
        raise ValueError("payload_too_large")
    body = handler.rfile.read(length) if length else b"{}"
    return json.loads(body.decode("utf-8") or "{}")


def _require_authorization(
    handler: BaseHTTPRequestHandler,
    *,
    request_id: str,
    required_scope: str,
) -> tuple[bool, int, ApiPrincipal | None]:
    if not _auth_is_configured():
        _json_response(handler, 503, {"error": "server_auth_not_configured"}, request_id=request_id)
        return False, 503, None
    allowed, status_code = _enforce_rate_limit(handler, request_id=request_id)
    if not allowed:
        return False, status_code, None
    header = handler.headers.get("Authorization", "")
    token = header.removeprefix("Bearer ").strip() if header.startswith("Bearer ") else None
    principal = _token_principal(token)
    if principal is None:
        _json_response(handler, 401, {"error": "unauthorized"}, request_id=request_id)
        return False, 401, None
    transport_allowed, transport_status = _enforce_transport_security(handler, request_id=request_id, principal=principal)
    if not transport_allowed:
        return False, transport_status, principal
    if not _scope_satisfies(principal.scope, required_scope):
        _json_response(
            handler,
            403,
            {"error": "insufficient_scope", "required_scope": required_scope, "granted_scope": principal.scope},
            request_id=request_id,
        )
        return False, 403, principal
    return True, 200, principal


class BoundedThreadPoolHTTPServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int], request_handler_class: type[BaseHTTPRequestHandler]) -> None:
        super().__init__(server_address, request_handler_class)
        max_workers = int(os.getenv("SKILGEN_SERVER_MAX_WORKERS", "8"))
        max_queue = int(os.getenv("SKILGEN_SERVER_MAX_QUEUE", "32"))
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="skilgen-api")
        self._request_slots = threading.BoundedSemaphore(max_workers + max_queue)

    def process_request(self, request, client_address) -> None:  # type: ignore[override]
        if not self._request_slots.acquire(blocking=False):
            try:
                request.sendall(
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Content-Type: application/json\r\n"
                    b"Connection: close\r\n\r\n"
                    b"{\"error\":\"server_busy\"}"
                )
            except OSError:
                pass
            self.shutdown_request(request)
            return
        self._executor.submit(self._process_request_task, request, client_address)

    def _process_request_task(self, request, client_address) -> None:
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        finally:
            self._request_slots.release()

    def server_close(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)
        super().server_close()


def create_handler() -> type[BaseHTTPRequestHandler]:
    class SkilgenHandler(BaseHTTPRequestHandler):
        def _finish_request(
            self,
            *,
            status_code: int,
            request_id: str,
            project_root: Path | None,
            start_time: float,
            principal: ApiPrincipal | None,
        ) -> None:
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            _record_metrics(status_code, duration_ms)
            LOGGER.info(
                "request_complete",
                extra={
                    "event": "access",
                    "request_id": request_id,
                    "method": self.command,
                    "path": self.path,
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "remote_addr": self.client_address[0],
                    "principal": principal.principal if principal is not None else "anonymous",
                    "scope": principal.scope if principal is not None else None,
                    "tenant": principal.tenant if principal is not None else None,
                    "secure_transport": _request_is_secure(self),
                    "auth_method": principal.auth_method if principal is not None else None,
                },
            )
            if project_root is not None:
                append_audit_event(
                    project_root,
                    action=f"http_{self.command.lower()}",
                    outcome=str(status_code),
                    source="api",
                    actor=principal.principal if principal is not None else self.client_address[0],
                    principal=principal.principal if principal is not None else None,
                    scope=principal.scope if principal is not None else None,
                    tenant=principal.tenant if principal is not None else None,
                    request_id=request_id,
                    details={"path": self.path, "status": status_code, "remote_addr": self.client_address[0]},
                )
            else:
                append_central_audit_event(
                    action=f"http_{self.command.lower()}",
                    outcome=str(status_code),
                    source="api",
                    actor=principal.principal if principal is not None else self.client_address[0],
                    principal=principal.principal if principal is not None else None,
                    scope=principal.scope if principal is not None else None,
                    tenant=principal.tenant if principal is not None else None,
                    project_root=project_root,
                    request_id=request_id,
                    details={"path": self.path, "status": status_code, "remote_addr": self.client_address[0]},
                )

        def _handle_exception(self, exc: Exception, *, request_id: str, project_root: Path | None) -> int:
            if isinstance(exc, PermissionError):
                _json_response(self, 403, {"error": "forbidden", "message": str(exc)}, request_id=request_id)
                return 403
            if isinstance(exc, FileNotFoundError):
                _json_response(self, 404, {"error": "not_found", "message": str(exc)}, request_id=request_id)
                return 404
            if isinstance(exc, ValueError) and str(exc) == "payload_too_large":
                _json_response(self, 413, {"error": "payload_too_large"}, request_id=request_id)
                return 413
            if isinstance(exc, json.JSONDecodeError):
                _json_response(self, 400, {"error": "invalid_json"}, request_id=request_id)
                return 400
            if isinstance(exc, KeyError):
                missing_key = str(exc).strip("'")
                _json_response(
                    self,
                    400,
                    {"error": "invalid_request", "message": f"Missing required field `{missing_key}`"},
                    request_id=request_id,
                )
                return 400
            if isinstance(exc, ValueError):
                _json_response(self, 400, {"error": "invalid_request", "message": str(exc)}, request_id=request_id)
                return 400
            LOGGER.exception("request_failed", extra={"event": "request_error", "request_id": request_id, "path": self.path})
            _json_response(self, 500, {"error": "internal_error"}, request_id=request_id)
            return 500

        def _project_root_from_query(self, query: dict[str, list[str]], *, principal: ApiPrincipal | None) -> Path | None:
            if "project_root" not in query:
                if principal is not None and len(principal.allowed_roots) == 1:
                    return principal.allowed_roots[0]
                return None
            return _resolve_project_root(query.get("project_root", ["."])[0], principal=principal)

        def _project_root_from_data(self, data: dict[str, object], *, principal: ApiPrincipal | None) -> Path | None:
            if "project_root" not in data:
                if principal is not None and len(principal.allowed_roots) == 1:
                    return principal.allowed_roots[0]
                return None
            return _resolve_project_root(str(data.get("project_root", ".")), principal=principal)

        def _query_path(
            self,
            query: dict[str, list[str]],
            key: str,
            *,
            project_root: Path | None,
            must_exist: bool = False,
        ) -> Path | None:
            raw = query.get(key, [None])[0]
            if raw in {None, ""}:
                return None
            return _resolve_scoped_path(str(raw), project_root=project_root, must_exist=must_exist)

        def _data_path(
            self,
            data: dict[str, object],
            key: str,
            *,
            project_root: Path | None,
            must_exist: bool = False,
        ) -> Path | None:
            raw = data.get(key)
            if raw in {None, ""}:
                return None
            return _resolve_scoped_path(str(raw), project_root=project_root, must_exist=must_exist)

        def _data_path_list(
            self,
            data: dict[str, object],
            key: str,
            *,
            project_root: Path | None,
            must_exist: bool = False,
        ) -> list[Path]:
            raw = data.get(key, [])
            if not isinstance(raw, list):
                raise ValueError(f"`{key}` must be a list of paths")
            return [
                _resolve_scoped_path(str(item), project_root=project_root, must_exist=must_exist)
                for item in raw
                if str(item).strip()
            ]

        def _data_remote_source(
            self,
            data: dict[str, object],
            key: str,
            *,
            project_root: Path | None,
            allow_local: bool = True,
        ) -> str | None:
            raw = data.get(key)
            if raw in {None, ""}:
                return None
            return _normalize_remote_source(str(raw), project_root=project_root, allow_local=allow_local)

        def do_GET(self) -> None:  # noqa: N802
            _ensure_logging()
            request_id = uuid.uuid4().hex
            start_time = time.monotonic()
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            project_root: Path | None = None
            principal: ApiPrincipal | None = None
            status_code = 500
            try:
                if parsed.path == "/health":
                    transport_allowed, status_code = _enforce_transport_security(self, request_id=request_id, principal=None)
                    if not transport_allowed:
                        return
                    _json_response(self, 200, health_payload(), request_id=request_id)
                    status_code = 200
                    return
                authorized, status_code, principal = _require_authorization(
                    self,
                    request_id=request_id,
                    required_scope=_required_scope_for_get(parsed.path, query),
                )
                if not authorized:
                    return
                project_root = self._project_root_from_query(query, principal=principal)
                if project_root is not None:
                    prune_runtime_data(project_root)
                requirements_path = self._query_path(query, "requirements", project_root=project_root, must_exist=True)
                badge_file = self._query_path(query, "badge_file", project_root=project_root, must_exist=False)
                lock_export_path = self._query_path(query, "output_path", project_root=project_root, must_exist=False)
                if parsed.path == "/metrics":
                    _text_response(self, 200, _metrics_payload(), content_type="text/plain; version=0.0.4", request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/status":
                    _json_response(self, 200, status_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/score":
                    _json_response(
                        self,
                        200,
                        score_payload(
                            project_root or Path("."),
                            badge_file,
                            history=query.get("history", ["0"])[0] not in {"0", "false", "False", ""},
                            history_limit=int(query.get("history_limit", ["10"])[0]),
                        ),
                        request_id=request_id,
                    )
                    status_code = 200
                    return
                if parsed.path == "/analytics":
                    _json_response(self, 200, analytics_payload(project_root or Path("."), limit=int(query.get("limit", ["10"])[0])), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/badge.svg":
                    _svg_response(self, 200, score_badge_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/doctor":
                    _json_response(self, 200, doctor_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/diff":
                    _json_response(self, 200, diff_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills":
                    _json_response(self, 200, skills_list_payload(project_root or Path("."), query.get("ecosystem", [None])[0], query.get("search", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/detect":
                    _json_response(self, 200, skills_detect_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/active":
                    _json_response(self, 200, skills_active_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/lock":
                    _json_response(self, 200, skills_lock_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/lock/export":
                    _json_response(self, 200, skills_lock_export_payload(project_root or Path("."), lock_export_path), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/policy":
                    _json_response(self, 200, skills_policy_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/rank":
                    _json_response(self, 200, skills_rank_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/enterprise":
                    _json_response(self, 200, enterprise_list_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/connectors":
                    _json_response(self, 200, connectors_list_payload(query.get("system", [None])[0], query.get("search", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/connectors/recommend":
                    _json_response(self, 200, connectors_recommend_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/connectors/active":
                    _json_response(self, 200, connectors_active_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path.startswith("/skills/"):
                    _json_response(self, 200, skills_show_payload(parsed.path.split("/")[-1], project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/decide":
                    _json_response(self, 200, decision_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/architecture":
                    _json_response(self, 200, architecture_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/dashboard":
                    _json_response(self, 200, dashboard_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/jobs":
                    _json_response(self, 200, jobs_payload(project_root), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path.startswith("/jobs/"):
                    _json_response(self, 200, job_status_payload(parsed.path.split("/")[-1], project_root), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/report":
                    _json_response(self, 200, report_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/validate":
                    _json_response(self, 200, validate_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                _json_response(self, 404, {"error": "not_found"}, request_id=request_id)
                status_code = 404
            except Exception as exc:  # noqa: BLE001
                status_code = self._handle_exception(exc, request_id=request_id, project_root=project_root)
            finally:
                self._finish_request(
                    status_code=status_code,
                    request_id=request_id,
                    project_root=project_root,
                    start_time=start_time,
                    principal=principal,
                )

        def do_POST(self) -> None:  # noqa: N802
            _ensure_logging()
            request_id = uuid.uuid4().hex
            start_time = time.monotonic()
            project_root: Path | None = None
            principal: ApiPrincipal | None = None
            status_code = 500
            try:
                authorized, status_code, principal = _require_authorization(
                    self,
                    request_id=request_id,
                    required_scope=_required_scope_for_post(self.path),
                )
                if not authorized:
                    return
                data = _read_json(self)
                project_root = self._project_root_from_data(data, principal=principal)
                if project_root is not None:
                    prune_runtime_data(project_root)
                requirements_path = self._data_path(data, "requirements", project_root=project_root, must_exist=True)
                input_path = self._data_path(data, "input_path", project_root=project_root, must_exist=True)
                local_source_path = self._data_path(data, "path", project_root=project_root, must_exist=True)
                source_paths = self._data_path_list(data, "source_paths", project_root=project_root, must_exist=True)
                remote_git_url = self._data_remote_source(data, "git_url", project_root=project_root, allow_local=True)
                remote_url = self._data_remote_source(data, "url", project_root=project_root, allow_local=False)
                if self.path in {
                    "/analyze",
                    "/architecture",
                    "/dashboard",
                    "/decide",
                    "/intent",
                    "/plan",
                    "/features",
                    "/deliver",
                    "/preview",
                    "/jobs/deliver",
                } and requirements_path is None:
                    raise ValueError("`requirements` is required for this endpoint")
                if self.path == "/skills/lock/import" and input_path is None:
                    raise ValueError("`input_path` is required for this endpoint")
                if self.path == "/enterprise/ingest" and not any((local_source_path, remote_git_url, remote_url)):
                    raise ValueError("One of `path`, `git_url`, or `url` is required for this endpoint")
                if self.path == "/enterprise/generate" and not source_paths:
                    raise ValueError("`source_paths` must contain at least one path")
                if self.path == "/fingerprint":
                    _json_response(self, 200, fingerprint_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/map":
                    _json_response(self, 200, map_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/analyze":
                    _json_response(self, 200, analyze_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/architecture":
                    _json_response(self, 200, architecture_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/dashboard":
                    _json_response(self, 200, dashboard_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/decide":
                    _json_response(self, 200, decision_payload(project_root or Path("."), requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/intent":
                    _json_response(self, 200, intent_payload(requirements_path), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/plan":
                    _json_response(self, 200, plan_payload(requirements_path, project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/features":
                    _json_response(self, 200, features_payload(requirements_path, project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/deliver":
                    _json_response(self, 200, deliver_payload(requirements_path, project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/preview":
                    targets = tuple(data.get("targets", ("docs", "skills")))
                    domains = tuple(data.get("domains", ()))
                    _json_response(self, 200, preview_payload(requirements_path, project_root or Path("."), targets=targets, domains=domains), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/install":
                    _json_response(
                        self,
                        200,
                        skills_install_payload(
                            project_root or Path("."),
                            slug=str(data["slug"]) if "slug" in data and data.get("slug") is not None else None,
                            git_url=remote_git_url,
                            name=str(data["name"]) if "name" in data and data.get("name") is not None else None,
                            force=bool(data.get("force", False)),
                            ref=str(data["ref"]) if "ref" in data and data.get("ref") is not None else None,
                            active=data.get("active") if isinstance(data.get("active"), bool) else None,
                        ),
                        request_id=request_id,
                    )
                    status_code = 200
                    return
                if self.path == "/skills/import":
                    _json_response(self, 200, skills_import_payload(project_root or Path("."), str(data["slug"]), limit=int(data.get("limit", 5)), active=data.get("active") if isinstance(data.get("active"), bool) else None), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/lock/import":
                    _json_response(self, 200, skills_lock_import_payload(project_root or Path("."), input_path, sync_existing=bool(data.get("sync_existing", False))), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/sync":
                    _json_response(self, 200, skills_sync_payload(project_root or Path("."), str(data["slug"]) if "slug" in data and data.get("slug") is not None else None, all_sources=bool(data.get("all", False))), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/remove":
                    _json_response(self, 200, skills_remove_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/activate":
                    _json_response(self, 200, skills_activate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/deactivate":
                    _json_response(self, 200, skills_deactivate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/enterprise/ingest":
                    _json_response(
                        self,
                        200,
                        enterprise_ingest_payload(
                            project_root or Path("."),
                            name=str(data["name"]),
                            path=local_source_path,
                            git_url=remote_git_url,
                            url=remote_url,
                            ref=str(data["ref"]) if "ref" in data and data.get("ref") is not None else None,
                            activate=data.get("activate") if isinstance(data.get("activate"), bool) else None,
                            kind=str(data.get("kind", "enterprise")),
                        ),
                        request_id=request_id,
                    )
                    status_code = 200
                    return
                if self.path == "/enterprise/generate":
                    _json_response(self, 200, enterprise_generate_payload(project_root or Path("."), name=str(data["name"]), source_paths=source_paths, kind=str(data.get("kind", "domain")), activate=bool(data.get("activate", True))), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/connectors/activate":
                    _json_response(self, 200, connectors_activate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/connectors/deactivate":
                    _json_response(self, 200, connectors_deactivate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/jobs/deliver":
                    _json_response(self, 202, create_deliver_job(requirements_path, project_root or Path(".")), request_id=request_id)
                    status_code = 202
                    return
                if self.path.startswith("/jobs/") and self.path.endswith("/cancel"):
                    parts = self.path.strip("/").split("/")
                    _json_response(self, 200, cancel_job_payload(parts[1], project_root), request_id=request_id)
                    status_code = 200
                    return
                if self.path.startswith("/jobs/") and self.path.endswith("/resume"):
                    parts = self.path.strip("/").split("/")
                    _json_response(self, 202, resume_job_payload(parts[1], project_root), request_id=request_id)
                    status_code = 202
                    return
                _json_response(self, 404, {"error": "not_found"}, request_id=request_id)
                status_code = 404
            except Exception as exc:  # noqa: BLE001
                status_code = self._handle_exception(exc, request_id=request_id, project_root=project_root)
            finally:
                self._finish_request(
                    status_code=status_code,
                    request_id=request_id,
                    project_root=project_root,
                    start_time=start_time,
                    principal=principal,
                )

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

    return SkilgenHandler


def create_server(host: str = "127.0.0.1", port: int = 8000) -> BoundedThreadPoolHTTPServer:
    _ensure_logging()
    os.environ.setdefault("SKILGEN_REDACT_MODEL_ERRORS", "1")
    for allowed_root in _allowed_project_roots():
        prune_runtime_data(allowed_root)
    return BoundedThreadPoolHTTPServer((host, port), create_handler())


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(host, port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
