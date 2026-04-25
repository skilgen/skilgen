from __future__ import annotations

import os
import sys
import time
import urllib.request

# Fire /skills/load once per Claude Code session (not on every file read).
# A session is identified by the CLAUDE_SESSION_ID env var (set by Claude Code).
# If that var is absent, we fall back to a 5-minute cooldown window using a
# timestamp file — so repeated short runs don't spam the API either.
_COOLDOWN_SECONDS = 300  # 5 minutes


def _session_lock_path(repo_id: str) -> str:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if session_id:
        tag = f"{repo_id}_{session_id}"
    else:
        tag = repo_id
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), f".skilgen_hook_{tag}")


def _already_fired(lock_path: str) -> bool:
    """Return True if we already fired during this session / cooldown window."""
    try:
        mtime = os.path.getmtime(lock_path)
        # If CLAUDE_SESSION_ID is set the lock file is session-scoped (always skip).
        # Without it, respect the cooldown window.
        if os.environ.get("CLAUDE_SESSION_ID"):
            return True
        return (time.time() - mtime) < _COOLDOWN_SECONDS
    except FileNotFoundError:
        return False


def _mark_fired(lock_path: str) -> None:
    try:
        with open(lock_path, "w") as fh:
            fh.write(str(time.time()))
    except OSError:
        pass


def main() -> None:
    api_key = os.environ.get("SKILLAYER_API_KEY")
    repo_id = os.environ.get("SKILLAYER_REPO_ID")
    if not api_key or not repo_id:
        return

    lock_path = _session_lock_path(repo_id)
    if _already_fired(lock_path):
        return

    url = f"https://api.skillayer.com/repos/{repo_id}/skills/load"
    req = urllib.request.Request(
        url,
        headers={"API-Key": api_key, "User-Agent": "claude-code/1.0 anthropic"},
    )
    try:
        urllib.request.urlopen(req, timeout=1).close()
    except Exception:
        pass

    _mark_fired(lock_path)


if __name__ == "__main__":
    main()
