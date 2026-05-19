#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _parse_timestamp(value: object) -> str | None:
    return str(value) if isinstance(value, str) and value else None


def _safe_json(line: str) -> dict[str, Any] | None:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _thread_names(codex_home: Path) -> dict[str, str]:
    index = codex_home / "session_index.jsonl"
    names: dict[str, str] = {}
    if not index.exists():
        return names
    for line in index.read_text(encoding="utf-8", errors="ignore").splitlines():
        entry = _safe_json(line)
        if entry and entry.get("id"):
            names[str(entry["id"])] = str(entry.get("thread_name") or "Codex session")
    return names


def _session_files(codex_home: Path) -> list[Path]:
    sessions = codex_home / "sessions"
    if not sessions.exists():
        return []
    return sorted(sessions.glob("**/*.jsonl"))


def _claude_session_files(claude_home: Path) -> list[Path]:
    projects = claude_home / "projects"
    if not projects.exists():
        return []
    return sorted(projects.glob("**/*.jsonl"))


def _relative_path(path: str, project_root: Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(project_root).as_posix()
    except (OSError, ValueError):
        return path


def _belongs_to_project(turn: dict[str, Any], project_root: Path) -> bool:
    cwd = turn.get("cwd")
    if isinstance(cwd, str) and cwd:
        try:
            Path(cwd).resolve().relative_to(project_root)
            return True
        except (OSError, ValueError):
            pass
        root_name = project_root.resolve().name
        if root_name and root_name in Path(cwd).parts:
            return True
        # Local Claude Code worktrees often live beside the dashboard checkout
        # with a sibling folder name such as skilgen-upstream-work.
        if project_root.resolve().parent.name and project_root.resolve().parent.name in Path(cwd).parts:
            return True
    for path in (turn.get("file_targets") or {}).keys():
        candidate = Path(str(path))
        if not candidate.is_absolute():
            return True
        try:
            candidate.resolve().relative_to(project_root)
            return True
        except (OSError, ValueError):
            continue
    return False


def _new_turn(turn_id: str, session_meta: dict[str, Any], thread_name: str, source_file: Path) -> dict[str, Any]:
    return {
        "turn_id": turn_id,
        "thread_id": str(session_meta.get("id") or ""),
        "thread_name": thread_name,
        "source_file": source_file.as_posix(),
        "started_at": None,
        "ended_at": None,
        "cwd": session_meta.get("cwd"),
        "model": None,
        "reasoning_effort": None,
        "approval_policy": None,
        "sandbox_policy": None,
        "permission_profile": None,
        "messages": 0,
        "agent_messages": 0,
        "tool_calls": [],
        "mcp_tools": [],
        "file_targets": {},
        "explored_file_paths": set(),
        "activity_details": {
            "edited_files": [],
            "explored_files": [],
            "searches": [],
            "lists": [],
            "commands": [],
            "tools": [],
        },
        "activity_metrics": {
            "edited_files": 0,
            "explored_files": 0,
            "searches": 0,
            "lists": 0,
            "commands": 0,
            "tool_calls": 0,
            "mcp_tools": 0,
        },
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_total": 0,
        "tokens_cached_input": 0,
        "tokens_reasoning_output": 0,
        "tokens_base_input": 0,
        "tokens_cache_creation_input": 0,
        "tokens_cache_creation_5m_input": 0,
        "tokens_cache_creation_1h_input": 0,
        "tokens_cache_read_input": 0,
        "token_source": None,
        "cost_usd": None,
    }


def _new_claude_turn(session_id: str, source_file: Path) -> dict[str, Any]:
    turn = _new_turn(f"claude-{session_id}-{source_file.stem}", {"id": session_id}, "Claude Code session", source_file)
    turn["thread_id"] = session_id
    return turn


def _reasoning_mode(effort: object, model: object) -> str:
    normalized = str(effort or "").strip().lower()
    model_name = str(model or "").strip().lower()
    if normalized in {"minimal", "low"} or "mini" in model_name or "fast" in model_name:
        return "fast"
    if normalized in {"high", "xhigh", "extra_high", "extra-high"}:
        return normalized.replace("_", "-")
    return "normal"


def _tool_permissions(turn: dict[str, Any]) -> list[str]:
    permissions = set(str(tool) for tool in (turn.get("tool_calls") or []) if tool)
    if turn.get("file_targets"):
        permissions.add("filesystem.write")
        permissions.add("apply_patch")
    if any("exec" in tool or "command" in tool for tool in permissions):
        permissions.add("shell")
    return sorted(permissions)


def _access_scope(turn: dict[str, Any]) -> tuple[str, bool]:
    sandbox = turn.get("sandbox_policy")
    sandbox_type = sandbox.get("type") if isinstance(sandbox, dict) else str(sandbox or "")
    if str(sandbox_type).lower() == "danger-full-access":
        return "full-access", True
    permission = str(turn.get("permission_profile") or "").strip().lower()
    if permission in {"bypasspermissions", "bypass-permissions", "full-access", "danger-full-access"}:
        return "full-access", True
    if permission in {"acceptedits", "accept-edits"}:
        return "workspace-write", False
    if turn.get("file_targets"):
        return "workspace-write", False
    if _tool_permissions(turn):
        return "tool-permission", False
    return "read-only", False


def _record_tokens(turn: dict[str, Any], payload: dict[str, Any]) -> None:
    usage = payload.get("info")
    if not isinstance(usage, dict):
        return
    last = usage.get("last_token_usage")
    if not isinstance(last, dict):
        return
    turn["tokens_input"] += int(last.get("input_tokens") or 0)
    turn["tokens_output"] += int(last.get("output_tokens") or 0)
    turn["tokens_total"] += int(last.get("total_tokens") or 0)
    turn["tokens_cached_input"] += int(last.get("cached_input_tokens") or 0)
    turn["tokens_reasoning_output"] += int(last.get("reasoning_output_tokens") or 0)
    turn["token_source"] = "codex_jsonl_last_token_usage"


def _record_claude_usage(turn: dict[str, Any], usage: object) -> None:
    if not isinstance(usage, dict):
        return
    input_tokens = int(usage.get("input_tokens") or 0)
    cache_creation = int(usage.get("cache_creation_input_tokens") or 0)
    cache_read = int(usage.get("cache_read_input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    cache_creation_detail = usage.get("cache_creation") if isinstance(usage.get("cache_creation"), dict) else {}
    cache_creation_5m = int(cache_creation_detail.get("ephemeral_5m_input_tokens") or 0)
    cache_creation_1h = int(cache_creation_detail.get("ephemeral_1h_input_tokens") or 0)
    turn["tokens_input"] += input_tokens + cache_creation + cache_read
    turn["tokens_output"] += output_tokens
    turn["tokens_total"] += input_tokens + cache_creation + cache_read + output_tokens
    turn["tokens_base_input"] += input_tokens
    turn["tokens_cache_creation_input"] += cache_creation
    turn["tokens_cache_creation_5m_input"] += cache_creation_5m
    turn["tokens_cache_creation_1h_input"] += cache_creation_1h
    turn["tokens_cache_read_input"] += cache_read
    turn["token_source"] = "claude_code_jsonl_message_usage"
    if usage.get("speed") and not turn.get("reasoning_effort"):
        turn["reasoning_effort"] = str(usage.get("speed"))


def _openai_rates(model: str) -> tuple[float, float, float]:
    normalized = model.lower()
    if "gpt-5.5" in normalized:
        return (5.0, 0.5, 30.0)
    if "gpt-5.4-mini" in normalized or "gpt-5.4 mini" in normalized:
        return (0.75, 0.075, 4.5)
    if "gpt-5.4" in normalized:
        return (2.5, 0.25, 15.0)
    if "mini" in normalized or "fast" in normalized:
        return (0.25, 0.025, 1.25)
    return (1.25, 0.125, 10.0)


def _claude_base_rates(model: str) -> tuple[float, float]:
    normalized = model.lower()
    if "haiku-4-5" in normalized or "haiku 4.5" in normalized:
        return (1.0, 5.0)
    if "sonnet" in normalized:
        return (3.0, 15.0)
    if "opus-4-7" in normalized or "opus-4-6" in normalized or "opus-4-5" in normalized or "opus 4.7" in normalized or "opus 4.6" in normalized or "opus 4.5" in normalized:
        return (5.0, 25.0)
    if "opus" in normalized:
        return (15.0, 75.0)
    return (3.0, 15.0)


def _estimated_cost_usd(
    model: str | None,
    input_tokens: int,
    output_tokens: int,
    *,
    provider: str | None = None,
    cached_input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
    cache_creation_5m_input_tokens: int = 0,
    cache_creation_1h_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
    base_input_tokens: int = 0,
) -> float | None:
    if input_tokens <= 0 and output_tokens <= 0 and cache_creation_input_tokens <= 0 and cache_read_input_tokens <= 0:
        return None
    normalized = str(model or "").lower()
    provider_key = str(provider or "").lower()
    if "claude" in provider_key or "claude" in normalized:
        input_rate, output_rate = _claude_base_rates(normalized)
        cache_5m = cache_creation_5m_input_tokens
        cache_1h = cache_creation_1h_input_tokens
        unattributed_cache_creation = max(0, cache_creation_input_tokens - cache_5m - cache_1h)
        billable_base_input = base_input_tokens if base_input_tokens > 0 else max(0, input_tokens - cache_creation_input_tokens - cache_read_input_tokens)
        return round(
            (billable_base_input / 1_000_000) * input_rate
            + (cache_5m / 1_000_000) * (input_rate * 1.25)
            + (cache_1h / 1_000_000) * (input_rate * 2.0)
            + (unattributed_cache_creation / 1_000_000) * (input_rate * 1.25)
            + (cache_read_input_tokens / 1_000_000) * (input_rate * 0.1)
            + (output_tokens / 1_000_000) * output_rate,
            6,
        )
    input_rate, cached_input_rate, output_rate = _openai_rates(normalized)
    cached = max(0, cached_input_tokens)
    uncached_input = max(0, input_tokens - cached)
    return round((uncached_input / 1_000_000) * input_rate + (cached / 1_000_000) * cached_input_rate + (output_tokens / 1_000_000) * output_rate, 6)


def _record_patch_files(turn: dict[str, Any], payload: dict[str, Any], project_root: Path) -> None:
    changes = payload.get("changes")
    if not isinstance(changes, dict):
        return
    for file_path, change in changes.items():
        if not isinstance(file_path, str):
            continue
        relative = _relative_path(file_path, project_root)
        diff = change.get("unified_diff") if isinstance(change, dict) else None
        digest_input = str(diff or change or file_path).encode("utf-8")
        turn["file_targets"][relative] = {
            "file_path": relative,
            "tool": "apply_patch",
            "after_hash": hashlib.sha256(digest_input).hexdigest(),
        }
    metrics = turn.get("activity_metrics")
    if isinstance(metrics, dict):
        metrics["edited_files"] = len(turn.get("file_targets") or {})
    details = turn.get("activity_details")
    if isinstance(details, dict):
        details["edited_files"] = sorted((turn.get("file_targets") or {}).keys())


def _record_edited_file(turn: dict[str, Any], file_path: object, tool: str, project_root: Path) -> None:
    if not isinstance(file_path, str) or not file_path:
        return
    relative = _relative_path(file_path, project_root)
    digest_input = f"{tool}:{relative}".encode("utf-8")
    turn["file_targets"][relative] = {
        "file_path": relative,
        "tool": tool,
        "after_hash": hashlib.sha256(digest_input).hexdigest(),
    }
    metrics = turn.get("activity_metrics")
    if isinstance(metrics, dict):
        metrics["edited_files"] = len(turn.get("file_targets") or {})
    details = turn.get("activity_details")
    if isinstance(details, dict):
        details["edited_files"] = sorted((turn.get("file_targets") or {}).keys())


def _record_explored_file(turn: dict[str, Any], file_path: object, project_root: Path) -> None:
    if not isinstance(file_path, str) or not file_path:
        return
    explored = turn.get("explored_file_paths")
    if isinstance(explored, set):
        explored.add(_relative_path(file_path, project_root))
    metrics = turn.get("activity_metrics")
    if isinstance(metrics, dict):
        metrics["explored_files"] = len(explored or [])
    details = turn.get("activity_details")
    if isinstance(details, dict):
        details["explored_files"] = sorted(explored or [])


def _redact_command(command: str) -> str:
    sanitized = command.strip()
    sanitized = re.sub(r"(?i)(api[_-]?key|token|secret|password|authorization)(\\s*=\\s*|\\s+)[^\\s]+", r"\\1\\2[redacted]", sanitized)
    sanitized = re.sub(r"(?i)(bearer\\s+)[a-z0-9._~+/=-]+", r"\\1[redacted]", sanitized)
    return sanitized[:240] + ("..." if len(sanitized) > 240 else "")


def _append_detail(turn: dict[str, Any], key: str, value: str) -> None:
    details = turn.get("activity_details")
    if not isinstance(details, dict) or not value:
        return
    items = details.setdefault(key, [])
    if isinstance(items, list) and value not in items:
        items.append(value)


def _extract_command(payload: dict[str, Any]) -> str:
    raw = payload.get("arguments")
    if isinstance(raw, str) and raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}
        if isinstance(parsed, dict) and isinstance(parsed.get("cmd"), str):
            return parsed["cmd"]
    if isinstance(raw, dict) and isinstance(raw.get("cmd"), str):
        return raw["cmd"]
    return ""


def _command_words(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _first_command(words: list[str]) -> str:
    if not words:
        return ""
    if words[0] in {"cd", "env"}:
        for index, word in enumerate(words[1:], start=1):
            if word in {"&&", ";"} and index + 1 < len(words):
                return words[index + 1]
    return Path(words[0]).name


def _record_command_metrics(turn: dict[str, Any], payload: dict[str, Any], project_root: Path) -> None:
    command = _extract_command(payload)
    if not command:
        return
    words = _command_words(command)
    executable = _first_command(words)
    metrics = turn.get("activity_metrics")
    if not isinstance(metrics, dict):
        return
    metrics["commands"] = int(metrics.get("commands") or 0) + 1
    command_summary = _redact_command(command)
    _append_detail(turn, "commands", command_summary)
    command_text = " ".join(words)
    is_file_listing = executable == "rg" and "--files" in words
    if (not is_file_listing and executable in {"rg", "grep", "ag", "ack"}) or " git grep " in f" {command_text} ":
        metrics["searches"] = int(metrics.get("searches") or 0) + 1
        _append_detail(turn, "searches", command_summary)
    if executable in {"ls", "tree"} or (executable == "find" and "-maxdepth" in words) or is_file_listing:
        metrics["lists"] = int(metrics.get("lists") or 0) + 1
        _append_detail(turn, "lists", command_summary)
    if executable in {"cat", "sed", "nl", "head", "tail", "less", "more"}:
        explored = turn.get("explored_file_paths")
        if isinstance(explored, set):
            for word in words[1:]:
                if word.startswith("-") or word in {"|", ">", ">>", "&&", ";"}:
                    continue
                if "/" not in word and "." not in Path(word).name:
                    continue
                explored.add(_relative_path(word, project_root))
            metrics["explored_files"] = len(explored)
            details = turn.get("activity_details")
            if isinstance(details, dict):
                details["explored_files"] = sorted(explored)


def _record_tool_call(turn: dict[str, Any], payload: dict[str, Any]) -> None:
    name = payload.get("name")
    if not isinstance(name, str) or not name:
        return
    turn["tool_calls"].append(name)
    _append_detail(turn, "tools", name)
    namespace = payload.get("namespace")
    if isinstance(namespace, str) and namespace.startswith("mcp__"):
        turn["mcp_tools"].append(name)
    metrics = turn.get("activity_metrics")
    if isinstance(metrics, dict):
        metrics["tool_calls"] = len(turn.get("tool_calls") or [])
        metrics["mcp_tools"] = len(turn.get("mcp_tools") or [])


def _turn_payload(
    turn: dict[str, Any],
    *,
    repo_id: str | None,
    repo_full_name: str | None,
    provider: str = "Codex",
    agent_provider: str = "Codex Desktop",
    source_provider: str = "codex_desktop",
    source_record_type: str = "codex_desktop_jsonl",
    agent_vendor: str = "OpenAI",
    agent_product: str = "Codex Desktop",
    agent_runtime: str = "codex_cli",
) -> dict[str, Any] | None:
    if not turn.get("started_at"):
        return None
    tool_permissions = _tool_permissions(turn)
    access_scope, full_access = _access_scope(turn)
    reasoning_effort = turn.get("reasoning_effort")
    reasoning_mode = _reasoning_mode(reasoning_effort, turn.get("model"))
    cost_usd = _estimated_cost_usd(
        str(turn.get("model") or ""),
        int(turn.get("tokens_input") or 0),
        int(turn.get("tokens_output") or 0),
        provider=provider,
        cached_input_tokens=int(turn.get("tokens_cached_input") or 0),
        cache_creation_input_tokens=int(turn.get("tokens_cache_creation_input") or 0),
        cache_creation_5m_input_tokens=int(turn.get("tokens_cache_creation_5m_input") or 0),
        cache_creation_1h_input_tokens=int(turn.get("tokens_cache_creation_1h_input") or 0),
        cache_read_input_tokens=int(turn.get("tokens_cache_read_input") or 0),
        base_input_tokens=int(turn.get("tokens_base_input") or 0),
    )
    metadata = {
        "provider": provider,
        "agent_provider": agent_provider,
        "source_provider": source_provider,
        "source_record_types": [source_record_type],
        "codex_thread_id": turn.get("thread_id"),
        "codex_turn_id": turn.get("turn_id"),
        "codex_thread_name": turn.get("thread_name"),
        "codex_session_file": turn.get("source_file"),
        "provider_session_id": turn.get("thread_id"),
        "provider_run_id": turn.get("turn_id"),
        "provider_session_file": turn.get("source_file"),
        "cwd": turn.get("cwd"),
        "model": turn.get("model"),
        "reasoning_tier": reasoning_effort,
        "reasoning_effort": reasoning_effort,
        "reasoning_mode": reasoning_mode,
        "approval_policy": turn.get("approval_policy"),
        "sandbox_policy": turn.get("sandbox_policy"),
        "permission_profile": turn.get("permission_profile"),
        "access_scope": access_scope,
        "full_access": full_access,
        "task_type": "coding-agent-session",
        "message_count": int(turn.get("messages") or 0),
        "agent_message_count": int(turn.get("agent_messages") or 0),
        "tool_calls": sorted(set(turn.get("tool_calls") or [])),
        "tool_permissions": tool_permissions,
        "mcp_tools": sorted(set(turn.get("mcp_tools") or [])),
        "file_targets": sorted((turn.get("file_targets") or {}).keys()),
        "activity_metrics": turn.get("activity_metrics"),
        "activity_details": turn.get("activity_details"),
        "edited_files": int((turn.get("activity_metrics") or {}).get("edited_files") or 0),
        "explored_files": int((turn.get("activity_metrics") or {}).get("explored_files") or 0),
        "searches": int((turn.get("activity_metrics") or {}).get("searches") or 0),
        "lists": int((turn.get("activity_metrics") or {}).get("lists") or 0),
        "commands": int((turn.get("activity_metrics") or {}).get("commands") or 0),
        "tokens_input": int(turn.get("tokens_input") or 0),
        "tokens_output": int(turn.get("tokens_output") or 0),
        "tokens_total": int(turn.get("tokens_total") or 0),
        "tokens_cached_input": int(turn.get("tokens_cached_input") or 0),
        "tokens_reasoning_output": int(turn.get("tokens_reasoning_output") or 0),
        "tokens_base_input": int(turn.get("tokens_base_input") or 0),
        "tokens_cache_creation_input": int(turn.get("tokens_cache_creation_input") or 0),
        "tokens_cache_creation_5m_input": int(turn.get("tokens_cache_creation_5m_input") or 0),
        "tokens_cache_creation_1h_input": int(turn.get("tokens_cache_creation_1h_input") or 0),
        "tokens_cache_read_input": int(turn.get("tokens_cache_read_input") or 0),
        "token_source": turn.get("token_source"),
        "cost_usd": cost_usd,
        "cost_source": "estimated_from_provider_token_usage" if cost_usd is not None else None,
        "cost_estimate": cost_usd is not None,
        "content_retention": "metadata-only",
        "redaction_state": "raw-content-dropped",
    }
    metadata = {key: value for key, value in metadata.items() if value is not None and value != "" and value != 0 and value != []}
    payload: dict[str, Any] = {
        "spec_version": "0",
        "session_id": str(turn["turn_id"]),
        "agent": {"vendor": agent_vendor, "product": agent_product, "runtime": agent_runtime},
        "repo_id": repo_id,
        "repo": {"full_name": repo_full_name} if repo_full_name else None,
        "user": {"login": os.getenv("USER") or f"local-{agent_runtime}"},
        "started_at": turn["started_at"],
        "ended_at": turn.get("ended_at"),
        "code_artifacts": list((turn.get("file_targets") or {}).values()),
        "outcome": "success" if turn.get("ended_at") else "unknown",
        "metadata": metadata,
    }
    return {key: value for key, value in payload.items() if value is not None}


def build_agent_run_payloads(
    *,
    codex_home: Path,
    project_root: Path,
    repo_id: str | None = None,
    repo_full_name: str | None = None,
) -> list[dict[str, Any]]:
    project_root = project_root.resolve()
    names = _thread_names(codex_home)
    payloads: list[dict[str, Any]] = []
    for source_file in _session_files(codex_home):
        session_meta: dict[str, Any] = {}
        thread_name = "Codex session"
        current: dict[str, Any] | None = None
        for line in source_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            record = _safe_json(line)
            if not record:
                continue
            timestamp = _parse_timestamp(record.get("timestamp"))
            record_type = record.get("type")
            payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
            if record_type == "session_meta":
                session_meta = payload
                thread_name = names.get(str(session_meta.get("id") or ""), "Codex session")
                continue
            event_type = payload.get("type")
            if event_type == "task_started" and payload.get("turn_id"):
                if current:
                    built = _turn_payload(current, repo_id=repo_id, repo_full_name=repo_full_name) if _belongs_to_project(current, project_root) else None
                    if built:
                        payloads.append(built)
                current = _new_turn(str(payload["turn_id"]), session_meta, thread_name, source_file)
                current["started_at"] = timestamp
                continue
            if current is None:
                continue
            if record_type == "turn_context":
                current["cwd"] = payload.get("cwd") or current.get("cwd")
                current["model"] = payload.get("model") or current.get("model")
                current["reasoning_effort"] = payload.get("effort") or current.get("reasoning_effort")
                current["approval_policy"] = payload.get("approval_policy") or current.get("approval_policy")
                current["sandbox_policy"] = payload.get("sandbox_policy") or current.get("sandbox_policy")
                current["permission_profile"] = payload.get("permission_profile") or current.get("permission_profile")
            elif event_type == "user_message":
                current["messages"] += 1
            elif event_type == "agent_message":
                current["messages"] += 1
                current["agent_messages"] += 1
            elif event_type == "token_count":
                _record_tokens(current, payload)
            elif event_type == "patch_apply_end":
                _record_patch_files(current, payload, project_root)
            elif record_type == "response_item" and payload.get("type") == "function_call":
                _record_tool_call(current, payload)
                if payload.get("name") == "exec_command":
                    _record_command_metrics(current, payload, project_root)
            if event_type == "task_complete":
                current["ended_at"] = timestamp
                built = _turn_payload(current, repo_id=repo_id, repo_full_name=repo_full_name) if _belongs_to_project(current, project_root) else None
                if built:
                    payloads.append(built)
                current = None
        if current:
            built = _turn_payload(current, repo_id=repo_id, repo_full_name=repo_full_name) if _belongs_to_project(current, project_root) else None
            if built:
                payloads.append(built)
    return payloads


def _claude_tool_summary(name: str, tool_input: dict[str, Any]) -> str:
    if name == "Bash":
        return _redact_command(str(tool_input.get("command") or ""))
    if name in {"Read", "Edit", "Write", "MultiEdit"}:
        return str(tool_input.get("file_path") or tool_input.get("path") or "")
    if name == "NotebookEdit":
        return str(tool_input.get("notebook_path") or tool_input.get("file_path") or "")
    if name in {"Grep", "Glob", "LS"}:
        bits = [str(tool_input.get(key) or "") for key in ("pattern", "path", "glob") if tool_input.get(key)]
        return " ".join([name, *bits]).strip()
    return name


def _record_claude_tool(turn: dict[str, Any], name: str, tool_input: object, project_root: Path) -> None:
    payload = {"name": name, "namespace": name if name.startswith("mcp__") else ""}
    _record_tool_call(turn, payload)
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    metrics = turn.get("activity_metrics")
    if not isinstance(metrics, dict):
        return

    if name == "Bash":
        command = str(tool_input.get("command") or "")
        _record_command_metrics(turn, {"arguments": {"cmd": command}}, project_root)
        return
    if name == "Read":
        _record_explored_file(turn, tool_input.get("file_path"), project_root)
        return
    if name in {"Edit", "Write", "MultiEdit"}:
        _record_edited_file(turn, tool_input.get("file_path") or tool_input.get("path"), name, project_root)
        return
    if name == "NotebookEdit":
        _record_edited_file(turn, tool_input.get("notebook_path") or tool_input.get("file_path"), name, project_root)
        return
    if name == "Grep":
        metrics["searches"] = int(metrics.get("searches") or 0) + 1
        _append_detail(turn, "searches", _claude_tool_summary(name, tool_input))
        return
    if name in {"Glob", "LS"}:
        metrics["lists"] = int(metrics.get("lists") or 0) + 1
        _append_detail(turn, "lists", _claude_tool_summary(name, tool_input))


def build_claude_agent_run_payloads(
    *,
    claude_home: Path,
    project_root: Path,
    repo_id: str | None = None,
    repo_full_name: str | None = None,
) -> list[dict[str, Any]]:
    project_root = project_root.resolve()
    payloads: list[dict[str, Any]] = []
    for source_file in _claude_session_files(claude_home):
        current: dict[str, Any] | None = None
        for line in source_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            record = _safe_json(line)
            if not record:
                continue
            session_id = str(record.get("sessionId") or source_file.stem)
            if current is None:
                current = _new_claude_turn(session_id, source_file)
            timestamp = _parse_timestamp(record.get("timestamp"))
            if timestamp:
                current["started_at"] = current.get("started_at") or timestamp
                current["ended_at"] = timestamp
            current["cwd"] = record.get("cwd") or current.get("cwd")
            current["permission_profile"] = record.get("permissionMode") or current.get("permission_profile")
            message = record.get("message") if isinstance(record.get("message"), dict) else {}
            if record.get("type") in {"user", "assistant"}:
                current["messages"] += 1
            if record.get("type") == "assistant":
                current["agent_messages"] += 1
                current["model"] = message.get("model") or current.get("model")
                _record_claude_usage(current, message.get("usage"))
            content = message.get("content")
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                name = str(item.get("name") or "")
                if name:
                    _record_claude_tool(current, name, item.get("input"), project_root)
        if current:
            built = (
                _turn_payload(
                    current,
                    repo_id=repo_id,
                    repo_full_name=repo_full_name,
                    provider="Claude Code",
                    agent_provider="Claude Code",
                    source_provider="claude_code",
                    source_record_type="claude_code_jsonl",
                    agent_vendor="Anthropic",
                    agent_product="Claude Code",
                    agent_runtime="claude_code",
                )
                if _belongs_to_project(current, project_root)
                else None
            )
            if built:
                payloads.append(built)
    return payloads


def post_payload(api_url: str, org_id: str, payload: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        f"{api_url.rstrip('/')}/orgs/{org_id}/agent-runs",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Import local coding-agent session metadata into Skillayer AgentRun telemetry.")
    parser.add_argument("--codex-home", default=str(Path.home() / ".codex"))
    parser.add_argument("--claude-home", default=str(Path.home() / ".claude"))
    parser.add_argument("--providers", default=os.getenv("SKILLAYER_AGENT_IMPORT_PROVIDERS", "codex,claude"), help="Comma-separated providers: codex, claude, or all.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--api-url", default=os.getenv("SKILLAYER_API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--org-id", default=os.getenv("SKILLAYER_ORG_ID", "org_skilgen"))
    parser.add_argument("--repo-id", default=os.getenv("SKILLAYER_REPO_ID"))
    parser.add_argument("--repo-full-name", default=os.getenv("SKILLAYER_REPO_FULL_NAME", "ravichanduummadisetti/skilgen"))
    parser.add_argument("--token", default=os.getenv("SKILLAYER_API_KEY"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    providers = {item.strip().lower() for item in str(args.providers).split(",") if item.strip()}
    if "all" in providers:
        providers = {"codex", "claude"}
    payloads: list[dict[str, Any]] = []
    if "codex" in providers:
        payloads.extend(
            build_agent_run_payloads(
                codex_home=Path(args.codex_home).expanduser(),
                project_root=Path(args.project_root),
                repo_id=args.repo_id,
                repo_full_name=args.repo_full_name,
            )
        )
    if "claude" in providers or "claude_code" in providers or "claude-code" in providers:
        payloads.extend(
            build_claude_agent_run_payloads(
                claude_home=Path(args.claude_home).expanduser(),
                project_root=Path(args.project_root),
                repo_id=args.repo_id,
                repo_full_name=args.repo_full_name,
            )
        )
    posted = 0
    failed = 0
    for payload in payloads:
        if args.dry_run:
            posted += 1
            continue
        try:
            post_payload(args.api_url, args.org_id, payload, args.token)
            posted += 1
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            failed += 1
            print(f"failed {payload.get('session_id')}: {exc}")
    print(json.dumps({"discovered": len(payloads), "posted": posted, "failed": failed}, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
