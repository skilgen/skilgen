from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from packages.skillayer_agent import cli


def _write_codex_session(root: Path, codex_home: Path) -> None:
    sessions = codex_home / "sessions" / "2026" / "05" / "20"
    sessions.mkdir(parents=True)
    (codex_home / "session_index.jsonl").write_text(
        json.dumps({"id": "thread_cli", "thread_name": "Skillayer CLI proof"}) + "\n",
        encoding="utf-8",
    )
    records = [
        {"timestamp": "2026-05-20T12:00:00Z", "type": "session_meta", "payload": {"id": "thread_cli", "cwd": str(root), "originator": "Codex Desktop"}},
        {"timestamp": "2026-05-20T12:00:01Z", "type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn_cli"}},
        {"timestamp": "2026-05-20T12:00:02Z", "type": "turn_context", "payload": {"turn_id": "turn_cli", "cwd": str(root), "model": "gpt-5.5"}},
        {"timestamp": "2026-05-20T12:00:03Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "rg TODO apps"})}},
        {"timestamp": "2026-05-20T12:00:04Z", "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn_cli"}},
    ]
    (sessions / "rollout.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _run_cli(argv: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = cli.main(argv)
    return code, output.getvalue()


class SkillayerAgentCliTests(unittest.TestCase):
    def test_connect_writes_private_config_without_echoing_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "agent.json"
            code, output = _run_cli(
                [
                    "connect",
                    "--config",
                    str(config),
                    "--org-id",
                    "org_1",
                    "--token",
                    "secret-token",
                    "--project-root",
                    tmp,
                    "--repo-full-name",
                    "acme/app",
                    "--machine-id",
                    "machine-manual",
                    "--machine-label",
                    "Manual Laptop",
                    "--json",
                ]
            )

            self.assertEqual(code, 0)
            self.assertNotIn("secret-token", output)
            saved = json.loads(config.read_text(encoding="utf-8"))
            self.assertEqual(saved["org_id"], "org_1")
            self.assertEqual(saved["api_key"], "secret-token")
            self.assertEqual(saved["machine_id"], "machine-manual")
            self.assertEqual(saved["machine_label"], "Manual Laptop")
            self.assertEqual(saved["project_roots"][0]["repo_full_name"], "acme/app")
            self.assertEqual(oct(config.stat().st_mode & 0o777), "0o600")

    def test_connect_device_flow_writes_private_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "agent.json"
            calls: list[tuple[str, dict[str, object]]] = []
            responses = [
                {
                    "device_code": "device-1",
                    "user_code": "ABCD-1234",
                    "verification_uri_complete": "https://app.skillayer.com/device?user_code=ABCD-1234",
                    "interval": 1,
                    "expires_in": 60,
                },
                {"error": "authorization_pending", "interval": 1},
                {
                    "access_token": "device-token",
                    "org_id": "org_device",
                    "api_url": "https://api.skillayer.test",
                    "repo_full_name": "acme/device",
                },
            ]

            def fake_post(api_url: str, path: str, payload: dict[str, object], *, timeout: float = 10) -> dict[str, object]:
                calls.append((path, payload))
                return responses.pop(0)

            with mock.patch.object(cli, "_post_json", side_effect=fake_post), mock.patch.object(cli.time, "sleep"), mock.patch.object(cli.webbrowser, "open") as open_browser:
                code, output = _run_cli(
                    [
                        "connect",
                        "--config",
                        str(config),
                        "--api-url",
                        "https://api.skillayer.test",
                        "--project-root",
                        tmp,
                        "--machine-id",
                        "machine-device",
                        "--machine-label",
                        "Device Laptop",
                        "--json",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertNotIn("device-token", output)
            self.assertEqual([path for path, _ in calls], ["/v1/device/code", "/v1/device/token", "/v1/device/token"])
            self.assertEqual(calls[0][1]["machine_id"], "machine-device")
            self.assertEqual(calls[0][1]["machine_label"], "Device Laptop")
            open_browser.assert_called_once_with("https://app.skillayer.com/device?user_code=ABCD-1234")
            saved = json.loads(config.read_text(encoding="utf-8"))
            self.assertEqual(saved["org_id"], "org_device")
            self.assertEqual(saved["api_key"], "device-token")
            self.assertEqual(saved["machine_id"], "machine-device")
            self.assertEqual(saved["machine_label"], "Device Laptop")
            self.assertEqual(saved["api_url"], "https://api.skillayer.test")
            self.assertEqual(saved["project_roots"][0]["repo_full_name"], "acme/device")
            self.assertEqual(oct(config.stat().st_mode & 0o777), "0o600")

    def test_status_dry_run_reports_detected_runtimes_and_discoverable_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            claude_home = root / ".claude"
            (claude_home / "projects").mkdir(parents=True)
            _write_codex_session(root, codex_home)

            code, output = _run_cli(
                [
                    "status",
                    "--config",
                    str(root / "missing-agent.json"),
                    "--state",
                    str(root / "state.json"),
                    "--project-root",
                    str(root),
                    "--codex-home",
                    str(codex_home),
                    "--claude-home",
                    str(claude_home),
                    "--cursor-home",
                    str(root / "missing-cursor"),
                    "--windsurf-home",
                    str(root / "missing-windsurf"),
                    "--providers",
                    "codex,claude",
                    "--dry-run",
                    "--json",
                ]
            )

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["command"], "status")
            self.assertEqual(payload["discoverable_runs"], 1)
            self.assertEqual(
                {runtime["runtime"]: runtime["detected"] for runtime in payload["runtimes"]},
                {"codex_desktop": True, "codex_cli": True, "claude_code": True, "cursor": False, "windsurf": False},
            )

    def test_sync_dry_run_uses_skillayer_importer_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            _write_codex_session(root, codex_home)

            code, output = _run_cli(
                [
                    "sync",
                    "--config",
                    str(root / "missing-agent.json"),
                    "--state",
                    str(root / "state.json"),
                    "--org-id",
                    "org_1",
                    "--project-root",
                    str(root),
                    "--codex-home",
                    str(codex_home),
                    "--providers",
                    "codex",
                    "--dry-run",
                    "--json",
                ]
            )

            self.assertEqual(code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["command"], "sync")
            self.assertEqual(payload["discovered"], 1)
            self.assertEqual(payload["posted"], 1)
            self.assertEqual(payload["failed"], 0)
            self.assertFalse((root / "state.json").exists())

    def test_watch_once_posts_only_new_runs_and_records_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "state.json"
            state_path.write_text(json.dumps({"posted_session_ids": ["already-posted"]}) + "\n", encoding="utf-8")
            payloads = [
                {"session_id": "already-posted"},
                {"session_id": "new-run", "metadata": {"provider": "Codex"}},
            ]

            with mock.patch.object(cli, "discover_payloads", return_value=payloads), mock.patch.object(cli, "post_payload") as post:
                code, output = _run_cli(
                    [
                        "watch",
                        "--config",
                        str(root / "missing-agent.json"),
                        "--state",
                        str(state_path),
                        "--org-id",
                        "org_1",
                        "--token",
                        "secret-token",
                        "--project-root",
                        str(root),
                        "--providers",
                        "codex",
                        "--once",
                        "--interval",
                        "1",
                        "--json",
                    ]
                )

            self.assertEqual(code, 0)
            post.assert_called_once()
            payload = json.loads(output)
            self.assertEqual(payload["command"], "watch")
            self.assertEqual(payload["discovered"], 2)
            self.assertEqual(payload["new"], 1)
            self.assertEqual(payload["posted"], 1)
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["last_new"], 1)
            self.assertEqual(saved["last_posted"], 1)
            self.assertEqual(saved["posted_session_ids"], ["already-posted", "new-run"])


if __name__ == "__main__":
    unittest.main()
