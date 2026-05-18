from __future__ import annotations

from datetime import datetime
import hashlib
import json
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import AgentSession, AuditEvent, PullRequest, Repo


router = APIRouter(prefix="/orgs", tags=["agent-runs"])


class AgentRunAgent(BaseModel):
    vendor: str
    product: str
    version: str | None = None
    runtime: str | None = None


class AgentRunRepo(BaseModel):
    id: str | None = None
    full_name: str | None = None
    name: str | None = None


class AgentRunUser(BaseModel):
    login: str | None = None
    email: str | None = None
    name: str | None = None


class AgentRunArtifact(BaseModel):
    file_path: str
    tool: str | None = None
    before_hash: str | None = None
    after_hash: str | None = None
    diff: str | None = None
    content: str | None = None
    ts: datetime | None = None


class AgentRunPayload(BaseModel):
    spec_version: str = "0"
    run_id: str | None = None
    session_id: str | None = None
    agent: AgentRunAgent
    repo_id: str | None = None
    repo: AgentRunRepo | None = None
    user: AgentRunUser | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    skills_loaded: list[str | dict[str, Any]] = Field(default_factory=list)
    code_artifacts: list[AgentRunArtifact] = Field(default_factory=list)
    code_produced: str | list[dict[str, Any]] | None = None
    outcome: Literal["success", "needs_rework", "unknown"] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def _runtime(agent: AgentRunAgent) -> str:
    if agent.runtime:
        return agent.runtime
    product = f"{agent.vendor} {agent.product}".lower()
    if "claude" in product:
        return "claude_code"
    if "codex" in product:
        return "codex_cli"
    if "cursor" in product:
        return "cursor"
    if "copilot" in product:
        return "copilot"
    if "devin" in product:
        return "devin"
    return product.replace(" ", "_")[:64] or "agent"


def _skill_name(item: str | dict[str, Any]) -> str:
    if isinstance(item, str):
        return item
    for key in ("skill_path", "path", "domain", "name", "id"):
        value = item.get(key)
        if value:
            return str(value)
    return json.dumps(item, sort_keys=True)


def _artifact_dict(artifact: AgentRunArtifact) -> dict[str, Any]:
    payload = artifact.model_dump(mode="json", exclude_none=True)
    if not payload.get("after_hash") and payload.get("content") is not None:
        payload["after_hash"] = hashlib.sha256(str(payload["content"]).encode("utf-8")).hexdigest()
    payload["tool"] = payload.get("tool") or "AgentRun"
    payload["ts"] = payload.get("ts") or datetime.utcnow().isoformat() + "Z"
    return payload


def _code_text(payload: AgentRunPayload, artifacts: list[dict[str, Any]]) -> str | None:
    if isinstance(payload.code_produced, str):
        return payload.code_produced
    if isinstance(payload.code_produced, list):
        return "\n\n".join(json.dumps(item, sort_keys=True) for item in payload.code_produced)
    chunks = [str(item.get("diff") or item.get("content") or "") for item in artifacts]
    return "\n\n".join(chunk for chunk in chunks if chunk).strip() or None


def _metadata_string(metadata: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = metadata.get(key)
        if value not in {None, ""}:
            return str(value)
    return None


def _metadata_bool(metadata: dict[str, Any], *keys: str) -> bool:
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "full", "full-access", "autonomous"}:
            return True
    return False


def _metadata_int(metadata: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.strip():
            try:
                return int(float(value))
            except ValueError:
                continue
    return None


def _metadata_float(metadata: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str) and value.strip():
            try:
                return float(value)
            except ValueError:
                continue
    return None


def _metadata_list(metadata: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if item not in {None, ""})
        elif isinstance(value, dict):
            values.extend(str(item) for item in value.keys())
        elif isinstance(value, str) and value.strip():
            values.append(value.strip())
    return sorted(dict.fromkeys(values))


def _safe_tool_label(value: object) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("name", "tool", "tool_name", "mcp_tool", "id"):
            label = value.get(key)
            if isinstance(label, str) and label.strip():
                return label.strip()
        return None
    return None


def _tool_names(artifacts: list[dict[str, Any]], metadata: dict[str, Any]) -> list[str]:
    names = [str(item.get("tool")) for item in artifacts if item.get("tool")]
    for key in ("tool_permissions", "tools", "tool_calls", "mcp_tools"):
        value = metadata.get(key)
        if isinstance(value, list):
            names.extend(label for item in value if (label := _safe_tool_label(item)))
        elif isinstance(value, dict):
            label = _safe_tool_label(value)
            if label:
                names.append(label)
            else:
                names.extend(str(item) for item in value.keys() if item not in {"args", "arguments", "parameters", "params", "input", "content", "prompt", "diff"})
        elif isinstance(value, str) and value.strip():
            names.append(value.strip())
    return sorted(dict.fromkeys(names))


def _activity_metrics(metadata: dict[str, Any], artifacts: list[dict[str, Any]], tool_permissions: list[str]) -> dict[str, int]:
    raw = metadata.get("activity_metrics")
    raw_metrics = raw if isinstance(raw, dict) else {}

    def metric(name: str, *fallback_keys: str, fallback: int = 0) -> int:
        value = raw_metrics.get(name)
        if isinstance(value, bool):
            value = None
        if isinstance(value, int | float):
            return int(value)
        if isinstance(value, str) and value.strip():
            try:
                return int(float(value))
            except ValueError:
                pass
        direct = _metadata_int(metadata, name, *fallback_keys)
        return int(direct if direct is not None else fallback)

    return {
        "edited_files": metric("edited_files", fallback=len([item for item in artifacts if item.get("file_path")])),
        "explored_files": metric("explored_files"),
        "searches": metric("searches", "search_count"),
        "lists": metric("lists", "list_count"),
        "commands": metric("commands", "command_count"),
        "tool_calls": metric("tool_calls", "tool_call_count", fallback=len(tool_permissions)),
        "mcp_tools": metric("mcp_tools", "mcp_tool_count", fallback=len(_metadata_list(metadata, "mcp_tools"))),
    }


def _activity_details(metadata: dict[str, Any], artifacts: list[dict[str, Any]], tool_permissions: list[str]) -> dict[str, list[str]]:
    raw = metadata.get("activity_details")
    raw_details = raw if isinstance(raw, dict) else {}

    def detail(name: str, fallback: list[str] | None = None) -> list[str]:
        value = raw_details.get(name)
        if isinstance(value, list):
            return sorted(dict.fromkeys(str(item) for item in value if item not in {None, ""}))
        return sorted(dict.fromkeys(fallback or []))

    return {
        "edited_files": detail("edited_files", [str(item.get("file_path")) for item in artifacts if item.get("file_path")]),
        "explored_files": detail("explored_files"),
        "searches": detail("searches"),
        "lists": detail("lists"),
        "commands": detail("commands"),
        "tools": detail("tools", tool_permissions),
    }


async def _resolve_pr_context(db: AsyncSession, repo: Repo, metadata: dict[str, Any]) -> dict[str, Any]:
    pr_number = _metadata_int(metadata, "pr_number", "pull_request_number")
    pr_id = _metadata_string(metadata, "pr_id", "pull_request_id")
    head_sha = _metadata_string(metadata, "head_sha", "commit_sha", "sha")
    row = None
    try:
        if pr_number is not None:
            row = (
                await db.execute(select(PullRequest).where(PullRequest.repo_id == repo.id, PullRequest.github_pr_number == pr_number).limit(1))
            ).scalar_one_or_none()
        if row is None and pr_id:
            row = (await db.execute(select(PullRequest).where(PullRequest.repo_id == repo.id, PullRequest.id == pr_id).limit(1))).scalar_one_or_none()
        if row is None and head_sha:
            row = (await db.execute(select(PullRequest).where(PullRequest.repo_id == repo.id, PullRequest.head_sha == head_sha).limit(1))).scalar_one_or_none()
    except OperationalError:
        row = None
    if row is None:
        return {
            "pr_id": pr_id,
            "pr_number": pr_number,
            "pr_title": _metadata_string(metadata, "pr_title", "pull_request_title"),
            "head_sha": head_sha,
            "branch": _metadata_string(metadata, "branch", "head_branch"),
        }
    return {
        "pr_id": row.id,
        "pr_number": row.github_pr_number,
        "pr_title": row.title,
        "head_sha": row.head_sha,
        "branch": _metadata_string(metadata, "branch", "head_branch"),
    }


def _sanitized_agent_run_envelope(payload: AgentRunPayload, artifacts: list[dict[str, Any]], repo: Repo, session_key: str, runtime: str) -> dict[str, Any]:
    return {
        "spec_version": payload.spec_version,
        "run_id": payload.run_id,
        "session_id": session_key,
        "agent": payload.agent.model_dump(mode="json", exclude_none=True),
        "repo": {"id": repo.id, "name": repo.name, "full_name": repo.full_name},
        "user": payload.user.model_dump(mode="json", exclude_none=True) if payload.user else None,
        "runtime": runtime,
        "started_at": payload.started_at.isoformat() if payload.started_at else None,
        "ended_at": payload.ended_at.isoformat() if payload.ended_at else None,
        "skills_loaded": [_skill_name(item) for item in payload.skills_loaded],
        "artifacts": [
            {
                "file_path": item.get("file_path"),
                "tool": item.get("tool"),
                "before_hash": item.get("before_hash"),
                "after_hash": item.get("after_hash"),
                "ts": item.get("ts"),
            }
            for item in artifacts
        ],
        "outcome": payload.outcome,
    }


def _agent_compliance_audit_event(org_id: str, payload: AgentRunPayload, repo: Repo, session_key: str, runtime: str, artifacts: list[dict[str, Any]], pr_context: dict[str, Any] | None = None) -> AuditEvent:
    metadata = dict(payload.metadata or {})
    sanitized_envelope = _sanitized_agent_run_envelope(payload, artifacts, repo, session_key, runtime)
    envelope_hash = hashlib.sha256(json.dumps(sanitized_envelope, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    provider = _metadata_string(metadata, "provider", "agent_provider", "source_provider") or f"{payload.agent.vendor} {payload.agent.product}".strip()
    access_scope = _metadata_string(metadata, "access_scope", "permission_scope", "grant_scope") or ("full-access" if _metadata_bool(metadata, "full_access", "full_access_granted") else "unspecified")
    tool_permissions = _tool_names(artifacts, metadata)
    file_targets = sorted(dict.fromkeys([str(item.get("file_path")) for item in artifacts if item.get("file_path")] + _metadata_list(metadata, "file_targets", "files", "file_scope")))
    activity_metrics = _activity_metrics(metadata, artifacts, tool_permissions)
    activity_details = _activity_details(metadata, artifacts, tool_permissions)
    input_tokens = _metadata_int(metadata, "tokens_input", "input_tokens", "prompt_tokens")
    output_tokens = _metadata_int(metadata, "tokens_output", "output_tokens", "completion_tokens")
    total_tokens = _metadata_int(metadata, "tokens_total", "total_tokens") or ((input_tokens or 0) + (output_tokens or 0) or None)
    pr_context = {key: value for key, value in (pr_context or {}).items() if value not in {None, ""}}
    compliance_metadata: dict[str, Any] = {
        "provider": provider,
        "agent_provider": provider,
        "agent_runtime": runtime,
        "model": _metadata_string(metadata, "model", "model_name", "model_id"),
        "intelligence_tier": _metadata_string(metadata, "intelligence_tier", "model_tier", "reasoning_tier"),
        "task_type": _metadata_string(metadata, "task_type", "task", "workflow_type", "intent"),
        "access_scope": access_scope,
        "full_access": _metadata_bool(metadata, "full_access", "full_access_granted") or access_scope == "full-access",
        "autonomous_access": _metadata_bool(metadata, "autonomous_access", "autonomous"),
        "tool_permissions": tool_permissions,
        "mcp_tools": _metadata_list(metadata, "mcp_tools"),
        "file_targets": file_targets,
        "activity_metrics": activity_metrics,
        "activity_details": activity_details,
        "edited_files": activity_metrics["edited_files"],
        "explored_files": activity_metrics["explored_files"],
        "searches": activity_metrics["searches"],
        "lists": activity_metrics["lists"],
        "commands": activity_metrics["commands"],
        "repo_name": repo.full_name or repo.name,
        "session_id": session_key,
        "tokens_input": input_tokens,
        "tokens_output": output_tokens,
        "tokens_total": total_tokens,
        "cost_usd": _metadata_float(metadata, "cost_usd", "estimated_cost_usd"),
        "latency_ms": _metadata_float(metadata, "latency_ms", "duration_ms"),
        "policy_decision": _metadata_string(metadata, "policy_decision", "decision"),
        "approval_status": _metadata_string(metadata, "approval_status"),
        "source_record_types": _metadata_list(metadata, "source_record_types", "source_record_type"),
        **pr_context,
        "source_envelope_hash": envelope_hash,
        "provider_event_id": session_key,
        "formal_compliance_record": False,
        "content_retention": "metadata-only",
        "redaction_state": "raw-content-dropped",
    }
    compliance_metadata = {key: value for key, value in compliance_metadata.items() if value is not None and value != "" and value != []}
    severity = "critical" if compliance_metadata.get("full_access") or compliance_metadata.get("autonomous_access") else "warning" if tool_permissions else "info"
    return AuditEvent(
        org_id=org_id,
        event_type="agent.compliance",
        action="ingested",
        summary=f"Normalized AgentRun metadata for {provider}",
        actor_login=payload.user.login if payload.user else None,
        repo_id=repo.id,
        repo_name=repo.full_name or repo.name,
        resource_type="agent_run",
        resource_id=session_key,
        severity=severity,
        metadata_json=compliance_metadata,
    )


async def _resolve_repo(db: AsyncSession, org_id: str, payload: AgentRunPayload) -> Repo:
    repo_id = payload.repo_id or (payload.repo.id if payload.repo else None)
    if repo_id:
        repo = (await db.execute(select(Repo).where(Repo.id == repo_id, Repo.org_id == org_id))).scalar_one_or_none()
        if repo:
            return repo
        raise HTTPException(status_code=404, detail="Repo not found")

    full_name = payload.repo.full_name if payload.repo else None
    if full_name:
        repo = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.full_name == full_name))).scalar_one_or_none()
        if repo:
            return repo

    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).limit(2))).scalars().all()
    if len(repos) == 1:
        return repos[0]
    raise HTTPException(status_code=400, detail="AgentRun payload must include repo_id or repo.full_name")


@router.post("/{org_id}/agent-runs")
async def ingest_agent_run(
    org_id: str,
    payload: AgentRunPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, str]:
    if current_org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    repo = await _resolve_repo(db, org_id, payload)
    session_key = payload.session_id or payload.run_id
    if not session_key:
        raise HTTPException(status_code=400, detail="AgentRun payload must include session_id or run_id")

    runtime = _runtime(payload.agent)
    started_at = (payload.started_at or datetime.utcnow()).replace(tzinfo=None)
    ended_at = payload.ended_at.replace(tzinfo=None) if payload.ended_at else None
    skills_loaded = [_skill_name(item) for item in payload.skills_loaded]
    artifacts = [_artifact_dict(item) for item in payload.code_artifacts]
    code_text = _code_text(payload, artifacts)

    try:
        pr_context = await _resolve_pr_context(db, repo, payload.metadata or {})
        session = (
            await db.execute(select(AgentSession).where(AgentSession.repo_id == repo.id, AgentSession.session_id == session_key))
        ).scalar_one_or_none()
        existing_audit = (
            await db.execute(
                select(AuditEvent)
                .where(
                    AuditEvent.org_id == org_id,
                    AuditEvent.event_type == "agent.compliance",
                    AuditEvent.resource_type == "agent_run",
                    AuditEvent.resource_id == session_key,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        status = "updated"
        if session is None:
            session = AgentSession(
                repo_id=repo.id,
                org_id=org_id,
                session_id=session_key,
                agent_runtime=runtime,
                engineer_login=payload.user.login if payload.user else None,
                session_start=started_at,
                extraction_status="pending",
                created_at=started_at,
            )
            db.add(session)
            status = "created"

        session.agent_runtime = runtime
        if session.created_at is None or session.created_at > started_at:
            session.created_at = started_at
        if session.session_start is None or session.session_start > started_at:
            session.session_start = started_at
        session.session_end = ended_at or session.session_end
        session.closed_at = ended_at or session.closed_at
        session.outcome = payload.outcome or session.outcome
        session.skills_loaded = list(dict.fromkeys([*(session.skills_loaded or []), *skills_loaded]))
        session.skill_paths_loaded = list(dict.fromkeys([*(session.skill_paths_loaded or []), *skills_loaded]))
        session.produced_artifacts = [*(session.produced_artifacts or []), *artifacts]
        hashes = dict(session.produced_file_hashes or {})
        for artifact in artifacts:
            if artifact.get("after_hash"):
                hashes[str(artifact["file_path"])] = str(artifact["after_hash"])
        session.produced_file_hashes = hashes
        touched = list(session.files_touched or [])
        for artifact in artifacts:
            path = str(artifact.get("file_path") or "")
            if path and path not in touched:
                touched.append(path)
        session.files_touched = touched
        if code_text:
            session.code_produced = f"{session.code_produced}\n\n{code_text}".strip() if session.code_produced else code_text
        repo.last_analysed_at = max(filter(None, [repo.last_analysed_at, ended_at, started_at]), default=started_at)
        audit_event = _agent_compliance_audit_event(org_id, payload, repo, session_key, runtime, artifacts, pr_context)
        audit_event.created_at = ended_at or started_at
        if existing_audit is None:
            db.add(audit_event)
        else:
            existing_audit.action = audit_event.action
            existing_audit.summary = audit_event.summary
            existing_audit.actor_login = audit_event.actor_login
            existing_audit.repo_id = audit_event.repo_id
            existing_audit.repo_name = audit_event.repo_name
            existing_audit.severity = audit_event.severity
            existing_audit.metadata_json = audit_event.metadata_json
            existing_audit.created_at = audit_event.created_at
        await db.commit()
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise

    return {"session_id": str(session.id or session_key), "status": status}
