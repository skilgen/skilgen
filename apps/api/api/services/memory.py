from __future__ import annotations

import json
from typing import Protocol

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from packages.db.database import get_sessionmaker
from packages.db.models import AgentSession, Org, Skill, SkillMemoryStub
from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError, call_llm


class SessionMessageLike(Protocol):
    role: str
    content: str


async def _latest_repo_skills(db: AsyncSession, repo_id: str) -> list[Skill]:
    rows = (
        await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(desc(Skill.created_at)))
    ).scalars().all()
    latest_by_domain: dict[str, Skill] = {}
    for skill in rows:
        latest_by_domain.setdefault(str(skill.domain).lower(), skill)
    return list(latest_by_domain.values())


async def run_session_knowledge_extraction(
    session_db_id: str,
    messages: list[SessionMessageLike],
    repo_id: str,
    sessionmaker: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    maker = sessionmaker or get_sessionmaker()
    async with maker() as db:
        await _extract_session_knowledge(session_db_id, messages, repo_id, db)


async def _extract_session_knowledge(
    session_db_id: str,
    messages: list[SessionMessageLike],
    repo_id: str,
    db: AsyncSession,
) -> None:
    """Background task: extract skill discoveries from a session transcript."""
    session = await db.get(AgentSession, session_db_id)
    if not session:
        return

    try:
        await db.execute(
            update(AgentSession)
            .where(AgentSession.id == session_db_id)
            .values(extraction_status="processing")
        )
        await db.commit()

        existing_skills = await _latest_repo_skills(db, repo_id)
        existing_summary = "\n".join(
            f"- {skill.domain}: {(skill.content or '')[:300]}..."
            for skill in existing_skills[:20]
        )
        transcript_text = _build_transcript_text(messages, max_chars=12000)
        org = await db.get(Org, session.org_id)
        stubs = await _call_extraction_llm(
            org_settings=org.settings if org is not None and isinstance(org.settings, dict) else {},
            transcript=transcript_text,
            task_description=session.task_description or "",
            files_touched=list(session.files_touched or []),
            existing_skills_summary=existing_summary,
            skill_paths_loaded=list(session.skill_paths_loaded or []),
        )

        for stub_data in stubs:
            matched_skill = next(
                (skill for skill in existing_skills if skill.domain.lower() == str(stub_data["domain"]).lower()),
                None,
            )
            db.add(
                SkillMemoryStub(
                    org_id=session.org_id,
                    repo_id=repo_id,
                    session_id=session.id,
                    domain=str(stub_data["domain"]),
                    skill_id=matched_skill.id if matched_skill else None,
                    discovery_type=str(stub_data["type"]),
                    title=str(stub_data["title"])[:256],
                    proposed_content=str(stub_data["content"]),
                    evidence=stub_data.get("evidence"),
                    confidence=float(stub_data.get("confidence", 0.8)),
                    agent_runtime=session.agent_runtime,
                    engineer_login=session.engineer_login,
                    task_description=session.task_description,
                    status="pending",
                )
            )

        await db.execute(
            update(AgentSession)
            .where(AgentSession.id == session_db_id)
            .values(
                extraction_status="done",
                discoveries_found=len(stubs),
                transcript_summary=_summarise_transcript(messages),
            )
        )
        await db.commit()
    except Exception:
        await db.rollback()
        await db.execute(
            update(AgentSession)
            .where(AgentSession.id == session_db_id)
            .values(extraction_status="failed", discoveries_found=0)
        )
        await db.commit()
        raise


def _build_transcript_text(messages: list[SessionMessageLike], max_chars: int = 12000) -> str:
    lines = [f"[{message.role.upper()}]: {message.content[:2000]}" for message in messages]
    text = "\n\n".join(lines)
    if len(text) > max_chars:
        text = "...[earlier messages truncated]...\n\n" + text[-max_chars:]
    return text


def _summarise_transcript(messages: list[SessionMessageLike]) -> str:
    for message in messages:
        if message.role == "assistant" and len(message.content) > 20:
            return message.content[:300]
    return ""


async def _call_extraction_llm(
    org_settings: dict | None,
    transcript: str,
    task_description: str,
    files_touched: list[str],
    existing_skills_summary: str,
    skill_paths_loaded: list[str],
) -> list[dict[str, object]]:
    prompt = f"""You are analyzing a coding agent session to extract novel institutional knowledge discoveries
that should be added to this organization's skill tree.

TASK THE ENGINEER GAVE THE AGENT:
{task_description or "(not provided)"}

FILES TOUCHED IN SESSION:
{chr(10).join(files_touched[:30]) or "(none)"}

SKILLS LOADED BY AGENT (existing coverage):
{chr(10).join(skill_paths_loaded[:20]) or "(none)"}

EXISTING SKILL SUMMARIES (do NOT propose things already covered here):
{existing_skills_summary or "(no skills yet)"}

SESSION TRANSCRIPT:
{transcript}

INSTRUCTIONS:
Identify discoveries that meet ALL of these criteria:
1. Novel and codebase-specific — not generic programming knowledge
2. NOT already documented in the existing skills listed above
3. Would help future agents work more effectively in this specific codebase
4. Represent undocumented patterns, gotchas, workarounds, architectural insights,
   dependency patterns, or contradictions with existing skills

For each discovery, output a JSON object with:
- domain: which skill domain (e.g. "auth", "payments", "database")
- type: one of undocumented_pattern | workaround | architectural_insight |
         gotcha | dependency_insight | contradiction
- title: concise title, max 10 words, starts with a verb or noun
- content: proposed addition in SKILL.md markdown format, 50-200 words,
           includes specific file paths, function names, or patterns observed
- evidence: which files/lines/observations support this
- confidence: 0.0-1.0 (how confident this is novel and codebase-specific)

ONLY include discoveries with confidence >= 0.7.
LIMIT to maximum 5 discoveries per session.
If nothing novel was discovered, return an empty array.

Return ONLY a valid JSON array. No explanation, no markdown fence, just the array."""
    try:
        raw = (await call_llm(org_settings or {}, "Extract institutional coding knowledge as JSON.", prompt, max_tokens=2048)).strip()
    except (LLMNotConfiguredError, LLMCallError):
        return []
    try:
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1])
        discoveries = json.loads(raw)
        if not isinstance(discoveries, list):
            return []
        return [
            item
            for item in discoveries
            if isinstance(item, dict) and float(item.get("confidence", 0)) >= 0.7
        ][:5]
    except Exception:
        return []
