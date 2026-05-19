from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class AnthropicComplianceAdapterResult:
    status: str
    mode: str
    cursor: str | None
    next_cursor: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    blocked_reason: str | None = None
    next_actions: list[str] = field(default_factory=list)
    provider_adapter_required: bool = False


def _has_anthropic_credential(credentials: dict[str, Any]) -> bool:
    return bool(credentials.get("api_key") or credentials.get("access_token") or credentials.get("compliance_api_key"))


def _seeded_anthropic_events(cursor: str | None) -> list[dict[str, Any]]:
    occurred_at = datetime.now(UTC)
    return [
        {
            "provider_event_id": f"anthropic-seeded-{cursor or 'initial'}-1",
            "event_type": "agent.compliance",
            "actor_login": "ravi@skillayer.com",
            "occurred_at": occurred_at.isoformat(),
            "provider": "Anthropic Compliance API",
            "model": "claude-opus-4-7",
            "model_tier": "very-high",
            "intelligence_tier": "very-high",
            "access_scope": "full-access",
            "full_access": True,
            "autonomous_access": False,
            "tool_permissions": ["bash", "edit", "read", "mcp"],
            "tool_calls": 11,
            "mcp_tools": ["github", "linear"],
            "repo_id": "repo_skilgen",
            "repo_name": "ravichanduummadisetti/skilgen",
            "file_targets": [
                "apps/api/api/v8/settings/router.py",
                "apps/api/api/v8/settings/anthropic_compliance_adapter.py",
                "apps/api/tests/test_v8_settings_rbac.py",
            ],
            "policy_decision": "require_approval",
            "approval_status": "approved",
            "warnings": 2,
            "tokens_input": 420000,
            "tokens_output": 86000,
            "tokens_base_input": 260000,
            "tokens_cache_creation_input": 90000,
            "tokens_cache_read_input": 70000,
            "token_source": "anthropic_compliance_api",
            "cost_usd": 5.84,
            "cost_source": "provider_reported",
            "cost_estimate": False,
            "latency_ms": 124000,
            "session_id": f"anthropic-compliance-{cursor or 'initial'}",
            "source_record_type": "formal-compliance",
            "metadata": {
                "source": "seeded_anthropic_compliance_fixture",
                "cost_source": "provider_reported",
                "token_source": "anthropic_compliance_api",
                "usage_provenance_label": "Provider-reported by Anthropic compliance fixture",
                "pr_number": 11,
                "head_sha": "0e90c546f4bca6ccec03b9c33ffdec063444a718",
                "branch": "v8/next-feature-loop",
                "provider_native_token_buckets": {
                    "input_tokens": 260000,
                    "cache_creation_input_tokens": 90000,
                    "cache_read_input_tokens": 70000,
                    "output_tokens": 86000,
                },
                "privacy": "metadata-only; raw chat, file content, and tool parameters dropped",
            },
        },
        {
            "provider_event_id": f"anthropic-seeded-{cursor or 'initial'}-2",
            "event_type": "agent.compliance",
            "actor_login": "ravi@skillayer.com",
            "occurred_at": occurred_at.isoformat(),
            "provider": "Anthropic Compliance API",
            "model": "claude-haiku-4-5-20251001",
            "model_tier": "fast",
            "intelligence_tier": "low",
            "access_scope": "default",
            "full_access": False,
            "autonomous_access": False,
            "tool_permissions": ["read"],
            "tool_calls": 1,
            "repo_id": "repo_skilgen",
            "repo_name": "ravichanduummadisetti/skilgen",
            "file_targets": ["docs/v8-refactor/08-agent-compliance-ingestion.md"],
            "policy_decision": "log_only",
            "approval_status": "not_required",
            "tokens_input": 32000,
            "tokens_output": 7000,
            "tokens_base_input": 16000,
            "tokens_cache_read_input": 16000,
            "token_source": "anthropic_compliance_api",
            "cost_usd": 0.14,
            "cost_source": "provider_reported",
            "cost_estimate": False,
            "latency_ms": 6800,
            "session_id": f"anthropic-compliance-{cursor or 'initial'}",
            "source_record_type": "formal-compliance",
            "metadata": {
                "source": "seeded_anthropic_compliance_fixture",
                "cost_source": "provider_reported",
                "token_source": "anthropic_compliance_api",
                "usage_provenance_label": "Provider-reported by Anthropic compliance fixture",
                "commit_sha": "e60a760",
                "branch": "v8/next-feature-loop",
                "provider_native_token_buckets": {
                    "input_tokens": 16000,
                    "cache_read_input_tokens": 16000,
                    "output_tokens": 7000,
                },
                "privacy": "metadata-only; raw chat, file content, and tool parameters dropped",
            },
        },
    ]


def pull_anthropic_compliance_events(
    credentials: dict[str, Any],
    *,
    cursor: str | None,
    dry_run: bool,
) -> AnthropicComplianceAdapterResult:
    if dry_run:
        return AnthropicComplianceAdapterResult(
            status="pending",
            mode="dry-run",
            cursor=cursor,
            blocked_reason="Dry run only checks readiness; no Anthropic events were pulled.",
            next_actions=["Run sync with dry_run=false after credentials are configured."],
            provider_adapter_required=False,
        )

    if not _has_anthropic_credential(credentials):
        return AnthropicComplianceAdapterResult(
            status="failed",
            mode="provider-pull",
            cursor=cursor,
            blocked_reason="Missing Anthropic Compliance API credential.",
            next_actions=[
                "Store an encrypted Anthropic Compliance API key or OAuth access token on this connector.",
                "Enable the Anthropic Compliance API for the tenant and grant activity/chat/file audit read scope.",
                "Run the connector credential test, then retry sync.",
            ],
            provider_adapter_required=False,
        )

    if credentials.get("seeded_fixture") or credentials.get("mock_anthropic_compliance_fixture"):
        next_cursor = f"anthropic-fixture-{int(datetime.now(UTC).timestamp())}"
        return AnthropicComplianceAdapterResult(
            status="success",
            mode="fixture",
            cursor=cursor,
            next_cursor=next_cursor,
            events=_seeded_anthropic_events(cursor),
            next_actions=[
                "Review compliance events, provider coverage, and insights for Claude model/cache/cost provenance.",
                "Replace seeded fixture credentials with tenant Anthropic Compliance API credentials for production sync.",
            ],
            provider_adapter_required=False,
        )

    return AnthropicComplianceAdapterResult(
        status="failed",
        mode="provider-pull",
        cursor=cursor,
        blocked_reason="Live Anthropic Compliance API pull is scaffolded but requires tenant endpoint and scope confirmation.",
        next_actions=[
            "Add the tenant Anthropic Compliance API workspace context to encrypted credentials.",
            "Confirm compliance access key scopes for activity logs, chat metadata, file metadata, and audit events.",
            "Keep scheduled sync disabled until the live provider request contract is verified.",
        ],
        provider_adapter_required=False,
    )
