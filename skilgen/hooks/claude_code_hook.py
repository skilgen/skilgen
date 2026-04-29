from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
from typing import Any
import urllib.request

# Fire /skills/load once per Claude Code session (not on every file read).
_COOLDOWN_SECONDS = 300
_EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
_BEFORE_CONTENT_CACHE: dict[tuple[str, str], str | None] = {}


def _session_id() -> str:
    return os.environ.get("CLAUDE_SESSION_ID") or "default"


def _session_lock_path(repo_id: str) -> str:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    tag = f"{repo_id}_{session_id}" if session_id else repo_id
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f".skilgen_hook_{tag}")


def _artifact_cache_path(session_id: str, file_path: str) -> Path:
    safe = "".join(ch if ch.isalnum() else "_" for ch in f"{session_id}_{file_path}")[:180]
    return Path(os.environ.get("TMPDIR", "/tmp")) / f".skilgen_before_{safe}.json"


def _already_fired(lock_path: str) -> bool:
    try:
        mtime = os.path.getmtime(lock_path)
        if os.environ.get("CLAUDE_SESSION_ID"):
            return True
        return (time.time() - mtime) < _COOLDOWN_SECONDS
    except FileNotFoundError:
        return False


def _mark_fired(lock_path: str) -> None:
    try:
        with open(lock_path, "w", encoding="utf-8") as fh:
            fh.write(str(time.time()))
    except OSError:
        pass


def _api_base() -> str:
    return os.environ.get("SKILLAYER_API_URL", "https://api.skillayer.com").rstrip("/")


def _post_json(url: str, api_key: str, payload: dict[str, Any]) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "claude-code/1.0 anthropic",
        },
        method="POST",
    )
    urllib.request.urlopen(req, timeout=2).close()


def _fire_skill_load(api_key: str, repo_id: str) -> None:
    lock_path = _session_lock_path(repo_id)
    if _already_fired(lock_path):
        return
    url = f"{_api_base()}/repos/{repo_id}/skills/load"
    req = urllib.request.Request(
        url,
        headers={"API-Key": api_key, "User-Agent": "claude-code/1.0 anthropic"},
    )
    try:
        urllib.request.urlopen(req, timeout=1).close()
    except Exception:
        pass
    _mark_fired(lock_path)


def _load_event(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _hook_event_name(event: dict[str, Any]) -> str:
    return str(event.get("hook_event_name") or event.get("event") or event.get("hookEventName") or "")


def _tool_name(event: dict[str, Any]) -> str:
    return str(event.get("tool_name") or event.get("toolName") or event.get("tool") or "")


def _tool_input(event: dict[str, Any]) -> dict[str, Any]:
    value = event.get("tool_input") or event.get("toolInput") or event.get("input") or {}
    return value if isinstance(value, dict) else {}


def _tool_response(event: dict[str, Any]) -> dict[str, Any]:
    value = event.get("tool_response") or event.get("toolResponse") or event.get("tool_result") or event.get("result") or {}
    return value if isinstance(value, dict) else {}


def _file_path_for_tool(tool: str, payload: dict[str, Any]) -> str | None:
    if tool == "Edit":
        return payload.get("file_path") or payload.get("path")
    if tool == "Write":
        return payload.get("file_path") or payload.get("path")
    if tool == "NotebookEdit":
        return payload.get("notebook_path") or payload.get("file_path") or payload.get("path")
    return None


def _repo_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("PWD") or os.getcwd())


def _absolute_path(file_path: str) -> Path:
    path = Path(file_path)
    return path if path.is_absolute() else _repo_root() / path


def _read_content(file_path: str) -> str | None:
    try:
        return _absolute_path(file_path).read_text(encoding="utf-8")
    except Exception:
        return None


def _capture_before(session_id: str, file_path: str) -> None:
    content = _read_content(file_path)
    key = (session_id, file_path)
    _BEFORE_CONTENT_CACHE[key] = content
    try:
        _artifact_cache_path(session_id, file_path).write_text(json.dumps({"content": content}), encoding="utf-8")
    except OSError:
        pass


def _pop_before(session_id: str, file_path: str) -> str | None:
    key = (session_id, file_path)
    if key in _BEFORE_CONTENT_CACHE:
        return _BEFORE_CONTENT_CACHE.pop(key)
    path = _artifact_cache_path(session_id, file_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        path.unlink(missing_ok=True)
        return payload.get("content")
    except Exception:
        return None


def _after_content_for_tool(tool: str, payload: dict[str, Any], response: dict[str, Any], file_path: str) -> str | None:
    if tool == "Write":
        return payload.get("content") or response.get("content") or _read_content(file_path)
    if tool == "Edit":
        return response.get("content") or response.get("after_content") or _read_content(file_path)
    if tool == "NotebookEdit":
        return response.get("content") or response.get("after_content") or payload.get("new_source") or _read_content(file_path)
    return None


def _handle_pre_tool(event: dict[str, Any]) -> None:
    tool = _tool_name(event)
    if tool not in _EDIT_TOOLS:
        return
    file_path = _file_path_for_tool(tool, _tool_input(event))
    if file_path:
        _capture_before(_session_id(), str(file_path))


def _handle_post_tool(event: dict[str, Any], api_key: str, repo_id: str) -> None:
    tool = _tool_name(event)
    if tool == "Read":
        _fire_skill_load(api_key, repo_id)
        return
    if tool not in _EDIT_TOOLS:
        return
    payload = _tool_input(event)
    response = _tool_response(event)
    file_path = _file_path_for_tool(tool, payload)
    if not file_path:
        return
    file_path = str(file_path)
    before_content = _pop_before(_session_id(), file_path)
    after_content = _after_content_for_tool(tool, payload, response, file_path)
    artifact_payload = {
        "session_id": _session_id(),
        "agent_runtime": "claude_code",
        "tool": tool,
        "file_path": file_path,
        "before_content": before_content,
        "after_content": after_content,
        "tool_input": payload,
        "tool_response": response,
    }
    try:
        _post_json(f"{_api_base()}/repos/{repo_id}/sessions/artifacts", api_key, artifact_payload)
    except Exception:
        pass


def main() -> None:
    api_key = os.environ.get("SKILLAYER_API_KEY")
    repo_id = os.environ.get("SKILLAYER_REPO_ID")
    if not api_key or not repo_id:
        return

    event = _load_event(sys.argv[1] if len(sys.argv) > 1 else None)
    if not event:
        _fire_skill_load(api_key, repo_id)
        return

    hook_event = _hook_event_name(event)
    if hook_event == "PreToolUse":
        _handle_pre_tool(event)
    elif hook_event == "PostToolUse":
        _handle_post_tool(event, api_key, repo_id)
    else:
        _fire_skill_load(api_key, repo_id)


if __name__ == "__main__":
    main()
