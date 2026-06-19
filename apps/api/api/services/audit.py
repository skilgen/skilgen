from __future__ import annotations

import base64
import json
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AuditEvent


EVENT_TYPES = {
    "analysis.triggered",
    "analysis.completed",
    "analysis.failed",
    "skill.created",
    "skill.updated",
    "skill.deleted",
    "skill.content_edited",
    "skill.published",
    "skill.version_created",
    "gate.passed",
    "gate.failed",
    "gate.configured",
    "persona.created",
    "persona.updated",
    "persona.deleted",
    "persona.skill_added",
    "persona.skill_removed",
    "persona.published",
    "team.created",
    "team.updated",
    "team.deleted",
    "team.repo_added",
    "team.repo_removed",
    "memory.stub_approved",
    "memory.stub_rejected",
    "memory.session_uploaded",
    "policy.created",
    "policy.updated",
    "policy.deleted",
    "policy.violation_detected",
    "policy.check_passed",
    "policy.check_failed",
    "settings.updated",
    "settings.slack_configured",
    "settings.llm_configured",
    "settings.gate_configured",
    "api_key_rotated",
    "member.invited",
    "member.removed",
    "member.role_changed",
}


async def emit(
    db: AsyncSession,
    org_id: str,
    event_type: str,
    action: str,
    summary: str,
    *,
    actor_login: str | None = None,
    actor_ip: str | None = None,
    repo_id: str | None = None,
    repo_name: str | None = None,
    skill_id: str | None = None,
    skill_domain: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    severity: str = "info",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Fire-and-forget audit event. Never break the caller."""
    try:
        db.add(
            AuditEvent(
                org_id=org_id,
                event_type=event_type,
                action=action,
                summary=summary[:512],
                actor_login=actor_login,
                actor_ip=actor_ip,
                repo_id=repo_id,
                repo_name=repo_name,
                skill_id=skill_id,
                skill_domain=skill_domain,
                resource_type=resource_type,
                resource_id=resource_id,
                severity=severity,
                metadata_json=metadata or {},
            )
        )
    except Exception:
        pass


def get_actor_login(request: Request) -> str | None:
    """Best-effort actor extraction for bootstrap-mode bearer tokens."""
    auth = request.headers.get("authorization") or request.headers.get("Authorization") or ""
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return "unknown"
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode()).decode()
        claims = json.loads(decoded)
        actor = claims.get("preferred_username") or claims.get("sub")
        return str(actor) if actor else "unknown"
    except Exception:
        return "unknown"
