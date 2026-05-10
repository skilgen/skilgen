from __future__ import annotations

from datetime import datetime
import hashlib
import json
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import AgentSession, AuditEvent, Repo


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


def _agent_compliance_audit_event(org_id: str, payload: AgentRunPayload, repo: Repo, session_key: str, runtime: str, artifacts: list[dict[str, Any]]) -> AuditEvent:
    metadata = dict(payload.metadata or {})
    sanitized_envelope = _sanitized_agent_run_envelope(payload, artifacts, repo, session_key, runtime)
    envelope_hash = hashlib.sha256(json.dumps(sanitized_envelope, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    provider = _metadata_string(metadata, "provider", "agent_provider", "source_provider") or f"{payload.agent.vendor} {payload.agent.product}".strip()
    access_scope = _metadata_string(metadata, "access_scope", "permission_scope", "grant_scope") or ("full-access" if _metadata_bool(metadata, "full_access", "full_access_granted") else "unspecified")
    tool_permissions = _tool_names(artifacts, metadata)
    compliance_metadata: dict[str, Any] = {
        "provider": provider,
        "agent_provider": provider,
        "agent_runtime": runtime,
        "model": _metadata_string(metadata, "model", "model_name", "model_id"),
        "intelligence_tier": _metadata_string(metadata, "intelligence_tier", "model_tier", "reasoning_tier"),
        "access_scope": access_scope,
        "full_access": _metadata_bool(metadata, "full_access", "full_access_granted") or access_scope == "full-access",
        "autonomous_access": _metadata_bool(metadata, "autonomous_access", "autonomous"),
        "tool_permissions": tool_permissions,
        "repo_name": repo.full_name or repo.name,
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
        session = (
            await db.execute(select(AgentSession).where(AgentSession.repo_id == repo.id, AgentSession.session_id == session_key))
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
            )
            db.add(session)
            status = "created"

        session.agent_runtime = runtime
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
        db.add(_agent_compliance_audit_event(org_id, payload, repo, session_key, runtime, artifacts))
        await db.commit()
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise

    return {"session_id": str(session.id or session_key), "status": status}
