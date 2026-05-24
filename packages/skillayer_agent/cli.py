from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import plistlib
import shlex
import stat
import subprocess
import sys
import time
import uuid
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .local_importer import build_agent_run_payloads, build_claude_agent_run_payloads, build_copilot_agent_run_payloads, build_cursor_agent_run_payloads, build_windsurf_agent_run_payloads, post_payload

DEFAULT_API_URL = "https://api.skillayer.com"
DEFAULT_PROVIDERS = ("codex", "claude", "cursor", "windsurf", "copilot")
CONFIG_PATH = Path.home() / ".skillayer" / "agent.json"
STATE_PATH = Path.home() / ".skillayer" / "state.json"
SERVICE_LABEL = "com.skillayer.agent"


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
    windsurf_home: Path
    config_path: Path
    state_path: Path
    machine_id: str
    machine_label: str


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
    supported = {"codex", "claude", "cursor", "windsurf", "copilot"}
    unsupported = sorted(normalized - supported)
    if unsupported:
        raise SystemExit(f"error: unsupported provider(s): {', '.join(unsupported)}")
    return tuple(sorted(normalized)) or DEFAULT_PROVIDERS


def _default_machine_label() -> str:
    return platform.node() or "local-machine"


def _default_machine_id(label: str | None = None) -> str:
    seed = f"{label or _default_machine_label()}:{uuid.getnode()}"
    return "machine-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]


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
    machine_label = str(getattr(args, "machine_label", None) or os.getenv("SKILLAYER_MACHINE_LABEL") or config.get("machine_label") or _default_machine_label())
    machine_id = str(getattr(args, "machine_id", None) or os.getenv("SKILLAYER_MACHINE_ID") or config.get("machine_id") or _default_machine_id(machine_label))
    return AgentConfig(
        api_url=str(getattr(args, "api_url", None) or os.getenv("SKILLAYER_API_URL") or config.get("api_url") or DEFAULT_API_URL),
        org_id=str(getattr(args, "org_id", None) or os.getenv("SKILLAYER_ORG_ID") or config.get("org_id") or ""),
        api_key=getattr(args, "token", None) or os.getenv("SKILLAYER_API_KEY") or config.get("api_key"),
        providers=_providers(providers_value),
        project_roots=_project_roots(config, args),
        codex_home=Path(getattr(args, "codex_home", None) or os.getenv("CODEX_HOME") or config.get("codex_home") or Path.home() / ".codex").expanduser(),
        claude_home=Path(getattr(args, "claude_home", None) or os.getenv("CLAUDE_HOME") or config.get("claude_home") or Path.home() / ".claude").expanduser(),
        cursor_home=Path(getattr(args, "cursor_home", None) or os.getenv("CURSOR_HOME") or config.get("cursor_home") or Path.home() / "Library" / "Application Support" / "Cursor").expanduser(),
        windsurf_home=Path(getattr(args, "windsurf_home", None) or os.getenv("WINDSURF_HOME") or config.get("windsurf_home") or Path.home() / ".codeium" / "windsurf").expanduser(),
        config_path=config_path,
        state_path=state_path,
        machine_id=machine_id,
        machine_label=machine_label,
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
        if "windsurf" in config.providers:
            payloads.extend(
                build_windsurf_agent_run_payloads(
                    windsurf_home=config.windsurf_home,
                    project_root=project.path,
                    repo_id=project.repo_id,
                    repo_full_name=project.repo_full_name,
                )
            )
        if "copilot" in config.providers:
            payloads.extend(
                build_copilot_agent_run_payloads(
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


def _upload_payloads(config: AgentConfig, payloads: list[dict[str, Any]], *, dry_run: bool) -> tuple[int, int, list[dict[str, str]], list[str]]:
    posted = 0
    failed = 0
    failures: list[dict[str, str]] = []
    posted_session_ids: list[str] = []
    for payload in payloads:
        session_id = str(payload.get("session_id") or "")
        if dry_run:
            posted += 1
            if session_id:
                posted_session_ids.append(session_id)
            continue
        try:
            post_payload(config.api_url, config.org_id, payload, config.api_key)
            posted += 1
            if session_id:
                posted_session_ids.append(session_id)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            failed += 1
            failures.append({"session_id": session_id, "error": str(exc)})
    return posted, failed, failures, posted_session_ids


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
        {
            "runtime": "windsurf",
            "label": "Windsurf",
            "configured": "windsurf" in config.providers,
            "detected": (config.windsurf_home / "conversations").exists(),
            "store": str(config.windsurf_home / "conversations"),
        },
        {
            "runtime": "copilot",
            "label": "GitHub Copilot",
            "configured": "copilot" in config.providers,
            "detected": False,
            "store": "GitHub connector: Copilot metrics and audit logs",
            "capture_mode": "connector",
        },
    ]


def _agent_module_command(config_path: Path, state_path: Path, interval: float) -> list[str]:
    return [
        sys.executable,
        "-m",
        "packages.skillayer_agent.cli",
        "--config",
        str(config_path),
        "--state",
        str(state_path),
        "watch",
        "--config",
        str(config_path),
        "--state",
        str(state_path),
        "--interval",
        str(interval),
    ]


def _service_paths() -> dict[str, Path]:
    system = platform.system().lower()
    logs = Path.home() / ".skillayer" / "logs"
    if system == "darwin":
        unit = Path.home() / "Library" / "LaunchAgents" / f"{SERVICE_LABEL}.plist"
    elif system == "windows":
        unit = Path.home() / ".skillayer" / "skillayer-agent.schtask"
    else:
        unit = Path.home() / ".config" / "systemd" / "user" / "skillayer-agent.service"
    return {
        "unit": unit,
        "logs": logs,
        "stdout": logs / "agent.out.log",
        "stderr": logs / "agent.err.log",
    }


def _run_service_command(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return completed.returncode == 0, output


def _install_macos_launch_agent(command: list[str], paths: dict[str, Path], *, start: bool) -> dict[str, Any]:
    paths["unit"].parent.mkdir(parents=True, exist_ok=True)
    paths["logs"].mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": SERVICE_LABEL,
        "ProgramArguments": command,
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(paths["stdout"]),
        "StandardErrorPath": str(paths["stderr"]),
        "WorkingDirectory": str(Path.cwd()),
    }
    paths["unit"].write_bytes(plistlib.dumps(plist, sort_keys=True))
    if not start:
        return {"installed": True, "running": False, "manager": "launchd", "unit_path": str(paths["unit"])}
    uid = os.getuid() if hasattr(os, "getuid") else None
    domain = f"gui/{uid}" if uid is not None else "gui"
    _run_service_command(["launchctl", "bootout", domain, str(paths["unit"])])
    bootstrap_ok, bootstrap_output = _run_service_command(["launchctl", "bootstrap", domain, str(paths["unit"])])
    kick_ok, kick_output = _run_service_command(["launchctl", "kickstart", "-k", f"{domain}/{SERVICE_LABEL}"])
    return {
        "installed": True,
        "running": bootstrap_ok and kick_ok,
        "manager": "launchd",
        "unit_path": str(paths["unit"]),
        "message": "\n".join(part for part in [bootstrap_output, kick_output] if part),
    }


def _install_linux_systemd_service(command: list[str], paths: dict[str, Path], *, start: bool) -> dict[str, Any]:
    paths["unit"].parent.mkdir(parents=True, exist_ok=True)
    paths["logs"].mkdir(parents=True, exist_ok=True)
    unit = "\n".join(
        [
            "[Unit]",
            "Description=Skillayer local coding-agent watcher",
            "",
            "[Service]",
            "Type=simple",
            f"ExecStart={' '.join(shlex.quote(part) for part in command)}",
            "Restart=always",
            "RestartSec=10",
            f"WorkingDirectory={Path.cwd()}",
            f"StandardOutput=append:{paths['stdout']}",
            f"StandardError=append:{paths['stderr']}",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ]
    )
    paths["unit"].write_text(unit, encoding="utf-8")
    if not start:
        return {"installed": True, "running": False, "manager": "systemd", "unit_path": str(paths["unit"])}
    reload_ok, reload_output = _run_service_command(["systemctl", "--user", "daemon-reload"])
    enable_ok, enable_output = _run_service_command(["systemctl", "--user", "enable", "--now", "skillayer-agent.service"])
    return {
        "installed": True,
        "running": reload_ok and enable_ok,
        "manager": "systemd",
        "unit_path": str(paths["unit"]),
        "message": "\n".join(part for part in [reload_output, enable_output] if part),
    }


def _install_windows_task(command: list[str], paths: dict[str, Path], *, start: bool) -> dict[str, Any]:
    paths["unit"].parent.mkdir(parents=True, exist_ok=True)
    paths["logs"].mkdir(parents=True, exist_ok=True)
    command_line = subprocess.list2cmdline(command)
    paths["unit"].write_text(command_line + "\n", encoding="utf-8")
    if not start:
        return {"installed": True, "running": False, "manager": "schtasks", "unit_path": str(paths["unit"])}
    create_ok, create_output = _run_service_command(["schtasks", "/Create", "/TN", "SkillayerAgent", "/TR", command_line, "/SC", "ONLOGON", "/RL", "LIMITED", "/F"])
    run_ok, run_output = _run_service_command(["schtasks", "/Run", "/TN", "SkillayerAgent"])
    return {
        "installed": True,
        "running": create_ok and run_ok,
        "manager": "schtasks",
        "unit_path": str(paths["unit"]),
        "message": "\n".join(part for part in [create_output, run_output] if part),
    }


def install_background_watcher(config_path: Path, state_path: Path, *, interval: float = 60.0, start: bool = True) -> dict[str, Any]:
    command = _agent_module_command(config_path.expanduser(), state_path.expanduser(), interval)
    paths = _service_paths()
    system = platform.system().lower()
    if system == "darwin":
        return _install_macos_launch_agent(command, paths, start=start)
    if system == "windows":
        return _install_windows_task(command, paths, start=start)
    return _install_linux_systemd_service(command, paths, start=start)


def watcher_status() -> dict[str, Any]:
    paths = _service_paths()
    system = platform.system().lower()
    if system == "darwin":
        ok, output = _run_service_command(["launchctl", "print", f"gui/{os.getuid()}/{SERVICE_LABEL}"])
        return {"manager": "launchd", "status": "running" if ok else ("installed" if paths["unit"].exists() else "not installed"), "unit_path": str(paths["unit"]), "message": output}
    if system == "windows":
        ok, output = _run_service_command(["schtasks", "/Query", "/TN", "SkillayerAgent"])
        return {"manager": "schtasks", "status": "running" if ok else ("installed" if paths["unit"].exists() else "not installed"), "unit_path": str(paths["unit"]), "message": output}
    ok, output = _run_service_command(["systemctl", "--user", "is-active", "skillayer-agent.service"])
    return {"manager": "systemd", "status": "running" if ok and output.strip() == "active" else ("installed" if paths["unit"].exists() else "not installed"), "unit_path": str(paths["unit"]), "message": output}


def _print(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
        return
    if payload.get("command") == "status":
        print("Skillayer agent status")
        print(f"Config: {payload['config_path']}")
        print(f"API: {payload['api_url']}")
        print(f"Org: {payload.get('org_id') or 'not configured'}")
        print(f"Machine: {payload.get('machine_label') or 'unknown'} ({payload.get('machine_id') or 'unregistered'})")
        print(f"Project roots: {payload['project_root_count']}")
        print(f"Last sync: {payload.get('last_sync_at') or 'never'}")
        watcher = payload.get("watcher") or {}
        print(f"Watcher: {watcher.get('status') or 'unknown'}")
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
    machine_label = str(getattr(args, "machine_label", None) or os.getenv("SKILLAYER_MACHINE_LABEL") or _default_machine_label())
    machine_id = str(getattr(args, "machine_id", None) or os.getenv("SKILLAYER_MACHINE_ID") or _default_machine_id(machine_label))
    payload = {
        "api_url": api_url,
        "org_id": org_id,
        "api_key": token,
        "machine_id": machine_id,
        "machine_label": machine_label,
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
    return {"command": "connect", "config_path": str(config_path), "org_id": org_id, "providers": providers, "machine_id": machine_id, "machine_label": machine_label}


def command_status(args: argparse.Namespace) -> int:
    config = load_agent_config(args)
    state = _state(config)
    payload: dict[str, Any] = {
        "command": "status",
        "api_url": config.api_url,
        "org_id": config.org_id,
        "config_path": str(config.config_path),
        "state_path": str(config.state_path),
        "machine_id": config.machine_id,
        "machine_label": config.machine_label,
        "project_root_count": len(config.project_roots),
        "providers": list(config.providers),
        "runtimes": _runtime_status(config),
        "last_sync_at": state.get("last_sync_at"),
        "last_discovered": state.get("last_discovered", 0),
        "last_posted": state.get("last_posted", 0),
        "last_failed": state.get("last_failed", 0),
        "watcher": watcher_status(),
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
    posted, failed, failures, posted_session_ids = _upload_payloads(config, payloads, dry_run=bool(args.dry_run))
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
                "posted_session_ids": posted_session_ids[-5000:],
            },
        )
    _print(summary, as_json=args.json)
    return 1 if failed else 0


def command_connect(args: argparse.Namespace) -> int:
    if args.token:
        if not args.org_id:
            raise SystemExit("error: --org-id is required")
        result = _write_connect_config(args, token=args.token, org_id=args.org_id, api_url=args.api_url)
        if not args.no_start:
            result["watcher"] = install_background_watcher(
                Path(args.config).expanduser(),
                Path(args.state).expanduser(),
                interval=float(args.interval),
                start=True,
            )
        _print(result, as_json=args.json)
        return 0

    try:
        machine_label = str(getattr(args, "machine_label", None) or os.getenv("SKILLAYER_MACHINE_LABEL") or _default_machine_label())
        machine_id = str(getattr(args, "machine_id", None) or os.getenv("SKILLAYER_MACHINE_ID") or _default_machine_id(machine_label))
        code = _post_json(
            args.api_url,
            "/v1/device/code",
            {
                "project_root": str(Path(args.project_root).expanduser().resolve()),
                "repo_id": args.repo_id,
                "repo_full_name": args.repo_full_name,
                "machine_id": machine_id,
                "machine_label": machine_label,
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
    if not args.no_start:
        result["watcher"] = install_background_watcher(
            Path(args.config).expanduser(),
            Path(args.state).expanduser(),
            interval=float(args.interval),
            start=True,
        )
    _print(result, as_json=args.json)
    return 0


def command_watch(args: argparse.Namespace) -> int:
    config = load_agent_config(args)
    if not config.org_id:
        raise SystemExit("error: --org-id, SKILLAYER_ORG_ID, or ~/.skillayer/agent.json org_id is required")
    if not args.dry_run and not config.api_key:
        raise SystemExit("error: --token, SKILLAYER_API_KEY, or ~/.skillayer/agent.json api_key is required")

    state = _state(config)
    known_session_ids = {str(item) for item in state.get("posted_session_ids", []) if item}
    interval = max(1.0, float(args.interval))
    while True:
        payloads = discover_payloads(config)
        new_payloads = [payload for payload in payloads if str(payload.get("session_id") or "") not in known_session_ids]
        posted, failed, failures, posted_session_ids = _upload_payloads(config, new_payloads, dry_run=bool(args.dry_run))
        known_session_ids.update(posted_session_ids)
        summary = {
            "command": "watch",
            "discovered": len(payloads),
            "new": len(new_payloads),
            "posted": posted,
            "failed": failed,
            "dry_run": bool(args.dry_run),
            "providers": list(config.providers),
            "project_root_count": len(config.project_roots),
            "failures": failures[:10],
            "interval_seconds": interval,
        }
        if not args.dry_run:
            _write_state(
                config,
                {
                    "last_watch_at": datetime.now(timezone.utc).isoformat(),
                    "last_sync_at": datetime.now(timezone.utc).isoformat(),
                    "last_discovered": len(payloads),
                    "last_new": len(new_payloads),
                    "last_posted": posted,
                    "last_failed": failed,
                    "providers": list(config.providers),
                    "project_roots": [str(project.path) for project in config.project_roots],
                    "posted_session_ids": sorted(known_session_ids)[-5000:],
                },
            )
        _print(summary, as_json=args.json)
        sys.stdout.flush()
        if args.once:
            return 1 if failed else 0
        time.sleep(interval)


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
        subparser.add_argument("--machine-id")
        subparser.add_argument("--machine-label")
        subparser.add_argument("--codex-home")
        subparser.add_argument("--claude-home")
        subparser.add_argument("--cursor-home")
        subparser.add_argument("--windsurf-home")
        subparser.add_argument("--json", action="store_true")

    sync = subparsers.add_parser("sync", help="One-shot import of local coding-agent metadata.")
    add_common(sync)
    sync.add_argument("--dry-run", action="store_true", help="Discover payloads without posting to Skillayer.")
    sync.set_defaults(func=command_sync)

    status = subparsers.add_parser("status", help="Show configured local runtimes and last upload state.")
    add_common(status)
    status.add_argument("--dry-run", action="store_true", help="Also count discoverable local runs.")
    status.set_defaults(func=command_status)

    connect = subparsers.add_parser("connect", help="Write a local Skillayer agent config.")
    connect.add_argument("--config", default=str(CONFIG_PATH))
    connect.add_argument("--state", default=str(STATE_PATH))
    connect.add_argument("--api-url", default=os.getenv("SKILLAYER_API_URL", DEFAULT_API_URL))
    connect.add_argument("--org-id", default=os.getenv("SKILLAYER_ORG_ID"))
    connect.add_argument("--token", default=os.getenv("SKILLAYER_API_KEY"))
    connect.add_argument("--providers", default=os.getenv("SKILLAYER_AGENT_IMPORT_PROVIDERS", ",".join(DEFAULT_PROVIDERS)))
    connect.add_argument("--project-root", default=".")
    connect.add_argument("--repo-id", default=os.getenv("SKILLAYER_REPO_ID"))
    connect.add_argument("--repo-full-name", default=os.getenv("SKILLAYER_REPO_FULL_NAME"))
    connect.add_argument("--machine-id", default=os.getenv("SKILLAYER_MACHINE_ID"))
    connect.add_argument("--machine-label", default=os.getenv("SKILLAYER_MACHINE_LABEL"))
    connect.add_argument("--interval", type=float, default=float(os.getenv("SKILLAYER_AGENT_WATCH_INTERVAL", "60")), help="Seconds between background watch ticks.")
    connect.add_argument("--no-start", action="store_true", help="Write config without installing or starting the background watcher.")
    connect.add_argument("--no-browser", action="store_true", help="Print the device-flow URL without opening a browser.")
    connect.add_argument("--json", action="store_true")
    connect.set_defaults(func=command_connect)

    watch = subparsers.add_parser("watch", help="Poll local agent stores and upload newly discovered sessions.")
    add_common(watch)
    watch.add_argument("--dry-run", action="store_true", help="Discover new payloads without posting to Skillayer.")
    watch.add_argument("--interval", type=float, default=60.0, help="Seconds between watch ticks.")
    watch.add_argument("--once", action="store_true", help="Run one watch tick and exit.")
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
