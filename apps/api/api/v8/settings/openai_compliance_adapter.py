from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class OpenAIComplianceAdapterResult:
    status: str
    mode: str
    cursor: str | None
    next_cursor: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    blocked_reason: str | None = None
    next_actions: list[str] = field(default_factory=list)
    provider_adapter_required: bool = False


def _has_openai_credential(credentials: dict[str, Any]) -> bool:
    return bool(credentials.get("api_key") or credentials.get("access_token"))


def _seeded_openai_events(cursor: str | None) -> list[dict[str, Any]]:
    occurred_at = datetime.now(UTC)
    return [
        {
            "provider_event_id": f"openai-seeded-{cursor or 'initial'}-1",
            "event_type": "agent.compliance",
            "actor_login": "ravi@skillayer.com",
            "occurred_at": occurred_at.isoformat(),
            "provider": "OpenAI Compliance Platform",
            "model": "gpt-5.5",
            "model_tier": "high-reasoning",
            "intelligence_tier": "high",
            "access_scope": "full-access",
            "full_access": True,
            "autonomous_access": False,
            "tool_permissions": ["shell", "apply_patch", "browser"],
            "tool_calls": 7,
            "mcp_tools": ["github"],
            "repo_id": "repo_skilgen",
            "repo_name": "ravichanduummadisetti/skilgen",
            "file_targets": [
                "apps/api/api/v8/settings/router.py",
                "apps/dashboard/app/(v8)/settings/connectors/page.tsx",
            ],
            "policy_decision": "require_approval",
            "approval_status": "approved",
            "warnings": 1,
            "tokens_input": 1250000,
            "tokens_output": 210000,
            "tokens_reasoning_output": 48000,
            "token_source": "openai_compliance_api",
            "cost_usd": 3.42,
            "cost_source": "provider_reported",
            "cost_estimate": False,
            "latency_ms": 91300,
            "session_id": f"openai-compliance-{cursor or 'initial'}",
            "source_record_type": "formal-compliance",
            "metadata": {
                "source": "seeded_openai_compliance_fixture",
                "cost_source": "provider_reported",
                "token_source": "openai_compliance_api",
                "usage_provenance_label": "Provider-reported by OpenAI compliance fixture",
                "pr_number": 11,
                "head_sha": "0e90c546f4bca6ccec03b9c33ffdec063444a718",
                "branch": "v8/next-feature-loop",
                "privacy": "metadata-only; raw prompts, chat, diffs, and tool parameters dropped",
            },
        },
        {
            "provider_event_id": f"openai-seeded-{cursor or 'initial'}-2",
            "event_type": "agent.compliance",
            "actor_login": "ravi@skillayer.com",
            "occurred_at": occurred_at.isoformat(),
            "provider": "OpenAI Compliance Platform",
            "model": "gpt-5.4-mini",
            "model_tier": "fast",
            "intelligence_tier": "medium",
            "access_scope": "default",
            "full_access": False,
            "autonomous_access": False,
            "tool_permissions": ["read"],
            "tool_calls": 2,
            "repo_id": "repo_skilgen",
            "repo_name": "ravichanduummadisetti/skilgen",
            "file_targets": ["docs/v8-refactor/09-enterprise-provider-ingestion-roadmap.md"],
            "policy_decision": "log_only",
            "approval_status": "not_required",
            "tokens_input": 220000,
            "tokens_output": 36000,
            "token_source": "openai_compliance_api",
            "cost_usd": 0.19,
            "cost_source": "provider_reported",
            "cost_estimate": False,
            "latency_ms": 11800,
            "session_id": f"openai-compliance-{cursor or 'initial'}",
            "source_record_type": "formal-compliance",
            "metadata": {
                "source": "seeded_openai_compliance_fixture",
                "cost_source": "provider_reported",
                "token_source": "openai_compliance_api",
                "usage_provenance_label": "Provider-reported by OpenAI compliance fixture",
                "commit_sha": "ef3731e",
                "branch": "v8/next-feature-loop",
                "privacy": "metadata-only; raw prompts, chat, diffs, and tool parameters dropped",
            },
        },
    ]


def pull_openai_compliance_events(
    credentials: dict[str, Any],
    *,
    cursor: str | None,
    dry_run: bool,
) -> OpenAIComplianceAdapterResult:
    if dry_run:
        return OpenAIComplianceAdapterResult(
            status="pending",
            mode="dry-run",
            cursor=cursor,
            blocked_reason="Dry run only checks readiness; no OpenAI events were pulled.",
            next_actions=["Run sync with dry_run=false after credentials are configured."],
            provider_adapter_required=False,
        )

    if not _has_openai_credential(credentials):
        return OpenAIComplianceAdapterResult(
            status="failed",
            mode="provider-pull",
            cursor=cursor,
            blocked_reason="Missing OpenAI Compliance API credential.",
            next_actions=[
                "Store an encrypted OpenAI Compliance API key or OAuth access token on this connector.",
                "Grant the tenant compliance/audit read scope before starting sync.",
                "Run the connector credential test, then retry sync.",
            ],
            provider_adapter_required=False,
        )

    if credentials.get("seeded_fixture") or credentials.get("mock_openai_compliance_fixture"):
        next_cursor = f"openai-fixture-{int(datetime.now(UTC).timestamp())}"
        return OpenAIComplianceAdapterResult(
            status="success",
            mode="fixture",
            cursor=cursor,
            next_cursor=next_cursor,
            events=_seeded_openai_events(cursor),
            next_actions=[
                "Review live feed, run replay, and insights for provider-reported usage and cost provenance.",
                "Replace seeded fixture credentials with tenant OpenAI Compliance API credentials for production sync.",
            ],
            provider_adapter_required=False,
        )

    return OpenAIComplianceAdapterResult(
        status="failed",
        mode="provider-pull",
        cursor=cursor,
        blocked_reason="Live OpenAI Compliance API pull is scaffolded but requires tenant endpoint and scope confirmation.",
        next_actions=[
            "Add the tenant OpenAI Compliance API base URL or OAuth workspace context to encrypted credentials.",
            "Confirm compliance log scopes and retention access for this workspace.",
            "Keep scheduled sync disabled until the live provider request contract is verified.",
        ],
        provider_adapter_required=False,
    )
