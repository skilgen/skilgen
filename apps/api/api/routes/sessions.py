from __future__ import annotations

from datetime import datetime
import re
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.services.memory import run_session_knowledge_extraction
from apps.api.api.services.session_artifacts import append_session_artifact, close_session, parse_tool_artifact
from packages.db.database import get_db
from packages.db.models import AgentSession, Repo, Skill, SkillVersion


router = APIRouter(tags=["sessions"])


class CreateSessionBody(BaseModel):
    agent_runtime: str
    skills_loaded: list[str] = []


class UpdateSessionBody(BaseModel):
    code_produced: str | None = None
    outcome: str | None = None
    session_end: datetime | None = None
    notes: str | None = None


class SessionArtifactBody(BaseModel):
    session_id: str | None = None
    agent_runtime: str = "claude_code"
    tool: str
    file_path: str | None = None
    before_content: str | None = None
    after_content: str | None = None
    tool_input: dict | None = None
    tool_response: dict | None = None
    task_description: str | None = None
    engineer_login: str | None = None
    ts: datetime | None = None


def _duration(session: AgentSession) -> int | None:
    end = session.session_end
    start = session.session_start or session.created_at
    if not end or not start:
        return None
    return max(0, int((end - start).total_seconds()))


def _session_payload(session: AgentSession, repo: Repo | None = None) -> dict:
    return {
        "id": session.id,
        "session_id": session.session_id,
        "org_id": session.org_id,
        "repo_id": session.repo_id,
        "repo_name": repo.name if repo else None,
        "agent_runtime": session.agent_runtime,
        "skills_loaded": list(session.skills_loaded or []),
        "skill_paths_loaded": list(session.skill_paths_loaded or []),
        "code_produced": session.code_produced,
        "produced_artifacts": list(getattr(session, "produced_artifacts", []) or []),
        "produced_file_hashes": dict(getattr(session, "produced_file_hashes", {}) or {}),
        "closed_at": session.closed_at.isoformat() if getattr(session, "closed_at", None) else None,
        "last_artifact_at": session.last_artifact_at.isoformat() if getattr(session, "last_artifact_at", None) else None,
        "outcome": session.outcome or "unknown",
        "notes": session.notes,
        "session_start": (session.session_start or session.created_at).isoformat(),
        "session_end": session.session_end.isoformat() if session.session_end else None,
        "duration_seconds": _duration(session),
        "created_at": session.created_at.isoformat(),
    }


async def _repo(db: AsyncSession, repo_id: str, org_id: str) -> Repo:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return repo


@router.post("/repos/{repo_id}/sessions")
async def create_session(repo_id: str, body: CreateSessionBody, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = await _repo(db, repo_id, current_org_id)
    session = AgentSession(
        repo_id=repo_id,
        org_id=repo.org_id,
        session_id=str(uuid4()),
        agent_runtime=body.agent_runtime,
        skills_loaded=list(body.skills_loaded),
        skill_paths_loaded=list(body.skills_loaded),
        extraction_status="complete",
    )
    db.add(session)
    await db.commit()
    return {"session_id": session.id}


@router.patch("/repos/{repo_id}/sessions/{session_id}")
async def update_session(repo_id: str, session_id: str, body: UpdateSessionBody, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    await _repo(db, repo_id, current_org_id)
    session = (await db.execute(select(AgentSession).where(AgentSession.repo_id == repo_id, AgentSession.id == session_id))).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    for field in ("code_produced", "outcome", "notes"):
        value = getattr(body, field)
        if value is not None:
            setattr(session, field, value)
    session.session_end = body.session_end.replace(tzinfo=None) if body.session_end else datetime.utcnow()
    await db.commit()
    return _session_payload(session)


@router.post("/repos/{repo_id}/sessions/artifacts")
async def record_session_artifact(
    repo_id: str,
    body: SessionArtifactBody,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict:
    repo = await _repo(db, repo_id, current_org_id)
    parsed = parse_tool_artifact(body.tool, body.tool_input, body.tool_response)
    file_path = body.file_path or (parsed.file_path if parsed else None)
    after_content = body.after_content if body.after_content is not None else (parsed.after_content if parsed else None)
    if body.tool not in {"Edit", "Write", "NotebookEdit"} or not file_path:
        raise HTTPException(status_code=400, detail="Unsupported or incomplete artifact payload")
    try:
        session, artifact, closed_sessions = await append_session_artifact(
            db,
            repo=repo,
            agent_runtime=body.agent_runtime,
            file_path=file_path,
            tool=body.tool,
            before_content=body.before_content,
            after_content=after_content,
            external_session_id=body.session_id,
            task_description=body.task_description,
            engineer_login=body.engineer_login,
            ts=body.ts,
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    for closed in closed_sessions:
        background_tasks.add_task(run_session_knowledge_extraction, closed.id, [], repo_id)
    return {
        "session_id": session.id,
        "external_session_id": session.session_id,
        "artifact": artifact,
        "artifact_count": len(session.produced_artifacts or []),
        "closed_sessions": [closed.id for closed in closed_sessions],
    }


@router.post("/repos/{repo_id}/sessions/{session_id}/close")
async def close_agent_session(
    repo_id: str,
    session_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict:
    await _repo(db, repo_id, current_org_id)
    try:
        session = await close_session(db, repo_id=repo_id, session_id=session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        await db.commit()
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise
    background_tasks.add_task(run_session_knowledge_extraction, session.id, [], repo_id)
    return _session_payload(session)


@router.get("/repos/{repo_id}/agent-sessions")
async def list_repo_sessions(repo_id: str, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = await _repo(db, repo_id, current_org_id)
    total = int((await db.execute(select(func.count(AgentSession.id)).where(AgentSession.repo_id == repo_id))).scalar() or 0)
    sessions = (await db.execute(select(AgentSession).where(AgentSession.repo_id == repo_id).order_by(desc(AgentSession.created_at)).limit(limit).offset(offset))).scalars().all()
    return {"sessions": [_session_payload(session, repo) for session in sessions], "total": total}


@router.get("/repos/{repo_id}/agent-sessions/{session_id}")
async def get_session(repo_id: str, session_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = await _repo(db, repo_id, current_org_id)
    session = (await db.execute(select(AgentSession).where(AgentSession.repo_id == repo_id, AgentSession.id == session_id))).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_payload(session, repo)


def _chunks(code: str) -> list[str]:
    parts = re.split(r"(?=^\\s*(?:def|class|function|export function)\\s+)", code, flags=re.MULTILINE)
    if len(parts) <= 1:
        lines = code.splitlines()
        return ["\n".join(lines[index : index + 20]) for index in range(0, len(lines), 20) if lines[index : index + 20]]
    return [part.strip() for part in parts if part.strip()]


def _overlap(left: str, right: str) -> float:
    left_words = {word.lower() for word in re.findall(r"[A-Za-z_]{5,}", left)}
    right_words = {word.lower() for word in re.findall(r"[A-Za-z_]{5,}", right)}
    if not left_words or not right_words:
        return 0.0
    return len(left_words & right_words) / max(1, len(left_words))


@router.get("/repos/{repo_id}/sessions/{session_id}/replay")
async def replay_session(repo_id: str, session_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = await _repo(db, repo_id, current_org_id)
    session = (await db.execute(select(AgentSession).where(AgentSession.repo_id == repo_id, AgentSession.id == session_id))).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    skill_names = set(session.skills_loaded or session.skill_paths_loaded or [])
    skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
    if skill_names:
        skills = [skill for skill in skills if skill.id in skill_names or skill.domain in skill_names or skill.skill_path in skill_names] or skills
    versions = {}
    for skill in skills:
        version = (await db.execute(select(SkillVersion).where(SkillVersion.skill_id == skill.id).order_by(desc(SkillVersion.version_number)).limit(1))).scalar_one_or_none()
        versions[skill.domain] = {"name": skill.domain, "content": version.content if version else skill.content or ""}
    replay = []
    for index, chunk in enumerate(_chunks(session.code_produced or "")):
        best_name = None
        best_score = 0.0
        for name, payload in versions.items():
            score = _overlap(chunk, payload["content"])
            if score > best_score:
                best_name = name
                best_score = score
        replay.append({"chunk_index": index, "code": chunk, "matched_skill": best_name if best_score > 0 else None, "confidence": round(min(1, best_score), 2)})
    return {"session": _session_payload(session, repo), "replay": replay, "skills": versions}


@router.get("/orgs/{org_id}/sessions")
async def list_org_sessions(org_id: str, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    actual_org_id = current_org_id or org_id
    repos = {repo.id: repo for repo in (await db.execute(select(Repo).where(Repo.org_id == actual_org_id))).scalars().all()}
    total = int((await db.execute(select(func.count(AgentSession.id)).where(AgentSession.org_id == actual_org_id))).scalar() or 0)
    sessions = (await db.execute(select(AgentSession).where(AgentSession.org_id == actual_org_id).order_by(desc(AgentSession.created_at)).limit(limit).offset(offset))).scalars().all()
    return {"sessions": [_session_payload(session, repos.get(session.repo_id)) for session in sessions], "total": total}
