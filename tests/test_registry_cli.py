from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import subprocess
import sys
import threading
from tempfile import TemporaryDirectory
from typing import ClassVar
import unittest


class RegistryCliTests(unittest.TestCase):
    def test_skills_publish_and_import_call_registry_api(self) -> None:
        requests: list[dict[str, object]] = []

        class Handler(BaseHTTPRequestHandler):
            server_version = "RegistryCliTest/1.0"
            protocol_version = "HTTP/1.1"
            responses: ClassVar[dict[str, dict[str, object]]] = {
                "/registry/publish": {
                    "id": "reg_1",
                    "name": "API skill",
                    "skill_id": "skill_1",
                },
                "/registry/reg_1/import": {
                    "id": "reg_1",
                    "content": "# Imported\n\nRegistry skill.",
                    "import_count": 1,
                },
            }

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length).decode("utf-8")
                requests.append(
                    {
                        "path": self.path,
                        "authorization": self.headers.get("Authorization"),
                        "body": json.loads(body or "{}"),
                    }
                )
                payload = json.dumps(self.responses[self.path]).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, _format: str, *_args: object) -> None:
                return

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        api_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                skill_file = root / "SKILL.md"
                skill_file.write_text("# API\n\nUse API patterns.", encoding="utf-8")
                target = root / "imported"
                target.mkdir()
                env = {"SKILLAYER_API_KEY": "test_key"}
                publish = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "skilgen.cli.main",
                        "skills",
                        "publish",
                        str(skill_file),
                        "--skill-id",
                        "skill_1",
                        "--name",
                        "API skill",
                        "--description",
                        "Reusable API guidance.",
                        "--tag",
                        "api",
                        "--api-url",
                        api_url,
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                    env={**os.environ, **env},
                )
                imported = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "skilgen.cli.main",
                        "skills",
                        "import",
                        "reg_1",
                        "--target-dir",
                        str(target),
                        "--api-url",
                        api_url,
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                    env={**os.environ, **env},
                )

                self.assertEqual(json.loads(publish.stdout)["published_skill"]["id"], "reg_1")
                self.assertEqual(Path(json.loads(imported.stdout)["imported_skill"]["path"]), (target / "SKILL.md").resolve())
                self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "# Imported\n\nRegistry skill.")
                self.assertEqual(requests[0]["authorization"], "Bearer test_key")
                self.assertEqual(requests[0]["body"]["skill_id"], "skill_1")
                self.assertEqual(requests[1]["path"], "/registry/reg_1/import")
        finally:
            server.shutdown()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
