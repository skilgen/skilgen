from __future__ import annotations

from pathlib import Path


WATCHER_SCRIPT = """#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import time


WATCHED_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".md"}
IGNORED_PARTS = {".git", ".skilgen", "skills", "node_modules", ".venv", "dist", "build"}


def snapshot(root: Path) -> dict[str, int]:
    files = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in WATCHED_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in rel.parts):
            continue
        files[rel.as_posix()] = path.stat().st_mtime_ns
    return files


def main() -> int:
    root = Path.cwd()
    previous = snapshot(root)
    while True:
        time.sleep(2)
        current = snapshot(root)
        if current != previous:
            subprocess.run(
                [sys.executable, "-m", "skilgen.cli.main", "deliver", "--project-root", str(root), "--target", "skills", "--skip-index"],
                text=True,
            )
            previous = snapshot(root)


if __name__ == "__main__":
    raise SystemExit(main())
"""


RULE_TEXT = """---
description: Keep generated Skilgen skills synchronized with source edits in Cursor.
globs:
  - "**/*"
alwaysApply: false
---

When source files change, run `.cursor/skilgen-watch.py` from the repository root to refresh `skills/**/SKILL.md` without touching generated dashboards.
"""


def write_cursor_watcher(project_root: str | Path) -> list[Path]:
    """Write a Cursor-friendly watcher script and rule note for Skilgen refreshes."""
    root = Path(project_root).resolve()
    cursor_dir = root / ".skilgen" / "hooks" / "cursor"
    rules_dir = cursor_dir / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)

    watcher = cursor_dir / "skilgen-watch.py"
    watcher.write_text(WATCHER_SCRIPT, encoding="utf-8")
    try:
        watcher.chmod(0o755)
    except OSError:
        pass

    rule = rules_dir / "skilgen-sync.mdc"
    rule.write_text(RULE_TEXT, encoding="utf-8")
    return [watcher, rule]
