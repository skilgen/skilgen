from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from packages.skillayer_agent.local_importer import build_agent_run_payloads


class CodexCliRuntimeTaggingTests(unittest.TestCase):
    def test_codex_cli_session_meta_tags_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions = codex_home / "sessions" / "2026" / "05" / "20"
            sessions.mkdir(parents=True)
            (codex_home / "session_index.jsonl").write_text(json.dumps({"id": "thread_cli", "thread_name": "CLI session"}) + "\n", encoding="utf-8")

            source = sessions / "cli.jsonl"
            records = [
                {
                    "timestamp": "2026-05-20T04:00:00Z",
                    "type": "session_meta",
                    "payload": {"id": "thread_cli", "cwd": str(root), "originator": "Codex CLI", "client": "codex-cli"},
                },
                {"timestamp": "2026-05-20T04:01:00Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn_cli"}},
                {"timestamp": "2026-05-20T04:01:01Z", "type": "turn_context", "payload": {"turn_id": "turn_cli", "cwd": str(root), "model": "gpt-5.5", "effort": "medium"}},
                {"timestamp": "2026-05-20T04:02:00Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn_cli"}},
            ]
            source.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

            payloads = build_agent_run_payloads(codex_home=codex_home, project_root=root, repo_id="repo_1")

        self.assertEqual(len(payloads), 1)
        payload = payloads[0]
        self.assertEqual(payload["agent"]["runtime"], "codex_cli")
        self.assertEqual(payload["agent"]["product"], "Codex CLI")
        self.assertEqual(payload["metadata"]["agent_provider"], "Codex CLI")
        self.assertEqual(payload["metadata"]["source_provider"], "codex_cli")


if __name__ == "__main__":
    unittest.main()

