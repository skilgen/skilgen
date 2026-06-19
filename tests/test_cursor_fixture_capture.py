from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.cursor_fixture_capture import capture_cursor_fixture


class CursorFixtureCaptureTests(unittest.TestCase):
    def test_capture_cursor_fixture_redacts_prompts_paths_and_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "state.vscdb"
            connection = sqlite3.connect(db_path)
            try:
                connection.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
                connection.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", ("workspace.folder", "/Users/alice/work/secret-repo"))
                connection.execute(
                    "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
                    (
                        "chat-data",
                        json.dumps(
                            {
                                "prompt": "please read sk-live-secret-token-value and paste file contents",
                                "messages": [{"role": "assistant", "content": "raw source code here"}],
                            }
                        ),
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            fixture = capture_cursor_fixture(db_path)
            encoded = json.dumps(fixture, sort_keys=True)

            self.assertEqual(fixture["source"], "cursor_state_vscdb_anonymized")
            self.assertNotIn("/Users/alice", encoded)
            self.assertNotIn("sk-live-secret-token-value", encoded)
            self.assertNotIn("raw source code here", encoded)
            self.assertIn("<home>", encoded)
            self.assertIn("<redacted:", encoded)


if __name__ == "__main__":
    unittest.main()
