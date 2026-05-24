"""Product-facing local coding-agent importer boundary.

This module is the Skillayer-owned API for local agent capture. The legacy
``scripts.import_codex_sessions`` entry point remains available for existing
operators while the product CLI moves toward ``skillayer-agent``.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from scripts.import_codex_sessions import (
    _belongs_to_project,
    _new_turn,
    _parse_timestamp,
    _record_claude_tool,
    _record_claude_usage,
    _safe_json,
    _turn_payload,
    build_agent_run_payloads,
    build_claude_agent_run_payloads,
    post_payload,
)


def _cursor_workspace_root(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    text = value
    try:
        parsed = json.loads(value)
        if isinstance(parsed, str):
            text = parsed
        elif isinstance(parsed, dict):
            text = str(parsed.get("folder") or parsed.get("uri") or parsed.get("path") or text)
    except json.JSONDecodeError:
        pass
    if text.startswith("file://"):
        parsed = urlparse(text)
        return Path(unquote(parsed.path)).expanduser().resolve()
    return Path(text).expanduser().resolve()


def _sqlite_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _cursor_rows(db_path: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        table_rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for (table_name,) in table_rows:
            table_identifier = _sqlite_identifier(str(table_name))
            columns = [row[1] for row in connection.execute(f"PRAGMA table_info({table_identifier})").fetchall()]
            key_column = next((column for column in columns if column.lower() in {"key", "id"}), None)
            value_column = next((column for column in columns if column.lower() in {"value", "contents"}), None)
            if not key_column or not value_column:
                continue
            key_identifier = _sqlite_identifier(key_column)
            value_identifier = _sqlite_identifier(value_column)
            for key, value in connection.execute(f"SELECT {key_identifier}, {value_identifier} FROM {table_identifier}"):
                if isinstance(key, str) and isinstance(value, str):
                    values[key] = value
    except sqlite3.Error:
        return {}
    finally:
        if connection is not None:
            connection.close()
    return values


def _cursor_chat_payloads(values: dict[str, Any]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for key, value in values.items():
        if "chat" not in str(key).lower() or not isinstance(value, str):
            continue
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            payloads.append(parsed)
        elif isinstance(parsed, list):
            payloads.extend(item for item in parsed if isinstance(item, dict))
    return payloads


def _cursor_conversations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("conversations", "chats", "sessions", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return [payload] if payload else []


def _cursor_messages(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("messages", "conversation", "timeline", "items"):
        value = conversation.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _cursor_time(message: dict[str, Any]) -> str | None:
    value = message.get("timestamp") or message.get("createdAt") or message.get("time")
    if isinstance(value, (int, float)):
        from datetime import datetime, timezone

        return datetime.fromtimestamp(float(value) / (1000 if value > 10_000_000_000 else 1), tz=timezone.utc).isoformat()
    return str(value) if value else None


def _cursor_model(conversation: dict[str, Any], message: dict[str, Any]) -> str | None:
    assistant = message.get("assistant") if isinstance(message.get("assistant"), dict) else {}
    model_info = assistant.get("modelInfo") if isinstance(assistant.get("modelInfo"), dict) else {}
    return str(message.get("model") or model_info.get("name") or conversation.get("model") or "") or None


def _cursor_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for key in ("tool_calls", "toolCalls", "tools"):
        value = message.get(key)
        if isinstance(value, list):
            calls.extend(item for item in value if isinstance(item, dict))
    if message.get("type") in {"tool_call", "tool-call"}:
        calls.append(message)
    return calls


def _cursor_tool_name(call: dict[str, Any]) -> str:
    return str(call.get("name") or call.get("toolName") or call.get("type") or "tool")


def _cursor_tool_input(call: dict[str, Any]) -> dict[str, Any]:
    raw = call.get("input") or call.get("args") or call.get("arguments") or call.get("params") or {}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {"command": raw}
    return raw if isinstance(raw, dict) else {}


def _cursor_to_claude_tool(name: str) -> str:
    normalized = name.lower()
    if normalized in {"edit_file", "multi_edit", "apply_patch"}:
        return "Edit"
    if normalized in {"read_file", "open_file"}:
        return "Read"
    if normalized in {"run_command", "terminal", "bash"}:
        return "Bash"
    if normalized in {"search", "grep"}:
        return "Grep"
    if normalized in {"list", "ls", "glob"}:
        return "LS"
    return name


def _local_usage_payload(usage: object) -> dict[str, Any] | None:
    if not isinstance(usage, dict):
        return None
    return {
        "input_tokens": usage.get("input_tokens") or usage.get("prompt_tokens") or usage.get("tokens_in"),
        "output_tokens": usage.get("output_tokens") or usage.get("completion_tokens") or usage.get("tokens_out"),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
    }


def build_cursor_agent_run_payloads(
    *,
    cursor_home: Path | None = None,
    project_root: Path,
    repo_id: str | None = None,
    repo_full_name: str | None = None,
) -> list[dict[str, Any]]:
    cursor_home = cursor_home or Path.home() / "Library" / "Application Support" / "Cursor"
    workspace_root = cursor_home / "User" / "workspaceStorage"
    if not workspace_root.exists():
        return []
    payloads: list[dict[str, Any]] = []
    project_root = project_root.expanduser().resolve()
    for db_path in sorted(workspace_root.glob("*/state.vscdb")):
        values = _cursor_rows(db_path)
        folder_value = next((value for key, value in values.items() if "workspace.folder" in key.lower()), None)
        cwd = _cursor_workspace_root(folder_value) or project_root
        try:
            cwd.relative_to(project_root)
        except ValueError:
            continue
        for chat_payload in _cursor_chat_payloads(values):
            for conversation in _cursor_conversations(chat_payload):
                messages = _cursor_messages(conversation)
                if not messages:
                    continue
                session_id = str(conversation.get("id") or conversation.get("conversationId") or db_path.parent.name)
                turn = _new_turn(f"cursor-{session_id}", {"id": session_id, "cwd": str(cwd)}, "Cursor session", db_path)
                turn["thread_id"] = session_id
                turn["started_at"] = _cursor_time(messages[0])
                turn["ended_at"] = _cursor_time(messages[-1])
                for message in messages:
                    turn["messages"] += 1
                    role = str(message.get("role") or message.get("speaker") or "").lower()
                    if role == "assistant":
                        turn["agent_messages"] += 1
                    turn["model"] = turn.get("model") or _cursor_model(conversation, message)
                    usage = message.get("usage") if isinstance(message.get("usage"), dict) else None
                    if usage:
                        _record_claude_usage(turn, _local_usage_payload(usage))
                        turn["token_source"] = "cursor_state_vscdb_message_usage"
                    for call in _cursor_tool_calls(message):
                        tool_name = _cursor_tool_name(call)
                        _record_claude_tool(turn, _cursor_to_claude_tool(tool_name), _cursor_tool_input(call), project_root)
                payload = _turn_payload(
                    turn,
                    repo_id=repo_id,
                    repo_full_name=repo_full_name,
                    provider="Cursor",
                    agent_provider="Cursor",
                    source_provider="cursor_local",
                    source_record_type="cursor_state_vscdb",
                    agent_vendor="Cursor",
                    agent_product="Cursor",
                    agent_runtime="cursor",
                )
                if payload:
                    payloads.append(payload)
    return payloads


def _windsurf_session_files(windsurf_home: Path) -> list[Path]:
    candidates: set[Path] = set()
    for pattern in ("conversations/**/*.jsonl", "**/conversations/**/*.jsonl", "**/*.jsonl"):
        candidates.update(path for path in windsurf_home.glob(pattern) if path.is_file())
    return sorted(candidates)


def _windsurf_value(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value:
            return value
    workspace = record.get("workspace") if isinstance(record.get("workspace"), dict) else {}
    for key in keys:
        value = workspace.get(key)
        if value:
            return value
    return None


def _windsurf_message(record: dict[str, Any]) -> dict[str, Any]:
    message = record.get("message")
    return message if isinstance(message, dict) else record


def _windsurf_role(record: dict[str, Any], message: dict[str, Any]) -> str:
    return str(record.get("role") or record.get("type") or message.get("role") or message.get("type") or "").lower()


def _windsurf_tool_calls(record: dict[str, Any], message: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    sources = (record,) if message is record else (record, message)
    for source in sources:
        for key in ("tool_calls", "toolCalls", "tools"):
            value = source.get(key)
            if isinstance(value, list):
                calls.extend(item for item in value if isinstance(item, dict))
        content = source.get("content")
        if isinstance(content, list):
            calls.extend(item for item in content if isinstance(item, dict) and item.get("type") in {"tool_use", "tool_call", "tool-call"})
    if record.get("type") in {"tool_use", "tool_call", "tool-call"}:
        calls.append(record)
    return calls


def _windsurf_tool_name(call: dict[str, Any]) -> str:
    return str(call.get("name") or call.get("toolName") or call.get("tool") or call.get("type") or "tool")


def build_windsurf_agent_run_payloads(
    *,
    windsurf_home: Path | None = None,
    project_root: Path,
    repo_id: str | None = None,
    repo_full_name: str | None = None,
) -> list[dict[str, Any]]:
    windsurf_home = windsurf_home or Path.home() / ".codeium" / "windsurf"
    if not windsurf_home.exists():
        return []
    payloads: list[dict[str, Any]] = []
    project_root = project_root.expanduser().resolve()
    for source_file in _windsurf_session_files(windsurf_home):
        current: dict[str, Any] | None = None
        session_id = source_file.stem
        for line in source_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            record = _safe_json(line)
            if not record:
                continue
            message = _windsurf_message(record)
            session_id = str(record.get("sessionId") or record.get("conversationId") or record.get("chatId") or session_id)
            if current is None:
                current = _new_turn(f"windsurf-{session_id}-{source_file.stem}", {"id": session_id}, "Windsurf session", source_file)
                current["thread_id"] = session_id
            timestamp = _parse_timestamp(record.get("timestamp") or record.get("createdAt") or record.get("time"))
            if timestamp:
                current["started_at"] = current.get("started_at") or timestamp
                current["ended_at"] = timestamp
            current["cwd"] = str(_windsurf_value(record, "cwd", "workspaceRoot", "workspace_root", "projectPath", "path") or current.get("cwd") or "")
            current["model"] = str(record.get("model") or message.get("model") or current.get("model") or "") or current.get("model")
            current["permission_profile"] = str(record.get("permissionMode") or record.get("permissionProfile") or current.get("permission_profile") or "") or current.get("permission_profile")
            role = _windsurf_role(record, message)
            if role in {"user", "assistant"}:
                current["messages"] += 1
            if role == "assistant":
                current["agent_messages"] += 1
            usage = message.get("usage") if isinstance(message.get("usage"), dict) else record.get("usage")
            usage_payload = _local_usage_payload(usage)
            if usage_payload:
                _record_claude_usage(current, usage_payload)
                current["token_source"] = "windsurf_jsonl_message_usage"
            for call in _windsurf_tool_calls(record, message):
                _record_claude_tool(current, _cursor_to_claude_tool(_windsurf_tool_name(call)), _cursor_tool_input(call), project_root)
        if current and _belongs_to_project(current, project_root):
            payload = _turn_payload(
                current,
                repo_id=repo_id,
                repo_full_name=repo_full_name,
                provider="Windsurf",
                agent_provider="Windsurf",
                source_provider="windsurf_local",
                source_record_type="windsurf_jsonl",
                agent_vendor="Codeium",
                agent_product="Windsurf",
                agent_runtime="windsurf",
            )
            if payload:
                payloads.append(payload)
    return payloads


def build_copilot_agent_run_payloads(
    *,
    project_root: Path,
    repo_id: str | None = None,
    repo_full_name: str | None = None,
) -> list[dict[str, Any]]:
    """Copilot is ingested through GitHub APIs, not a stable local session store."""
    _ = (project_root, repo_id, repo_full_name)
    return []


__all__ = [
    "build_agent_run_payloads",
    "build_claude_agent_run_payloads",
    "build_copilot_agent_run_payloads",
    "build_cursor_agent_run_payloads",
    "build_windsurf_agent_run_payloads",
    "post_payload",
]
