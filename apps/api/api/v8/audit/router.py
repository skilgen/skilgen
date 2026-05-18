from __future__ import annotations

from datetime import UTC, datetime, timedelta
from io import StringIO
import csv
import json
import os
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
import apps.api.api.v8.audit.chain as chain
from apps.api.api.v8.audit.evidence import build_evidence_package_zip
from apps.api.api.v8.audit.reports import REPORTS, REPORTS_BY_ID, report_sql
from apps.api.api.v8.audit.storage import WormStorageProvider, publish_worm_root, root_document, worm_target_status
from apps.api.api.v8.flags import is_v8, request_flag_cache
from packages.db.database import get_db
from packages.db.models.base import new_uuid
from packages.db.models import AuditEvent, AuditHashChain, AuditWormRoot, Job, OrgPolicy, SkillVersion


router = APIRouter(prefix="/v8/orgs/{org_id}/audit", tags=["v8-audit"], dependencies=[Depends(request_flag_cache)])


class AuditChainResponse(BaseModel):
    event_id: str
    sequence: int
    event_hash: str
    previous_hash: str
    root_hash: str
    merkle_proof: list[dict[str, str]]


class AuditEventResponse(BaseModel):
    id: str
    event_type: str
    action: str
    actor_login: str | None
    repo_id: str | None
    repo_name: str | None
    skill_id: str | None
    skill_domain: str | None
    resource_type: str | None
    resource_id: str | None
    summary: str
    severity: Literal["info", "warning", "critical"]
    metadata: dict[str, object]
    created_at: datetime
    chain: AuditChainResponse | None = None


class AuditEventLogResponse(BaseModel):
    total: int
    events: list[AuditEventResponse]
    has_more: bool
    next_cursor: str | None = None
    chain_root: str | None = None


class AuditReportDefinitionResponse(BaseModel):
    id: str
    title: str
    control_mapping: str
    description: str


class AuditReportRow(BaseModel):
    id: str
    event_type: str
    action: str
    actor_login: str | None = None
    repo_name: str | None = None
    skill_domain: str | None = None
    severity: str
    summary: str
    created_at: datetime
    commit_sha: str | None = None
    policy_id: str | None = None
    policy_decision: str | None = None
    control_mapping: str | None = None
    agent_runtime: str | None = None
    sensitivity_tier: str | None = None


class AuditReportResponse(BaseModel):
    report: AuditReportDefinitionResponse
    rows: list[AuditReportRow]
    generated_at: datetime


class ExportRequest(BaseModel):
    format: Literal["csv", "json", "splunk_hec", "datadog_cloud_siem", "sumo_logic", "microsoft_sentinel", "raw_ndjson_s3"]
    event_type: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    destination: str | None = None


class ExportResponse(BaseModel):
    format: str
    event_count: int
    content_type: str
    body: str | list[dict[str, Any]] | dict[str, Any] | None = None
    destination: str | None = None
    audit_event_logged: bool = True


class PublishRootRequest(BaseModel):
    cadence: str = Field(default="daily", max_length=32)
    storage_provider: WormStorageProvider = "s3_object_lock"


class PublishRootResponse(BaseModel):
    root_hash: str
    object_key: str | None
    status: str
    event_count: int
    storage_provider: WormStorageProvider


class WormTargetResponse(BaseModel):
    provider: WormStorageProvider
    label: str
    configured: bool
    bucket_env: str
    prefix_env: str
    prefix: str
    status: Literal["configured", "pending"]
    content_retention: Literal["root-and-proof-only"]


class EvidencePackageRequest(BaseModel):
    control: str
    period_start: datetime
    period_end: datetime


class EvidencePackageResponse(BaseModel):
    job_id: str
    status: str
    queued: bool
    result: dict[str, Any] = Field(default_factory=dict)


AGENT_COMPLIANCE_EVENT_TYPES = {
    "agent.compliance",
    "agent_compliance",
    "agent.telemetry",
    "agent_telemetry",
    "coding_agent.compliance",
    "coding_agent.telemetry",
}


class AgentComplianceAuditEvent(BaseModel):
    id: str
    event_type: str
    actor_login: str | None
    provider: str | None
    model: str | None
    intelligence_tier: str | None
    access_scope: str | None
    repo_name: str | None
    policy_decision: str | None
    source_envelope_hash: str | None
    severity: Literal["info", "warning", "critical"]
    summary: str
    created_at: datetime


class AgentComplianceAuditResponse(BaseModel):
    total: int
    window_days: int
    content_retention: Literal["metadata-only"] = "metadata-only"
    events: list[AgentComplianceAuditEvent]


def _event_payload(event: AuditEvent) -> dict[str, Any]:
    return {
        "event_type": event.event_type,
        "action": event.action,
        "actor_login": event.actor_login,
        "actor_ip": event.actor_ip,
        "repo_id": event.repo_id,
        "repo_name": event.repo_name,
        "skill_id": event.skill_id,
        "skill_domain": event.skill_domain,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "summary": event.summary,
        "severity": event.severity,
        "metadata": event.metadata_json or {},
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


async def _assert_enabled(org_id: str, current_org_id: str, db: AsyncSession) -> None:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="v8 audit is not enabled")


def _chain_response(row: AuditHashChain | None) -> AuditChainResponse | None:
    if row is None:
        return None
    return AuditChainResponse(
        event_id=row.event_id,
        sequence=row.sequence,
        event_hash=row.event_hash,
        previous_hash=row.previous_hash,
        root_hash=row.root_hash,
        merkle_proof=list(row.merkle_proof or []),
    )


def _event_response(event: AuditEvent, chain_row: AuditHashChain | None = None) -> AuditEventResponse:
    return AuditEventResponse(
        id=event.id,
        event_type=event.event_type,
        action=event.action,
        actor_login=event.actor_login,
        repo_id=event.repo_id,
        repo_name=event.repo_name,
        skill_id=event.skill_id,
        skill_domain=event.skill_domain,
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        summary=event.summary,
        severity=event.severity if event.severity in {"info", "warning", "critical"} else "info",
        metadata=event.metadata_json or {},
        created_at=event.created_at,
        chain=_chain_response(chain_row),
    )


def _metadata_value(metadata: object, *keys: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    for key in keys:
        value = metadata.get(key)
        if value not in {None, ""}:
            return str(value)
    return None


def _agent_compliance_response(event: AuditEvent) -> AgentComplianceAuditEvent:
    metadata = event.metadata_json or {}
    severity = event.severity if event.severity in {"info", "warning", "critical"} else "info"
    return AgentComplianceAuditEvent(
        id=event.id,
        event_type=event.event_type,
        actor_login=event.actor_login,
        provider=_metadata_value(metadata, "provider", "agent_provider", "source_provider"),
        model=_metadata_value(metadata, "model", "model_name", "model_id"),
        intelligence_tier=_metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier"),
        access_scope=_metadata_value(metadata, "access_scope", "permission_scope", "grant_scope"),
        repo_name=event.repo_name or _metadata_value(metadata, "repo_name", "repo"),
        policy_decision=_metadata_value(metadata, "policy_decision", "decision", "outcome"),
        source_envelope_hash=_metadata_value(metadata, "source_envelope_hash", "envelope_hash", "event_hash"),
        severity=severity,
        summary=event.summary,
        created_at=event.created_at,
    )


RAW_CONTENT_KEYS = {
    "args",
    "argument",
    "arguments",
    "prompt",
    "raw_prompt",
    "completion",
    "raw_completion",
    "content",
    "contents",
    "messages",
    "chat",
    "chat_content",
    "diff",
    "input",
    "inputs",
    "output",
    "outputs",
    "patch",
    "parameter",
    "parameters",
    "file_content",
    "file_contents",
    "tool_parameters",
    "tool_params",
    "tool_arguments",
    "tool_args",
}


def _safe_label(value: object) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int | float | str):
        return str(value)
    if isinstance(value, dict):
        for key in ("name", "tool", "id", "type", "path", "file", "repo", "provider"):
            item = value.get(key)
            if isinstance(item, bool):
                return str(item).lower()
            if isinstance(item, int | float | str) and str(item):
                return str(item)
    return None


def _metadata_list(metadata: object, key: str) -> list[str]:
    if not isinstance(metadata, dict):
        return []
    value = metadata.get(key)
    if isinstance(value, list):
        return [label for item in value if (label := _safe_label(item))]
    if isinstance(value, dict):
        return [label for item in value.keys() if (label := _safe_label(item))]
    label = _safe_label(value)
    if label:
        return [label]
    return []


def _metadata_int(metadata: object, *keys: str) -> int:
    if not isinstance(metadata, dict):
        return 0
    for key in keys:
        value = metadata.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int | float):
            return max(0, int(value))
        if isinstance(value, str):
            try:
                return max(0, int(float(value)))
            except ValueError:
                continue
    return 0


def _metadata_float(metadata: object, *keys: str) -> float:
    if not isinstance(metadata, dict):
        return 0.0
    for key in keys:
        value = metadata.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, int | float):
            return max(0.0, float(value))
        if isinstance(value, str):
            try:
                return max(0.0, float(value))
            except ValueError:
                continue
    return 0.0


def _metadata_bool(metadata: object, *keys: str) -> bool:
    if not isinstance(metadata, dict):
        return False
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "full-access", "autonomous"}
    return False


def _tool_permission_count(metadata: object) -> int:
    if not isinstance(metadata, dict):
        return 0
    tool_permissions = _metadata_list(metadata, "tool_permissions")
    if tool_permissions:
        return len(tool_permissions)
    return _metadata_int(metadata, "tool_calls", "tool_call_count")


def _count(counter: dict[str, int], values: list[str]) -> None:
    for value in values:
        counter[value] = counter.get(value, 0) + 1


def _counter_payload(counter: dict[str, int], *, limit: int = 12) -> list[dict[str, Any]]:
    return [
        {"key": key, "label": key, "count": count}
        for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _safe_agent_compliance_metadata(metadata: object) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in metadata.items():
        key_text = str(key)
        if key_text.lower() in RAW_CONTENT_KEYS:
            continue
        if isinstance(value, dict):
            nested = _safe_agent_compliance_metadata(value)
            if nested:
                sanitized[key_text] = nested
        elif isinstance(value, list):
            safe_items = []
            for item in value:
                if isinstance(item, dict):
                    nested = _safe_agent_compliance_metadata(item)
                    if nested:
                        safe_items.append(nested)
                elif (label := _safe_label(item)) is not None:
                    safe_items.append(label)
            sanitized[key_text] = safe_items
        elif value is None or isinstance(value, bool | int | float | str):
            sanitized[key_text] = value
    return sanitized


def _agent_compliance_evidence(rows: list[AuditEvent]) -> dict[str, Any]:
    actors: set[str] = set()
    providers: set[str] = set()
    sessions: set[str] = set()
    repos: set[str] = set()
    source_hashes: set[str] = set()
    top_tools: dict[str, int] = {}
    top_mcp_tools: dict[str, int] = {}
    top_files: dict[str, int] = {}
    policy_decisions: dict[str, int] = {}
    approval_statuses: dict[str, int] = {}
    source_record_types: dict[str, int] = {}
    retention_states: dict[str, int] = {}
    latency_values: list[float] = []
    summary = {
        "events": 0,
        "users": 0,
        "providers": 0,
        "sessions": 0,
        "repos": 0,
        "file_targets": 0,
        "tool_permission_events": 0,
        "mcp_tool_events": 0,
        "full_access_events": 0,
        "autonomous_events": 0,
        "approvals": 0,
        "denials": 0,
        "warnings": 0,
        "violations": 0,
        "errors": 0,
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_total": 0,
        "cost_usd": 0.0,
        "avg_latency_ms": None,
        "source_envelope_hashes": 0,
    }
    sanitized_events: list[dict[str, Any]] = []
    for row in rows:
        if str(row.event_type or "").lower() not in AGENT_COMPLIANCE_EVENT_TYPES:
            continue
        metadata = row.metadata_json or {}
        actor = row.actor_login or _metadata_value(metadata, "actor_login", "user") or "unknown"
        provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or row.resource_type or "unknown"
        repo = row.repo_name or _metadata_value(metadata, "repo_name", "repo") or "unknown"
        session_id = _metadata_value(metadata, "session_id", "agent_session_id", "thread_id")
        source_hash = _metadata_value(metadata, "source_envelope_hash", "envelope_hash", "event_hash")
        tool_count = _tool_permission_count(metadata)
        mcp_tools = _metadata_list(metadata, "mcp_tools")
        file_targets = _metadata_list(metadata, "file_targets")
        warning_count = _metadata_int(metadata, "warnings", "warning_count")
        violation_count = len(_metadata_list(metadata, "violations"))
        error_count = _metadata_int(metadata, "error_count", "errors")
        input_tokens = _metadata_int(metadata, "tokens_input", "input_tokens", "prompt_tokens")
        output_tokens = _metadata_int(metadata, "tokens_output", "output_tokens", "completion_tokens")
        total_tokens = _metadata_int(metadata, "tokens_total", "total_tokens") or input_tokens + output_tokens
        cost_usd = _metadata_float(metadata, "cost_usd", "estimated_cost_usd")
        latency_ms = _metadata_float(metadata, "latency_ms", "duration_ms")
        decision = _metadata_value(metadata, "policy_decision", "decision", "outcome")
        approval = _metadata_value(metadata, "approval_status")

        summary["events"] += 1
        summary["file_targets"] += len(file_targets)
        summary["tool_permission_events"] += tool_count
        summary["mcp_tool_events"] += len(mcp_tools)
        summary["full_access_events"] += int(_metadata_bool(metadata, "full_access", "full_access_granted") or _metadata_value(metadata, "access_scope") == "full-access")
        summary["autonomous_events"] += int(_metadata_bool(metadata, "autonomous_access", "autonomous"))
        summary["warnings"] += warning_count
        summary["violations"] += violation_count
        summary["errors"] += error_count
        summary["tokens_input"] += input_tokens
        summary["tokens_output"] += output_tokens
        summary["tokens_total"] += total_tokens
        summary["cost_usd"] += cost_usd
        if latency_ms:
            latency_values.append(latency_ms)
        if decision:
            policy_decisions[decision] = policy_decisions.get(decision, 0) + 1
            if decision.lower() in {"deny", "denied", "block", "blocked", "reject", "rejected"}:
                summary["denials"] += 1
        if approval:
            approval_statuses[approval] = approval_statuses.get(approval, 0) + 1
            if approval.lower() in {"approved", "approve", "allowed", "allow"}:
                summary["approvals"] += 1
            elif approval.lower() in {"denied", "deny", "rejected", "reject", "blocked", "block"}:
                summary["denials"] += 1
        source_record_type = _metadata_value(metadata, "source_record_type") or "unknown"
        retention_state = _metadata_value(metadata, "content_retention", "redaction_state") or "metadata-only"
        source_record_types[source_record_type] = source_record_types.get(source_record_type, 0) + 1
        retention_states[retention_state] = retention_states.get(retention_state, 0) + 1
        _count(top_tools, _metadata_list(metadata, "tool_permissions"))
        _count(top_mcp_tools, mcp_tools)
        _count(top_files, file_targets)
        actors.add(actor)
        providers.add(provider)
        repos.add(repo)
        if session_id:
            sessions.add(session_id)
        if source_hash:
            source_hashes.add(source_hash)
        sanitized_events.append(
            {
                "id": row.id,
                "actor_login": actor,
                "provider": provider,
                "model": _metadata_value(metadata, "model", "model_name", "model_id"),
                "intelligence_tier": _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier"),
                "access_scope": _metadata_value(metadata, "access_scope", "permission_scope", "grant_scope"),
                "repo_name": repo,
                "policy_decision": decision,
                "approval_status": approval,
                "source_envelope_hash": source_hash,
                "summary": row.summary,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "metadata": _safe_agent_compliance_metadata(metadata),
            }
        )
    summary["users"] = len(actors)
    summary["providers"] = len(providers)
    summary["sessions"] = len(sessions)
    summary["repos"] = len(repos)
    summary["source_envelope_hashes"] = len(source_hashes)
    summary["cost_usd"] = round(float(summary["cost_usd"]), 6)
    summary["avg_latency_ms"] = round(sum(latency_values) / len(latency_values), 2) if latency_values else None
    return {
        "content_retention": "metadata-only",
        "excluded_raw_content_keys": sorted(RAW_CONTENT_KEYS),
        "summary": summary,
        "top_tools": _counter_payload(top_tools),
        "top_mcp_tools": _counter_payload(top_mcp_tools),
        "top_files": _counter_payload(top_files),
        "policy_decisions": _counter_payload(policy_decisions),
        "approval_statuses": _counter_payload(approval_statuses),
        "source_record_types": _counter_payload(source_record_types),
        "retention_states": _counter_payload(retention_states),
        "events": sanitized_events,
    }


def _evidence_event_payload(row: AuditEvent) -> dict[str, Any]:
    payload = {"id": row.id, **_event_payload(row)}
    if str(row.event_type or "").lower() in AGENT_COMPLIANCE_EVENT_TYPES:
        payload["metadata"] = _safe_agent_compliance_metadata(row.metadata_json or {})
    return payload


async def _ensure_chain(db: AsyncSession, org_id: str) -> list[AuditHashChain]:
    try:
        existing_rows = (
            await db.execute(select(AuditHashChain).where(AuditHashChain.org_id == org_id).order_by(AuditHashChain.sequence))
        ).scalars().all()
    except SQLAlchemyError:
        await db.rollback()
        return []
    existing_entries = [
        chain.ChainEntry(
            event_id=row.event_id,
            sequence=row.sequence,
            event_hash=row.event_hash,
            previous_hash=row.previous_hash,
            root_hash=row.root_hash,
            merkle_proof=tuple(row.merkle_proof or []),
        )
        for row in existing_rows
    ]
    chained_event_ids = {row.event_id for row in existing_rows}
    events = (
        await db.execute(
            select(AuditEvent)
            .where(AuditEvent.org_id == org_id, AuditEvent.id.not_in(chained_event_ids) if chained_event_ids else text("true"))
            .order_by(AuditEvent.created_at, AuditEvent.id)
            .limit(5000)
        )
    ).scalars().all()
    appended = chain.append_events(
        existing_entries,
        [chain.EventInput(event_id=event.id, payload=_event_payload(event)) for event in events],
    )
    existing_by_id = {row.event_id: row for row in existing_rows}
    for entry in appended:
        row = existing_by_id.get(entry.event_id)
        if row is None:
            db.add(
                AuditHashChain(
                    org_id=org_id,
                    event_id=entry.event_id,
                    sequence=entry.sequence,
                    event_hash=entry.event_hash,
                    previous_hash=entry.previous_hash,
                    root_hash=entry.root_hash,
                    merkle_proof=list(entry.merkle_proof),
                )
            )
        else:
            row.merkle_proof = list(entry.merkle_proof)
    if events:
        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            return []
    try:
        return (await db.execute(select(AuditHashChain).where(AuditHashChain.org_id == org_id).order_by(AuditHashChain.sequence))).scalars().all()
    except SQLAlchemyError:
        await db.rollback()
        return []


def _filters(
    org_id: str,
    *,
    event_type: str | None = None,
    actor: str | None = None,
    repo_id: str | None = None,
    severity: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[Any]:
    filters: list[Any] = [AuditEvent.org_id == org_id]
    if event_type:
        filters.append(AuditEvent.event_type == event_type)
    if actor:
        filters.append(AuditEvent.actor_login.ilike(f"%{actor}%"))
    if repo_id:
        filters.append(AuditEvent.repo_id == repo_id)
    if severity:
        filters.append(AuditEvent.severity == severity)
    if date_from:
        filters.append(AuditEvent.created_at >= date_from.replace(tzinfo=None))
    if date_to:
        filters.append(AuditEvent.created_at <= date_to.replace(tzinfo=None))
    return filters


async def _export_rows(db: AsyncSession, org_id: str, payload: ExportRequest) -> list[AuditEvent]:
    return (
        await db.execute(
            select(AuditEvent)
            .where(*_filters(org_id, event_type=payload.event_type, date_from=payload.date_from, date_to=payload.date_to))
            .order_by(desc(AuditEvent.created_at))
            .limit(10000)
        )
    ).scalars().all()


def _rows_as_dicts(rows: list[AuditEvent]) -> list[dict[str, Any]]:
    return [{"id": row.id, **_event_payload(row)} for row in rows]


def _csv_body(rows: list[AuditEvent]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["id", "created_at", "actor_login", "event_type", "severity", "repo_name", "summary", "metadata"])
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "id": row.id,
                "created_at": row.created_at.isoformat(),
                "actor_login": row.actor_login or "system",
                "event_type": row.event_type,
                "severity": row.severity,
                "repo_name": row.repo_name or "",
                "summary": row.summary,
                "metadata": json.dumps(row.metadata_json or {}, sort_keys=True),
            }
        )
    return buffer.getvalue()


def _siem_body(format_name: str, rows: list[AuditEvent]) -> list[dict[str, Any]] | dict[str, Any]:
    events = _rows_as_dicts(rows)
    if format_name == "splunk_hec":
        return [{"time": row.created_at.timestamp(), "event": event, "sourcetype": "skillayer:audit"} for row, event in zip(rows, events)]
    if format_name == "datadog_cloud_siem":
        return [{"ddsource": "skillayer", "service": "audit", "message": event["summary"], **event} for event in events]
    if format_name == "sumo_logic":
        return [{"_sourceCategory": "skillayer/audit", **event} for event in events]
    if format_name == "microsoft_sentinel":
        return {"records": [{"TimeGenerated": event["created_at"], "SourceSystem": "Skillayer", **event} for event in events]}
    return events


def _write_raw_ndjson(destination: str, rows: list[AuditEvent]) -> None:
    body = "\n".join(json.dumps(item, sort_keys=True, default=str) for item in _rows_as_dicts(rows)).encode("utf-8")
    if destination.startswith("file://"):
        from pathlib import Path

        Path(destination.removeprefix("file://")).write_bytes(body)
        return
    if destination.startswith("s3://"):
        try:
            import boto3  # type: ignore[import-not-found]
        except Exception as exc:
            raise HTTPException(status_code=400, detail="boto3 is required for raw NDJSON S3 exports") from exc
        bucket_key = destination.removeprefix("s3://")
        bucket, _, key = bucket_key.partition("/")
        if not bucket or not key:
            raise HTTPException(status_code=400, detail="raw NDJSON S3 destination must be s3://bucket/key")
        boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/x-ndjson")
        return
    raise HTTPException(status_code=400, detail="raw NDJSON destination must be s3://bucket/key or file://path")


@router.get("/event-log", response_model=AuditEventLogResponse)
async def get_event_log(
    org_id: str,
    event_type: str | None = None,
    actor: str | None = None,
    repo_id: str | None = None,
    severity: Literal["info", "warning", "critical"] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    cursor: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AuditEventLogResponse:
    await _assert_enabled(org_id, current_org_id, db)
    chain_rows = await _ensure_chain(db, org_id)
    filters = _filters(org_id, event_type=event_type, actor=actor, repo_id=repo_id, severity=severity, date_from=date_from, date_to=date_to)
    if cursor:
        filters.append(AuditEvent.created_at < cursor.replace(tzinfo=None))
    total = int((await db.execute(select(func.count(AuditEvent.id)).where(*filters))).scalar() or 0)
    rows = (
        await db.execute(select(AuditEvent).where(*filters).order_by(desc(AuditEvent.created_at)).limit(limit + 1))
    ).scalars().all()
    has_more = len(rows) > limit
    page_rows = list(rows[:limit])
    chain_by_event = {row.event_id: row for row in chain_rows}
    return AuditEventLogResponse(
        total=total,
        events=[_event_response(event, chain_by_event.get(event.id)) for event in page_rows],
        has_more=has_more,
        next_cursor=page_rows[-1].created_at.isoformat() if has_more and page_rows else None,
        chain_root=chain_rows[-1].root_hash if chain_rows else None,
    )


@router.get("/agent-compliance", response_model=AgentComplianceAuditResponse)
async def get_agent_compliance_audit(
    org_id: str,
    provider: str | None = None,
    actor: str | None = None,
    window_days: int = Query(default=30, ge=1, le=180),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceAuditResponse:
    await _assert_enabled(org_id, current_org_id, db)
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=window_days)
    filters: list[Any] = [
        AuditEvent.org_id == org_id,
        AuditEvent.created_at >= cutoff,
        AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
    ]
    if actor:
        filters.append(AuditEvent.actor_login.ilike(f"%{actor}%"))
    rows = (
        await db.execute(
            select(AuditEvent)
            .where(*filters)
            .order_by(desc(AuditEvent.created_at))
            .limit(limit)
        )
    ).scalars().all()
    events = [_agent_compliance_response(event) for event in rows]
    if provider:
        provider_lower = provider.lower()
        events = [event for event in events if (event.provider or "").lower() == provider_lower]
    return AgentComplianceAuditResponse(total=len(events), window_days=window_days, events=events)


@router.get("/reports", response_model=list[AuditReportDefinitionResponse])
async def list_reports(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> list[AuditReportDefinitionResponse]:
    await _assert_enabled(org_id, current_org_id, db)
    return [AuditReportDefinitionResponse(**report.__dict__) for report in REPORTS]


@router.get("/reports/{report_id}", response_model=AuditReportResponse)
async def get_report(
    org_id: str,
    report_id: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    repo_id: str | None = None,
    actor: str | None = None,
    limit: int = Query(default=500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AuditReportResponse:
    await _assert_enabled(org_id, current_org_id, db)
    if report_id not in REPORTS_BY_ID:
        raise HTTPException(status_code=404, detail="Unknown audit report")
    result = await db.execute(
        text(report_sql(report_id)),
        {
            "org_id": org_id,
            "date_from": date_from.replace(tzinfo=None) if date_from else None,
            "date_to": date_to.replace(tzinfo=None) if date_to else None,
            "repo_id": repo_id,
            "actor": actor,
            "actor_pattern": f"%{actor}%" if actor else None,
            "limit": limit,
        },
    )
    rows = [AuditReportRow(**dict(row._mapping)) for row in result]
    report = REPORTS_BY_ID[report_id]
    return AuditReportResponse(report=AuditReportDefinitionResponse(**report.__dict__), rows=rows, generated_at=datetime.now(UTC))


@router.get("/reports/{report_id}/export")
async def export_report(
    org_id: str,
    report_id: str,
    format: Literal["csv", "json"] = "csv",
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> Response:
    response = await get_report(org_id, report_id, limit=5000, db=db, current_org_id=current_org_id)
    rows = [row.model_dump(mode="json") for row in response.rows]
    if format == "json":
        return JSONResponse({"report": response.report.model_dump(), "rows": rows, "generated_at": response.generated_at.isoformat()})
    buffer = StringIO()
    fieldnames = list(AuditReportRow.model_fields.keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return Response(buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={report_id}.csv"})


@router.get("/chain/worm-targets", response_model=list[WormTargetResponse])
async def get_worm_targets(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[WormTargetResponse]:
    await _assert_enabled(org_id, current_org_id, db)
    return [WormTargetResponse(**target) for target in worm_target_status()]


@router.post("/exports", response_model=ExportResponse)
async def create_export(
    org_id: str,
    payload: ExportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ExportResponse:
    await _assert_enabled(org_id, current_org_id, db)
    rows = await _export_rows(db, org_id, payload)
    body: str | list[dict[str, Any]] | dict[str, Any] | None
    content_type = "application/json"
    destination = payload.destination
    if payload.format == "csv":
        body = _csv_body(rows)
        content_type = "text/csv"
    elif payload.format == "json":
        body = _rows_as_dicts(rows)
    elif payload.format == "raw_ndjson_s3":
        body = None
        if not destination:
            destination = os.getenv("AUDIT_EXPORT_S3_URI")
        if not destination:
            raise HTTPException(status_code=400, detail="raw NDJSON S3 export requires a destination")
        _write_raw_ndjson(destination, rows)
        content_type = "application/x-ndjson"
    else:
        body = _siem_body(payload.format, rows)
    await audit.emit(
        db,
        org_id,
        "audit.export.created",
        "exported",
        f"Audit export created in {payload.format}",
        actor_login=get_actor_login(request),
        resource_type="audit_export",
        resource_id=payload.format,
        metadata={"format": payload.format, "event_count": len(rows), "destination": destination},
    )
    await db.commit()
    return ExportResponse(format=payload.format, event_count=len(rows), content_type=content_type, body=body, destination=destination)


@router.post("/chain/publish-root", response_model=PublishRootResponse)
async def publish_root(
    org_id: str,
    payload: PublishRootRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PublishRootResponse:
    await _assert_enabled(org_id, current_org_id, db)
    chain_rows = await _ensure_chain(db, org_id)
    if not chain_rows:
        raise HTTPException(status_code=400, detail="No audit events to publish")
    last = chain_rows[-1]
    document = root_document(
        org_id=org_id,
        root_hash=last.root_hash,
        start_sequence=chain_rows[0].sequence,
        end_sequence=last.sequence,
        event_count=len(chain_rows),
        merkle_proof=list(last.merkle_proof or []),
        cadence=payload.cadence,
        storage_provider=payload.storage_provider,
    )
    object_key, status = publish_worm_root(document, provider=payload.storage_provider)
    db.add(
        AuditWormRoot(
            org_id=org_id,
            root_hash=last.root_hash,
            start_sequence=chain_rows[0].sequence,
            end_sequence=last.sequence,
            event_count=len(chain_rows),
            object_key=object_key,
            cadence=payload.cadence,
            merkle_proof=list(last.merkle_proof or []),
            status=status,
        )
    )
    await db.commit()
    return PublishRootResponse(root_hash=last.root_hash, object_key=object_key, status=status, event_count=len(chain_rows), storage_provider=payload.storage_provider)


@router.post("/evidence-packages", response_model=EvidencePackageResponse)
async def create_evidence_package(
    org_id: str,
    payload: EvidencePackageRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> EvidencePackageResponse:
    await _assert_enabled(org_id, current_org_id, db)
    preview = {
        "control": payload.control,
        "period_start": payload.period_start.isoformat(),
        "period_end": payload.period_end.isoformat(),
        "index_format": "html",
        "content_retention": "metadata-only",
        "included_files": [
            "index.html",
            "manifest.json",
            "events.json",
            "agent-compliance-summary.json",
            "policies.json",
            "skills.json",
            "chain-root.json",
        ],
        "agent_compliance": {
            "status": "queued",
            "metrics": [
                "events",
                "users",
                "providers",
                "sessions",
                "repos",
                "file_targets",
                "tool_permission_events",
                "mcp_tool_events",
                "full_access_events",
                "autonomous_events",
                "approvals",
                "denials",
                "warnings",
                "violations",
                "errors",
                "tokens_input",
                "tokens_output",
                "tokens_total",
                "cost_usd",
                "avg_latency_ms",
                "source_envelope_hashes",
                "top_tools",
                "top_mcp_tools",
                "top_files",
                "policy_decisions",
                "approval_statuses",
                "source_record_types",
                "retention_states",
            ],
        },
        "excluded_raw_content_keys": sorted(RAW_CONTENT_KEYS),
    }
    job = Job(
        id=new_uuid(),
        org_id=org_id,
        type="audit_evidence_package",
        status="pending",
        result_json=preview,
    )
    db.add(job)
    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        preview["agent_compliance"]["status"] = "preview"
        return EvidencePackageResponse(job_id=job.id, status="preview", queued=False, result=preview)
    try:
        from apps.worker.worker import build_evidence_package_task

        build_evidence_package_task.apply_async(
            args=[job.id, org_id, payload.control, payload.period_start.isoformat(), payload.period_end.isoformat()],
            retry=False,
            ignore_result=True,
        )
    except Exception:
        pass
    return EvidencePackageResponse(job_id=job.id, status=job.status, queued=True, result=preview)


@router.get("/evidence-packages/{job_id}", response_model=dict[str, Any])
async def get_evidence_package(
    org_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _assert_enabled(org_id, current_org_id, db)
    job = await db.get(Job, job_id)
    if job is None or job.org_id != org_id or job.type != "audit_evidence_package":
        raise HTTPException(status_code=404, detail="Evidence package not found")
    return {"job_id": job.id, "status": job.status, "result": job.result_json or {}, "created_at": job.created_at.isoformat()}


async def build_evidence_package_for_job(db: AsyncSession, job_id: str, org_id: str, control: str, period_start: str, period_end: str) -> dict[str, Any]:
    start = datetime.fromisoformat(period_start)
    end = datetime.fromisoformat(period_end)
    await _ensure_chain(db, org_id)
    rows = (await db.execute(select(AuditEvent).where(*_filters(org_id, date_from=start, date_to=end)).order_by(AuditEvent.created_at))).scalars().all()
    agent_compliance = _agent_compliance_evidence(list(rows))
    latest_root = (
        await db.execute(select(AuditHashChain).where(AuditHashChain.org_id == org_id).order_by(desc(AuditHashChain.sequence)).limit(1))
    ).scalars().first()
    policies = (await db.execute(select(OrgPolicy).where(OrgPolicy.org_id == org_id).limit(500))).scalars().all()
    skills = (await db.execute(select(SkillVersion).limit(500))).scalars().all()
    chain_root = (
        {
            "root_hash": latest_root.root_hash,
            "sequence": latest_root.sequence,
            "merkle_proof": latest_root.merkle_proof or [],
        }
        if latest_root
        else None
    )
    package_bytes = build_evidence_package_zip(
        org_id=org_id,
        control=control,
        period_start=period_start,
        period_end=period_end,
        events=[_evidence_event_payload(row) for row in rows],
        chain_root=chain_root,
        policies=[{"id": row.id, "name": row.name, "rule_type": row.rule_type} for row in policies],
        skills=[{"id": row.id, "version": row.version_number, "skill_id": row.skill_id, "domain": row.domain} for row in skills],
        agent_compliance=agent_compliance,
    )
    output_dir = os.getenv("AUDIT_EVIDENCE_PACKAGE_DIR", "/tmp/skillayer-evidence")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{job_id}.zip")
    with open(output_path, "wb") as handle:
        handle.write(package_bytes)
    return {
        "path": output_path,
        "bytes": len(package_bytes),
        "event_count": len(rows),
        "index_format": "html",
        "chain_root": chain_root,
        "content_retention": "metadata-only",
        "agent_compliance": agent_compliance,
    }
