from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import desc, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import digest as legacy_digest
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
from apps.api.api.v8.flags import is_v8, request_flag_cache
from apps.api.api.v8.settings.anthropic_compliance_adapter import pull_anthropic_compliance_events
from apps.api.api.v8.settings.connectors_registry import connector_registry
from apps.api.api.v8.settings.openai_compliance_adapter import pull_openai_compliance_events
from apps.api.api.v8.settings.rbac import PERMISSIONS, has_permission, require_permission
from packages.db.database import get_db, get_sessionmaker
from packages.db.llm_key import decrypt_key, encrypt_key, key_hint
from packages.db.models import AuditEvent, DigestConfig, Job, Org, PullRequest, Repo, Role, RoleBinding, SourceConnection
from packages.db.models.base import new_uuid


router = APIRouter(
    prefix="/v8/orgs/{org_id}/settings",
    tags=["v8-settings"],
    dependencies=[Depends(request_flag_cache)],
)

DEFAULT_DIGEST_WIDGETS = [
    "memory_score",
    "agent_loads",
    "active_repos",
    "top_skill",
    "skill_gaps",
    "roi_multiplier",
]
ADMIN_AUDIT_ROLLUP_LIMIT = 5000
BILLING_UNLIMITED_SEAT_LIMIT = 999999
BILLING_ATTENTION_STATUSES = {"past_due", "unpaid", "incomplete", "incomplete_expired"}


class RolePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    permissions: list[str] = Field(default_factory=list)


class BindingPayload(BaseModel):
    role_id: str
    principal_type: Literal["user", "team"] = "user"
    principal_id: str = Field(min_length=1, max_length=255)
    scope_expression: dict[str, object] | str | None = Field(default_factory=dict)


class PermissionCheckPayload(BaseModel):
    principal_id: str
    permission: str
    scope: dict[str, object] = Field(default_factory=dict)


class DigestConfigPayload(BaseModel):
    title: str = Field(default="Weekly AI Readiness Digest", min_length=1, max_length=255)
    subject: str = Field(default="Your Weekly AI Readiness Report", min_length=1, max_length=255)
    frequency: str = Field(default="weekly", max_length=32)
    recipients: list[str] = Field(default_factory=list)
    widgets: list[str] = Field(default_factory=list)
    layout: dict[str, object] = Field(default_factory=dict)


class DigestPreviewPayload(BaseModel):
    config: DigestConfigPayload | None = None


class DigestSendNowPayload(BaseModel):
    recipient_email: str | None = None
    config: DigestConfigPayload | None = None


class AgentComplianceConnectorPayload(BaseModel):
    connector_id: str = Field(min_length=1, max_length=64)
    enabled: bool = True
    source_types: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    credentials: dict[str, Any] | None = None
    credential_kind: Literal["api_token", "oauth", "webhook", "local_hook", "none"] = "none"
    cursor: str | None = Field(default=None, max_length=512)
    last_sync_status: Literal["pending", "success", "failed"] | None = None
    content_retention: Literal["metadata-only", "tenant-enabled-content"] = "metadata-only"


class AgentComplianceCredentialTestResponse(BaseModel):
    connector_id: str
    success: bool
    status: Literal["missing", "configured", "connected", "failed"]
    credential_state: Literal["missing", "encrypted", "legacy-migrated"]
    credential_kind: str | None = None
    credential_hint: dict[str, Any] = Field(default_factory=dict)
    message: str
    tested_at: datetime


class AgentComplianceSyncPayload(BaseModel):
    cursor: str | None = Field(default=None, max_length=512)
    dry_run: bool = True


class AgentComplianceSyncResponse(BaseModel):
    connector_id: str
    status: Literal["pending", "success", "failed"]
    mode: Literal["dry-run", "provider-pull", "fixture"]
    cursor: str | None = None
    next_cursor: str | None = None
    next_cursor_required: bool
    provider_adapter_required: bool = True
    pagination_strategy: str
    retention_window_days: int
    retention_deadline_at: str
    content_retention: Literal["metadata-only"] = "metadata-only"
    source_record_type: Literal["formal-compliance", "operational-telemetry"]
    ready_for_provider_pull: bool
    blocked_reason: str
    next_actions: list[str]
    ingested_count: int = 0
    skipped_count: int = 0
    metrics: dict[str, Any] = Field(default_factory=dict)


class AgentComplianceEventPayload(BaseModel):
    provider_event_id: str = Field(min_length=1, max_length=255)
    event_type: str = Field(default="agent.compliance", max_length=128)
    actor_login: str | None = Field(default=None, max_length=128)
    occurred_at: datetime | None = None
    provider: str | None = Field(default=None, max_length=128)
    model: str | None = Field(default=None, max_length=128)
    model_tier: str | None = Field(default=None, max_length=64)
    intelligence_tier: Literal["very-high", "high", "medium", "low"] | None = None
    access_scope: str | None = Field(default=None, max_length=128)
    full_access: bool = False
    autonomous_access: bool = False
    tool_permissions: list[str] = Field(default_factory=list)
    tool_calls: int | None = Field(default=None, ge=0)
    mcp_tools: list[str] = Field(default_factory=list)
    repo_id: str | None = Field(default=None, max_length=128)
    repo_name: str | None = Field(default=None, max_length=255)
    file_targets: list[str] = Field(default_factory=list)
    policy_decision: str | None = Field(default=None, max_length=64)
    approval_status: str | None = Field(default=None, max_length=64)
    violations: list[str] = Field(default_factory=list)
    warnings: int | None = Field(default=None, ge=0)
    tokens_input: int | None = Field(default=None, ge=0)
    tokens_output: int | None = Field(default=None, ge=0)
    tokens_cached_input: int | None = Field(default=None, ge=0)
    tokens_reasoning_output: int | None = Field(default=None, ge=0)
    tokens_base_input: int | None = Field(default=None, ge=0)
    tokens_cache_creation_input: int | None = Field(default=None, ge=0)
    tokens_cache_creation_5m_input: int | None = Field(default=None, ge=0)
    tokens_cache_creation_1h_input: int | None = Field(default=None, ge=0)
    tokens_cache_read_input: int | None = Field(default=None, ge=0)
    token_source: str | None = Field(default=None, max_length=128)
    cost_usd: float | None = Field(default=None, ge=0)
    cost_source: str | None = Field(default=None, max_length=128)
    cost_estimate: bool = False
    latency_ms: int | None = Field(default=None, ge=0)
    error_count: int | None = Field(default=None, ge=0)
    session_id: str | None = Field(default=None, max_length=255)
    source_record_type: Literal["formal-compliance", "operational-telemetry"] = "formal-compliance"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentComplianceIngestPayload(BaseModel):
    cursor: str | None = Field(default=None, max_length=512)
    next_cursor: str | None = Field(default=None, max_length=512)
    events: list[AgentComplianceEventPayload] = Field(default_factory=list, max_length=500)


class AgentComplianceIngestResponse(BaseModel):
    connector_id: str
    ingested_count: int
    skipped_count: int
    next_cursor: str | None = None
    content_retention: Literal["metadata-only"] = "metadata-only"
    metrics: dict[str, Any]


class AgentComplianceIngestJobResponse(BaseModel):
    job_id: str
    connector_id: str
    status: str
    queued: bool
    cursor: str | None = None
    next_cursor: str | None = None
    event_count: int
    content_retention: Literal["metadata-only"] = "metadata-only"


class AgentComplianceSyncJobResponse(BaseModel):
    job_id: str
    connector_id: str
    status: str
    queued: bool
    cursor: str | None = None
    next_sync_at: str | None = None
    content_retention: Literal["metadata-only"] = "metadata-only"


class AgentComplianceIngestJobStatusResponse(BaseModel):
    job_id: str
    connector_id: str
    status: str
    result: dict[str, Any]
    created_at: datetime


RAW_CONTENT_KEYS = {
    "prompt",
    "prompts",
    "chat",
    "chat_content",
    "messages",
    "message_content",
    "file_content",
    "content",
    "diff",
    "patch",
    "tool_parameters",
    "tool_args",
    "arguments",
    "params",
    "input",
    "raw",
    "raw_event",
}
AGENT_COMPLIANCE_SOURCE_PREFIX = "agent_compliance:"
SECRET_FIELD_NAMES = {
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "token",
    "client_secret",
    "secret",
    "password",
    "private_key",
    "webhook_secret",
}
SAFE_CREDENTIAL_CONTEXT_KEYS = {
    "base_url",
    "endpoint",
    "url",
    "tenant_id",
    "workspace_id",
    "org_id",
    "organization_id",
    "installation_id",
    "account_id",
    "region",
}


async def _assert_v8_org(org_id: str, current_org_id: str, db: AsyncSession) -> None:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="v8 Settings is disabled")


def _role_response(role: Role) -> dict[str, object]:
    return {
        "id": role.id,
        "org_id": role.org_id,
        "name": role.name,
        "description": role.description,
        "permissions": list(role.permissions or []),
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }


def _binding_response(binding: RoleBinding, role: Role | None = None) -> dict[str, object]:
    return {
        "id": binding.id,
        "org_id": binding.org_id,
        "role_id": binding.role_id,
        "role_name": role.name if role else None,
        "principal_type": binding.principal_type,
        "principal_id": binding.principal_id,
        "scope_expression": binding.scope_expression or {},
        "created_at": binding.created_at,
        "updated_at": binding.updated_at,
    }


def _digest_response(config: DigestConfig) -> dict[str, object]:
    return {
        "id": config.id,
        "org_id": config.org_id,
        "title": config.title,
        "subject": config.subject,
        "frequency": config.frequency,
        "recipients": list(config.recipients or []),
        "widgets": list(config.widgets or DEFAULT_DIGEST_WIDGETS),
        "layout": dict(config.layout or {}),
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }


def _legacy_digest_config(payload: DigestConfigPayload | None) -> legacy_digest.DigestConfigBody | None:
    if payload is None:
        return None
    return legacy_digest.DigestConfigBody(**payload.model_dump())


def _billing_response(org: Org) -> dict[str, object]:
    seat_count = int(org.seat_count or 0)
    seat_limit = int(org.plan_seat_limit or 0)
    finite_limit = seat_limit if 0 < seat_limit < BILLING_UNLIMITED_SEAT_LIMIT else None
    available_seats = max(finite_limit - seat_count, 0) if finite_limit is not None else None
    seat_utilization_pct = round((seat_count / finite_limit) * 100) if finite_limit else 0
    subscription_status = org.stripe_subscription_status or ("free" if org.plan == "free" else "not_configured")
    billing_account_connected = bool(org.stripe_customer_id)
    needs_attention = bool(getattr(org, "is_suspended", False)) or subscription_status in BILLING_ATTENTION_STATUSES
    actions: list[str] = []
    if not billing_account_connected and org.plan != "free":
        actions.append("connect_stripe_customer")
    if subscription_status in BILLING_ATTENTION_STATUSES:
        actions.append("review_payment_method")
    if finite_limit is not None and available_seats == 0:
        actions.append("increase_seat_limit")
    if not actions:
        actions.append("monitor_usage")

    return {
        "plan": org.plan,
        "seat_count": seat_count,
        "seat_limit": seat_limit,
        "seat_limit_label": "Unlimited" if finite_limit is None else str(finite_limit),
        "available_seats": available_seats,
        "seat_utilization_pct": seat_utilization_pct,
        "stripe_customer_id": org.stripe_customer_id,
        "stripe_subscription_id": org.stripe_subscription_id,
        "stripe_subscription_status": org.stripe_subscription_status,
        "subscription_state": subscription_status,
        "billing_account_connected": billing_account_connected,
        "portal_available": billing_account_connected,
        "needs_attention": needs_attention,
        "next_actions": actions,
    }


def _sso_response(org: Org) -> dict[str, object]:
    settings = org.settings if isinstance(org.settings, dict) else {}
    workos_linked = bool(org.workos_org_id)
    oidc_enabled = bool(settings.get("oidc_enabled"))
    scim_enabled = bool(settings.get("scim_enabled"))
    saml_enabled = workos_linked
    ready = workos_linked and (saml_enabled or oidc_enabled)
    next_actions: list[str] = []
    if not workos_linked:
        next_actions.append("link_workos_organization")
    if not saml_enabled and not oidc_enabled:
        next_actions.append("configure_identity_protocol")
    if workos_linked and not scim_enabled:
        next_actions.append("review_scim_provisioning")
    if not next_actions:
        next_actions.append("monitor_identity_sync")

    return {
        "workos_org_id": org.workos_org_id,
        "saml_enabled": saml_enabled,
        "oidc_enabled": oidc_enabled,
        "scim_enabled": scim_enabled,
        "managed_by": "WorkOS",
        "ready": ready,
        "connection_state": "linked" if workos_linked else "not_linked",
        "protocols_enabled": [protocol for protocol, enabled in (("SAML", saml_enabled), ("OIDC", oidc_enabled)) if enabled],
        "provisioning_state": "enabled" if scim_enabled else "not_configured",
        "next_actions": next_actions,
    }


def _agent_compliance_registry() -> list[dict[str, Any]]:
    return [
        item
        for item in connector_registry()
        if item.get("category") in {"compliance-telemetry", "coding-agent", "ci-cd"} or item.get("id") == "internal-mcp"
    ]


def _agent_connection_source_type(connector_id: str) -> str:
    return f"{AGENT_COMPLIANCE_SOURCE_PREFIX}{connector_id}"


def _is_secret_field(key: str) -> bool:
    lowered = key.lower()
    return lowered in SECRET_FIELD_NAMES or any(part in lowered for part in ("token", "secret", "password", "private_key"))


def _credential_params_hint(params: dict[str, Any]) -> dict[str, Any]:
    hint: dict[str, Any] = {}
    for key, value in params.items():
        if _is_secret_field(key):
            if isinstance(value, str) and value:
                hint[f"{key}_hint"] = key_hint(value)
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            hint[key] = value
    return hint


def _encrypt_agent_credentials(params: dict[str, Any]) -> str:
    return encrypt_key(json.dumps(params, sort_keys=True, default=str))


def _decrypt_agent_credentials(connection: SourceConnection | None) -> dict[str, Any]:
    if connection is None:
        return {}
    try:
        decoded = json.loads(decrypt_key(connection.encrypted_params))
        return decoded if isinstance(decoded, dict) else {}
    except Exception:
        return {}


def _extract_legacy_credentials(row: dict[str, object]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for nested_key in ("credentials", "credential", "params", "provider_params"):
        nested = row.get(nested_key)
        if isinstance(nested, dict):
            params.update({str(key): value for key, value in nested.items()})
    for key, value in row.items():
        key_str = str(key)
        if _is_secret_field(key_str) or key_str in SAFE_CREDENTIAL_CONTEXT_KEYS:
            params[key_str] = value
    return {key: value for key, value in params.items() if value not in (None, "")}


def _settings_row_without_credentials(row: dict[str, object]) -> dict[str, object]:
    clean: dict[str, object] = {}
    for key, value in row.items():
        key_str = str(key)
        if key_str in {"credentials", "credential", "params", "provider_params"} or _is_secret_field(key_str):
            continue
        clean[key_str] = value
    return clean


async def _agent_credential_connection(db: AsyncSession, org_id: str, connector_id: str) -> SourceConnection | None:
    try:
        return (
            await db.execute(
                select(SourceConnection).where(
                    SourceConnection.org_id == org_id,
                    SourceConnection.source_type == _agent_connection_source_type(connector_id),
                )
            )
        ).scalar_one_or_none()
    except SQLAlchemyError:
        info = getattr(db, "info", None)
        if isinstance(info, dict):
            info["agent_credential_store_unavailable"] = True
        return None


async def _upsert_agent_credential_connection(
    db: AsyncSession,
    org_id: str,
    connector_id: str,
    *,
    credentials: dict[str, Any],
    credential_kind: str,
    display_name: str | None = None,
    status: str = "configured",
) -> SourceConnection:
    now = datetime.utcnow()
    connection = await _agent_credential_connection(db, org_id, connector_id)
    if connection is None:
        connection = SourceConnection(
            org_id=org_id,
            source_type=_agent_connection_source_type(connector_id),
            created_at=now,
        )
    connection.display_name = display_name or connector_id
    connection.status = status
    connection.encrypted_params = _encrypt_agent_credentials(credentials)
    connection.params_hint = {
        **_credential_params_hint(credentials),
        "connector_id": connector_id,
        "credential_kind": credential_kind,
        "stored_for": "agent_compliance_provider",
    }
    connection.last_tested_at = now
    connection.last_connected_at = now if status in {"connected", "configured"} else connection.last_connected_at
    connection.last_error = None if status in {"connected", "configured"} else "Credential test failed"
    connection.updated_at = now
    db.add(connection)
    return connection


async def _migrate_legacy_agent_credentials(
    db: AsyncSession,
    org: Org,
    configured: dict[str, dict[str, object]],
) -> tuple[dict[str, dict[str, object]], dict[str, SourceConnection], bool]:
    connections: dict[str, SourceConnection] = {}
    changed = False
    for connector_id, row in list(configured.items()):
        connection = await _agent_credential_connection(db, org.id, connector_id)
        info = getattr(db, "info", None)
        if isinstance(info, dict) and info.get("agent_credential_store_unavailable"):
            return configured, connections, changed
        if connection is None:
            legacy_credentials = _extract_legacy_credentials(row)
            if legacy_credentials:
                connection = await _upsert_agent_credential_connection(
                    db,
                    org.id,
                    connector_id,
                    credentials=legacy_credentials,
                    credential_kind=str(row.get("credential_kind") or "api_token"),
                    display_name=str(row.get("display_name") or connector_id),
                    status="configured",
                )
                configured[connector_id] = {
                    **_settings_row_without_credentials(row),
                    "credential_migrated_at": datetime.utcnow().isoformat(),
                }
                changed = True
        else:
            sanitized = _settings_row_without_credentials(row)
            if sanitized != row:
                configured[connector_id] = sanitized
                changed = True
        if connection is not None:
            connections[connector_id] = connection
    if changed:
        settings = dict(org.settings or {})
        settings["v8_agent_compliance_connectors"] = configured
        org.settings = settings
        flag_modified(org, "settings")
    return configured, connections, changed


def _agent_connector_settings(org: Org | None) -> dict[str, dict[str, object]]:
    settings = dict(getattr(org, "settings", None) or {}) if org else {}
    raw = settings.get("v8_agent_compliance_connectors")
    if not isinstance(raw, dict):
        return {}
    return {str(key): dict(value) for key, value in raw.items() if isinstance(value, dict)}


def _agent_sync_contract(connector_id: str, connector: dict[str, Any], row: dict[str, object], cursor: str | None) -> dict[str, object]:
    category = str(connector.get("category") or "")
    retention_window_days = 30 if connector_id in {"openai-compliance", "anthropic-compliance"} else 7
    source_record_type = "formal-compliance" if category == "compliance-telemetry" and connector_id != "claude-cowork-otel" else "operational-telemetry"
    source_types = list(row.get("source_types") or connector.get("capabilities") or [])
    scopes = list(row.get("scopes") or [])
    next_actions = [
        "Attach encrypted provider credentials or tenant-authorized telemetry hook.",
        "Run provider adapter with cursor resume and page-by-page ingest into metadata-only normalized events.",
        "Persist next cursor only after each page is normalized without raw prompt, chat, file content, diff, or tool-parameter storage.",
    ]
    if connector_id in {"openai-compliance", "anthropic-compliance"}:
        next_actions.insert(1, "Schedule continuous pulls before the 30-day compliance-log retention window expires.")
    elif connector_id == "claude-cowork-otel":
        next_actions.insert(1, "Route OpenTelemetry spans as operational telemetry because Cowork is not covered by Anthropic compliance logs.")
    else:
        next_actions.insert(1, "Install local or enterprise agent telemetry hook for sessions, tools, files, model tier, and approvals.")
    ready = bool(row.get("enabled")) and bool(scopes or source_types)
    return {
        "connector_id": connector_id,
        "status": "pending",
        "mode": "dry-run",
        "cursor": cursor,
        "next_cursor_required": bool(cursor),
        "provider_adapter_required": True,
        "pagination_strategy": "cursor-resume",
        "retention_window_days": retention_window_days,
        "retention_deadline_at": (datetime.now(UTC) + timedelta(days=retention_window_days)).isoformat(),
        "content_retention": "metadata-only",
        "source_record_type": source_record_type,
        "ready_for_provider_pull": ready,
        "blocked_reason": "provider adapter and credentials are required before live pulls" if ready else "connector setup is incomplete",
        "next_actions": next_actions,
    }


async def _agent_connector_response(db: AsyncSession, org: Org | None) -> dict[str, object]:
    configured = _agent_connector_settings(org)
    credential_connections: dict[str, SourceConnection] = {}
    source_connections: list[SourceConnection] = []
    if org is not None:
        configured, credential_connections, changed = await _migrate_legacy_agent_credentials(db, org, configured)
        if changed:
            flush = getattr(db, "flush", None)
            if flush is not None:
                await flush()
        try:
            source_connections = (await db.execute(select(SourceConnection).where(SourceConnection.org_id == org.id))).scalars().all()
        except SQLAlchemyError:
            source_connections = []
    connectors: list[dict[str, object]] = []
    for item in _agent_compliance_registry():
        connector_id = str(item["id"])
        row = configured.get(connector_id) or {}
        credential_connection = credential_connections.get(connector_id)
        if credential_connection is None and org is not None:
            credential_connection = await _agent_credential_connection(db, org.id, connector_id)
        enabled = bool(row.get("enabled"))
        sync_plan = row.get("last_sync_plan")
        if not isinstance(sync_plan, dict):
            sync_plan = None
        credential_hint = credential_connection.params_hint if credential_connection is not None and isinstance(credential_connection.params_hint, dict) else {}
        credential_state = "encrypted" if credential_connection is not None else "missing"
        connectors.append(
            {
                **item,
                "configured": connector_id in configured,
                "enabled": enabled,
                "connected": credential_connection is not None,
                "connection_status": credential_connection.status if credential_connection is not None else None,
                "credential_state": credential_state,
                "credential_kind": credential_hint.get("credential_kind") if credential_hint else row.get("credential_kind"),
                "credential_hint": credential_hint,
                "credential_source_type": _agent_connection_source_type(connector_id),
                "last_tested_at": credential_connection.last_tested_at if credential_connection is not None else None,
                "last_connected_at": credential_connection.last_connected_at if credential_connection is not None else None,
                "last_error": credential_connection.last_error if credential_connection is not None else None,
                "source_types": list(row.get("source_types") or []),
                "scopes": list(row.get("scopes") or []),
                "last_cursor": row.get("cursor"),
                "last_sync_status": row.get("last_sync_status") or ("pending" if enabled else None),
                "last_sync_requested_at": row.get("last_sync_requested_at"),
                "last_sync_mode": row.get("last_sync_mode"),
                "last_sync_plan": sync_plan,
                "last_provider_sync_job": row.get("last_provider_sync_job") if isinstance(row.get("last_provider_sync_job"), dict) else None,
                "next_sync_at": row.get("next_sync_at"),
                "last_success_at": row.get("last_success_at"),
                "last_failure_at": row.get("last_failure_at"),
                "last_ingested_at": row.get("last_ingested_at"),
                "last_ingested_count": int(row.get("last_ingested_count") or 0),
                "total_ingested_count": int(row.get("total_ingested_count") or 0),
                "last_provider_event_id": row.get("last_provider_event_id"),
                "content_retention": row.get("content_retention") or "metadata-only",
                "updated_at": row.get("updated_at"),
            }
        )
    return {
        "content_retention_default": "metadata-only",
        "configured_count": sum(1 for item in connectors if item["configured"]),
        "enabled_count": sum(1 for item in connectors if item["enabled"]),
        "enterprise_setup": _enterprise_setup_response(org, connectors, source_connections),
        "connectors": connectors,
    }


def _enterprise_setup_response(org: Org | None, connectors: list[dict[str, object]], source_connections: list[SourceConnection]) -> dict[str, object]:
    by_id = {str(item.get("id")): item for item in connectors}
    openai = by_id.get("openai-compliance") or {}
    anthropic = by_id.get("anthropic-compliance") or {}
    normalized_connections = [item[0] if isinstance(item, tuple) else item for item in source_connections]
    github_connected = any(connection.source_type == "github" and connection.status in {"connected", "configured", "active"} for connection in normalized_connections)
    if not github_connected:
        settings = dict(getattr(org, "settings", None) or {}) if org else {}
        github_connected = bool(settings.get("github_app_installed") or settings.get("github_connected") or settings.get("github_installation_id"))

    def provider_configured(connector: dict[str, object]) -> bool:
        return bool(connector.get("enabled")) and connector.get("credential_state") in {"encrypted", "legacy-migrated"}

    def provider_tested(connector: dict[str, object]) -> bool:
        return provider_configured(connector) and bool(connector.get("last_tested_at"))

    def provider_synced(connector: dict[str, object]) -> bool:
        return provider_configured(connector) and (connector.get("last_sync_status") == "success" or bool(connector.get("last_success_at")))

    providers_configured = provider_configured(openai) and provider_configured(anthropic)
    providers_tested = provider_tested(openai) and provider_tested(anthropic)
    providers_synced = provider_synced(openai) and provider_synced(anthropic)

    provider_gaps = []
    for connector_id, connector in (("openai-compliance", openai), ("anthropic-compliance", anthropic)):
        if not connector:
            provider_gaps.append(f"{connector_id}: connector catalog missing")
        elif connector.get("credential_state") not in {"encrypted", "legacy-migrated"}:
            provider_gaps.append(f"{connector.get('label', connector_id)}: encrypted credential missing")
        elif not connector.get("last_tested_at"):
            provider_gaps.append(f"{connector.get('label', connector_id)}: credential test not run")
        elif not provider_synced(connector):
            provider_gaps.append(f"{connector.get('label', connector_id)}: provider sync not successful yet")

    coverage_gaps: list[dict[str, object]] = []
    if not github_connected:
        coverage_gaps.append(
            {
                "id": "github-app",
                "label": "GitHub App is not connected",
                "severity": "high",
                "next_action": "Install the GitHub App so provider runs can join to repos, PRs, commits, and branches.",
            }
        )
    for index, gap in enumerate(provider_gaps):
        coverage_gaps.append(
            {
                "id": f"provider-{index}",
                "label": gap,
                "severity": "medium",
                "next_action": "Connect credentials, test them, then start provider sync.",
            }
        )

    steps = [
        {
            "id": "install-github-app",
            "label": "Install GitHub App",
            "status": "complete" if github_connected else "blocked",
            "detail": "Required for repo, PR, commit, and branch enrichment.",
            "next_action": "Install GitHub App" if not github_connected else "Monitor GitHub enrichment",
        },
        {
            "id": "connect-openai",
            "label": "Connect OpenAI",
            "status": "complete" if provider_configured(openai) else "blocked",
            "detail": "Store encrypted OpenAI Compliance API credentials.",
            "next_action": "Connect OpenAI" if not provider_configured(openai) else "Test OpenAI credentials",
        },
        {
            "id": "connect-anthropic",
            "label": "Connect Anthropic",
            "status": "complete" if provider_configured(anthropic) else "blocked",
            "detail": "Store encrypted Anthropic Compliance API credentials.",
            "next_action": "Connect Anthropic" if not provider_configured(anthropic) else "Test Anthropic credentials",
        },
        {
            "id": "test-connections",
            "label": "Test connections",
            "status": "complete" if providers_tested else ("pending" if providers_configured else "blocked"),
            "detail": "Credential tests prove Skillayer can reach the provider vault entry.",
            "next_action": (
                "Monitor credential health"
                if providers_tested
                else ("Test connection" if providers_configured else "Connect provider credentials")
            ),
        },
        {
            "id": "start-sync",
            "label": "Start sync",
            "status": "complete" if providers_synced else ("pending" if providers_tested else "blocked"),
            "detail": "Provider sync pulls metadata-only compliance records with cursors.",
            "next_action": (
                "Monitor sync freshness"
                if providers_synced
                else ("Start sync" if providers_tested else "Finish credential tests")
            ),
        },
        {
            "id": "review-coverage",
            "label": "Review coverage gaps",
            "status": "complete" if not coverage_gaps else "pending",
            "detail": "Coverage gaps explain what is still missing before automatic developer rollups are trustworthy.",
            "next_action": "Review coverage gaps" if coverage_gaps else "Monitor connector health",
        },
    ]
    return {
        "setup_complete": all(step["status"] == "complete" for step in steps),
        "github_connected": github_connected,
        "required_provider_ids": ["openai-compliance", "anthropic-compliance"],
        "steps": steps,
        "coverage_gaps": coverage_gaps,
    }


async def _test_agent_credentials(db: AsyncSession, org_id: str, connector_id: str) -> AgentComplianceCredentialTestResponse:
    connection = await _agent_credential_connection(db, org_id, connector_id)
    tested_at = datetime.utcnow()
    if connection is None:
        return AgentComplianceCredentialTestResponse(
            connector_id=connector_id,
            success=False,
            status="missing",
            credential_state="missing",
            message="No encrypted credentials are stored for this connector.",
            tested_at=tested_at,
        )
    params = _decrypt_agent_credentials(connection)
    has_secret = any(_is_secret_field(key) and bool(value) for key, value in params.items())
    success = bool(params and has_secret)
    connection.last_tested_at = tested_at
    connection.status = "configured" if success else "failed"
    connection.last_error = None if success else "Stored credential bundle does not include an API token, OAuth token, secret, or password."
    connection.updated_at = tested_at
    db.add(connection)
    return AgentComplianceCredentialTestResponse(
        connector_id=connector_id,
        success=success,
        status="configured" if success else "failed",
        credential_state="encrypted",
        credential_kind=(connection.params_hint or {}).get("credential_kind") if isinstance(connection.params_hint, dict) else None,
        credential_hint=connection.params_hint if isinstance(connection.params_hint, dict) else {},
        message="Encrypted credentials are present and ready for provider adapter use." if success else connection.last_error or "Credential test failed.",
        tested_at=tested_at,
    )


async def _load_or_create_digest_config(db: AsyncSession, org_id: str) -> DigestConfig:
    config = (await db.execute(select(DigestConfig).where(DigestConfig.org_id == org_id))).scalar_one_or_none()
    if config is not None:
        if not config.widgets:
            config.widgets = DEFAULT_DIGEST_WIDGETS
        return config
    config = DigestConfig(
        org_id=org_id,
        widgets=DEFAULT_DIGEST_WIDGETS,
        recipients=[],
        layout={"columns": 2},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(config)
    await db.flush()
    return config


def _metadata_without_raw_content(metadata: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in metadata.items():
        if key.lower() in RAW_CONTENT_KEYS:
            continue
        if isinstance(value, dict):
            clean[key] = _metadata_without_raw_content(value)
        elif isinstance(value, list):
            clean[key] = [
                _metadata_without_raw_content(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            clean[key] = value
    return clean


def _normalized_event_metadata(
    connector_id: str,
    event: AgentComplianceEventPayload,
    actor_login: str | None = None,
    github_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = event.provider or connector_id
    model_tier = event.intelligence_tier or event.model_tier
    resolved_actor = event.actor_login or actor_login
    sanitized_envelope = {
        "connector_id": connector_id,
        "provider_event_id": event.provider_event_id,
        "event_type": event.event_type,
        "actor_login": resolved_actor,
        "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None,
        "provider": provider,
        "model": event.model,
        "intelligence_tier": model_tier,
        "access_scope": event.access_scope,
        "repo_id": event.repo_id,
        "repo_name": event.repo_name,
        "file_targets": event.file_targets,
        "tool_permissions": event.tool_permissions,
        "mcp_tools": event.mcp_tools,
        "policy_decision": event.policy_decision,
        "approval_status": event.approval_status,
        "source_record_type": event.source_record_type,
    }
    envelope_hash = hashlib.sha256(json.dumps(sanitized_envelope, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    metadata = {
        **_metadata_without_raw_content(event.metadata),
        "connector_id": connector_id,
        "provider": provider,
        "agent_provider": provider,
        "provider_event_id": event.provider_event_id,
        "actor_login": resolved_actor,
        "source_record_type": event.source_record_type,
        "formal_compliance_record": event.source_record_type == "formal-compliance",
        "model": event.model,
        "model_tier": event.model_tier,
        "intelligence_tier": model_tier,
        "access_scope": event.access_scope,
        "full_access": event.full_access or event.access_scope == "full-access",
        "autonomous_access": event.autonomous_access,
        "tool_permissions": event.tool_permissions,
        "tool_calls": event.tool_calls,
        "mcp_tools": event.mcp_tools,
        "repo_id": event.repo_id,
        "repo_name": event.repo_name,
        "file_targets": event.file_targets,
        "policy_decision": event.policy_decision,
        "approval_status": event.approval_status,
        "violations": event.violations,
        "warnings": event.warnings,
        "tokens_input": event.tokens_input,
        "tokens_output": event.tokens_output,
        "tokens_total": (event.tokens_input or 0) + (event.tokens_output or 0) if event.tokens_input is not None or event.tokens_output is not None else None,
        "tokens_cached_input": event.tokens_cached_input,
        "tokens_reasoning_output": event.tokens_reasoning_output,
        "tokens_base_input": event.tokens_base_input,
        "tokens_cache_creation_input": event.tokens_cache_creation_input,
        "tokens_cache_creation_5m_input": event.tokens_cache_creation_5m_input,
        "tokens_cache_creation_1h_input": event.tokens_cache_creation_1h_input,
        "tokens_cache_read_input": event.tokens_cache_read_input,
        "token_source": event.token_source or event.metadata.get("token_source"),
        "cost_usd": event.cost_usd,
        "cost_source": event.cost_source or event.metadata.get("cost_source") or ("provider_reported" if event.cost_usd is not None else None),
        "cost_estimate": event.cost_estimate,
        "latency_ms": event.latency_ms,
        "error_count": event.error_count,
        "session_id": event.session_id,
        "source_envelope_hash": envelope_hash,
        "content_retention": "metadata-only",
        "redaction_state": "raw-content-dropped",
    }
    if github_context:
        metadata.update(github_context)
    return {key: value for key, value in metadata.items() if value is not None and value != "" and value != []}


def _metadata_string(metadata: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = metadata.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _metadata_int_value(metadata: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = metadata.get(key)
        if value is None or value == "":
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _github_pr_url(repo_name: str | None, pr_number: int | None) -> str | None:
    if repo_name and pr_number:
        return f"https://github.com/{repo_name}/pull/{pr_number}"
    return None


def _github_commit_url(repo_name: str | None, sha: str | None) -> str | None:
    if repo_name and sha:
        return f"https://github.com/{repo_name}/commit/{sha}"
    return None


async def _provider_github_context(
    db: AsyncSession,
    org_id: str,
    event: AgentComplianceEventPayload,
) -> tuple[str | None, str | None, dict[str, Any]]:
    metadata = _metadata_without_raw_content(event.metadata)
    repo_id = event.repo_id or _metadata_string(metadata, "repo_id")
    repo_name = event.repo_name or _metadata_string(metadata, "repo_name", "repository", "repository_name", "github_repo")
    pr_number = _metadata_int_value(metadata, "pr_number", "pull_request_number", "github_pr_number")
    pr_id = _metadata_string(metadata, "pr_id", "pull_request_id")
    head_sha = _metadata_string(metadata, "head_sha", "commit_sha", "sha")
    branch = _metadata_string(metadata, "branch", "head_branch", "source_branch")
    pr_title = _metadata_string(metadata, "pr_title", "pull_request_title")

    repo: Repo | None = None
    if repo_id:
        repo = (
            await db.execute(
                select(Repo).where(
                    Repo.org_id == org_id,
                    Repo.id == repo_id,
                ).limit(1)
            )
        ).scalar_one_or_none()
    if repo is None and repo_name:
        repo = (
            await db.execute(
                select(Repo)
                .where(
                    Repo.org_id == org_id,
                    or_(Repo.full_name == repo_name, Repo.name == repo_name),
                )
                .limit(1)
            )
        ).scalar_one_or_none()

    resolved_repo_id = getattr(repo, "id", None) or repo_id
    resolved_repo_name = getattr(repo, "full_name", None) or repo_name
    github_context: dict[str, Any] = {
        "repo_id": resolved_repo_id,
        "repo_name": resolved_repo_name,
        "branch": branch,
        "head_sha": head_sha,
        "commit_sha": head_sha,
    }

    has_join_candidate = bool(pr_number or pr_id or head_sha or branch)
    if not has_join_candidate:
        github_context.update(
            {
                "github_enrichment_status": "not_provided",
                "github_enrichment_gap": "Provider event did not include PR, commit, head SHA, or branch metadata.",
            }
        )
        return resolved_repo_id, resolved_repo_name, github_context

    pr: PullRequest | None = None
    pr_lookup_gap: str | None = None
    try:
        if repo is not None and pr_number is not None:
            pr = (
                await db.execute(
                    select(PullRequest)
                    .where(
                        PullRequest.repo_id == repo.id,
                        PullRequest.github_pr_number == pr_number,
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
        if repo is not None and pr is None and pr_id:
            pr = (
                await db.execute(
                    select(PullRequest)
                    .where(
                        PullRequest.repo_id == repo.id,
                        PullRequest.id == pr_id,
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
        if repo is not None and pr is None and head_sha:
            pr = (
                await db.execute(
                    select(PullRequest)
                    .where(
                        PullRequest.repo_id == repo.id,
                        PullRequest.head_sha == head_sha,
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
    except SQLAlchemyError:
        pr_lookup_gap = "GitHub PR/commit tables are unavailable, so provider metadata could not be joined."

    if pr is not None:
        matched_pr_number = getattr(pr, "github_pr_number", None)
        matched_sha = getattr(pr, "head_sha", None) or head_sha
        github_context.update(
            {
                "github_enrichment_status": "matched",
                "github_enrichment_source": "pull_requests",
                "pr_id": getattr(pr, "id", None),
                "pr_number": matched_pr_number,
                "pr_title": getattr(pr, "title", None) or pr_title or (f"PR #{matched_pr_number}" if matched_pr_number else None),
                "head_sha": matched_sha,
                "commit_sha": matched_sha,
                "git_url": _github_pr_url(resolved_repo_name, matched_pr_number) or _github_commit_url(resolved_repo_name, matched_sha),
            }
        )
        return resolved_repo_id, resolved_repo_name, github_context

    github_context.update(
        {
            "github_enrichment_status": "missing",
            "github_enrichment_gap": pr_lookup_gap or "Provider event included GitHub metadata, but no matching PR/commit record was found.",
            "pr_number": pr_number,
            "pr_title": pr_title,
            "git_url": _github_pr_url(resolved_repo_name, pr_number) or _github_commit_url(resolved_repo_name, head_sha),
        }
    )
    return resolved_repo_id, resolved_repo_name, github_context


def _compliance_event_severity(event: AgentComplianceEventPayload) -> str:
    if event.error_count or event.violations or event.policy_decision in {"deny", "denied", "block"}:
        return "critical"
    if event.full_access or event.autonomous_access or event.access_scope == "full-access" or event.warnings:
        return "warning"
    return "info"


def _ingest_metrics(events: list[AgentComplianceEventPayload]) -> dict[str, Any]:
    providers = sorted({event.provider for event in events if event.provider})
    actors = sorted({event.actor_login for event in events if event.actor_login})
    models = sorted({event.model for event in events if event.model})
    tiers: dict[str, int] = {}
    for event in events:
        tier = event.intelligence_tier or event.model_tier
        if tier:
            tiers[tier] = tiers.get(tier, 0) + 1
    return {
        "events": len(events),
        "providers": providers,
        "actors": len(actors),
        "models": models,
        "intelligence_tiers": tiers,
        "full_access_events": sum(1 for event in events if event.full_access or event.access_scope == "full-access"),
        "autonomous_access_events": sum(1 for event in events if event.autonomous_access),
        "tool_permission_events": sum(len(event.tool_permissions) + (event.tool_calls or 0) + len(event.mcp_tools) for event in events),
        "file_targets": sum(len(event.file_targets) for event in events),
        "violations": sum(len(event.violations) for event in events),
        "warnings": sum(event.warnings or 0 for event in events),
        "tokens_input": sum(event.tokens_input or 0 for event in events),
        "tokens_output": sum(event.tokens_output or 0 for event in events),
        "cost_usd": round(sum(event.cost_usd or 0 for event in events), 6),
        "latency_ms": sum(event.latency_ms or 0 for event in events),
        "errors": sum(event.error_count or 0 for event in events),
    }


async def _ingest_agent_compliance_payload(
    db: AsyncSession,
    org: Org,
    connector_id: str,
    payload: AgentComplianceIngestPayload,
    actor_login: str | None,
) -> AgentComplianceIngestResponse:
    org_id = org.id
    settings = dict(org.settings or {})
    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
    current = dict(configured.get(connector_id) or {})
    if not current.get("enabled"):
        raise HTTPException(status_code=409, detail="Agent compliance connector must be enabled before ingest")
    if current.get("content_retention") not in {None, "metadata-only"}:
        raise HTTPException(status_code=400, detail="Only metadata-only ingestion is enabled for this release")

    ingested: list[AgentComplianceEventPayload] = []
    skipped = 0
    for event in payload.events:
        resolved_actor = event.actor_login or actor_login
        resource_id = f"{connector_id}:{event.provider_event_id}"
        existing = (
            await db.execute(
                select(AuditEvent.id).where(
                    AuditEvent.org_id == org_id,
                    AuditEvent.resource_type == "agent_compliance_event",
                    AuditEvent.resource_id == resource_id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        resolved_repo_id, resolved_repo_name, github_context = await _provider_github_context(db, org_id, event)
        metadata = _normalized_event_metadata(connector_id, event, actor_login=actor_login, github_context=github_context)
        db.add(
            AuditEvent(
                org_id=org_id,
                event_type="agent.compliance",
                action="ingested",
                summary=f"Normalized {event.source_record_type.replace('-', ' ')} from {event.provider or connector_id}",
                actor_login=resolved_actor,
                repo_id=resolved_repo_id,
                repo_name=resolved_repo_name,
                resource_type="agent_compliance_event",
                resource_id=resource_id,
                severity=_compliance_event_severity(event),
                metadata_json=metadata,
                created_at=(event.occurred_at or datetime.now(UTC)).replace(tzinfo=None),
            )
        )
        ingested.append(event)

    now = datetime.now(UTC).isoformat()
    current.update(
        {
            "cursor": payload.next_cursor or payload.cursor or current.get("cursor"),
            "last_sync_status": "success",
            "last_sync_mode": "ingest",
            "last_ingested_at": now,
            "last_ingested_count": len(ingested),
            "total_ingested_count": int(current.get("total_ingested_count") or 0) + len(ingested),
            "last_provider_event_id": ingested[-1].provider_event_id if ingested else current.get("last_provider_event_id"),
            "content_retention": "metadata-only",
            "updated_at": now,
        }
    )
    configured[connector_id] = current
    settings["v8_agent_compliance_connectors"] = configured
    org.settings = settings
    flag_modified(org, "settings")

    metrics = _ingest_metrics(ingested)
    await audit.emit(
        db,
        org_id,
        "settings.agent_compliance_events_ingested",
        "ingested",
        f"Ingested {len(ingested)} metadata-only agent compliance events from {connector_id}",
        actor_login=actor_login,
        resource_type="agent_compliance_connector",
        resource_id=connector_id,
        metadata={
            "connector_id": connector_id,
            "ingested_count": len(ingested),
            "skipped_count": skipped,
            "content_retention": "metadata-only",
            "metrics": metrics,
        },
    )
    return AgentComplianceIngestResponse(
        connector_id=connector_id,
        ingested_count=len(ingested),
        skipped_count=skipped,
        next_cursor=payload.next_cursor or payload.cursor,
        metrics=metrics,
    )


async def _run_agent_compliance_ingest_job(
    job_id: str,
    org_id: str,
    connector_id: str,
    payload_data: dict[str, Any],
    actor_login: str | None,
) -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        job = await db.get(Job, job_id)
        org = await db.get(Org, org_id)
        if job is None or org is None:
            return
        job.status = "running"
        result = dict(job.result_json or {})
        result["started_at"] = datetime.now(UTC).isoformat()
        job.result_json = result
        await db.commit()
        try:
            payload = AgentComplianceIngestPayload.model_validate(payload_data)
            response = await _ingest_agent_compliance_payload(db, org, connector_id, payload, actor_login)
            settings = dict(org.settings or {})
            configured = dict(settings.get("v8_agent_compliance_connectors") or {})
            current = dict(configured.get(connector_id) or {})
            last_job = dict(current.get("last_ingest_job") or {})
            last_job.update(
                {
                    "job_id": job_id,
                    "status": "completed",
                    "event_count": int(result.get("event_count") or len(payload.events)),
                    "cursor": payload.cursor,
                    "next_cursor": response.next_cursor,
                    "content_retention": response.content_retention,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "ingested_count": response.ingested_count,
                    "skipped_count": response.skipped_count,
                }
            )
            current["last_ingest_job"] = last_job
            configured[connector_id] = current
            settings["v8_agent_compliance_connectors"] = configured
            org.settings = settings
            flag_modified(org, "settings")
            job.status = "completed"
            job.result_json = {
                **result,
                "completed_at": datetime.now(UTC).isoformat(),
                "ingested_count": response.ingested_count,
                "skipped_count": response.skipped_count,
                "next_cursor": response.next_cursor,
                "metrics": response.metrics,
                "content_retention": response.content_retention,
            }
            await db.commit()
        except Exception as exc:
            await db.rollback()
            job = await db.get(Job, job_id)
            if job is not None:
                org = await db.get(Org, org_id)
                if org is not None:
                    settings = dict(org.settings or {})
                    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
                    current = dict(configured.get(connector_id) or {})
                    last_job = dict(current.get("last_ingest_job") or {})
                    last_job.update(
                        {
                            "job_id": job_id,
                            "status": "failed",
                            "content_retention": "metadata-only",
                            "failed_at": datetime.now(UTC).isoformat(),
                        }
                    )
                    current["last_sync_status"] = "failed"
                    current["last_ingest_job"] = last_job
                    configured[connector_id] = current
                    settings["v8_agent_compliance_connectors"] = configured
                    org.settings = settings
                    flag_modified(org, "settings")
                job.status = "failed"
                job.result_json = {
                    **result,
                    "failed_at": datetime.now(UTC).isoformat(),
                    "error": str(exc),
                    "content_retention": "metadata-only",
                }
                await db.commit()


def _provider_sync_adapter(connector_id: str, credentials: dict[str, Any], cursor: str | None):
    if connector_id == "anthropic-compliance":
        return pull_anthropic_compliance_events(credentials, cursor=cursor, dry_run=False), "Anthropic Compliance", "anthropic_compliance_api"
    if connector_id == "openai-compliance":
        return pull_openai_compliance_events(credentials, cursor=cursor, dry_run=False), "OpenAI Compliance", "openai_compliance_api"
    raise HTTPException(status_code=400, detail="Live provider sync is currently implemented for OpenAI and Anthropic Compliance only")


async def _run_agent_compliance_provider_sync_job(
    job_id: str,
    org_id: str,
    connector_id: str,
    actor_login: str | None,
) -> None:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as db:
        job = await db.get(Job, job_id)
        org = await db.get(Org, org_id)
        if job is None or org is None:
            return
        job.status = "running"
        result = dict(job.result_json or {})
        result["started_at"] = datetime.now(UTC).isoformat()
        job.result_json = result
        await db.commit()
        try:
            settings = dict(org.settings or {})
            configured = dict(settings.get("v8_agent_compliance_connectors") or {})
            current = dict(configured.get(connector_id) or {})
            if not current.get("enabled"):
                raise RuntimeError("Agent compliance connector must be enabled before sync")
            credential_connection = await _agent_credential_connection(db, org_id, connector_id)
            cursor = str(current.get("cursor") or "") or None
            adapter_result, provider_label, token_source = _provider_sync_adapter(
                connector_id,
                _decrypt_agent_credentials(credential_connection),
                cursor,
            )
            connector = next((item for item in _agent_compliance_registry() if item.get("id") == connector_id), {})
            sync_plan = _agent_sync_contract(connector_id, connector, current, cursor)
            sync_plan.update(
                {
                    "status": adapter_result.status,
                    "mode": adapter_result.mode,
                    "cursor": cursor,
                    "next_cursor": adapter_result.next_cursor,
                    "provider_adapter_required": adapter_result.provider_adapter_required,
                    "ready_for_provider_pull": adapter_result.status == "success",
                    "blocked_reason": adapter_result.blocked_reason or "",
                    "next_actions": adapter_result.next_actions,
                    "ingested_count": 0,
                    "skipped_count": 0,
                    "metrics": {},
                }
            )
            now = datetime.now(UTC).isoformat()
            if adapter_result.status == "success":
                response = await _ingest_agent_compliance_payload(
                    db,
                    org,
                    connector_id,
                    AgentComplianceIngestPayload(
                        cursor=cursor,
                        next_cursor=adapter_result.next_cursor,
                        events=[AgentComplianceEventPayload.model_validate(event) for event in adapter_result.events],
                    ),
                    actor_login,
                )
                settings = dict(org.settings or {})
                configured = dict(settings.get("v8_agent_compliance_connectors") or {})
                current = dict(configured.get(connector_id) or {})
                sync_plan.update(
                    {
                        "next_cursor": response.next_cursor,
                        "ingested_count": response.ingested_count,
                        "skipped_count": response.skipped_count,
                        "metrics": response.metrics,
                    }
                )
                current.update(
                    {
                        "cursor": response.next_cursor or cursor,
                        "last_sync_status": "success",
                        "last_sync_mode": adapter_result.mode,
                        "last_sync_plan": sync_plan,
                        "last_provider_sync_job": {
                            "job_id": job.id,
                            "status": "completed",
                            "cursor": cursor,
                            "next_cursor": response.next_cursor,
                            "ingested_count": response.ingested_count,
                            "skipped_count": response.skipped_count,
                            "content_retention": "metadata-only",
                            "completed_at": now,
                            "next_sync_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
                        },
                        "last_success_at": now,
                        "last_failure_at": None,
                        "last_error": None,
                        "next_sync_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
                        "updated_at": now,
                    }
                )
                job.status = "completed"
            else:
                current.update(
                    {
                        "last_sync_status": "failed",
                        "last_sync_mode": adapter_result.mode,
                        "last_sync_plan": sync_plan,
                        "last_provider_sync_job": {
                            "job_id": job.id,
                            "status": "failed",
                            "cursor": cursor,
                            "content_retention": "metadata-only",
                            "failed_at": now,
                            "blocked_reason": adapter_result.blocked_reason,
                            "next_sync_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
                        },
                        "last_failure_at": now,
                        "last_error": adapter_result.blocked_reason,
                        "next_sync_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
                        "updated_at": now,
                    }
                )
                job.status = "failed"
            configured[connector_id] = current
            settings["v8_agent_compliance_connectors"] = configured
            org.settings = settings
            flag_modified(org, "settings")
            job.result_json = {
                **result,
                "completed_at": datetime.now(UTC).isoformat(),
                "connector_id": connector_id,
                "status": adapter_result.status,
                "mode": adapter_result.mode,
                "cursor": cursor,
                "next_cursor": sync_plan.get("next_cursor"),
                "ingested_count": sync_plan.get("ingested_count", 0),
                "skipped_count": sync_plan.get("skipped_count", 0),
                "metrics": sync_plan.get("metrics", {}),
                "cost_source": "provider_reported" if adapter_result.status == "success" else "unknown",
                "token_source": token_source if adapter_result.status == "success" else "unknown",
                "blocked_reason": adapter_result.blocked_reason,
                "content_retention": "metadata-only",
            }
            await audit.emit(
                db,
                org_id,
                f"settings.{connector_id.replace('-', '_')}_provider_sync_job_completed",
                "synced" if adapter_result.status == "success" else "blocked",
                f"{provider_label} provider sync job {adapter_result.status}",
                actor_login=actor_login,
                resource_type="agent_compliance_connector",
                resource_id=connector_id,
                metadata=job.result_json,
            )
            await db.commit()
        except Exception as exc:
            await db.rollback()
            job = await db.get(Job, job_id)
            org = await db.get(Org, org_id)
            if job is not None:
                job.status = "failed"
                result = dict(job.result_json or result)
                result.update({"failed_at": datetime.now(UTC).isoformat(), "error": str(exc), "content_retention": "metadata-only"})
                job.result_json = result
                if org is not None:
                    settings = dict(org.settings or {})
                    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
                    current = dict(configured.get(connector_id) or {})
                    current.update(
                        {
                            "last_sync_status": "failed",
                            "last_sync_mode": "provider-sync-job",
                            "last_provider_sync_job": {
                                "job_id": job.id,
                                "status": "failed",
                                "content_retention": "metadata-only",
                                "failed_at": result["failed_at"],
                                "error": str(exc),
                                "next_sync_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
                            },
                            "last_failure_at": result["failed_at"],
                            "last_error": str(exc),
                            "next_sync_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat(),
                            "updated_at": result["failed_at"],
                        }
                    )
                    configured[connector_id] = current
                    settings["v8_agent_compliance_connectors"] = configured
                    org.settings = settings
                    flag_modified(org, "settings")
                await db.commit()


@router.get("")
async def get_settings_home(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {
        "org": {
            "id": org.id,
            "name": org.name,
            "login": org.login,
            "plan": org.plan,
        },
        "tabs": ["teams", "rbac", "sso", "connectors", "admin-audit", "billing", "notifications"],
    }


@router.get("/teams")
async def get_settings_teams(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    from apps.api.api.routes.orgs import _team_rows

    rows = await _team_rows(org_id, db)
    return {"teams": rows, "total": len(rows)}


@router.get("/rbac")
async def list_rbac(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    roles = (await db.execute(select(Role).where(Role.org_id == org_id).order_by(Role.name))).scalars().all()
    binding_rows = (
        await db.execute(
            select(RoleBinding, Role)
            .join(Role, Role.id == RoleBinding.role_id)
            .where(RoleBinding.org_id == org_id)
            .order_by(RoleBinding.created_at.desc())
        )
    ).all()
    return {
        "permissions": PERMISSIONS,
        "roles": [_role_response(role) for role in roles],
        "bindings": [_binding_response(binding, role) for binding, role in binding_rows],
    }


@router.post("/rbac/roles", status_code=201)
async def create_role(
    org_id: str,
    payload: RolePayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    invalid = [permission for permission in payload.permissions if permission not in PERMISSIONS and not permission.endswith("*")]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Unknown permissions: {', '.join(invalid)}")
    role = Role(org_id=org_id, name=payload.name.strip(), description=payload.description, permissions=payload.permissions)
    db.add(role)
    try:
        await db.flush()
        await audit.emit(
            db,
            org_id,
            "settings.rbac_role_created",
            "created",
            f"Created RBAC role {role.name}",
            actor_login=get_actor_login(request),
            resource_type="role",
            resource_id=role.id,
            metadata={"permissions": role.permissions},
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create role") from exc
    return _role_response(role)


@router.post("/rbac/bindings", status_code=201)
async def create_binding(
    org_id: str,
    payload: BindingPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    role = await db.get(Role, payload.role_id)
    if role is None or role.org_id != org_id:
        raise HTTPException(status_code=404, detail="Role not found")
    binding = RoleBinding(
        org_id=org_id,
        role_id=role.id,
        principal_type=payload.principal_type,
        principal_id=payload.principal_id,
        scope_expression=payload.scope_expression or {},
    )
    db.add(binding)
    try:
        await db.flush()
        await audit.emit(
            db,
            org_id,
            "settings.rbac_binding_created",
            "created",
            f"Bound role {role.name} to {binding.principal_id}",
            actor_login=get_actor_login(request),
            resource_type="role_binding",
            resource_id=binding.id,
            metadata={"role_id": role.id, "scope_expression": binding.scope_expression or {}},
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create role binding") from exc
    return _binding_response(binding, role)


@router.post("/rbac/check")
async def check_permission(
    org_id: str,
    payload: PermissionCheckPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    allowed = await has_permission(
        db,
        org_id=org_id,
        principal_id=payload.principal_id,
        permission=payload.permission,
        scope=payload.scope,
    )
    return {"allowed": allowed}


@router.get("/sso", dependencies=[Depends(require_permission("settings.sso.read"))])
async def get_sso(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return _sso_response(org)


@router.get("/connectors")
async def get_connectors(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    connections = (
        await db.execute(select(SourceConnection).where(SourceConnection.org_id == org_id))
    ).scalars().all()
    by_source_type = {connection.source_type: connection for connection in connections}
    connectors = []
    for item in connector_registry():
        source_type = item.get("source_type")
        connection = by_source_type.get(str(source_type)) if source_type else None
        connectors.append(
            {
                **item,
                "connected": connection is not None,
                "connection_status": connection.status if connection else None,
                "last_connected_at": connection.last_connected_at if connection else None,
            }
        )
    return {"connectors": connectors}


@router.get("/connectors/agent-compliance")
async def get_agent_compliance_connectors(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    payload = await _agent_connector_response(db, org)
    await db.commit()
    return payload


@router.post(
    "/connectors/agent-compliance",
    dependencies=[Depends(require_permission("settings.connectors.manage"))],
)
async def configure_agent_compliance_connector(
    org_id: str,
    payload: AgentComplianceConnectorPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    registry_ids = {str(item["id"]) for item in _agent_compliance_registry()}
    if payload.connector_id not in registry_ids:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")

    settings = dict(org.settings or {})
    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
    configured, _, _ = await _migrate_legacy_agent_credentials(db, org, configured)
    connector = next((item for item in _agent_compliance_registry() if item.get("id") == payload.connector_id), None)
    existing_row = dict(configured.get(payload.connector_id) or {})
    credentials = payload.credentials or {}
    credential_connection = await _agent_credential_connection(db, org_id, payload.connector_id)
    if credentials:
        credential_connection = await _upsert_agent_credential_connection(
            db,
            org_id,
            payload.connector_id,
            credentials=credentials,
            credential_kind=payload.credential_kind if payload.credential_kind != "none" else "api_token",
            display_name=str(connector.get("label") if connector else payload.connector_id),
            status="configured",
        )
    configured[payload.connector_id] = {
        **_settings_row_without_credentials(existing_row),
        "enabled": payload.enabled,
        "source_types": [item.strip() for item in payload.source_types if item.strip()],
        "scopes": [item.strip() for item in payload.scopes if item.strip()],
        "credential_kind": (credential_connection.params_hint or {}).get("credential_kind") if credential_connection is not None and isinstance(credential_connection.params_hint, dict) else (payload.credential_kind if payload.credential_kind != "none" else existing_row.get("credential_kind")),
        "credential_state": "encrypted" if credential_connection is not None else "missing",
        "cursor": payload.cursor,
        "last_sync_status": payload.last_sync_status or ("pending" if payload.enabled else None),
        "content_retention": payload.content_retention,
        "updated_at": datetime.utcnow().isoformat(),
    }
    settings["v8_agent_compliance_connectors"] = configured
    org.settings = settings
    flag_modified(org, "settings")
    await audit.emit(
        db,
        org_id,
        "settings.agent_compliance_connector_configured",
        "updated",
        f"Configured agent compliance connector {payload.connector_id}",
        actor_login=get_actor_login(request),
        resource_type="agent_compliance_connector",
        resource_id=payload.connector_id,
        metadata={
            "enabled": payload.enabled,
            "source_type_count": len(payload.source_types),
            "scope_count": len(payload.scopes),
            "credential_state": "encrypted" if credential_connection is not None else "missing",
            "credential_kind": (credential_connection.params_hint or {}).get("credential_kind") if credential_connection is not None and isinstance(credential_connection.params_hint, dict) else None,
            "credential_source_type": _agent_connection_source_type(payload.connector_id),
            "content_retention": payload.content_retention,
        },
    )
    await db.commit()
    return await _agent_connector_response(db, org)


@router.post(
    "/connectors/{connector_id}/credentials/test",
    response_model=AgentComplianceCredentialTestResponse,
    dependencies=[Depends(require_permission("settings.connectors.manage"))],
)
async def test_agent_compliance_connector_credentials(
    org_id: str,
    connector_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceCredentialTestResponse:
    await _assert_v8_org(org_id, current_org_id, db)
    registry_ids = {str(item["id"]) for item in _agent_compliance_registry()}
    if connector_id not in registry_ids:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    configured = _agent_connector_settings(org)
    configured, _, changed = await _migrate_legacy_agent_credentials(db, org, configured)
    response = await _test_agent_credentials(db, org_id, connector_id)
    if changed:
        settings = dict(org.settings or {})
        settings["v8_agent_compliance_connectors"] = configured
        org.settings = settings
        flag_modified(org, "settings")
    await audit.emit(
        db,
        org_id,
        "settings.agent_compliance_credentials_tested",
        "tested",
        f"Tested encrypted credentials for {connector_id}",
        actor_login=get_actor_login(request),
        resource_type="agent_compliance_connector",
        resource_id=connector_id,
        metadata={
            "connector_id": connector_id,
            "success": response.success,
            "status": response.status,
            "credential_state": response.credential_state,
            "credential_kind": response.credential_kind,
            "credential_source_type": _agent_connection_source_type(connector_id),
        },
    )
    await db.commit()
    return response


@router.post(
    "/connectors/{connector_id}/sync",
    response_model=AgentComplianceSyncResponse,
    dependencies=[Depends(require_permission("settings.connectors.manage"))],
)
async def request_agent_compliance_connector_sync(
    org_id: str,
    connector_id: str,
    payload: AgentComplianceSyncPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    registry_ids = {str(item["id"]) for item in _agent_compliance_registry()}
    if connector_id not in registry_ids:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")

    settings = dict(org.settings or {})
    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
    configured, credential_connections, _ = await _migrate_legacy_agent_credentials(db, org, configured)
    current = dict(configured.get(connector_id) or {})
    if not current.get("enabled"):
        raise HTTPException(status_code=409, detail="Agent compliance connector must be enabled before sync")
    connector = next((item for item in _agent_compliance_registry() if item.get("id") == connector_id), None)
    if connector is None:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    now = datetime.now(UTC).isoformat()
    cursor = payload.cursor or str(current.get("cursor") or "") or None
    sync_plan = _agent_sync_contract(connector_id, connector, current, cursor)
    credential_connection = credential_connections.get(connector_id) or await _agent_credential_connection(db, org_id, connector_id)
    live_provider_adapters = {"openai-compliance", "anthropic-compliance"}
    if not payload.dry_run and connector_id not in live_provider_adapters:
        raise HTTPException(status_code=400, detail="Live provider sync is currently implemented for OpenAI and Anthropic Compliance only")
    if not payload.dry_run and connector_id in live_provider_adapters:
        credentials = _decrypt_agent_credentials(credential_connection)
        if connector_id == "anthropic-compliance":
            adapter_result = pull_anthropic_compliance_events(credentials, cursor=cursor, dry_run=False)
            provider_label = "Anthropic Compliance"
            token_source = "anthropic_compliance_api"
        else:
            adapter_result = pull_openai_compliance_events(credentials, cursor=cursor, dry_run=False)
            provider_label = "OpenAI Compliance"
            token_source = "openai_compliance_api"
        sync_plan.update(
            {
                "status": adapter_result.status,
                "mode": adapter_result.mode,
                "cursor": cursor,
                "next_cursor": adapter_result.next_cursor,
                "provider_adapter_required": adapter_result.provider_adapter_required,
                "ready_for_provider_pull": adapter_result.status == "success",
                "blocked_reason": adapter_result.blocked_reason or "",
                "next_actions": adapter_result.next_actions,
                "ingested_count": 0,
                "skipped_count": 0,
                "metrics": {},
            }
        )
        if adapter_result.status == "success":
            ingest_response = await _ingest_agent_compliance_payload(
                db,
                org,
                connector_id,
                AgentComplianceIngestPayload(
                    cursor=cursor,
                    next_cursor=adapter_result.next_cursor,
                    events=[AgentComplianceEventPayload.model_validate(event) for event in adapter_result.events],
                ),
                get_actor_login(request),
            )
            settings = dict(org.settings or {})
            configured = dict(settings.get("v8_agent_compliance_connectors") or {})
            current = dict(configured.get(connector_id) or {})
            now = datetime.now(UTC).isoformat()
            current.update(
                {
                    "cursor": ingest_response.next_cursor or cursor,
                    "last_sync_status": "success",
                    "last_sync_requested_at": now,
                    "last_sync_mode": adapter_result.mode,
                    "last_sync_plan": sync_plan,
                    "last_success_at": now,
                    "last_failure_at": None,
                    "last_error": None,
                    "credential_state": "encrypted" if credential_connection is not None else "missing",
                    "updated_at": now,
                }
            )
            configured[connector_id] = current
            settings["v8_agent_compliance_connectors"] = configured
            org.settings = settings
            flag_modified(org, "settings")
            sync_plan.update(
                {
                    "next_cursor": ingest_response.next_cursor,
                    "ingested_count": ingest_response.ingested_count,
                    "skipped_count": ingest_response.skipped_count,
                    "metrics": ingest_response.metrics,
                }
            )
        else:
            current.update(
                {
                    "cursor": cursor,
                    "last_sync_status": "failed",
                    "last_sync_requested_at": now,
                    "last_sync_mode": adapter_result.mode,
                    "last_sync_plan": sync_plan,
                    "last_failure_at": now,
                    "last_error": adapter_result.blocked_reason,
                    "credential_state": "encrypted" if credential_connection is not None else "missing",
                    "updated_at": now,
                }
            )
            configured[connector_id] = current
            settings["v8_agent_compliance_connectors"] = configured
            org.settings = settings
            flag_modified(org, "settings")
        await audit.emit(
            db,
            org_id,
            f"settings.{connector_id.replace('-', '_')}_connector_sync_completed",
            "synced" if adapter_result.status == "success" else "blocked",
            f"{provider_label} connector sync {adapter_result.status}",
            actor_login=get_actor_login(request),
            resource_type="agent_compliance_connector",
            resource_id=connector_id,
            metadata={
                "connector_id": connector_id,
                "status": adapter_result.status,
                "mode": adapter_result.mode,
                "cursor_supplied": bool(payload.cursor),
                "next_cursor": sync_plan.get("next_cursor"),
                "ingested_count": sync_plan.get("ingested_count", 0),
                "cost_source": "provider_reported" if adapter_result.status == "success" else "unknown",
                "token_source": token_source if adapter_result.status == "success" else "unknown",
                "content_retention": "metadata-only",
                "blocked_reason": adapter_result.blocked_reason,
            },
        )
        await db.commit()
        return AgentComplianceSyncResponse.model_validate(sync_plan)
    current.update(
        {
            "cursor": cursor,
            "last_sync_status": "pending",
            "last_sync_requested_at": now,
            "last_sync_mode": "dry-run",
            "last_sync_plan": sync_plan,
            "credential_state": "encrypted" if credential_connection is not None else "missing",
            "updated_at": now,
        }
    )
    configured[connector_id] = current
    settings["v8_agent_compliance_connectors"] = configured
    org.settings = settings
    flag_modified(org, "settings")
    await audit.emit(
        db,
        org_id,
        "settings.agent_compliance_connector_sync_requested",
        "requested",
        f"Requested agent compliance connector sync for {connector_id}",
        actor_login=get_actor_login(request),
        resource_type="agent_compliance_connector",
        resource_id=connector_id,
        metadata={
            "dry_run": payload.dry_run,
            "cursor_supplied": bool(payload.cursor),
            "pagination_strategy": sync_plan["pagination_strategy"],
            "retention_window_days": sync_plan["retention_window_days"],
            "source_record_type": sync_plan["source_record_type"],
            "ready_for_provider_pull": sync_plan["ready_for_provider_pull"],
            "credential_state": "encrypted" if credential_connection is not None else "missing",
            "credential_source_type": _agent_connection_source_type(connector_id),
            "content_retention": current.get("content_retention") or "metadata-only",
        },
    )
    await db.commit()
    return AgentComplianceSyncResponse.model_validate(sync_plan)


@router.post(
    "/connectors/{connector_id}/ingest-events",
    response_model=AgentComplianceIngestResponse,
    dependencies=[Depends(require_permission("settings.connectors.manage"))],
)
async def ingest_agent_compliance_events(
    org_id: str,
    connector_id: str,
    payload: AgentComplianceIngestPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceIngestResponse:
    await _assert_v8_org(org_id, current_org_id, db)
    registry_ids = {str(item["id"]) for item in _agent_compliance_registry()}
    if connector_id not in registry_ids:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")

    response = await _ingest_agent_compliance_payload(db, org, connector_id, payload, get_actor_login(request))
    await db.commit()
    return response


@router.post(
    "/connectors/{connector_id}/ingest-jobs",
    response_model=AgentComplianceIngestJobResponse,
    dependencies=[Depends(require_permission("settings.connectors.manage"))],
)
async def queue_agent_compliance_ingest_job(
    org_id: str,
    connector_id: str,
    payload: AgentComplianceIngestPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceIngestJobResponse:
    await _assert_v8_org(org_id, current_org_id, db)
    registry_ids = {str(item["id"]) for item in _agent_compliance_registry()}
    if connector_id not in registry_ids:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")

    settings = dict(org.settings or {})
    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
    current = dict(configured.get(connector_id) or {})
    if not current.get("enabled"):
        raise HTTPException(status_code=409, detail="Agent compliance connector must be enabled before ingest")
    if current.get("content_retention") not in {None, "metadata-only"}:
        raise HTTPException(status_code=400, detail="Only metadata-only ingestion is enabled for this release")

    job = Job(
        id=new_uuid(),
        org_id=org_id,
        type="agent_compliance.ingest",
        status="queued",
        result_json={
            "connector_id": connector_id,
            "cursor": payload.cursor,
            "next_cursor": payload.next_cursor,
            "event_count": len(payload.events),
            "content_retention": "metadata-only",
            "pagination_strategy": "cursor-resume",
            "queued_at": datetime.now(UTC).isoformat(),
        },
    )
    db.add(job)
    current.update(
        {
            "last_sync_status": "queued",
            "last_sync_mode": "ingest-job",
            "last_ingest_job": {
                "job_id": job.id,
                "status": job.status,
                "event_count": len(payload.events),
                "cursor": payload.cursor,
                "next_cursor": payload.next_cursor,
                "content_retention": "metadata-only",
                "queued_at": job.result_json["queued_at"],
            },
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    configured[connector_id] = current
    settings["v8_agent_compliance_connectors"] = configured
    org.settings = settings
    flag_modified(org, "settings")
    await audit.emit(
        db,
        org_id,
        "settings.agent_compliance_ingest_job_queued",
        "queued",
        f"Queued metadata-only agent compliance ingest job for {connector_id}",
        actor_login=get_actor_login(request),
        resource_type="agent_compliance_connector",
        resource_id=connector_id,
        metadata={
            "job_id": job.id,
            "connector_id": connector_id,
            "event_count": len(payload.events),
            "cursor_supplied": bool(payload.cursor),
            "next_cursor_supplied": bool(payload.next_cursor),
            "content_retention": "metadata-only",
            "pagination_strategy": "cursor-resume",
        },
    )
    await db.commit()
    background_tasks.add_task(
        _run_agent_compliance_ingest_job,
        job.id,
        org_id,
        connector_id,
        payload.model_dump(mode="json"),
        get_actor_login(request),
    )
    return AgentComplianceIngestJobResponse(
        job_id=job.id,
        connector_id=connector_id,
        status=job.status,
        queued=True,
        cursor=payload.cursor,
        next_cursor=payload.next_cursor,
        event_count=len(payload.events),
    )


@router.post(
    "/connectors/{connector_id}/sync-jobs",
    response_model=AgentComplianceSyncJobResponse,
    dependencies=[Depends(require_permission("settings.connectors.manage"))],
)
async def queue_agent_compliance_provider_sync_job(
    org_id: str,
    connector_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceSyncJobResponse:
    await _assert_v8_org(org_id, current_org_id, db)
    if connector_id not in {"openai-compliance", "anthropic-compliance"}:
        raise HTTPException(status_code=400, detail="Provider sync jobs are currently implemented for OpenAI and Anthropic Compliance only")
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    settings = dict(org.settings or {})
    configured = dict(settings.get("v8_agent_compliance_connectors") or {})
    current = dict(configured.get(connector_id) or {})
    if not current.get("enabled"):
        raise HTTPException(status_code=409, detail="Agent compliance connector must be enabled before sync")
    now = datetime.now(UTC)
    next_sync_at = (now + timedelta(minutes=15)).isoformat()
    job = Job(
        id=new_uuid(),
        org_id=org_id,
        type="agent_compliance.provider_sync",
        status="queued",
        result_json={
            "connector_id": connector_id,
            "cursor": current.get("cursor"),
            "content_retention": "metadata-only",
            "pagination_strategy": "cursor-resume",
            "queued_at": now.isoformat(),
            "next_sync_at": next_sync_at,
        },
    )
    db.add(job)
    current.update(
        {
            "last_sync_status": "queued",
            "last_sync_mode": "provider-sync-job",
            "last_sync_requested_at": now.isoformat(),
            "next_sync_at": next_sync_at,
            "last_provider_sync_job": {
                "job_id": job.id,
                "status": job.status,
                "cursor": current.get("cursor"),
                "content_retention": "metadata-only",
                "queued_at": now.isoformat(),
                "next_sync_at": next_sync_at,
            },
            "updated_at": now.isoformat(),
        }
    )
    configured[connector_id] = current
    settings["v8_agent_compliance_connectors"] = configured
    org.settings = settings
    flag_modified(org, "settings")
    await audit.emit(
        db,
        org_id,
        "settings.agent_compliance_provider_sync_job_queued",
        "queued",
        f"Queued provider sync job for {connector_id}",
        actor_login=get_actor_login(request),
        resource_type="agent_compliance_connector",
        resource_id=connector_id,
        metadata={
            "job_id": job.id,
            "connector_id": connector_id,
            "cursor_supplied": bool(current.get("cursor")),
            "content_retention": "metadata-only",
            "pagination_strategy": "cursor-resume",
            "next_sync_at": next_sync_at,
        },
    )
    await db.commit()
    background_tasks.add_task(_run_agent_compliance_provider_sync_job, job.id, org_id, connector_id, get_actor_login(request))
    return AgentComplianceSyncJobResponse(
        job_id=job.id,
        connector_id=connector_id,
        status=job.status,
        queued=True,
        cursor=str(current.get("cursor")) if current.get("cursor") else None,
        next_sync_at=next_sync_at,
    )


@router.get(
    "/connectors/{connector_id}/sync-jobs/{job_id}",
    response_model=AgentComplianceIngestJobStatusResponse,
)
async def get_agent_compliance_provider_sync_job(
    org_id: str,
    connector_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceIngestJobStatusResponse:
    await _assert_v8_org(org_id, current_org_id, db)
    job = await db.get(Job, job_id)
    result = job.result_json if job is not None and isinstance(job.result_json, dict) else {}
    if job is None or job.org_id != org_id or job.type != "agent_compliance.provider_sync" or result.get("connector_id") != connector_id:
        raise HTTPException(status_code=404, detail="Agent compliance provider sync job not found")
    return AgentComplianceIngestJobStatusResponse(
        job_id=job.id,
        connector_id=connector_id,
        status=job.status,
        result=result,
        created_at=job.created_at,
    )


@router.get(
    "/connectors/{connector_id}/ingest-jobs/{job_id}",
    response_model=AgentComplianceIngestJobStatusResponse,
)
async def get_agent_compliance_ingest_job(
    org_id: str,
    connector_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceIngestJobStatusResponse:
    await _assert_v8_org(org_id, current_org_id, db)
    job = await db.get(Job, job_id)
    result = job.result_json if job is not None and isinstance(job.result_json, dict) else {}
    if job is None or job.org_id != org_id or job.type != "agent_compliance.ingest" or result.get("connector_id") != connector_id:
        raise HTTPException(status_code=404, detail="Agent compliance ingest job not found")
    return AgentComplianceIngestJobStatusResponse(
        job_id=job.id,
        connector_id=connector_id,
        status=job.status,
        result=result,
        created_at=job.created_at,
    )


def _admin_audit_payload(
    *,
    events: list[AuditEvent],
    page_events: list[AuditEvent],
    rollup_truncated: bool,
    window_days: int,
    actor: str | None,
    event_type: str | None,
    resource_type: str | None,
    severity: str | None,
    limit: int,
) -> dict[str, object]:
    actors = {event.actor_login for event in events if event.actor_login}
    event_types: dict[str, int] = {}
    resource_types: dict[str, int] = {}
    severity_counts = {"info": 0, "warning": 0, "critical": 0}
    for event in events:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        if event.resource_type:
            resource_types[event.resource_type] = resource_types.get(event.resource_type, 0) + 1
        if event.severity in severity_counts:
            severity_counts[event.severity] += 1
    event_type_rows = [
        {"key": key, "label": key, "count": count}
        for key, count in sorted(event_types.items(), key=lambda item: (-item[1], item[0]))[:10]
    ]
    resource_type_rows = [
        {"key": key, "label": key, "count": count}
        for key, count in sorted(resource_types.items(), key=lambda item: (-item[1], item[0]))[:10]
    ]
    return {
        "window_days": window_days,
        "summary": {
            "events": len(events),
            "actors": len(actors),
            "critical": severity_counts["critical"],
            "warnings": severity_counts["warning"],
            "resource_types": len(resource_types),
        },
        "filters": {
            "actor": actor,
            "event_type": event_type,
            "resource_type": resource_type,
            "severity": severity,
            "limit": limit,
        },
        "rollup": {
            "source_events": len(events),
            "limit": ADMIN_AUDIT_ROLLUP_LIMIT,
            "truncated": rollup_truncated,
        },
        "event_types": event_type_rows,
        "resource_types": resource_type_rows,
        "severity_counts": severity_counts,
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "actor_login": event.actor_login,
                "action": event.action,
                "summary": event.summary,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "severity": event.severity,
                "created_at": event.created_at,
            }
            for event in page_events
        ],
    }


@router.get("/admin-audit", dependencies=[Depends(require_permission("settings.admin_audit.read"))])
async def get_admin_audit(
    org_id: str,
    actor: str | None = None,
    event_type: str | None = None,
    resource_type: str | None = None,
    severity: Literal["info", "warning", "critical"] | None = None,
    window_days: int = 30,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    window_days = max(1, min(window_days, 180))
    limit = max(1, min(limit, 100))
    filters: list[Any] = [
        AuditEvent.org_id == org_id,
        AuditEvent.created_at >= datetime.now(UTC).replace(tzinfo=None) - timedelta(days=window_days),
        or_(
            AuditEvent.event_type.like("settings.%"),
            AuditEvent.event_type.like("member.%"),
            AuditEvent.event_type == "api_key_rotated",
        ),
    ]
    if actor:
        filters.append(AuditEvent.actor_login.ilike(f"%{actor}%"))
    if event_type:
        filters.append(AuditEvent.event_type == event_type)
    if resource_type:
        filters.append(AuditEvent.resource_type == resource_type)
    if severity:
        filters.append(AuditEvent.severity == severity)
    try:
        rollup_events = (
            await db.execute(
                select(AuditEvent)
                .where(*filters)
                .order_by(desc(AuditEvent.created_at))
                .limit(ADMIN_AUDIT_ROLLUP_LIMIT + 1)
            )
        ).scalars().all()
        page_events = (
            await db.execute(
                select(AuditEvent)
                .where(*filters)
                .order_by(desc(AuditEvent.created_at))
                .limit(limit)
            )
        ).scalars().all()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Admin audit data unavailable") from exc
    rollup_truncated = len(rollup_events) > ADMIN_AUDIT_ROLLUP_LIMIT
    rollup_events = list(rollup_events)[:ADMIN_AUDIT_ROLLUP_LIMIT]
    return _admin_audit_payload(
        events=rollup_events,
        page_events=list(page_events),
        rollup_truncated=rollup_truncated,
        window_days=window_days,
        actor=actor,
        event_type=event_type,
        resource_type=resource_type,
        severity=severity,
        limit=limit,
    )


@router.get("/billing", dependencies=[Depends(require_permission("settings.billing.read"))])
async def get_billing(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return _billing_response(org)


@router.get("/notifications/digest", dependencies=[Depends(require_permission("settings.notifications.read"))])
async def get_notifications_digest(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    config = await _load_or_create_digest_config(db, org_id)
    await db.commit()
    return _digest_response(config)

@router.put("/notifications/digest", dependencies=[Depends(require_permission("settings.notifications.manage"))])
async def update_notifications_digest(
    org_id: str,
    payload: DigestConfigPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    config = await _load_or_create_digest_config(db, org_id)
    config.title = payload.title
    config.subject = payload.subject
    config.frequency = payload.frequency or "weekly"
    config.recipients = [recipient.strip() for recipient in payload.recipients if recipient.strip()]
    config.widgets = payload.widgets or DEFAULT_DIGEST_WIDGETS
    config.layout = payload.layout or {}
    config.updated_at = datetime.utcnow()
    await audit.emit(
        db,
        org_id,
        "settings.notifications_updated",
        "updated",
        "Updated digest notification settings",
        actor_login=get_actor_login(request),
        resource_type="digest_config",
        resource_id=config.id,
        metadata={"frequency": config.frequency, "recipient_count": len(config.recipients)},
    )
    await db.commit()
    return _digest_response(config)


@router.get("/notifications/digest/preview", dependencies=[Depends(require_permission("settings.notifications.read"))])
async def get_notifications_digest_preview(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _assert_v8_org(org_id, current_org_id, db)
    return await legacy_digest._preview(org_id, db)


@router.post("/notifications/digest/preview", dependencies=[Depends(require_permission("settings.notifications.read"))])
async def preview_notifications_digest(
    org_id: str,
    payload: DigestPreviewPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _assert_v8_org(org_id, current_org_id, db)
    return await legacy_digest._preview(org_id, db, _legacy_digest_config(payload.config))


@router.post("/notifications/digest/send-now", dependencies=[Depends(require_permission("settings.notifications.manage"))])
async def send_notifications_digest_now(
    org_id: str,
    payload: DigestSendNowPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _assert_v8_org(org_id, current_org_id, db)
    preview = await legacy_digest._preview(org_id, db, _legacy_digest_config(payload.config))
    recipient = payload.recipient_email or (preview.get("recipients") or ["owner@skillayer.com"])[0]
    return await legacy_digest._send_payload(preview, recipient)
