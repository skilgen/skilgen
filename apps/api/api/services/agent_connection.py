from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import SkillUsageEvent


AGENT_RUNTIMES = ["claude_code", "codex_cli", "cursor", "copilot", "gemini_cli", "unidentified_agent"]
RUNTIME_ALIASES = {
    "anthropic": "claude_code",
    "claude": "claude_code",
    "codex": "codex_cli",
    "codex-cli": "codex_cli",
    "codex_cli": "codex_cli",
    "openai": "codex_cli",
    "claude-code": "claude_code",
    "claude_code": "claude_code",
    "claudecode": "claude_code",
    "cursor": "cursor",
    "github-copilot": "copilot",
    "github_copilot": "copilot",
    "copilot": "copilot",
    "gemini": "gemini_cli",
    "gemini-cli": "gemini_cli",
    "gemini_cli": "gemini_cli",
    "unknown": "unidentified_agent",
    "other": "unidentified_agent",
    "": "unidentified_agent",
}
RUNTIME_DISPLAY_NAMES = {
    "claude_code": "Claude Code",
    "codex_cli": "Codex CLI",
    "cursor": "Cursor",
    "copilot": "GitHub Copilot",
    "gemini_cli": "Gemini CLI",
    "unidentified_agent": "Unidentified Agent",
}
_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def normalize_runtime(runtime: str | None) -> str:
    raw = str(runtime or "").strip().lower()
    token = _TOKEN_RE.sub("_", raw).strip("_")
    return RUNTIME_ALIASES.get(raw) or RUNTIME_ALIASES.get(token) or token or "unidentified_agent"


def runtime_display_name(runtime: str | None) -> str:
    normalized = normalize_runtime(runtime)
    return RUNTIME_DISPLAY_NAMES.get(normalized, normalized.replace("_", " ").title())


def detect_runtime_from_headers(headers: Mapping[str, str]) -> str:
    agent_header = headers.get("x-agent") or headers.get("X-Agent") or headers.get("x-agent-runtime") or headers.get("X-Agent-Runtime")
    if agent_header:
        return normalize_runtime(agent_header)

    ua = (headers.get("user-agent") or headers.get("User-Agent") or "").lower()
    if "claude" in ua or "anthropic" in ua:
        return "claude_code"
    if "codex" in ua or "openai" in ua:
        return "codex_cli"
    if "cursor" in ua:
        return "cursor"
    if "copilot" in ua or "github" in ua:
        return "copilot"
    if "gemini" in ua:
        return "gemini_cli"
    return "unidentified_agent"


async def get_agent_connection_status(org_id: str, db: AsyncSession) -> dict:
    now = datetime.utcnow()
    cutoff_14 = now - timedelta(days=14)
    cutoff_30 = now - timedelta(days=30)
    rows = (
        await db.execute(
            select(
                SkillUsageEvent.agent_runtime,
                func.max(SkillUsageEvent.loaded_at).label("last_seen_at"),
                func.count(SkillUsageEvent.id).filter(SkillUsageEvent.loaded_at >= cutoff_30).label("load_count_30d"),
            )
            .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
            .group_by(SkillUsageEvent.agent_runtime)
        )
    ).all()
    status = {runtime: {"connected": False, "last_seen_at": None, "load_count_30d": 0} for runtime in AGENT_RUNTIMES}
    for row in rows:
        runtime = normalize_runtime(row.agent_runtime)
        if runtime not in status:
            continue
        last_seen = row.last_seen_at
        status[runtime] = {
            "connected": bool(last_seen and last_seen >= cutoff_14),
            "last_seen_at": last_seen.isoformat() if last_seen else None,
            "load_count_30d": int(row.load_count_30d or 0),
        }
    return status
