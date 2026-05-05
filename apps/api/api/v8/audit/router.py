from __future__ import annotations

from datetime import UTC, datetime
from io import StringIO
import csv
import json
import os
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
import apps.api.api.v8.audit.chain as chain
from apps.api.api.v8.audit.evidence import build_evidence_package_zip
from apps.api.api.v8.audit.reports import REPORTS, REPORTS_BY_ID, report_sql
from apps.api.api.v8.audit.storage import publish_worm_root, root_document
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


class PublishRootResponse(BaseModel):
    root_hash: str
    object_key: str | None
    status: str
    event_count: int


class EvidencePackageRequest(BaseModel):
    control: str
    period_start: datetime
    period_end: datetime


class EvidencePackageResponse(BaseModel):
    job_id: str
    status: str
    queued: bool


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


async def _ensure_chain(db: AsyncSession, org_id: str) -> list[AuditHashChain]:
    existing_rows = (
        await db.execute(select(AuditHashChain).where(AuditHashChain.org_id == org_id).order_by(AuditHashChain.sequence))
    ).scalars().all()
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
        await db.commit()
    return (await db.execute(select(AuditHashChain).where(AuditHashChain.org_id == org_id).order_by(AuditHashChain.sequence))).scalars().all()


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
    )
    object_key, status = publish_worm_root(document)
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
    return PublishRootResponse(root_hash=last.root_hash, object_key=object_key, status=status, event_count=len(chain_rows))


@router.post("/evidence-packages", response_model=EvidencePackageResponse)
async def create_evidence_package(
    org_id: str,
    payload: EvidencePackageRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> EvidencePackageResponse:
    await _assert_enabled(org_id, current_org_id, db)
    job = Job(
        id=new_uuid(),
        org_id=org_id,
        type="audit_evidence_package",
        status="pending",
        result_json={
            "control": payload.control,
            "period_start": payload.period_start.isoformat(),
            "period_end": payload.period_end.isoformat(),
            "index_format": "html",
        },
    )
    db.add(job)
    await db.commit()
    try:
        from apps.worker.worker import build_evidence_package_task

        build_evidence_package_task.apply_async(
            args=[job.id, org_id, payload.control, payload.period_start.isoformat(), payload.period_end.isoformat()],
            retry=False,
            ignore_result=True,
        )
    except Exception:
        pass
    return EvidencePackageResponse(job_id=job.id, status=job.status, queued=True)


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
        events=[{"id": row.id, **_event_payload(row)} for row in rows],
        chain_root=chain_root,
        policies=[{"id": row.id, "name": row.name, "rule_type": row.rule_type} for row in policies],
        skills=[{"id": row.id, "version": row.version_number, "skill_id": row.skill_id, "domain": row.domain} for row in skills],
    )
    output_dir = os.getenv("AUDIT_EVIDENCE_PACKAGE_DIR", "/tmp/skillayer-evidence")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{job_id}.zip")
    with open(output_path, "wb") as handle:
        handle.write(package_bytes)
    return {"path": output_path, "bytes": len(package_bytes), "event_count": len(rows), "index_format": "html", "chain_root": chain_root}
