from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import difflib
import hashlib
from uuid import uuid4

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AgentSession, Repo


EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
DEFAULT_TIMEOUT_MINUTES = 30


@dataclass(frozen=True)
class ParsedToolArtifact:
    tool: str
    file_path: str
    after_content: str | None = None


def sha256_text(content: str | None) -> str | None:
    if content is None:
        return None
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def unified_diff(file_path: str, before_content: str | None, after_content: str | None) -> str:
    before_lines = (before_content or "").splitlines(keepends=True)
    after_lines = (after_content or "").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
    )


def parse_tool_artifact(tool: str, tool_input: dict | None = None, tool_response: dict | None = None) -> ParsedToolArtifact | None:
    """Extract artifact fields from Claude Code's distinct edit tool payloads."""
    payload = tool_input or {}
    response = tool_response or {}
    if tool == "Edit":
        file_path = payload.get("file_path") or payload.get("path")
        after_content = response.get("content") or response.get("after_content")
    elif tool == "Write":
        file_path = payload.get("file_path") or payload.get("path")
        after_content = payload.get("content") or response.get("content")
    elif tool == "NotebookEdit":
        file_path = payload.get("notebook_path") or payload.get("file_path") or payload.get("path")
        after_content = response.get("content") or response.get("after_content") or payload.get("new_source")
    else:
        return None
    if not file_path:
        return None
    return ParsedToolArtifact(tool=tool, file_path=str(file_path), after_content=after_content)


def should_run_close_pass(session: AgentSession | None, now: datetime) -> bool:
    if session is None:
        return True
    last_artifact_at = getattr(session, "last_artifact_at", None)
    if last_artifact_at is None:
        return True
    timeout = getattr(session, "inactivity_timeout_minutes", DEFAULT_TIMEOUT_MINUTES) or DEFAULT_TIMEOUT_MINUTES
    normalized = _naive(last_artifact_at)
    return bool(normalized and (now - normalized) > timedelta(minutes=timeout / 2))


def _artifact_timestamp(ts: datetime | None) -> datetime:
    return ts.replace(tzinfo=None) if ts else datetime.utcnow()


def _naive(ts: datetime | None) -> datetime | None:
    return ts.replace(tzinfo=None) if ts else None


def make_artifact_record(
    *,
    file_path: str,
    tool: str,
    before_content: str | None,
    after_content: str | None,
    ts: datetime | None = None,
) -> dict:
    timestamp = _artifact_timestamp(ts)
    return {
        "file_path": file_path,
        "tool": tool,
        "before_hash": sha256_text(before_content),
        "after_hash": sha256_text(after_content),
        "diff": unified_diff(file_path, before_content, after_content),
        "ts": timestamp.isoformat() + "Z",
    }


async def _latest_open_session(
    db: AsyncSession,
    *,
    org_id: str,
    repo_id: str,
    agent_runtime: str,
    external_session_id: str | None = None,
) -> AgentSession | None:
    filters = [
        AgentSession.org_id == org_id,
        AgentSession.repo_id == repo_id,
        AgentSession.agent_runtime == agent_runtime,
        AgentSession.closed_at.is_(None),
    ]
    if external_session_id:
        exact = (
            await db.execute(
                select(AgentSession)
                .where(*filters, AgentSession.session_id == external_session_id)
                .order_by(desc(AgentSession.last_artifact_at), desc(AgentSession.created_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if exact is not None:
            return exact
        return None
    return (
        await db.execute(
            select(AgentSession)
            .where(*filters)
            .order_by(desc(AgentSession.last_artifact_at), desc(AgentSession.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()


async def close_inactive_sessions(db: AsyncSession, *, org_id: str, repo_id: str, now: datetime) -> list[AgentSession]:
    open_sessions = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.org_id == org_id,
                AgentSession.repo_id == repo_id,
                AgentSession.closed_at.is_(None),
            )
        )
    ).scalars().all()
    closed: list[AgentSession] = []
    for session in open_sessions:
        timeout = session.inactivity_timeout_minutes or DEFAULT_TIMEOUT_MINUTES
        last_seen = _naive(session.last_artifact_at or session.session_end or session.session_start or session.created_at)
        if last_seen and (now - last_seen) > timedelta(minutes=timeout):
            session.closed_at = now
            session.session_end = session.session_end or now
            closed.append(session)
    return closed


async def append_session_artifact(
    db: AsyncSession,
    *,
    repo: Repo,
    agent_runtime: str,
    file_path: str,
    tool: str,
    before_content: str | None,
    after_content: str | None,
    external_session_id: str | None = None,
    task_description: str | None = None,
    engineer_login: str | None = None,
    ts: datetime | None = None,
) -> tuple[AgentSession, dict, list[AgentSession]]:
    now = _artifact_timestamp(ts)
    session = await _latest_open_session(
        db,
        org_id=repo.org_id,
        repo_id=repo.id,
        agent_runtime=agent_runtime,
        external_session_id=external_session_id,
    )
    closed_sessions: list[AgentSession] = []
    if should_run_close_pass(session, now):
        closed_sessions = await close_inactive_sessions(db, org_id=repo.org_id, repo_id=repo.id, now=now)
        if session in closed_sessions:
            session = None
    if session is None:
        session = AgentSession(
            repo_id=repo.id,
            org_id=repo.org_id,
            session_id=external_session_id or str(uuid4()),
            agent_runtime=agent_runtime,
            task_description=task_description,
            engineer_login=engineer_login,
            session_start=now,
            extraction_status="pending",
        )
        db.add(session)

    artifact = make_artifact_record(
        file_path=file_path,
        tool=tool,
        before_content=before_content,
        after_content=after_content,
        ts=now,
    )
    artifacts = list(session.produced_artifacts or [])
    artifacts.append(artifact)
    session.produced_artifacts = artifacts

    hashes = dict(session.produced_file_hashes or {})
    if artifact["after_hash"]:
        hashes[file_path] = artifact["after_hash"]
    session.produced_file_hashes = hashes

    touched = list(session.files_touched or [])
    if file_path not in touched:
        touched.append(file_path)
    session.files_touched = touched

    diff_block = artifact["diff"]
    session.code_produced = f"{session.code_produced}\n\n{diff_block}".strip() if session.code_produced else diff_block
    session.last_artifact_at = now
    session.session_end = now
    return session, artifact, closed_sessions


async def close_session(db: AsyncSession, *, repo_id: str, session_id: str, now: datetime | None = None) -> AgentSession | None:
    timestamp = _artifact_timestamp(now)
    session = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.repo_id == repo_id,
                or_(AgentSession.id == session_id, AgentSession.session_id == session_id),
            )
        )
    ).scalar_one_or_none()
    if session is None:
        return None
    if session.closed_at is None:
        session.closed_at = timestamp
    session.session_end = session.session_end or timestamp
    return session
