"""
Run this as a background process while using Cursor:

  skilgen watch --repo-id <uuid>

Watches generated skills for file access and logs loads to Skillayer.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


def _skills_dir(repo_root: str | Path) -> Path:
    root = Path(repo_root).resolve()
    dot_skilgen = root / ".skilgen" / "skills"
    if dot_skilgen.exists():
        return dot_skilgen
    return root / "skills"


def watch_skills(
    repo_root: str,
    repo_id: str,
    api_key: str,
    api_url: str = "https://api.skillayer.com",
    poll_interval: int = 5,
    max_cycles: int | None = None,
) -> None:
    """Poll SKILL.md files for access time changes."""
    skills_dir = _skills_dir(repo_root)
    if not skills_dir.exists():
        print(f"No skills directory found at {skills_dir}")
        return

    access_times: dict[str, float] = {}

    def scan() -> None:
        for path in skills_dir.rglob("SKILL.md"):
            try:
                access_times[str(path)] = path.stat().st_atime
            except OSError:
                pass

    scan()
    print(f"👁  Watching {len(access_times)} skills for agent loads... (Ctrl+C to stop)")

    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        time.sleep(poll_interval)
        cycles += 1
        for path_text, last_atime in list(access_times.items()):
            path = Path(path_text)
            try:
                new_atime = path.stat().st_atime
            except OSError:
                continue
            if new_atime <= last_atime + 1:
                continue
            access_times[path_text] = new_atime
            from skilgen.core.analytics import log_skill_usage

            log_skill_usage(
                repo_root,
                [str(path)],
                event="loaded",
                context="cursor_watcher",
                session_id="cursor-watch",
            )
            skill_name = path.parent.name
            print(f"📖 Skill loaded: {skill_name}")
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "skilgen.cli.main",
                    "analytics",
                    "--upload",
                    "--repo-id",
                    repo_id,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={**os.environ, "SKILLAYER_API_KEY": api_key, "SKILLAYER_REPO_ID": repo_id, "SKILLAYER_API_URL": api_url},
            )
