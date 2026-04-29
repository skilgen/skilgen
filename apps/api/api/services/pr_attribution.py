from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AgentSession, Commit, PRAttribution, PullRequest


AGENT_VALUES = {"claude_code", "codex", "cursor", "copilot", "devin", "human", "mixed"}
TIER1_VENDOR_CONFIDENCE_CAPS = {
    "claude_code": 0.95,
    "codex": 0.90,
    "copilot": 0.75,
    "cursor": 0.80,
    "devin": 0.85,
    "mixed": 0.70,
    "human": 1.0,
}


@dataclass(frozen=True)
class AttributionDecision:
    primary_agent: str
    confidence: float
    lines_by_agent: dict[str, int]
    lines_by_human: int
    sessions: list[str]
    skills_loaded: list[str]


def _normalize_agent(value: str | None) -> str | None:
    text = (value or "").lower().strip()
    if not text:
        return None
    if "claude" in text:
        return "claude_code"
    if "copilot" in text:
        return "copilot"
    if "codex" in text:
        return "codex"
    if "cursor" in text:
        return "cursor"
    if "devin" in text:
        return "devin"
    if text in AGENT_VALUES:
        return text
    return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _commit_line_count(commit: Commit) -> int:
    return int(commit.additions or 0) + int(commit.deletions or 0)


def _extract_commit_content_hashes(raw: Any) -> set[str]:
    if not isinstance(raw, dict):
        return set()
    hashes: set[str] = set()

    for key in ("produced_file_hashes", "file_hashes", "resulting_file_hashes", "content_hashes"):
        values = raw.get(key)
        if isinstance(values, dict):
            hashes.update(str(value) for value in values.values() if value)
        elif isinstance(values, list):
            hashes.update(str(value) for value in values if value)

    files = raw.get("files")
    if isinstance(files, list):
        for item in files:
            if not isinstance(item, dict):
                continue
            for key in ("sha256", "content_sha256", "after_hash", "resulting_hash"):
                if item.get(key):
                    hashes.add(str(item[key]))
    return hashes


def _raw_get(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


def _extract_session_hashes(session: AgentSession) -> dict[str, str]:
    hashes_by_hash: dict[str, str] = {}

    produced_file_hashes = session.produced_file_hashes or {}
    if isinstance(produced_file_hashes, dict):
        for file_path, content_hash in produced_file_hashes.items():
            if content_hash:
                hashes_by_hash[str(content_hash)] = str(file_path or "")

    produced_artifacts = session.produced_artifacts or []
    if isinstance(produced_artifacts, list):
        for artifact in produced_artifacts:
            if not isinstance(artifact, dict):
                continue
            after_hash = artifact.get("after_hash")
            if after_hash:
                hashes_by_hash[str(after_hash)] = str(artifact.get("file_path") or artifact.get("path") or artifact.get("file") or "")

    raw = getattr(session, "raw", None)
    codex = _raw_get(raw, "codex")
    codex_files = _raw_get(codex, "files")
    if isinstance(codex_files, list):
        for item in codex_files:
            after_hash = _raw_get(item, "after_sha256")
            if after_hash:
                hashes_by_hash[str(after_hash)] = str(_raw_get(item, "path") or "")

    copilot = _raw_get(raw, "copilot")
    suggestions = _raw_get(copilot, "suggestions")
    if isinstance(suggestions, list):
        for item in suggestions:
            content_hash = _raw_get(item, "content_hash")
            if content_hash:
                hashes_by_hash[str(content_hash)] = str(_raw_get(item, "file") or "")

    return hashes_by_hash


def _tier1_session_hash_match(commits: list[Commit], sessions: list[AgentSession]) -> AttributionDecision | None:
    sessions_by_hash: dict[str, list[AgentSession]] = defaultdict(list)
    for session in sessions:
        for content_hash in _extract_session_hashes(session):
            sessions_by_hash[content_hash].append(session)

    if not sessions_by_hash:
        return None

    lines_by_agent: dict[str, int] = defaultdict(int)
    matched_session_ids: list[str] = []
    matched_skills: list[str] = []
    matched = False
    for commit in commits:
        commit_hashes = _extract_commit_content_hashes(commit.raw)
        matched_sessions = []
        seen_session_ids: set[str] = set()
        for value in commit_hashes:
            for session in sessions_by_hash.get(value, []):
                if session.id in seen_session_ids:
                    continue
                seen_session_ids.add(session.id)
                matched_sessions.append(session)
        if not matched_sessions:
            continue
        matched = True
        lines = _commit_line_count(commit)
        if lines == 0:
            lines = 1
        seen_agents_for_commit = _dedupe([session.agent_runtime for session in matched_sessions])
        for agent in seen_agents_for_commit:
            normalized = _normalize_agent(agent) or agent
            lines_by_agent[normalized] += lines
        for session in matched_sessions:
            matched_session_ids.append(session.id)
            matched_skills.extend(session.skills_loaded or [])

    if not matched:
        return None
    deduped_sessions = _dedupe(matched_session_ids)
    deduped_skills = _dedupe(matched_skills)
    agent_keys = sorted(lines_by_agent)
    primary = agent_keys[0] if len(agent_keys) == 1 else "mixed"
    confidence = TIER1_VENDOR_CONFIDENCE_CAPS.get(primary, 0.70)
    return AttributionDecision(
        primary_agent=primary,
        confidence=confidence,
        lines_by_agent=dict(lines_by_agent),
        lines_by_human=0,
        sessions=deduped_sessions,
        skills_loaded=deduped_skills,
    )


def _tier2_commit_trailer(commits: list[Commit]) -> AttributionDecision | None:
    for commit in commits:
        message = commit.message or ""
        agent = None
        if re.search(r"co-authored-by:\s*claude", message, re.IGNORECASE):
            agent = "claude_code"
        elif re.search(r"co-authored-by:\s*github copilot", message, re.IGNORECASE):
            agent = "copilot"
        elif re.search(r"co-authored-by:\s*codex", message, re.IGNORECASE):
            agent = "codex"
        elif re.search(r"generated by\s+cursor", message, re.IGNORECASE):
            agent = "cursor"
        elif re.search(r"generated by\s+devin", message, re.IGNORECASE):
            agent = "devin"
        if agent:
            return AttributionDecision(agent, 0.85, {agent: max(1, _commit_line_count(commit))}, 0, [], [])
    return None


def _tier3_bot_author(pr: PullRequest) -> AttributionDecision | None:
    login = (pr.author_login or "").lower()
    agent = _normalize_agent(login)
    if agent and (pr.author_type == "Bot" or login.endswith("[bot]")):
        return AttributionDecision(agent, 0.80, {agent: max(1, int(pr.additions or 0) + int(pr.deletions or 0))}, 0, [], [])
    if pr.author_type == "Bot":
        return AttributionDecision("human", 1.0, {}, int(pr.additions or 0) + int(pr.deletions or 0), [], [])
    return None


def _tier4_branch_name(pr: PullRequest) -> AttributionDecision | None:
    raw = pr.raw or {}
    github = raw.get("github") if isinstance(raw, dict) else {}
    head = github.get("head") if isinstance(github, dict) else {}
    branch = str(head.get("ref") or "").lower() if isinstance(head, dict) else ""
    for prefix, agent in (("claude", "claude_code"), ("codex", "codex"), ("cursor", "cursor"), ("devin", "devin")):
        if branch.startswith(f"{prefix}/") or branch.startswith(f"{prefix}-"):
            return AttributionDecision(agent, 0.50, {agent: max(1, int(pr.additions or 0) + int(pr.deletions or 0))}, 0, [], [])
    return None


def _human_fallback(pr: PullRequest) -> AttributionDecision:
    return AttributionDecision(
        primary_agent="human",
        confidence=1.0,
        lines_by_agent={},
        lines_by_human=int(pr.additions or 0) + int(pr.deletions or 0),
        sessions=[],
        skills_loaded=[],
    )


async def _load_pr_context(pr_id: str, db: AsyncSession) -> tuple[PullRequest, list[Commit], list[AgentSession]]:
    pr = (await db.execute(select(PullRequest).where(PullRequest.id == pr_id))).scalar_one_or_none()
    if pr is None:
        raise ValueError("pull_request_not_found")
    commits = (await db.execute(select(Commit).where(Commit.pr_id == pr.id))).scalars().all()
    sessions = (await db.execute(select(AgentSession).where(AgentSession.repo_id == pr.repo_id))).scalars().all()
    return pr, list(commits), list(sessions)


async def attribute_pr(pr_id: str, db: AsyncSession) -> PRAttribution:
    pr, commits, sessions = await _load_pr_context(pr_id, db)
    decision = (
        _tier1_session_hash_match(commits, sessions)
        or _tier2_commit_trailer(commits)
        or _tier3_bot_author(pr)
        or _tier4_branch_name(pr)
        or _human_fallback(pr)
    )

    existing = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id == pr.id))).scalar_one_or_none()
    attribution = existing or PRAttribution(pr_id=pr.id, primary_agent=decision.primary_agent, confidence=decision.confidence)
    if existing is None:
        db.add(attribution)
        await db.flush()

    attribution.primary_agent = decision.primary_agent
    attribution.confidence = decision.confidence
    attribution.lines_by_agent = decision.lines_by_agent
    attribution.lines_by_human = decision.lines_by_human
    attribution.sessions = decision.sessions
    attribution.skills_loaded = decision.skills_loaded
    attribution.skills_violated = attribution.skills_violated or []
    attribution.computed_at = datetime.utcnow()
    attribution.updated_at = datetime.utcnow()
    await db.commit()
    return attribution
