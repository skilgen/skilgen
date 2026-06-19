from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def test_memory_init_session_creates_valid_json(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "skilgen.cli.main", "memory", "--init-session", "--project-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Session file created:" in result.stdout
    files = list((tmp_path / ".skilgen" / "sessions").glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert {"session_id", "agent_runtime", "task_description", "engineer_login", "duration_minutes", "files_touched", "skill_paths_loaded", "messages"} <= set(payload)


def test_memory_upload_missing_api_key_exits_one(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "skilgen.cli.main", "memory", "--upload", "--repo-id", "repo_123", "--project-root", str(tmp_path)],
        text=True,
        capture_output=True,
        env={key: value for key, value in os.environ.items() if key != "SKILLAYER_API_KEY"},
    )
    assert result.returncode == 1
    assert "SKILLAYER_API_KEY" in result.stderr


class UploadHandler(BaseHTTPRequestHandler):
    seen_authorization = ""
    seen_path = ""

    def do_POST(self) -> None:  # noqa: N802
        UploadHandler.seen_authorization = self.headers.get("Authorization", "")
        UploadHandler.seen_path = self.path
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        body = json.dumps({"session_db_id": "sess_db", "status": "duplicate", "extraction_queued": False}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_memory_upload_handles_duplicate_response(tmp_path: Path) -> None:
    sessions = tmp_path / ".skilgen" / "sessions"
    sessions.mkdir(parents=True)
    (sessions / "session.json").write_text(json.dumps({"session_id": "abc", "agent_runtime": "codex", "messages": []}), encoding="utf-8")
    server = HTTPServer(("127.0.0.1", 0), UploadHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "skilgen.cli.main",
                "memory",
                "--upload",
                "--repo-id",
                "repo_123",
                "--project-root",
                str(tmp_path),
                "--api-url",
                f"http://127.0.0.1:{server.server_port}",
            ],
            text=True,
            capture_output=True,
            check=True,
            env={**os.environ, "SKILLAYER_API_KEY": "test_key"},
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)
    assert "Already uploaded" in result.stdout
    assert "0 session(s) uploaded, 1 skipped." in result.stdout
    assert UploadHandler.seen_authorization == "Bearer test_key"
    assert UploadHandler.seen_path == "/repos/repo_123/sessions"
