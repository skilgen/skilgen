from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any, Iterable, Literal

RiskBand = Literal["low", "medium", "high"]
RiskLevel = Literal["low", "medium", "high", "critical"]

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


def normalized_outcome(outcome: str | None, ended: object | None = None) -> str:
    value = str(outcome or "").strip().lower()
    if value in {"success", "succeeded", "completed", "complete", "allowed"}:
        return "success"
    if value in {"failed", "error", "errored"}:
        return "failed"
    if value in {"denied", "blocked"}:
        return value
    if value in {"running", "in_progress", "in-progress"}:
        return "in_progress"
    return "in_progress" if ended is None else "unknown"


def risk_reasons(
    action_class: str,
    sensitivity_tier: str,
    file_scope: Iterable[str] = (),
    signature_status: str = "verified",
    outcome: str = "allowed",
) -> list[str]:
    files = {path for path in file_scope if path}
    reasons = [f"{action_class} activity"]
    if sensitivity_tier != "public":
        reasons.append(f"{sensitivity_tier} repository")
    if files:
        reasons.append(f"{len(files)} file target{'s' if len(files) != 1 else ''}")
    if signature_status not in {"verified", "none"}:
        reasons.append(f"{signature_status} skill context")
    if outcome in {"denied", "blocked", "failed"}:
        reasons.append(f"{outcome} outcome")
    return reasons


def risk_band(score: int) -> RiskBand:
    if score >= 70:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def risk_level(score: int) -> RiskLevel:
    if score >= 85:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def compliance_status(compliance: dict[str, Any] | None) -> str:
    if not compliance:
        return "unknown"
    decision = str(compliance.get("policy_decision") or "").strip().lower()
    violations = compliance.get("policy_violations") or compliance.get("violations") or []
    has_violations = isinstance(violations, list) and any(bool(item) for item in violations)
    if decision in {"deny", "denied", "blocked", "block", "failed", "error"} or has_violations:
        return "failed"
    if decision in {"require_approval", "log_only", "redact", "route_to_dlp", "warn", "warning"}:
        return "warning"
    if bool(compliance.get("full_access")) or str(compliance.get("access_scope") or "").strip().lower() == "full-access":
        return "warning"
    if decision in {"allow", "allowed", "success"}:
        return "passed"
    return "passed" if (compliance.get("access_scope") or compliance.get("tool_permissions")) else "unknown"


def human_next_action(compliance: dict[str, Any] | None, *, risk: int) -> str | None:
    if not compliance:
        return None
    if bool(compliance.get("full_access")):
        return "Review why full access was granted"
    if str(compliance.get("github_enrichment_status") or "") == "missing":
        return "Fix missing GitHub join evidence"
    if compliance.get("policy_violations"):
        return "Review policy violations and approve exception"
    metrics = compliance.get("activity_metrics") if isinstance(compliance.get("activity_metrics"), dict) else {}
    if int(metrics.get("commands") or 0) > 0:
        return "Review command summaries"
    return "No action" if risk < 35 else "Review run risk reasons"


def external_api_calls(compliance: dict[str, Any] | None) -> list[dict[str, Any]]:
    raw = (compliance or {}).get("external_api_calls")
    if not isinstance(raw, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        count = int(item.get("count") or 0)
        if count <= 0:
            continue
        row = {
            "provider": item.get("provider"),
            "domain": item.get("domain"),
            "category": item.get("category"),
            "count": count,
        }
        rows.append({key: value for key, value in row.items() if value not in {None, ""}})
    return rows


def enrich_risk(
    base_score: int,
    base_reasons: list[str],
    *,
    compliance: dict[str, Any] | None,
) -> tuple[int, list[str]]:
    if not compliance:
        return base_score, base_reasons
    score = int(base_score)
    reasons = list(base_reasons)
    if bool(compliance.get("full_access")):
        score = max(score, 90)
        reasons.append("full filesystem access")
    if str(compliance.get("access_scope") or "").strip().lower() == "full-access":
        score = max(score, 85)
        reasons.append("full access scope")
    approval_policy = str(compliance.get("approval_policy") or "").lower()
    sandbox_policy = str(compliance.get("sandbox_policy") or "").lower()
    if any(token in f"{approval_policy} {sandbox_policy}" for token in ("auto", "autonomous")):
        score += 12
        reasons.append("auto-review policy")
    mcp_tools = compliance.get("mcp_tools") if isinstance(compliance.get("mcp_tools"), list) else []
    if mcp_tools:
        score += min(20, 6 + len(mcp_tools) * 2)
        reasons.append(f"{len(mcp_tools)} MCP tool(s) used")
    metrics = compliance.get("activity_metrics") if isinstance(compliance.get("activity_metrics"), dict) else {}
    command_count = int(metrics.get("commands") or 0)
    if command_count:
        score += min(15, command_count * 2)
        reasons.append(f"{command_count} shell command(s)")
    if str(compliance.get("github_enrichment_status") or "") == "missing":
        score += 10
        reasons.append("missing GitHub repo/PR/commit join evidence")
    return max(0, min(100, score)), reasons


def feed_event_view(event: object, repo: object | None, skill: object | None, session: object | None = None) -> dict[str, Any]:
    files = list(getattr(session, "files_touched", []) or [])
    action_class = action_class_for_event(event)
    sensitivity = repo_sensitivity_tier(repo)
    signature = skill_signature_status(skill)
    outcome = "allowed"
    score = risk_score(action_class, sensitivity, files, signature, outcome)
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
        "outcome": outcome,
        "trigger": linked_external_ticket(getattr(session, "task_description", None), getattr(session, "notes", None)),
        "risk_score": score,
        "risk_band": risk_band(score),
        "risk_reasons": risk_reasons(action_class, sensitivity, files, signature, outcome),
        "session_id": str(getattr(event, "session_id", "")),
        "session_db_id": str(getattr(session, "id", "")) if session is not None else None,
    }


def session_feed_event_view(session: object, repo: object | None, skills: dict[str, object] | None = None, compliance: dict[str, Any] | None = None) -> dict[str, Any]:
    """Project an agent session into the live feed so activity is visible before skill-load telemetry exists."""
    skill_map = skills or {}
    loaded = list(getattr(session, "skills_loaded", None) or getattr(session, "skill_paths_loaded", None) or [])
    resolved_skills = [skill_map[item] for item in loaded if item in skill_map]
    signature_statuses = [skill_signature_status(skill) for skill in resolved_skills]
    files = list(getattr(session, "files_touched", []) or [])
    artifacts = list(getattr(session, "produced_artifacts", []) or [])
    produced_code = bool(getattr(session, "code_produced", None))
    action_class = "write" if files or artifacts or produced_code else "read"
    sensitivity = repo_sensitivity_tier(repo)
    signature = "verified" if signature_statuses and all(status == "verified" for status in signature_statuses) else signature_statuses[0] if signature_statuses else "none"
    ended = getattr(session, "session_end", None) or getattr(session, "closed_at", None)
    outcome = normalized_outcome(str(getattr(session, "outcome", None) or ""), ended)
    base_score = risk_score(action_class, sensitivity, files, signature, outcome)
    base_reasons = risk_reasons(action_class, sensitivity, files, signature, outcome)
    score, reasons = enrich_risk(base_score, base_reasons, compliance=compliance)
    activity_at = getattr(session, "last_artifact_at", None) or getattr(session, "session_start", None) or getattr(session, "created_at", None)
    repo_name = getattr(repo, "full_name", None) or getattr(repo, "name", None) or "Unknown repo"
    session_id = str(getattr(session, "session_id", "") or getattr(session, "id", ""))
    session_db_id = str(getattr(session, "id", ""))
    skill_label = (
        f"{len(loaded)} skills loaded"
        if len(loaded) != 1
        else str(loaded[0])
    ) if loaded else "No skill loads recorded"
    return {
        "id": f"session:{session_db_id or session_id}",
        "timestamp": isoformat(activity_at),
        "ts": isoformat(activity_at),
        "agent": agent_label(getattr(session, "agent_runtime", None)),
        "agent_provider": str(getattr(session, "agent_runtime", "unknown")),
        "user": getattr(session, "engineer_login", None) or "unknown",
        "repo_id": str(getattr(session, "repo_id", "")),
        "repo": repo_name,
        "repo_name": repo_name,
        "repo_sensitivity_tier": sensitivity,
        "skill_id": str(loaded[0]) if loaded else "",
        "skill": f"Agent session - {skill_label}",
        "skill_signature_status": signature,
        "action": "agent session updated repository" if action_class == "write" else "agent session opened repository context",
        "action_class": action_class,
        "file_scope": files or ["repo context"],
        "outcome": outcome,
        "trigger": linked_external_ticket(getattr(session, "task_description", None), getattr(session, "notes", None)),
        "risk_score": score,
        "risk_band": risk_band(score),
        "risk_level": risk_level(score),
        "risk_reasons": reasons,
        "compliance_status": compliance_status(compliance),
        "policy_violations": list((compliance or {}).get("policy_violations") or []),
        "human_next_action": human_next_action(compliance, risk=score),
        "tokens_total": int((compliance or {}).get("tokens_total") or 0),
        "cost_usd": float((compliance or {}).get("cost_usd") or 0.0),
        "model": (compliance or {}).get("model"),
        "intelligence_tier": (compliance or {}).get("intelligence_tier"),
        "access_scope": (compliance or {}).get("access_scope"),
        "external_api_call_count": int((compliance or {}).get("external_api_call_count") or 0),
        "external_api_calls": external_api_calls(compliance),
        "full_access": bool((compliance or {}).get("full_access") or False),
        "approval_policy": (compliance or {}).get("approval_policy"),
        "sandbox_policy": (compliance or {}).get("sandbox_policy"),
        "permission_profile": (compliance or {}).get("permission_profile"),
        "policy_decision": (compliance or {}).get("policy_decision"),
        "tool_permissions": list((compliance or {}).get("tool_permissions") or []),
        "file_targets": list((compliance or {}).get("file_targets") or []),
        "external_api_call_count": int((compliance or {}).get("external_api_call_count") or 0),
        "external_api_calls": external_api_calls(compliance),
        "github_enrichment_status": (compliance or {}).get("github_enrichment_status"),
        "github_enrichment_gap": (compliance or {}).get("github_enrichment_gap"),
        "git_url": (compliance or {}).get("git_url"),
        "mcp_tools": list((compliance or {}).get("mcp_tools") or []),
        "activity_metrics": dict((compliance or {}).get("activity_metrics") or {}),
        "activity_details": dict((compliance or {}).get("activity_details") or {}),
        "replay_url": f"/activity/replay/{session_db_id or session_id}?repo={getattr(session, 'repo_id', '')}",
        "session_id": session_id,
        "session_db_id": session_db_id or None,
    }


def session_view(session: object, repo: object | None, skills: dict[str, object] | None = None, compliance: dict[str, Any] | None = None) -> dict[str, Any]:
    skill_map = skills or {}
    loaded = list(getattr(session, "skills_loaded", None) or getattr(session, "skill_paths_loaded", None) or [])
    resolved_skills = [skill_map[item] for item in loaded if item in skill_map]
    signature_statuses = [skill_signature_status(skill) for skill in resolved_skills] or ["missing" if loaded else "none"]
    files = list(getattr(session, "files_touched", []) or [])
    sensitivity = repo_sensitivity_tier(repo)
    action_class = "write" if files or getattr(session, "produced_artifacts", None) else "read"
    signature = "verified" if all(status == "verified" for status in signature_statuses) else signature_statuses[0]
    ended = getattr(session, "session_end", None) or getattr(session, "closed_at", None)
    outcome = normalized_outcome(str(getattr(session, "outcome", None) or ""), ended)
    base_score = risk_score(action_class, sensitivity, files, signature, outcome)
    base_reasons = risk_reasons(action_class, sensitivity, files, signature, outcome)
    score, reasons = enrich_risk(base_score, base_reasons, compliance=compliance)
    started = getattr(session, "session_start", None) or getattr(session, "created_at", None)
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
        "outcome": outcome,
        "trigger": linked_external_ticket(getattr(session, "task_description", None), getattr(session, "notes", None)),
        "risk_score": score,
        "risk_band": risk_band(score),
        "risk_level": risk_level(score),
        "risk_reasons": reasons,
        "compliance_status": compliance_status(compliance),
        "policy_violations": list((compliance or {}).get("policy_violations") or []),
        "human_next_action": human_next_action(compliance, risk=score),
        "tokens_total": int((compliance or {}).get("tokens_total") or 0),
        "cost_usd": float((compliance or {}).get("cost_usd") or 0.0),
        "model": (compliance or {}).get("model"),
        "intelligence_tier": (compliance or {}).get("intelligence_tier"),
        "access_scope": (compliance or {}).get("access_scope"),
        "full_access": bool((compliance or {}).get("full_access") or False),
        "approval_policy": (compliance or {}).get("approval_policy"),
        "sandbox_policy": (compliance or {}).get("sandbox_policy"),
        "permission_profile": (compliance or {}).get("permission_profile"),
        "policy_decision": (compliance or {}).get("policy_decision"),
        "tool_permissions": list((compliance or {}).get("tool_permissions") or []),
        "file_targets": list((compliance or {}).get("file_targets") or []),
        "github_enrichment_status": (compliance or {}).get("github_enrichment_status"),
        "github_enrichment_gap": (compliance or {}).get("github_enrichment_gap"),
        "git_url": (compliance or {}).get("git_url"),
        "mcp_tools": list((compliance or {}).get("mcp_tools") or []),
        "activity_metrics": dict((compliance or {}).get("activity_metrics") or {}),
        "activity_details": dict((compliance or {}).get("activity_details") or {}),
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
