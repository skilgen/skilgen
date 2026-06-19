"""skilgen check - scan a diff against org skills, exit 1 on violations."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_API_URL = "https://api.skillayer.com"
HOOK_TEMPLATE = """#!/bin/sh
skilgen check --staged
exit $?
"""


@dataclass(frozen=True)
class CheckConfig:
    api_key: str
    repo_id: str
    api_url: str = DEFAULT_API_URL


class CheckConfigError(ValueError):
    """Raised when skilgen check cannot find required configuration."""


def load_check_config(project_root: Path | None = None, *, api_url: str | None = None) -> CheckConfig:
    """Load check config from .skilgen/config.json, then environment variables."""
    root = (project_root or Path.cwd()).resolve()
    config_path = root / ".skilgen" / "config.json"
    config: dict[str, Any] = {}
    if config_path.exists():
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                config = raw
        except json.JSONDecodeError as exc:
            raise CheckConfigError(f"invalid config file {config_path}: {exc}") from exc

    api_key = _first_nonempty(
        config.get("api_key"),
        config.get("skillayer_api_key"),
        config.get("skilgen_api_key"),
        os.getenv("SKILGEN_API_KEY"),
        os.getenv("SKILLAYER_API_KEY"),
    )
    repo_id = _first_nonempty(
        config.get("repo_id"),
        config.get("skillayer_repo_id"),
        config.get("skilgen_repo_id"),
        os.getenv("SKILGEN_REPO_ID"),
        os.getenv("SKILLAYER_REPO_ID"),
    )
    resolved_api_url = _first_nonempty(
        api_url,
        config.get("api_url"),
        config.get("skillayer_api_url"),
        os.getenv("SKILGEN_API_URL"),
        os.getenv("SKILLAYER_API_URL"),
        DEFAULT_API_URL,
    )
    if not api_key:
        raise CheckConfigError("missing API key; set SKILGEN_API_KEY or .skilgen/config.json api_key")
    if not repo_id:
        raise CheckConfigError("missing repo id; set SKILGEN_REPO_ID or .skilgen/config.json repo_id")
    return CheckConfig(api_key=api_key, repo_id=repo_id, api_url=resolved_api_url.rstrip("/"))


def read_diff(*, diff_file: str | None = None, staged: bool = False, project_root: Path | None = None) -> str:
    """Read a diff from --staged, --diff, or stdin."""
    if staged and diff_file:
        raise CheckConfigError("choose either --staged or --diff, not both")
    if staged:
        root = (project_root or Path.cwd()).resolve()
        result = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or "git diff --cached failed"
            raise CheckConfigError(message)
        return result.stdout
    if diff_file:
        return Path(diff_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def post_check(config: CheckConfig, diff: str, *, timeout: int = 30) -> dict[str, Any]:
    """POST the diff to Skillayer's repo check endpoint."""
    body = json.dumps({"diff": diff}).encode("utf-8")
    request = Request(
        f"{config.api_url}/repos/{config.repo_id}/check",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": config.api_key,
            "API-Key": config.api_key,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise CheckConfigError(f"API returned {exc.code}: {detail}") from exc
    except URLError as exc:
        raise CheckConfigError(f"unable to reach API: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise CheckConfigError(f"API returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckConfigError("API returned an unexpected response")
    return payload


def render_check_result(payload: dict[str, Any]) -> tuple[str, int]:
    """Render the API response and return the intended process exit code."""
    violations = _items(payload.get("violations"))
    warnings = _items(payload.get("warnings"))
    lines: list[str] = []
    for item in violations:
        lines.append(_format_item("VIOLATION", item))
    for item in warnings:
        lines.append(_format_item("WARNING", item))
    if lines:
        lines.append("")
        lines.append(f"✗ {len(violations)} violation{'s' if len(violations) != 1 else ''}, {len(warnings)} warning{'s' if len(warnings) != 1 else ''}")
        return "\n".join(lines), 1 if violations else 0
    skills_checked = payload.get("skills_checked")
    suffix = f" ({skills_checked} skills checked)" if skills_checked is not None else ""
    return f"✓ No violations{suffix}", 0


def run_check_command(args: Any) -> int:
    """Command entrypoint used by skilgen.cli.main."""
    try:
        project_root = Path(getattr(args, "project_root", ".")).resolve()
        config = load_check_config(project_root, api_url=getattr(args, "api_url", None))
        diff = read_diff(
            diff_file=getattr(args, "diff", None),
            staged=bool(getattr(args, "staged", False)),
            project_root=project_root,
        )
        payload = post_check(config, diff)
        output, exit_code = render_check_result(payload)
        print(output)
        return exit_code
    except (OSError, CheckConfigError) as exc:
        print(f"skilgen check failed: {exc}", file=sys.stderr)
        return 2


def install_hook(project_root: Path | None = None) -> Path:
    """Install the Skilgen pre-commit hook into the current repo."""
    root = (project_root or Path.cwd()).resolve()
    git_dir = root / ".git"
    if not git_dir.exists():
        raise CheckConfigError(f"{root} is not a git repository")
    hook_path = git_dir / "hooks" / "pre-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(_hook_template(), encoding="utf-8")
    hook_path.chmod(0o755)
    return hook_path


def run_install_hook_command(args: Any) -> int:
    try:
        hook_path = install_hook(Path(getattr(args, "project_root", ".")).resolve())
    except (OSError, CheckConfigError) as exc:
        print(f"skilgen install-hook failed: {exc}", file=sys.stderr)
        return 2
    print(f"✓ Installed pre-commit hook at {hook_path}")
    return 0


def _hook_template() -> str:
    template_path = Path(__file__).resolve().parents[1] / "templates" / "pre-commit"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return HOOK_TEMPLATE


def _items(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _format_item(label: str, item: dict[str, Any]) -> str:
    file_path = str(item.get("file_path") or item.get("file") or "unknown")
    line_number = item.get("line_number", item.get("line", "?"))
    skill_name = str(item.get("skill_name") or item.get("skill") or "Skill")
    message = str(item.get("message") or item.get("explanation") or "")
    suggestion = str(item.get("suggestion") or item.get("fix_suggestion") or "")
    rendered = f"{label:<10} {file_path}:{line_number}  [{skill_name}]  {message}".rstrip()
    if suggestion:
        rendered = f"{rendered}\n           suggestion: {suggestion}"
    return rendered


def _first_nonempty(*values: object) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""
