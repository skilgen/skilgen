from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.import_codex_sessions import build_agent_run_payloads, build_claude_agent_run_payloads


class CodexSessionImporterTests(unittest.TestCase):
    def test_build_agent_run_payloads_keeps_metadata_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions = codex_home / "sessions" / "2026" / "05" / "17"
            sessions.mkdir(parents=True)
            (codex_home / "session_index.jsonl").write_text(
                json.dumps({"id": "thread_1", "thread_name": "Build Skillayer activity"}) + "\n",
                encoding="utf-8",
            )
            source = sessions / "rollout.jsonl"
            records = [
                {"timestamp": "2026-05-17T04:00:00Z", "type": "session_meta", "payload": {"id": "thread_1", "cwd": str(root), "originator": "Codex Desktop"}},
                {"timestamp": "2026-05-17T04:01:00Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn_1"}},
                {"timestamp": "2026-05-17T04:01:01Z", "type": "turn_context", "payload": {"turn_id": "turn_1", "cwd": str(root), "model": "gpt-5.5", "effort": "medium"}},
                {"timestamp": "2026-05-17T04:01:02Z", "type": "event_msg", "payload": {"type": "user_message", "message": "please edit secret file"}},
                {"timestamp": "2026-05-17T04:01:03Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "rg TODO apps"})}},
                {"timestamp": "2026-05-17T04:01:03Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "sed -n '1,20p' apps/api.py"})}},
                {"timestamp": "2026-05-17T04:01:03Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "rg --files apps"})}},
                {
                    "timestamp": "2026-05-17T04:01:04Z",
                    "type": "event_msg",
                    "payload": {
                        "type": "patch_apply_end",
                        "turn_id": "turn_1",
                        "success": True,
                        "changes": {str(root / "apps/api.py"): {"type": "update", "unified_diff": "+raw code"}},
                    },
                },
                {
                    "timestamp": "2026-05-17T04:01:05Z",
                    "type": "event_msg",
                    "payload": {
                        "type": "token_count",
                        "info": {
                            "last_token_usage": {
                                "input_tokens": 10,
                                "cached_input_tokens": 4,
                                "output_tokens": 5,
                                "reasoning_output_tokens": 2,
                                "total_tokens": 15,
                            }
                        },
                    },
                },
                {"timestamp": "2026-05-17T04:02:00Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn_1"}},
            ]
            source.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

            payloads = build_agent_run_payloads(codex_home=codex_home, project_root=root, repo_id="repo_1")

        self.assertEqual(len(payloads), 1)
        payload = payloads[0]
        self.assertEqual(payload["session_id"], "turn_1")
        self.assertEqual(payload["repo_id"], "repo_1")
        self.assertEqual(payload["metadata"]["model"], "gpt-5.5")
        self.assertEqual(payload["metadata"]["tokens_total"], 15)
        self.assertEqual(payload["metadata"]["tokens_cached_input"], 4)
        self.assertEqual(payload["metadata"]["tokens_reasoning_output"], 2)
        self.assertEqual(payload["metadata"]["token_source"], "codex_jsonl_last_token_usage")
        self.assertEqual(payload["metadata"]["cost_source"], "estimated_from_provider_token_usage")
        self.assertTrue(payload["metadata"]["cost_estimate"])
        self.assertEqual(payload["metadata"]["file_targets"], ["apps/api.py"])
        self.assertEqual(payload["metadata"]["activity_metrics"]["edited_files"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["explored_files"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["searches"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["lists"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["commands"], 3)
        self.assertEqual(payload["metadata"]["activity_details"]["edited_files"], ["apps/api.py"])
        self.assertEqual(payload["metadata"]["activity_details"]["explored_files"], ["apps/api.py"])
        self.assertEqual(len(payload["metadata"]["activity_details"]["commands"]), 3)
        self.assertIn("rg TODO apps", payload["metadata"]["activity_details"]["searches"])
        self.assertNotIn("please edit secret file", json.dumps(payload))
        self.assertNotIn("+raw code", json.dumps(payload))

    def test_build_claude_agent_run_payloads_matches_background_metrics_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_home = root / ".claude"
            project = claude_home / "projects" / "-tmp-skilgen-work"
            project.mkdir(parents=True)
            source = project / "claude-session.jsonl"
            records = [
                {
                    "type": "user",
                    "sessionId": "claude-session",
                    "cwd": str(root),
                    "permissionMode": "bypassPermissions",
                    "timestamp": "2026-05-18T03:00:00Z",
                    "message": {"role": "user", "content": [{"type": "text", "text": "raw request must not leak"}]},
                },
                {
                    "type": "assistant",
                    "sessionId": "claude-session",
                    "cwd": str(root),
                    "permissionMode": "bypassPermissions",
                    "timestamp": "2026-05-18T03:00:01Z",
                    "message": {
                        "role": "assistant",
                        "model": "claude-sonnet-4-5-20250929",
                        "usage": {
                            "input_tokens": 10,
                            "cache_creation_input_tokens": 20,
                            "cache_creation": {"ephemeral_5m_input_tokens": 12, "ephemeral_1h_input_tokens": 8},
                            "cache_read_input_tokens": 30,
                            "output_tokens": 5,
                            "speed": "standard",
                        },
                        "content": [
                            {"type": "tool_use", "name": "Read", "input": {"file_path": str(root / "apps/api.py")}},
                            {"type": "tool_use", "name": "Grep", "input": {"pattern": "TODO", "path": "apps"}},
                            {"type": "tool_use", "name": "Glob", "input": {"pattern": "**/*.py", "path": "apps"}},
                            {"type": "tool_use", "name": "Bash", "input": {"command": "rg TODO apps"}},
                            {"type": "tool_use", "name": "Edit", "input": {"file_path": str(root / "apps/api.py"), "old_string": "secret", "new_string": "raw code"}},
                        ],
                    },
                },
            ]
            source.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

            payloads = build_claude_agent_run_payloads(claude_home=claude_home, project_root=root, repo_id="repo_1")

        self.assertEqual(len(payloads), 1)
        payload = payloads[0]
        self.assertEqual(payload["agent"]["runtime"], "claude_code")
        self.assertEqual(payload["metadata"]["provider"], "Claude Code")
        self.assertEqual(payload["metadata"]["model"], "claude-sonnet-4-5-20250929")
        self.assertEqual(payload["metadata"]["tokens_input"], 60)
        self.assertEqual(payload["metadata"]["tokens_output"], 5)
        self.assertEqual(payload["metadata"]["tokens_total"], 65)
        self.assertEqual(payload["metadata"]["tokens_base_input"], 10)
        self.assertEqual(payload["metadata"]["tokens_cache_creation_input"], 20)
        self.assertEqual(payload["metadata"]["tokens_cache_creation_5m_input"], 12)
        self.assertEqual(payload["metadata"]["tokens_cache_creation_1h_input"], 8)
        self.assertEqual(payload["metadata"]["tokens_cache_read_input"], 30)
        self.assertEqual(payload["metadata"]["token_source"], "claude_code_jsonl_message_usage")
        self.assertEqual(payload["metadata"]["cost_source"], "estimated_from_provider_token_usage")
        self.assertTrue(payload["metadata"]["cost_estimate"])
        self.assertEqual(payload["metadata"]["access_scope"], "full-access")
        self.assertEqual(payload["metadata"]["activity_metrics"]["edited_files"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["explored_files"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["searches"], 2)
        self.assertEqual(payload["metadata"]["activity_metrics"]["lists"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["commands"], 1)
        self.assertEqual(payload["metadata"]["activity_metrics"]["tool_calls"], 5)
        self.assertEqual(payload["metadata"]["activity_details"]["edited_files"], ["apps/api.py"])
        self.assertEqual(payload["metadata"]["activity_details"]["explored_files"], ["apps/api.py"])
        self.assertIn("Grep TODO apps", payload["metadata"]["activity_details"]["searches"])
        self.assertIn("rg TODO apps", payload["metadata"]["activity_details"]["commands"])
        self.assertNotIn("raw request must not leak", json.dumps(payload))
        self.assertNotIn("raw code", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
