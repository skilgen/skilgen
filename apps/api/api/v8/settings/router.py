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
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
from apps.api.api.v8.flags import is_v8, request_flag_cache
from apps.api.api.v8.settings.connectors_registry import connector_registry
from apps.api.api.v8.settings.rbac import PERMISSIONS, has_permission, require_permission
from packages.db.database import get_db, get_sessionmaker
from packages.db.models import AuditEvent, DigestConfig, Job, Org, Role, RoleBinding, SourceConnection
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


class AgentComplianceConnectorPayload(BaseModel):
    connector_id: str = Field(min_length=1, max_length=64)
    enabled: bool = True
    source_types: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    cursor: str | None = Field(default=None, max_length=512)
    last_sync_status: Literal["pending", "success", "failed"] | None = None
    content_retention: Literal["metadata-only", "tenant-enabled-content"] = "metadata-only"


class AgentComplianceSyncPayload(BaseModel):
    cursor: str | None = Field(default=None, max_length=512)
    dry_run: bool = True


class AgentComplianceSyncResponse(BaseModel):
    connector_id: str
    status: Literal["pending"]
    mode: Literal["dry-run"]
    cursor: str | None = None
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
    cost_usd: float | None = Field(default=None, ge=0)
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


def _agent_compliance_registry() -> list[dict[str, Any]]:
    return [
        item
        for item in connector_registry()
        if item.get("category") in {"compliance-telemetry", "coding-agent"}
    ]


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


def _agent_connector_response(org: Org | None) -> dict[str, object]:
    configured = _agent_connector_settings(org)
    connectors: list[dict[str, object]] = []
    for item in _agent_compliance_registry():
        connector_id = str(item["id"])
        row = configured.get(connector_id) or {}
        enabled = bool(row.get("enabled"))
        sync_plan = row.get("last_sync_plan")
        if not isinstance(sync_plan, dict):
            sync_plan = None
        connectors.append(
            {
                **item,
                "configured": connector_id in configured,
                "enabled": enabled,
                "connected": False,
                "source_types": list(row.get("source_types") or []),
                "scopes": list(row.get("scopes") or []),
                "last_cursor": row.get("cursor"),
                "last_sync_status": row.get("last_sync_status") or ("pending" if enabled else None),
                "last_sync_requested_at": row.get("last_sync_requested_at"),
                "last_sync_mode": row.get("last_sync_mode"),
                "last_sync_plan": sync_plan,
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
        "connectors": connectors,
    }


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


def _normalized_event_metadata(connector_id: str, event: AgentComplianceEventPayload) -> dict[str, Any]:
    provider = event.provider or connector_id
    model_tier = event.intelligence_tier or event.model_tier
    sanitized_envelope = {
        "connector_id": connector_id,
        "provider_event_id": event.provider_event_id,
        "event_type": event.event_type,
        "actor_login": event.actor_login,
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
        "cost_usd": event.cost_usd,
        "latency_ms": event.latency_ms,
        "error_count": event.error_count,
        "session_id": event.session_id,
        "source_envelope_hash": envelope_hash,
        "content_retention": "metadata-only",
        "redaction_state": "raw-content-dropped",
    }
    return {key: value for key, value in metadata.items() if value is not None and value != "" and value != []}


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
        metadata = _normalized_event_metadata(connector_id, event)
        db.add(
            AuditEvent(
                org_id=org_id,
                event_type="agent.compliance",
                action="ingested",
                summary=f"Normalized {event.source_record_type.replace('-', ' ')} from {event.provider or connector_id}",
                actor_login=event.actor_login,
                repo_id=event.repo_id,
                repo_name=event.repo_name,
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


@router.get("/sso")
async def get_sso(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    settings = org.settings if isinstance(org.settings, dict) else {}
    return {
        "workos_org_id": org.workos_org_id,
        "saml_enabled": bool(org.workos_org_id),
        "oidc_enabled": bool(settings.get("oidc_enabled")),
        "scim_enabled": bool(settings.get("scim_enabled")),
        "managed_by": "WorkOS",
    }


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
    return _agent_connector_response(org)


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
    configured[payload.connector_id] = {
        "enabled": payload.enabled,
        "source_types": [item.strip() for item in payload.source_types if item.strip()],
        "scopes": [item.strip() for item in payload.scopes if item.strip()],
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
            "content_retention": payload.content_retention,
        },
    )
    await db.commit()
    return _agent_connector_response(org)


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
    current = dict(configured.get(connector_id) or {})
    if not current.get("enabled"):
        raise HTTPException(status_code=409, detail="Agent compliance connector must be enabled before sync")
    if not payload.dry_run:
        raise HTTPException(status_code=400, detail="Agent compliance sync readiness only supports dry-run requests")
    connector = next((item for item in _agent_compliance_registry() if item.get("id") == connector_id), None)
    if connector is None:
        raise HTTPException(status_code=404, detail="Agent compliance connector not found")
    now = datetime.now(UTC).isoformat()
    cursor = payload.cursor or str(current.get("cursor") or "") or None
    sync_plan = _agent_sync_contract(connector_id, connector, current, cursor)
    current.update(
        {
            "cursor": cursor,
            "last_sync_status": "pending",
            "last_sync_requested_at": now,
            "last_sync_mode": "dry-run",
            "last_sync_plan": sync_plan,
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


@router.get("/admin-audit")
async def get_admin_audit(
    org_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    try:
        events = (
            await db.execute(
                select(AuditEvent)
                .where(
                    AuditEvent.org_id == org_id,
                    or_(
                        AuditEvent.event_type.like("settings.%"),
                        AuditEvent.event_type.like("member.%"),
                        AuditEvent.event_type == "api_key_rotated",
                    ),
                )
                .order_by(desc(AuditEvent.created_at))
                .limit(max(1, min(limit, 100)))
            )
        ).scalars().all()
    except SQLAlchemyError:
        events = []
    return {
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
            for event in events
        ]
    }


@router.get("/billing")
async def get_billing(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {
        "plan": org.plan,
        "seat_count": org.seat_count,
        "seat_limit": org.plan_seat_limit,
        "stripe_customer_id": org.stripe_customer_id,
        "stripe_subscription_id": org.stripe_subscription_id,
        "stripe_subscription_status": org.stripe_subscription_status,
    }


@router.get("/notifications/digest")
async def get_notifications_digest(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    config = await _load_or_create_digest_config(db, org_id)
    await db.commit()
    return _digest_response(config)


@router.put("/notifications/digest")
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
