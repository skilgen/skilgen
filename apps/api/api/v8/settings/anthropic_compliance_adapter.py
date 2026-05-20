from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import httpx


ANTHROPIC_COMPLIANCE_MESSAGES_URL = "https://api.anthropic.com/v1/admin/compliance/api/messages"
ANTHROPIC_VERSION = "2023-06-01"
RAW_CONTENT_KEYS = {
    "prompt",
    "prompts",
    "messages",
    "message",
    "content",
    "input",
    "output",
    "diff",
    "patch",
    "tool_arguments",
    "arguments",
    "text",
}

HttpGet = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]


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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return max(int(value), 0)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _safe_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return max(float(value), 0.0)
    try:
        return max(float(str(value)), 0.0)
    except (TypeError, ValueError):
        return None


def _first_string(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _string_list(value: Any, *, limit: int = 50) -> list[str]:
    return [str(item) for item in _as_list(value) if item is not None and str(item).strip()][:limit]


def _parse_timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        parsed = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
    if isinstance(value, str) and value.strip():
        text = value.strip()
        if text.isdigit():
            return datetime.fromtimestamp(float(text), tz=timezone.utc).isoformat()
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except ValueError:
            return _utc_now().isoformat()
    return _utc_now().isoformat()


def _scrub_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        scrubbed: dict[str, Any] = {}
        for key, nested in value.items():
            key_text = str(key)
            if key_text.lower() in RAW_CONTENT_KEYS:
                continue
            cleaned = _scrub_metadata(nested)
            if cleaned is not None:
                scrubbed[key_text] = cleaned
        return scrubbed
    if isinstance(value, list):
        cleaned_items = []
        for item in value:
            cleaned = _scrub_metadata(item)
            if cleaned is not None:
                cleaned_items.append(cleaned)
        return cleaned_items[:50]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _event_digest(event: dict[str, Any]) -> str:
    encoded = json.dumps(_scrub_metadata(event), sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def _anthropic_compliance_url(credentials: dict[str, Any]) -> str:
    explicit = _first_string(credentials.get("compliance_api_url"), credentials.get("messages_url"))
    if explicit:
        return explicit
    base_url = _first_string(credentials.get("base_url"))
    if base_url:
        return f"{base_url.rstrip('/')}/v1/admin/compliance/api/messages"
    return ANTHROPIC_COMPLIANCE_MESSAGES_URL


def _default_http_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Anthropic compliance response must be a JSON object")
    return payload


def _event_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("data", "messages", "events", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _extract_next_cursor(payload: dict[str, Any]) -> str | None:
    return _first_string(
        payload.get("next_cursor"),
        payload.get("next"),
        payload.get("cursor"),
        payload.get("last_id") if payload.get("has_more") else None,
    )


def _actor_email(event: dict[str, Any]) -> str | None:
    actor = _as_mapping(event.get("actor"))
    user = _as_mapping(event.get("user"))
    return _first_string(
        event.get("actor_login"),
        event.get("actor_email"),
        actor.get("email"),
        actor.get("login"),
        user.get("email"),
        user.get("login"),
    )


def _usage(event: dict[str, Any]) -> dict[str, Any]:
    usage = _as_mapping(event.get("usage") or event.get("usage_metadata"))
    message = _as_mapping(event.get("message"))
    if not usage:
        usage = _as_mapping(message.get("usage"))
    return usage


def _repo_context(event: dict[str, Any]) -> tuple[str | None, str | None]:
    repo = _as_mapping(event.get("repo") or event.get("repository"))
    metadata = _as_mapping(event.get("metadata"))
    github = _as_mapping(event.get("github") or event.get("git"))
    return (
        _first_string(event.get("repo_id"), repo.get("id"), github.get("repo_id"), metadata.get("repo_id")),
        _first_string(
            event.get("repo_name"),
            event.get("repository_name"),
            repo.get("full_name"),
            repo.get("name"),
            github.get("repo_name"),
            metadata.get("repo_name"),
        ),
    )


def _policy_decision(event: dict[str, Any]) -> str | None:
    policy = _as_mapping(event.get("policy") or event.get("policy_evaluation"))
    return _first_string(event.get("policy_decision"), event.get("decision"), policy.get("decision"), policy.get("result"))


def _approval_status(event: dict[str, Any]) -> str | None:
    approval = _as_mapping(event.get("approval") or event.get("approval_request"))
    return _first_string(event.get("approval_status"), approval.get("status"))


def _intelligence_tier(value: Any) -> str | None:
    text = _first_string(value)
    if not text:
        return None
    normalized = text.lower().replace("_", "-").strip()
    if normalized in {"very-high", "high", "medium", "low"}:
        return normalized
    if normalized in {"opus", "max", "frontier"}:
        return "very-high"
    if normalized in {"sonnet", "standard", "balanced", "default"}:
        return "medium"
    if normalized in {"haiku", "fast", "economy"}:
        return "low"
    return None


def _cost_usd(event: dict[str, Any], usage: dict[str, Any]) -> float | None:
    cost = _as_mapping(event.get("cost"))
    return _safe_float(event.get("cost_usd") or cost.get("usd") or usage.get("cost_usd"))


def _normalize_anthropic_event(event: dict[str, Any]) -> dict[str, Any]:
    metadata = _as_mapping(event.get("metadata"))
    message = _as_mapping(event.get("message"))
    usage = _usage(event)
    repo_id, repo_name = _repo_context(event)
    event_id = (
        _first_string(event.get("id"), event.get("event_id"), event.get("message_id"), message.get("id"))
        or f"anthropic-compliance-{_event_digest(event)}"
    )
    event_type = _first_string(event.get("event_type"), event.get("type"), event.get("action")) or "message.completed"
    created_value = event.get("created_at") or event.get("timestamp") or event.get("created") or message.get("created_at")
    tool_calls = event.get("tool_calls") or message.get("tool_calls")
    tool_call_count = len(tool_calls) if isinstance(tool_calls, list) else _safe_int(tool_calls or event.get("tool_call_count"))
    cost_usd = _cost_usd(event, usage)
    provider_buckets = {
        "input_tokens": _safe_int(usage.get("input_tokens")),
        "cache_creation_input_tokens": _safe_int(usage.get("cache_creation_input_tokens")),
        "cache_read_input_tokens": _safe_int(usage.get("cache_read_input_tokens")),
        "output_tokens": _safe_int(usage.get("output_tokens")),
    }
    provider_buckets = {key: value for key, value in provider_buckets.items() if value is not None}
    normalized_metadata = {
        "source": "anthropic_compliance_api",
        "provider_event_type": event_type,
        "event_id": event_id,
        "workspace_id": _first_string(event.get("workspace_id"), metadata.get("workspace_id")),
        "organization_id": _first_string(event.get("organization_id"), metadata.get("organization_id")),
        "branch": _first_string(event.get("branch"), metadata.get("branch")),
        "commit_sha": _first_string(event.get("commit_sha"), metadata.get("commit_sha")),
        "head_sha": _first_string(event.get("head_sha"), metadata.get("head_sha")),
        "pr_number": _safe_int(event.get("pr_number") or metadata.get("pr_number")),
        "git_url": _first_string(event.get("git_url"), metadata.get("git_url")),
        "cost_source": "provider_reported" if cost_usd is not None else None,
        "token_source": "anthropic_compliance_api",
        "usage_provenance_label": "Provider-reported by Anthropic compliance API",
        "provider_native_token_buckets": provider_buckets,
        "provider_metadata": _scrub_metadata(metadata),
        "privacy": "metadata-only; raw chat, file content, and tool parameters dropped",
    }
    normalized_metadata = {key: value for key, value in normalized_metadata.items() if value not in (None, "", [], {})}
    return {
        "provider_event_id": event_id,
        "event_type": "agent.compliance",
        "actor_login": _actor_email(event),
        "occurred_at": _parse_timestamp(created_value),
        "provider": "Anthropic Compliance API",
        "model": _first_string(event.get("model"), message.get("model"), metadata.get("model")),
        "model_tier": _first_string(event.get("model_tier"), metadata.get("model_tier")),
        "intelligence_tier": _intelligence_tier(event.get("intelligence_tier") or metadata.get("intelligence_tier") or event.get("model") or message.get("model")),
        "access_scope": _first_string(event.get("access_scope"), metadata.get("access_scope")),
        "full_access": bool(event.get("full_access") or metadata.get("full_access")),
        "autonomous_access": bool(event.get("autonomous_access") or metadata.get("autonomous_access")),
        "tool_permissions": _string_list(event.get("tool_permissions") or metadata.get("tool_permissions")),
        "tool_calls": tool_call_count,
        "mcp_tools": _string_list(event.get("mcp_tools") or metadata.get("mcp_tools")),
        "repo_id": repo_id,
        "repo_name": repo_name,
        "file_targets": _string_list(event.get("file_targets") or metadata.get("file_targets")),
        "policy_decision": _policy_decision(event),
        "approval_status": _approval_status(event),
        "violations": _string_list(event.get("violations") or metadata.get("violations")),
        "warnings": _safe_int(event.get("warnings") or metadata.get("warnings")),
        "tokens_input": _safe_int(usage.get("input_tokens")),
        "tokens_output": _safe_int(usage.get("output_tokens")),
        "tokens_base_input": _safe_int(usage.get("input_tokens")),
        "tokens_cache_creation_input": _safe_int(usage.get("cache_creation_input_tokens")),
        "tokens_cache_creation_5m_input": _safe_int(usage.get("cache_creation_input_tokens_5m")),
        "tokens_cache_creation_1h_input": _safe_int(usage.get("cache_creation_input_tokens_1h")),
        "tokens_cache_read_input": _safe_int(usage.get("cache_read_input_tokens")),
        "token_source": "anthropic_compliance_api",
        "cost_usd": cost_usd,
        "cost_source": "provider_reported" if cost_usd is not None else None,
        "cost_estimate": False,
        "latency_ms": _safe_int(event.get("latency_ms") or usage.get("latency_ms")),
        "error_count": _safe_int(event.get("error_count") or usage.get("errors")),
        "session_id": _first_string(event.get("session_id"), event.get("conversation_id"), event.get("run_id"), message.get("id"), event_id),
        "source_record_type": "formal-compliance",
        "metadata": normalized_metadata,
    }


def _seeded_anthropic_events(cursor: str | None) -> list[dict[str, Any]]:
    occurred_at = _utc_now()
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
    http_get: HttpGet | None = None,
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
        next_cursor = f"anthropic-fixture-{int(_utc_now().timestamp())}"
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

    token = _first_string(credentials.get("compliance_api_key"), credentials.get("api_key"), credentials.get("access_token"))
    headers = {
        "Accept": "application/json",
        "anthropic-version": _first_string(credentials.get("anthropic_version")) or ANTHROPIC_VERSION,
        "User-Agent": "skillayer-anthropic-compliance-sync/1.0",
    }
    if credentials.get("access_token") and not credentials.get("api_key") and not credentials.get("compliance_api_key"):
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["x-api-key"] = token or ""

    params: dict[str, Any] = {"limit": _safe_int(credentials.get("page_size")) or 100}
    workspace_id = _first_string(credentials.get("workspace_id"))
    if workspace_id:
        params["workspace_id"] = workspace_id
    if cursor:
        params["cursor"] = cursor

    try:
        payload = (http_get or _default_http_get)(
            _anthropic_compliance_url(credentials),
            headers,
            params,
            float(credentials.get("timeout_seconds") or 30),
        )
    except httpx.HTTPStatusError as exc:
        retry_after = exc.response.headers.get("retry-after") if exc.response is not None else None
        action = "Retry after the Anthropic rate-limit window." if retry_after else "Check Anthropic Compliance API scopes and connector credentials, then retry sync."
        return AnthropicComplianceAdapterResult(
            status="failed",
            mode="provider-pull",
            cursor=cursor,
            blocked_reason=f"Anthropic Compliance API returned HTTP {exc.response.status_code}.",
            next_actions=[action],
            provider_adapter_required=False,
        )
    except (httpx.HTTPError, ValueError) as exc:
        return AnthropicComplianceAdapterResult(
            status="failed",
            mode="provider-pull",
            cursor=cursor,
            blocked_reason=f"Anthropic Compliance API pull failed: {exc}",
            next_actions=[
                "Confirm the Anthropic compliance endpoint is reachable from the API worker.",
                "Verify the credential has admin compliance read access.",
                "Retry sync; cursor will resume from the last successful page.",
            ],
            provider_adapter_required=False,
        )

    return AnthropicComplianceAdapterResult(
        status="success",
        mode="provider-pull",
        cursor=cursor,
        next_cursor=_extract_next_cursor(payload),
        events=[_normalize_anthropic_event(event) for event in _event_list(payload)],
        next_actions=[
            "Review provider coverage for unmatched workspaces, repos, or actors after ingest.",
            "Keep the scheduled connector enabled so Skillayer reconciles Claude compliance events with GitHub and local-agent evidence.",
        ],
        provider_adapter_required=False,
    )
