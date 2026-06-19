from __future__ import annotations

import json
import unittest
from typing import Any

import httpx

from apps.api.api.v8.settings.openai_compliance_adapter import pull_openai_compliance_events


class OpenAIComplianceSyncTests(unittest.TestCase):
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
                        "id": "audit_123",
                        "type": "response.completed",
                        "created_at": "2026-05-20T15:30:00Z",
                        "actor": {"email": "dev@example.com"},
                        "organization_id": "org-openai",
                        "project_id": "proj-skillayer",
                        "model": "gpt-5.5",
                        "model_tier": "high-reasoning",
                        "intelligence_tier": "high",
                        "access_scope": "full-access",
                        "full_access": True,
                        "tool_permissions": ["shell", "apply_patch"],
                        "tool_calls": [{"name": "exec_command", "arguments": {"cmd": "secret"}}],
                        "mcp_tools": ["github"],
                        "repo": {"id": "repo_1", "full_name": "acme/app"},
                        "file_targets": ["apps/api/api/v8/settings/router.py"],
                        "policy": {"decision": "require_approval"},
                        "approval": {"status": "approved"},
                        "violations": ["full-access outside default policy"],
                        "warnings": 1,
                        "usage": {
                            "input_tokens": 1200,
                            "output_tokens": 400,
                            "cached_input_tokens": 200,
                            "reasoning_output_tokens": 50,
                            "cost_usd": 0.42,
                            "latency_ms": 5300,
                        },
                        "session_id": "run_123",
                        "metadata": {
                            "branch": "v8/next-feature-loop",
                            "head_sha": "abc123",
                            "pr_number": 11,
                            "prompt": "do not store this",
                            "tool_arguments": {"cmd": "do not store this either"},
                        },
                    }
                ],
                "next_cursor": "cursor-2",
            }

        result = pull_openai_compliance_events(
            {
                "api_key": "sk-live",
                "organization_id": "org-openai",
                "project_id": "proj-skillayer",
                "page_size": 25,
                "event_types": ["response.completed", "tool.call.completed"],
            },
            cursor="cursor-1",
            dry_run=False,
            http_get=fake_get,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.mode, "provider-pull")
        self.assertEqual(result.cursor, "cursor-1")
        self.assertEqual(result.next_cursor, "cursor-2")
        self.assertEqual(len(result.events), 1)
        self.assertEqual(calls[0]["url"], "https://api.openai.com/v1/organization/audit_logs")
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer sk-live")
        self.assertEqual(calls[0]["headers"]["OpenAI-Organization"], "org-openai")
        self.assertEqual(calls[0]["headers"]["OpenAI-Project"], "proj-skillayer")
        self.assertEqual(calls[0]["params"]["after"], "cursor-1")
        self.assertEqual(calls[0]["params"]["limit"], 25)
        self.assertEqual(calls[0]["params"]["event_types[]"], ["response.completed", "tool.call.completed"])

        event = result.events[0]
        self.assertEqual(event["provider_event_id"], "audit_123")
        self.assertEqual(event["actor_login"], "dev@example.com")
        self.assertEqual(event["provider"], "OpenAI Compliance Platform")
        self.assertEqual(event["model"], "gpt-5.5")
        self.assertEqual(event["repo_name"], "acme/app")
        self.assertEqual(event["tokens_input"], 1200)
        self.assertEqual(event["tokens_output"], 400)
        self.assertEqual(event["cost_usd"], 0.42)
        self.assertEqual(event["tool_calls"], 1)
        self.assertEqual(event["policy_decision"], "require_approval")
        self.assertEqual(event["approval_status"], "approved")
        self.assertEqual(event["metadata"]["token_source"], "openai_compliance_api")
        self.assertEqual(event["metadata"]["privacy"], "metadata-only; raw prompts, chat, diffs, and tool parameters dropped")

        encoded = json.dumps(event, sort_keys=True)
        self.assertNotIn("do not store this", encoded)
        self.assertNotIn("tool_arguments", encoded)
        self.assertNotIn('"prompt"', encoded)

    def test_provider_event_id_fallback_is_stable_for_idempotency(self) -> None:
        payload = {
            "data": [
                {
                    "type": "thread.run.completed",
                    "created": 1779291000,
                    "actor_email": "dev@example.com",
                    "usage": {"input_tokens": 1, "output_tokens": 2},
                    "metadata": {"branch": "main", "prompt": "redacted"},
                }
            ],
            "has_more": True,
            "last_id": "audit_after_1",
        }

        def fake_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
            return payload

        first = pull_openai_compliance_events({"api_key": "sk-live"}, cursor=None, dry_run=False, http_get=fake_get)
        second = pull_openai_compliance_events({"api_key": "sk-live"}, cursor=None, dry_run=False, http_get=fake_get)

        self.assertEqual(first.status, "success")
        self.assertEqual(first.next_cursor, "audit_after_1")
        self.assertEqual(first.events[0]["provider_event_id"], second.events[0]["provider_event_id"])
        self.assertTrue(first.events[0]["provider_event_id"].startswith("openai-audit-"))

    def test_http_failure_returns_blocked_sync_result(self) -> None:
        request = httpx.Request("GET", "https://api.openai.com/v1/organization/audit_logs")
        response = httpx.Response(429, request=request, headers={"retry-after": "60"})

        def fake_get(url: str, headers: dict[str, str], params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
            raise httpx.HTTPStatusError("rate limited", request=request, response=response)

        result = pull_openai_compliance_events({"api_key": "sk-live"}, cursor="cursor-1", dry_run=False, http_get=fake_get)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.mode, "provider-pull")
        self.assertIn("HTTP 429", result.blocked_reason or "")
        self.assertIn("rate-limit", " ".join(result.next_actions))


if __name__ == "__main__":
    unittest.main()
