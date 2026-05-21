from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .local_importer import build_agent_run_payloads, build_claude_agent_run_payloads, build_cursor_agent_run_payloads, post_payload

DEFAULT_API_URL = "https://api.skillayer.com"
DEFAULT_PROVIDERS = ("codex", "claude")
CONFIG_PATH = Path.home() / ".skillayer" / "agent.json"
STATE_PATH = Path.home() / ".skillayer" / "state.json"


@dataclass(frozen=True)
class ProjectRoot:
    path: Path
    repo_id: str | None = None
    repo_full_name: str | None = None


@dataclass(frozen=True)
class AgentConfig:
    api_url: str
    org_id: str
    api_key: str | None
    providers: tuple[str, ...]
    project_roots: tuple[ProjectRoot, ...]
    codex_home: Path
    claude_home: Path
    cursor_home: Path
    config_path: Path
    state_path: Path


def _json_load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: invalid Skillayer agent config {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"error: invalid Skillayer agent config {path}: expected object")
    return value


def _providers(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        raw = [item.strip().lower() for item in value.split(",") if item.strip()]
    elif isinstance(value, list):
        raw = [str(item).strip().lower() for item in value if str(item).strip()]
    else:
        raw = list(DEFAULT_PROVIDERS)
    normalized = {"claude" if item in {"claude_code", "claude-code"} else item for item in raw}
    if "all" in normalized:
        normalized = set(DEFAULT_PROVIDERS)
    supported = {"codex", "claude", "cursor"}
    unsupported = sorted(normalized - supported)
    if unsupported:
        raise SystemExit(f"error: unsupported provider(s): {', '.join(unsupported)}")
    return tuple(sorted(normalized)) or DEFAULT_PROVIDERS


def _project_roots(config: dict[str, Any], args: argparse.Namespace) -> tuple[ProjectRoot, ...]:
    if getattr(args, "project_root", None):
        return (
            ProjectRoot(
                path=Path(args.project_root).expanduser().resolve(),
                repo_id=getattr(args, "repo_id", None) or os.getenv("SKILLAYER_REPO_ID"),
                repo_full_name=getattr(args, "repo_full_name", None) or os.getenv("SKILLAYER_REPO_FULL_NAME"),
            ),
        )
    configured = config.get("project_roots")
    roots: list[ProjectRoot] = []
    if isinstance(configured, list):
        for item in configured:
            if isinstance(item, dict) and item.get("path"):
                roots.append(
                    ProjectRoot(
                        path=Path(str(item["path"])).expanduser().resolve(),
                        repo_id=str(item["repo_id"]) if item.get("repo_id") else None,
                        repo_full_name=str(item["repo_full_name"]) if item.get("repo_full_name") else None,
                    )
                )
            elif isinstance(item, str) and item:
                roots.append(ProjectRoot(path=Path(item).expanduser().resolve()))
    if roots:
        return tuple(roots)
    return (
        ProjectRoot(
            path=Path.cwd().resolve(),
            repo_id=os.getenv("SKILLAYER_REPO_ID"),
            repo_full_name=os.getenv("SKILLAYER_REPO_FULL_NAME"),
        ),
    )


def load_agent_config(args: argparse.Namespace) -> AgentConfig:
    config_path = Path(getattr(args, "config", None) or os.getenv("SKILLAYER_AGENT_CONFIG") or CONFIG_PATH).expanduser()
    state_path = Path(getattr(args, "state", None) or os.getenv("SKILLAYER_AGENT_STATE") or STATE_PATH).expanduser()
    config = _json_load(config_path)
    providers_value: object = getattr(args, "providers", None) or os.getenv("SKILLAYER_AGENT_IMPORT_PROVIDERS") or config.get("providers")
    return AgentConfig(
        api_url=str(getattr(args, "api_url", None) or os.getenv("SKILLAYER_API_URL") or config.get("api_url") or DEFAULT_API_URL),
        org_id=str(getattr(args, "org_id", None) or os.getenv("SKILLAYER_ORG_ID") or config.get("org_id") or ""),
        api_key=getattr(args, "token", None) or os.getenv("SKILLAYER_API_KEY") or config.get("api_key"),
        providers=_providers(providers_value),
        project_roots=_project_roots(config, args),
        codex_home=Path(getattr(args, "codex_home", None) or os.getenv("CODEX_HOME") or config.get("codex_home") or Path.home() / ".codex").expanduser(),
        claude_home=Path(getattr(args, "claude_home", None) or os.getenv("CLAUDE_HOME") or config.get("claude_home") or Path.home() / ".claude").expanduser(),
        cursor_home=Path(getattr(args, "cursor_home", None) or os.getenv("CURSOR_HOME") or config.get("cursor_home") or Path.home() / "Library" / "Application Support" / "Cursor").expanduser(),
        config_path=config_path,
        state_path=state_path,
    )


def discover_payloads(config: AgentConfig) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for project in config.project_roots:
        if "codex" in config.providers:
            payloads.extend(
                build_agent_run_payloads(
                    codex_home=config.codex_home,
                    project_root=project.path,
                    repo_id=project.repo_id,
                    repo_full_name=project.repo_full_name,
                )
            )
        if "claude" in config.providers:
            payloads.extend(
                build_claude_agent_run_payloads(
                    claude_home=config.claude_home,
                    project_root=project.path,
                    repo_id=project.repo_id,
                    repo_full_name=project.repo_full_name,
                )
            )
        if "cursor" in config.providers:
            payloads.extend(
                build_cursor_agent_run_payloads(
                    cursor_home=config.cursor_home,
                    project_root=project.path,
                    repo_id=project.repo_id,
                    repo_full_name=project.repo_full_name,
                )
            )
    return payloads


def _state(config: AgentConfig) -> dict[str, Any]:
    return _json_load(config.state_path)


def _write_state(config: AgentConfig, payload: dict[str, Any]) -> None:
    config.state_path.parent.mkdir(parents=True, exist_ok=True)
    config.state_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(config.state_path, stat.S_IRUSR | stat.S_IWUSR)


def _runtime_status(config: AgentConfig) -> list[dict[str, Any]]:
    return [
        {
            "runtime": "codex_desktop",
            "label": "Codex Desktop",
            "configured": "codex" in config.providers,
            "detected": (config.codex_home / "sessions").exists(),
            "store": str(config.codex_home / "sessions"),
        },
        {
            "runtime": "codex_cli",
            "label": "Codex CLI",
            "configured": "codex" in config.providers,
            "detected": (config.codex_home / "sessions").exists(),
            "store": str(config.codex_home / "sessions"),
        },
        {
            "runtime": "claude_code",
            "label": "Claude Code",
            "configured": "claude" in config.providers,
            "detected": (config.claude_home / "projects").exists(),
            "store": str(config.claude_home / "projects"),
        },
        {
            "runtime": "cursor",
            "label": "Cursor",
            "configured": "cursor" in config.providers,
            "detected": (config.cursor_home / "User" / "workspaceStorage").exists(),
            "store": str(config.cursor_home / "User" / "workspaceStorage"),
        },
    ]


def _print(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
        return
    if payload.get("command") == "status":
        print("Skillayer agent status")
        print(f"Config: {payload['config_path']}")
        print(f"API: {payload['api_url']}")
        print(f"Org: {payload.get('org_id') or 'not configured'}")
        print(f"Project roots: {payload['project_root_count']}")
        print(f"Last sync: {payload.get('last_sync_at') or 'never'}")
        for runtime in payload["runtimes"]:
            marker = "detected" if runtime["detected"] else "not detected"
            configured = "enabled" if runtime["configured"] else "disabled"
            print(f"- {runtime['label']}: {marker}, {configured}")
        if payload.get("dry_run"):
            print(f"Discoverable runs: {payload['discoverable_runs']}")
        return
    print(json.dumps(payload, sort_keys=True))


def _post_json(api_url: str, path: str, payload: dict[str, Any], *, timeout: float = 10) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{api_url.rstrip('/')}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "skillayer-agent/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        decoded = json.loads(response.read().decode("utf-8"))
    if not isinstance(decoded, dict):
        raise RuntimeError(f"Unexpected response from {path}: expected JSON object")
    return decoded


def _write_connect_config(args: argparse.Namespace, *, token: str, org_id: str, api_url: str, repo_id: str | None = None, repo_full_name: str | None = None) -> dict[str, Any]:
    config_path = Path(args.config).expanduser()
    providers = list(_providers(args.providers))
    payload = {
        "api_url": api_url,
        "org_id": org_id,
        "api_key": token,
        "project_roots": [
            {
                "path": str(Path(args.project_root).expanduser().resolve()),
                **({"repo_id": repo_id or args.repo_id} if repo_id or args.repo_id else {}),
                **({"repo_full_name": repo_full_name or args.repo_full_name} if repo_full_name or args.repo_full_name else {}),
            }
        ],
        "providers": providers,
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)
    return {"command": "connect", "config_path": str(config_path), "org_id": org_id, "providers": providers}


def command_status(args: argparse.Namespace) -> int:
    config = load_agent_config(args)
    state = _state(config)
    payload: dict[str, Any] = {
        "command": "status",
        "api_url": config.api_url,
        "org_id": config.org_id,
        "config_path": str(config.config_path),
        "state_path": str(config.state_path),
        "project_root_count": len(config.project_roots),
        "providers": list(config.providers),
        "runtimes": _runtime_status(config),
        "last_sync_at": state.get("last_sync_at"),
        "last_discovered": state.get("last_discovered", 0),
        "last_posted": state.get("last_posted", 0),
        "last_failed": state.get("last_failed", 0),
        "dry_run": bool(args.dry_run),
    }
    if args.dry_run:
        payload["discoverable_runs"] = len(discover_payloads(config))
    _print(payload, as_json=args.json)
    return 0


def command_sync(args: argparse.Namespace) -> int:
    config = load_agent_config(args)
    if not config.org_id:
        raise SystemExit("error: --org-id, SKILLAYER_ORG_ID, or ~/.skillayer/agent.json org_id is required")
    if not args.dry_run and not config.api_key:
        raise SystemExit("error: --token, SKILLAYER_API_KEY, or ~/.skillayer/agent.json api_key is required")

    payloads = discover_payloads(config)
    posted = 0
    failed = 0
    failures: list[dict[str, str]] = []
    for payload in payloads:
        if args.dry_run:
            posted += 1
            continue
        try:
            post_payload(config.api_url, config.org_id, payload, config.api_key)
            posted += 1
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            failed += 1
            failures.append({"session_id": str(payload.get("session_id") or ""), "error": str(exc)})
    summary = {
        "command": "sync",
        "discovered": len(payloads),
        "posted": posted,
        "failed": failed,
        "dry_run": bool(args.dry_run),
        "providers": list(config.providers),
        "project_root_count": len(config.project_roots),
        "failures": failures[:10],
    }
    if not args.dry_run:
        _write_state(
            config,
            {
                "last_sync_at": datetime.now(timezone.utc).isoformat(),
                "last_discovered": len(payloads),
                "last_posted": posted,
                "last_failed": failed,
                "providers": list(config.providers),
                "project_roots": [str(project.path) for project in config.project_roots],
            },
        )
    _print(summary, as_json=args.json)
    return 1 if failed else 0


def command_connect(args: argparse.Namespace) -> int:
    if args.token:
        if not args.org_id:
            raise SystemExit("error: --org-id is required")
        result = _write_connect_config(args, token=args.token, org_id=args.org_id, api_url=args.api_url)
        _print(result, as_json=args.json)
        return 0

    try:
        code = _post_json(
            args.api_url,
            "/v1/device/code",
            {
                "project_root": str(Path(args.project_root).expanduser().resolve()),
                "repo_id": args.repo_id,
                "repo_full_name": args.repo_full_name,
            },
        )
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError) as exc:
        raise SystemExit(f"error: failed to start Skillayer device flow: {exc}") from exc

    verification_url = str(code.get("verification_uri_complete") or code.get("verification_uri") or "")
    user_code = str(code.get("user_code") or "")
    device_code = str(code.get("device_code") or "")
    interval = int(code.get("interval") or 5)
    expires_in = int(code.get("expires_in") or 900)
    if not device_code or not verification_url:
        raise SystemExit("error: invalid device flow response from Skillayer")
    if not args.json:
        print("Open this URL to connect Skillayer:")
        print(verification_url)
        if user_code:
            print(f"Code: {user_code}")
    if not args.no_browser:
        webbrowser.open(verification_url)

    deadline = time.monotonic() + expires_in
    token_response: dict[str, Any] = {}
    while time.monotonic() < deadline:
        time.sleep(interval)
        try:
            token_response = _post_json(args.api_url, "/v1/device/token", {"device_code": device_code})
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError) as exc:
            raise SystemExit(f"error: failed while polling Skillayer device flow: {exc}") from exc
        error = token_response.get("error")
        if not error:
            break
        if error == "authorization_pending":
            interval = int(token_response.get("interval") or interval)
            continue
        raise SystemExit(f"error: device flow failed: {error}")
    else:
        raise SystemExit("error: device flow expired before approval")

    token = str(token_response.get("access_token") or "")
    org_id = str(token_response.get("org_id") or args.org_id or "")
    if not token or not org_id:
        raise SystemExit("error: device flow completed without token/org_id")
    result = _write_connect_config(
        args,
        token=token,
        org_id=org_id,
        api_url=str(token_response.get("api_url") or args.api_url),
        repo_id=str(token_response.get("repo_id") or "") or None,
        repo_full_name=str(token_response.get("repo_full_name") or "") or None,
    )
    _print(result, as_json=args.json)
    return 0


def command_watch(args: argparse.Namespace) -> int:
    raise SystemExit("error: watch mode is scheduled for PR-X3; use `skillayer-agent sync` for one-shot imports")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillayer-agent", description="Skillayer local coding-agent metadata helper.")
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to ~/.skillayer/agent.json.")
    parser.add_argument("--state", default=str(STATE_PATH), help="Path to local sync state.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--config", default=str(CONFIG_PATH))
        subparser.add_argument("--state", default=str(STATE_PATH))
        subparser.add_argument("--api-url")
        subparser.add_argument("--org-id")
        subparser.add_argument("--token")
        subparser.add_argument("--providers")
        subparser.add_argument("--project-root")
        subparser.add_argument("--repo-id")
        subparser.add_argument("--repo-full-name")
        subparser.add_argument("--codex-home")
        subparser.add_argument("--claude-home")
        subparser.add_argument("--cursor-home")
        subparser.add_argument("--json", action="store_true")

    sync = subparsers.add_parser("sync", help="One-shot import of local Codex and Claude Code metadata.")
    add_common(sync)
    sync.add_argument("--dry-run", action="store_true", help="Discover payloads without posting to Skillayer.")
    sync.set_defaults(func=command_sync)

    status = subparsers.add_parser("status", help="Show configured local runtimes and last upload state.")
    add_common(status)
    status.add_argument("--dry-run", action="store_true", help="Also count discoverable local runs.")
    status.set_defaults(func=command_status)

    connect = subparsers.add_parser("connect", help="Write a local Skillayer agent config.")
    connect.add_argument("--config", default=str(CONFIG_PATH))
    connect.add_argument("--api-url", default=os.getenv("SKILLAYER_API_URL", DEFAULT_API_URL))
    connect.add_argument("--org-id", default=os.getenv("SKILLAYER_ORG_ID"))
    connect.add_argument("--token", default=os.getenv("SKILLAYER_API_KEY"))
    connect.add_argument("--providers", default=os.getenv("SKILLAYER_AGENT_IMPORT_PROVIDERS", ",".join(DEFAULT_PROVIDERS)))
    connect.add_argument("--project-root", default=".")
    connect.add_argument("--repo-id", default=os.getenv("SKILLAYER_REPO_ID"))
    connect.add_argument("--repo-full-name", default=os.getenv("SKILLAYER_REPO_FULL_NAME"))
    connect.add_argument("--no-browser", action="store_true", help="Print the device-flow URL without opening a browser.")
    connect.add_argument("--json", action="store_true")
    connect.set_defaults(func=command_connect)

    watch = subparsers.add_parser("watch", help="Watch local agent stores for new sessions.")
    watch.set_defaults(func=command_watch)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


def console_main() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    console_main()
