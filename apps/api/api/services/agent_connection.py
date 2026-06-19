from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AgentSession, AuditEvent, SkillUsageEvent


AGENT_RUNTIMES = ["claude_code", "codex_desktop", "codex_cli", "cursor", "windsurf", "copilot", "gemini_cli", "unidentified_agent"]
RUNTIME_ALIASES = {
    "anthropic": "claude_code",
    "claude": "claude_code",
    "codex": "codex_cli",
    "codex-desktop": "codex_desktop",
    "codex_desktop": "codex_desktop",
    "codex desktop": "codex_desktop",
    "codex-mac": "codex_cli",
    "codex_mac": "codex_cli",
    "codex-app": "codex_cli",
    "codex_app": "codex_cli",
    "codex-cli": "codex_cli",
    "codex_cli": "codex_cli",
    "openai": "codex_cli",
    "claude-code": "claude_code",
    "claude_code": "claude_code",
    "claudecode": "claude_code",
    "cursor": "cursor",
    "windsurf": "windsurf",
    "codeium": "windsurf",
    "codeium-windsurf": "windsurf",
    "codeium_windsurf": "windsurf",
    "github-copilot": "copilot",
    "github_copilot": "copilot",
    "copilot": "copilot",
    "gemini": "gemini_cli",
    "gemini-cli": "gemini_cli",
    "gemini_cli": "gemini_cli",
    "unidentified_agent": "codex_cli",
    "unknown": "unidentified_agent",
    "other": "unidentified_agent",
    "": "unidentified_agent",
}
RUNTIME_DISPLAY_NAMES = {
    "claude_code": "Claude Code",
    "codex_desktop": "Codex Desktop",
    "codex_cli": "Codex CLI",
    "cursor": "Cursor",
    "windsurf": "Windsurf",
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
    if "windsurf" in ua or "codeium" in ua:
        return "windsurf"
    if "copilot" in ua or "github" in ua:
        return "copilot"
    if "gemini" in ua:
        return "gemini_cli"
    # The Codex Mac app commonly executes the documented API-key skill load
    # command without an explicit X-Agent header. Preserve explicit headers above;
    # otherwise classify headless scripted clients as Codex instead of hiding
    # useful activity under "Unidentified Agent".
    if (headers.get("api-key") or headers.get("API-Key") or "").startswith("sk-"):
        return "codex_cli"
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    if auth.lower().startswith("bearer sk-"):
        return "codex_cli"
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
    status = {
        runtime: {
            "connected": False,
            "last_seen_at": None,
            "load_count_30d": 0,
            "uploads_30d": 0,
            "tokens_total_30d": 0,
            "cost_usd_30d": 0.0,
            "commands_30d": 0,
            "files_touched_30d": 0,
        }
        for runtime in AGENT_RUNTIMES
    }
    for row in rows:
        runtime = normalize_runtime(row.agent_runtime)
        if runtime not in status:
            continue
        last_seen = row.last_seen_at
        existing_seen_raw = status[runtime]["last_seen_at"]
        existing_seen = datetime.fromisoformat(existing_seen_raw) if existing_seen_raw else None
        latest_seen = max((seen for seen in (existing_seen, last_seen) if seen is not None), default=None)
        status[runtime]["connected"] = bool(latest_seen and latest_seen >= cutoff_14)
        status[runtime]["last_seen_at"] = latest_seen.isoformat() if latest_seen else None
        status[runtime]["load_count_30d"] = int(status[runtime]["load_count_30d"] or 0) + int(row.load_count_30d or 0)

    session_rows = (
        await db.execute(
            select(
                AgentSession.agent_runtime,
                func.max(AgentSession.session_start).label("last_seen_at"),
                func.count(AgentSession.id).label("uploads_30d"),
            )
            .where(AgentSession.org_id == org_id, AgentSession.session_start >= cutoff_30)
            .group_by(AgentSession.agent_runtime)
        )
    ).all()
    for row in session_rows:
        runtime = normalize_runtime(row.agent_runtime)
        if runtime not in status:
            continue
        last_seen = row.last_seen_at
        existing_seen_raw = status[runtime]["last_seen_at"]
        existing_seen = datetime.fromisoformat(existing_seen_raw) if existing_seen_raw else None
        latest_seen = max((seen for seen in (existing_seen, last_seen) if seen is not None), default=None)
        status[runtime]["connected"] = bool(latest_seen and latest_seen >= cutoff_14)
        status[runtime]["last_seen_at"] = latest_seen.isoformat() if latest_seen else None
        status[runtime]["uploads_30d"] = int(status[runtime]["uploads_30d"] or 0) + int(row.uploads_30d or 0)

    audit_rows = (
        await db.execute(
            select(AuditEvent).where(
                AuditEvent.org_id == org_id,
                AuditEvent.event_type == "agent.compliance",
                AuditEvent.created_at >= cutoff_30,
            )
        )
    ).scalars().all()
    for event in audit_rows:
        metadata = getattr(event, "metadata_json", None)
        if not isinstance(metadata, dict):
            continue
        runtime = normalize_runtime(str(metadata.get("agent_runtime") or ""))
        if runtime not in status:
            continue
        metrics = metadata.get("activity_metrics") if isinstance(metadata.get("activity_metrics"), dict) else {}
        status[runtime]["tokens_total_30d"] = int(status[runtime]["tokens_total_30d"] or 0) + int(metadata.get("tokens_total") or 0)
        status[runtime]["cost_usd_30d"] = round(float(status[runtime]["cost_usd_30d"] or 0.0) + float(metadata.get("cost_usd") or 0.0), 6)
        status[runtime]["commands_30d"] = int(status[runtime]["commands_30d"] or 0) + int(metadata.get("commands") or metrics.get("commands") or 0)
        status[runtime]["files_touched_30d"] = int(status[runtime]["files_touched_30d"] or 0) + len(metadata.get("file_targets") or [])
    return status
