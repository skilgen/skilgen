from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any, Iterable, Literal

RiskBand = Literal["low", "medium", "high"]

TICKET_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
URL_RE = re.compile(r"https?://[^\s)>\"]+")


def isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def agent_label(runtime: str | None) -> str:
    labels = {
        "claude_code": "Claude Code",
        "codex": "Codex",
        "codex_cli": "Codex CLI",
        "cursor": "Cursor",
        "copilot": "GitHub Copilot",
        "github_copilot": "GitHub Copilot",
        "gemini": "Gemini CLI",
        "gemini_cli": "Gemini CLI",
        "devin": "Devin",
    }
    normalized = str(runtime or "unknown").replace("-", "_")
    return labels.get(normalized, normalized.replace("_", " ").title())


def repo_sensitivity_tier(repo: object | None) -> str:
    if repo is None:
        return "internal"
    direct = getattr(repo, "sensitivity_tier", None) or getattr(repo, "sensitivity", None)
    if isinstance(direct, str) and direct:
        return direct
    settings = getattr(repo, "settings", None)
    if isinstance(settings, dict):
        value = settings.get("sensitivity_tier") or settings.get("sensitivity")
        if isinstance(value, str) and value:
            return value
    return "internal"


def skill_signature_status(skill: object | None) -> str:
    if skill is None:
        return "missing"
    if getattr(skill, "signature_status", None):
        return str(getattr(skill, "signature_status"))
    if getattr(skill, "content_hash", None):
        return "verified"
    return "unsigned"


def linked_external_ticket(*values: str | None) -> dict[str, str | None] | None:
    text = "\n".join(value for value in values if value)
    if not text:
        return None
    ticket = TICKET_RE.search(text)
    url = URL_RE.search(text)
    if not ticket and not url:
        return None
    label = ticket.group(1) if ticket else str(url.group(0)).rstrip(".,")
    return {"label": label, "url": str(url.group(0)).rstrip(".,") if url else None}


def action_class_for_event(event: object | None = None, artifact: dict[str, Any] | None = None) -> str:
    if artifact:
        tool = str(artifact.get("tool") or "").lower()
        if tool in {"bash", "shell", "terminal"}:
            return "exec"
        if tool in {"webfetch", "web_search", "http"}:
            return "network"
        if tool in {"read", "grep", "glob"}:
            return "read"
        if tool in {"edit", "write", "notebookedit"}:
            return "write"
    if event is not None:
        return "read"
    return "read"


def risk_score(
    action_class: str,
    sensitivity_tier: str,
    file_scope: Iterable[str] = (),
    signature_status: str = "verified",
    outcome: str = "allowed",
) -> int:
    base = {"read": 8, "write": 34, "exec": 48, "network": 44}.get(action_class, 10)
    sensitivity = {"public": 0, "internal": 5, "confidential": 18, "restricted": 28, "regulated": 32}.get(sensitivity_tier, 5)
    scope = min(20, len({path for path in file_scope if path}) * 3)
    signature = 0 if signature_status == "verified" else 10
    outcome_penalty = 25 if outcome in {"denied", "blocked"} else 0
    return max(0, min(100, base + sensitivity + scope + signature + outcome_penalty))


def risk_band(score: int) -> RiskBand:
    if score >= 70:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def feed_event_view(event: object, repo: object | None, skill: object | None, session: object | None = None) -> dict[str, Any]:
    files = list(getattr(session, "files_touched", []) or [])
    action_class = action_class_for_event(event)
    sensitivity = repo_sensitivity_tier(repo)
    signature = skill_signature_status(skill)
    score = risk_score(action_class, sensitivity, files, signature)
    loaded_at = getattr(event, "loaded_at", None)
    skill_name = getattr(skill, "domain", None) or getattr(skill, "skill_path", None) or "Unknown skill"
    repo_name = getattr(repo, "full_name", None) or getattr(repo, "name", None) or "Unknown repo"
    return {
        "id": str(getattr(event, "id", "")),
        "timestamp": isoformat(loaded_at),
        "ts": isoformat(loaded_at),
        "agent": agent_label(getattr(event, "agent_runtime", None)),
        "agent_provider": str(getattr(event, "agent_runtime", "unknown")),
        "user": getattr(session, "engineer_login", None) or "unknown",
        "repo_id": str(getattr(event, "repo_id", "")),
        "repo": repo_name,
        "repo_name": repo_name,
        "repo_sensitivity_tier": sensitivity,
        "skill_id": str(getattr(skill, "id", getattr(event, "skill_id", ""))),
        "skill": f"{skill_name} ({signature})",
        "skill_signature_status": signature,
        "action": "loaded skill context",
        "action_class": action_class,
        "file_scope": files or ["repo context"],
        "outcome": "allowed",
        "trigger": linked_external_ticket(getattr(session, "task_description", None), getattr(session, "notes", None)),
        "risk_score": score,
        "risk_band": risk_band(score),
        "session_id": str(getattr(event, "session_id", "")),
        "session_db_id": str(getattr(session, "id", "")) if session is not None else None,
    }


def session_view(session: object, repo: object | None, skills: dict[str, object] | None = None) -> dict[str, Any]:
    skill_map = skills or {}
    loaded = list(getattr(session, "skills_loaded", None) or getattr(session, "skill_paths_loaded", None) or [])
    resolved_skills = [skill_map[item] for item in loaded if item in skill_map]
    signature_statuses = [skill_signature_status(skill) for skill in resolved_skills] or ["missing" if loaded else "none"]
    files = list(getattr(session, "files_touched", []) or [])
    sensitivity = repo_sensitivity_tier(repo)
    action_class = "write" if files or getattr(session, "produced_artifacts", None) else "read"
    signature = "verified" if all(status == "verified" for status in signature_statuses) else signature_statuses[0]
    score = risk_score(action_class, sensitivity, files, signature, str(getattr(session, "outcome", None) or "allowed"))
    started = getattr(session, "session_start", None) or getattr(session, "created_at", None)
    ended = getattr(session, "session_end", None) or getattr(session, "closed_at", None)
    return {
        "id": str(getattr(session, "id", "")),
        "session_id": str(getattr(session, "session_id", "")),
        "repo_id": str(getattr(session, "repo_id", "")),
        "repo_name": getattr(repo, "full_name", None) or getattr(repo, "name", None) or "Unknown repo",
        "repo_sensitivity_tier": sensitivity,
        "agent_provider": str(getattr(session, "agent_runtime", "unknown")),
        "agent": agent_label(getattr(session, "agent_runtime", None)),
        "user": getattr(session, "engineer_login", None) or "unknown",
        "started_at": isoformat(started),
        "ended_at": isoformat(ended),
        "duration_minutes": getattr(session, "duration_minutes", None),
        "files_touched": files,
        "skills_loaded": loaded,
        "skill_signature_statuses": signature_statuses,
        "outcome": getattr(session, "outcome", None) or "unknown",
        "trigger": linked_external_ticket(getattr(session, "task_description", None), getattr(session, "notes", None)),
        "risk_score": score,
        "risk_band": risk_band(score),
        "replay_url": f"/activity/replay/{getattr(session, 'id', '')}?repo={getattr(session, 'repo_id', '')}",
    }


def replay_timeline(session: object, repo: object | None) -> list[dict[str, Any]]:
    artifacts = [item for item in list(getattr(session, "produced_artifacts", []) or []) if isinstance(item, dict)]
    timeline: list[dict[str, Any]] = []
    for index, artifact in enumerate(artifacts):
        action_class = action_class_for_event(artifact=artifact)
        file_path = str(artifact.get("file_path") or artifact.get("path") or "")
        score = risk_score(
            action_class,
            repo_sensitivity_tier(repo),
            [file_path] if file_path else [],
            "verified",
            str(getattr(session, "outcome", None) or "allowed"),
        )
        timeline.append(
            {
                "index": index,
                "timestamp": str(artifact.get("ts") or isoformat(getattr(session, "created_at", None)) or ""),
                "action": str(artifact.get("tool") or "tool"),
                "action_class": action_class,
                "reasoning": getattr(session, "transcript_summary", None),
                "tool_call": {"tool": artifact.get("tool"), "file_path": file_path},
                "result": {"after_hash": artifact.get("after_hash")},
                "policy_decision": "allowed",
                "file_diff": str(artifact.get("diff") or ""),
                "risk_score": score,
                "risk_band": risk_band(score),
            }
        )
    if timeline:
        return timeline

    code = str(getattr(session, "code_produced", None) or "")
    if not code:
        return []
    chunks = [chunk.strip() for chunk in code.split("\n\n") if chunk.strip()] or [code]
    for index, chunk in enumerate(chunks):
        timeline.append(
            {
                "index": index,
                "timestamp": isoformat(getattr(session, "created_at", None)),
                "action": "produced code",
                "action_class": "write",
                "reasoning": getattr(session, "transcript_summary", None),
                "tool_call": None,
                "result": {"excerpt": chunk[:240]},
                "policy_decision": "allowed",
                "file_diff": chunk,
                "risk_score": risk_score("write", repo_sensitivity_tier(repo), list(getattr(session, "files_touched", []) or [])),
                "risk_band": risk_band(risk_score("write", repo_sensitivity_tier(repo), list(getattr(session, "files_touched", []) or []))),
            }
        )
    return timeline


def standalone_replay_html(session_payload: dict[str, Any], timeline: list[dict[str, Any]]) -> str:
    title = html.escape(f"Skillayer replay {session_payload.get('session_id', '')}")
    rows = "\n".join(
        f"<section><h2>Step {step['index'] + 1}: {html.escape(str(step['action']))}</h2>"
        f"<p>{html.escape(str(step.get('timestamp') or ''))} - {html.escape(str(step.get('policy_decision') or ''))} - risk {step.get('risk_score')}</p>"
        f"<pre>{html.escape(str(step.get('file_diff') or step.get('result') or ''))}</pre></section>"
        for step in timeline
    )
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>"
        + title
        + "</title><style>body{font-family:system-ui;margin:32px;background:#0d0d14;color:#f4f4f5}"
        + "section{border:1px solid #2b2b34;border-radius:8px;padding:16px;margin:16px 0}"
        + "pre{white-space:pre-wrap;background:#050507;padding:12px;border-radius:6px}</style></head><body><h1>"
        + title
        + "</h1>"
        + rows
        + "</body></html>"
    )
