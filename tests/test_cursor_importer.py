from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from packages.skillayer_agent.local_importer import build_cursor_agent_run_payloads


def _write_cursor_fixture(cursor_home: Path, project_root: Path) -> None:
    workspace = cursor_home / "User" / "workspaceStorage" / "workspace-1"
    workspace.mkdir(parents=True)
    db_path = workspace / "state.vscdb"
    chat_data = {
        "conversations": [
            {
                "id": "cursor-session-1",
                "messages": [
                    {
                        "role": "user",
                        "timestamp": "2026-05-20T10:00:00Z",
                        "usage": {"prompt_tokens": 10, "completion_tokens": 0},
                    },
                    {
                        "role": "assistant",
                        "timestamp": "2026-05-20T10:02:00Z",
                        "assistant": {"modelInfo": {"name": "gpt-5.4"}},
                        "usage": {"prompt_tokens": 20, "completion_tokens": 5},
                        "tool_calls": [
                            {"name": "edit_file", "input": {"file_path": str(project_root / "apps/api.py")}},
                            {"name": "run_command", "input": {"command": "pytest tests/test_api.py"}},
                            {"name": "search", "input": {"pattern": "TODO", "path": str(project_root)}},
                        ],
                    },
                ],
            }
        ]
    }
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
        connection.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", ("workspace.folder", f"file://{project_root}"))
        connection.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", ("chat-data", json.dumps(chat_data)))
        connection.commit()
    finally:
        connection.close()


class CursorImporterTests(unittest.TestCase):
    def test_cursor_state_vscdb_imports_metadata_only_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = root / "repo"
            project_root.mkdir()
            cursor_home = root / "Cursor"
            _write_cursor_fixture(cursor_home, project_root)

            payloads = build_cursor_agent_run_payloads(
                cursor_home=cursor_home,
                project_root=project_root,
                repo_id="repo_1",
                repo_full_name="acme/api",
            )

            self.assertEqual(len(payloads), 1)
            payload = payloads[0]
            metadata = payload["metadata"]
            self.assertEqual(payload["agent"], {"vendor": "Cursor", "product": "Cursor", "runtime": "cursor"})
            self.assertEqual(payload["session_id"], "cursor-cursor-session-1")
            self.assertEqual(metadata["source_provider"], "cursor_local")
            self.assertEqual(metadata["source_record_types"], ["cursor_state_vscdb"])
            self.assertEqual(metadata["tokens_input"], 30)
            self.assertEqual(metadata["tokens_output"], 5)
            self.assertEqual(metadata["activity_metrics"]["edited_files"], 1)
            self.assertEqual(metadata["activity_metrics"]["commands"], 1)
            self.assertEqual(metadata["activity_metrics"]["searches"], 1)
            self.assertIn("apps/api.py", metadata["file_targets"])
            self.assertEqual(metadata["activity_details"]["commands"], ["pytest tests/test_api.py"])
            encoded = json.dumps(payload, sort_keys=True)
            self.assertNotIn("file contents", encoded)


if __name__ == "__main__":
    unittest.main()
