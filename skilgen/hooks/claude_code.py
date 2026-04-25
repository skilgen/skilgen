from __future__ import annotations

from pathlib import Path


HOOK_SCRIPT = """#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys


def main() -> int:
    root = Path.cwd()
    skills = root / "skills"
    if not skills.exists():
        return 0
    result = subprocess.run(
        [sys.executable, "-m", "skilgen.cli.main", "deliver", "--project-root", str(root), "--target", "skills", "--skip-index"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
"""


SETTINGS_SNIPPET = """{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/skilgen-sync.py"
          }
        ]
      }
    ]
  }
}
"""


def write_claude_code_hook(project_root: str | Path) -> list[Path]:
    """Write a Claude Code hook that refreshes repo-local skills after edits."""
    root = Path(project_root).resolve()
    hook_dir = root / ".skilgen" / "hooks" / "claude-code"
    hook_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hook_dir / "skilgen-sync.py"
    hook_path.write_text(HOOK_SCRIPT, encoding="utf-8")
    try:
        hook_path.chmod(0o755)
    except OSError:
        pass

    settings_example = hook_dir / "skilgen-hooks.example.json"
    settings_example.write_text(SETTINGS_SNIPPET, encoding="utf-8")
    return [hook_path, settings_example]
