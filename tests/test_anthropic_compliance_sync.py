from __future__ import annotations

import json
import unittest
from typing import Any

import httpx

from apps.api.api.v8.settings.anthropic_compliance_adapter import pull_anthropic_compliance_events


class AnthropicComplianceSyncTests(unittest.TestCase):
    def test_live_pull_uses_cursor_and_normalizes_metadata_only_events(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
            calls.append(
                {
                    "url": url,
                    "headers": headers,
                    "params": params,
                    "timeout_seconds": timeout_seconds,
                }
            )
            return {
                "data": [
                    {
                        "id": "msg_audit_123",
                        "type": "message.completed",
                        "created_at": "2026-05-20T16:15:00Z",
                        "actor": {"email": "dev@example.com"},
                        "workspace_id": "workspace-1",
                        "organization_id": "anthropic-org-1",
                        "model": "claude-opus-4-7",
                        "model_tier": "very-high",
                        "access_scope": "full-access",
                        "full_access": True,
                        "tool_permissions": ["bash", "edit", "read"],
                        "tool_calls": [{"name": "Bash", "arguments": {"command": "secret"}}],
                        "mcp_tools": ["github", "linear"],
                        "repo": {"id": "repo_1", "full_name": "acme/app"},
                        "file_targets": ["apps/api/api/v8/settings/anthropic_compliance_adapter.py"],
                        "policy": {"decision": "require_approval"},
                        "approval": {"status": "approved"},
                        "violations": ["full-access outside default policy"],
                        "warnings": 2,
                        "usage": {
                            "input_tokens": 260000,
                            "cache_creation_input_tokens": 90000,
                            "cache_read_input_tokens": 70000,
                            "output_tokens": 86000,
                            "cost_usd": 5.84,
                            "latency_ms": 124000,
                        },
                        "session_id": "claude-run-123",
                        "metadata": {
                            "branch": "v8/next-feature-loop",
                            "head_sha": "abc123",
                            "pr_number": 11,
                            "message": "do not store this",
                            "tool_arguments": {"command": "do not store this either"},
                        },
                    }
                ],
                "next_cursor": "cursor-2",
            }

        result = pull_anthropic_compliance_events(
            {
                "api_key": "anthropic-live",
                "workspace_id": "workspace-1",
                "page_size": 50,
            },
            cursor="cursor-1",
            dry_run=False,
            http_get=fake_get,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.mode, "provider-pull")
        self.assertEqual(result.cursor, "cursor-1")
        self.assertEqual(result.next_cursor, "cursor-2")
        self.assertEqual(calls[0]["url"], "https://api.anthropic.com/v1/admin/compliance/api/messages")
        self.assertEqual(calls[0]["headers"]["x-api-key"], "anthropic-live")
        self.assertEqual(calls[0]["headers"]["anthropic-version"], "2023-06-01")
        self.assertEqual(calls[0]["params"]["cursor"], "cursor-1")
        self.assertEqual(calls[0]["params"]["limit"], 50)
        self.assertEqual(calls[0]["params"]["workspace_id"], "workspace-1")

        event = result.events[0]
        self.assertEqual(event["provider_event_id"], "msg_audit_123")
        self.assertEqual(event["actor_login"], "dev@example.com")
        self.assertEqual(event["provider"], "Anthropic Compliance API")
        self.assertEqual(event["model"], "claude-opus-4-7")
        self.assertEqual(event["repo_name"], "acme/app")
        self.assertEqual(event["tokens_input"], 260000)
        self.assertEqual(event["tokens_output"], 86000)
        self.assertEqual(event["tokens_cache_creation_input"], 90000)
        self.assertEqual(event["tokens_cache_read_input"], 70000)
        self.assertEqual(event["cost_usd"], 5.84)
        self.assertEqual(event["tool_calls"], 1)
        self.assertEqual(event["policy_decision"], "require_approval")
        self.assertEqual(event["approval_status"], "approved")
        self.assertEqual(event["metadata"]["token_source"], "anthropic_compliance_api")
        self.assertEqual(event["metadata"]["provider_native_token_buckets"]["cache_read_input_tokens"], 70000)

        encoded = json.dumps(event, sort_keys=True)
        self.assertNotIn("do not store this", encoded)
        self.assertNotIn("tool_arguments", encoded)
        self.assertNotIn('"message"', encoded)

    def test_access_token_uses_bearer_auth(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
            calls.append({"headers": headers})
            return {"data": []}

        result = pull_anthropic_compliance_events(
            {"access_token": "oauth-token"},
            cursor=None,
            dry_run=False,
            http_get=fake_get,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer oauth-token")
        self.assertNotIn("x-api-key", calls[0]["headers"])

    def test_provider_event_id_fallback_is_stable_for_idempotency(self) -> None:
        payload = {
            "messages": [
                {
                    "type": "message.completed",
                    "created": 1779291000,
                    "actor_email": "dev@example.com",
                    "usage": {"input_tokens": 1, "output_tokens": 2},
                    "metadata": {"branch": "main", "content": "redacted"},
                }
            ],
            "has_more": True,
            "last_id": "anthropic-after-1",
        }

        def fake_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
            return payload

        first = pull_anthropic_compliance_events({"api_key": "anthropic-live"}, cursor=None, dry_run=False, http_get=fake_get)
        second = pull_anthropic_compliance_events({"api_key": "anthropic-live"}, cursor=None, dry_run=False, http_get=fake_get)

        self.assertEqual(first.status, "success")
        self.assertEqual(first.next_cursor, "anthropic-after-1")
        self.assertEqual(first.events[0]["provider_event_id"], second.events[0]["provider_event_id"])
        self.assertTrue(first.events[0]["provider_event_id"].startswith("anthropic-compliance-"))

    def test_http_failure_returns_blocked_sync_result(self) -> None:
        request = httpx.Request("GET", "https://api.anthropic.com/v1/admin/compliance/api/messages")
        response = httpx.Response(429, request=request, headers={"retry-after": "60"})

        def fake_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
            raise httpx.HTTPStatusError("rate limited", request=request, response=response)

        result = pull_anthropic_compliance_events({"api_key": "anthropic-live"}, cursor="cursor-1", dry_run=False, http_get=fake_get)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.mode, "provider-pull")
        self.assertIn("HTTP 429", result.blocked_reason or "")
        self.assertIn("rate-limit", " ".join(result.next_actions))


if __name__ == "__main__":
    unittest.main()
