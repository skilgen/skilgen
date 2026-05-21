from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from packages.skillayer_agent.local_importer import build_windsurf_agent_run_payloads


def _write_windsurf_fixture(windsurf_home: Path, project_root: Path) -> None:
    conversations = windsurf_home / "conversations" / "acme"
    conversations.mkdir(parents=True)
    records = [
        {
            "sessionId": "windsurf-session-1",
            "timestamp": "2026-05-20T11:00:00Z",
            "type": "user",
            "cwd": str(project_root),
            "usage": {"prompt_tokens": 8},
        },
        {
            "sessionId": "windsurf-session-1",
            "timestamp": "2026-05-20T11:03:00Z",
            "type": "assistant",
            "cwd": str(project_root),
            "model": "claude-sonnet-4.5",
            "usage": {"prompt_tokens": 12, "completion_tokens": 6},
            "tool_calls": [
                {"name": "edit_file", "input": {"file_path": str(project_root / "src/app.ts")}},
                {"name": "run_command", "input": {"command": "npm test -- --runInBand"}},
                {"name": "grep", "input": {"pattern": "TODO", "path": str(project_root / "src")}},
            ],
        },
    ]
    (conversations / "session-1.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


class WindsurfImporterTests(unittest.TestCase):
    def test_windsurf_jsonl_imports_metadata_only_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = root / "repo"
            project_root.mkdir()
            windsurf_home = root / ".codeium" / "windsurf"
            _write_windsurf_fixture(windsurf_home, project_root)

            payloads = build_windsurf_agent_run_payloads(
                windsurf_home=windsurf_home,
                project_root=project_root,
                repo_id="repo_1",
                repo_full_name="acme/web",
            )

            self.assertEqual(len(payloads), 1)
            payload = payloads[0]
            metadata = payload["metadata"]
            self.assertEqual(payload["agent"], {"vendor": "Codeium", "product": "Windsurf", "runtime": "windsurf"})
            self.assertEqual(payload["session_id"], "windsurf-windsurf-session-1-session-1")
            self.assertEqual(metadata["source_provider"], "windsurf_local")
            self.assertEqual(metadata["source_record_types"], ["windsurf_jsonl"])
            self.assertEqual(metadata["tokens_input"], 20)
            self.assertEqual(metadata["tokens_output"], 6)
            self.assertEqual(metadata["activity_metrics"]["edited_files"], 1)
            self.assertEqual(metadata["activity_metrics"]["commands"], 1)
            self.assertEqual(metadata["activity_metrics"]["searches"], 1)
            self.assertIn("src/app.ts", metadata["file_targets"])
            self.assertEqual(metadata["activity_details"]["commands"], ["npm test -- --runInBand"])
            encoded = json.dumps(payload, sort_keys=True)
            self.assertNotIn("raw prompt", encoded)


if __name__ == "__main__":
    unittest.main()
