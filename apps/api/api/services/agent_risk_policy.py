from __future__ import annotations

from fnmatch import fnmatch
import re
import shlex
from typing import Any


DEFAULT_AGENT_RISK_POLICY: dict[str, Any] = {
    "critical_threshold": 90,
    "high_threshold": 70,
    "medium_threshold": 35,
    "critical_requires_danger_signal": True,
    "full_access_score_floor": 75,
    "dangerous_command_score_floor": 90,
    "sensitive_path_score_floor": 90,
    "unknown_external_score_floor": 90,
    "unapproved_mcp_score_floor": 90,
    "dangerous_command_patterns": [
        "rm -rf",
        "sudo *",
        "chmod 777",
        "curl *| sh",
        "wget *| sh",
        "git push --force",
        "git reset --hard",
        "kubectl delete",
        "terraform destroy",
        "vercel deploy --prod",
        "npm publish",
        "twine upload",
        "security find-generic-password",
        "cat .env",
        "printenv",
    ],
    "sensitive_path_patterns": [
        ".env",
        ".env.*",
        "**/.env",
        "**/.env.*",
        "**/id_rsa",
        "**/.npmrc",
        "**/.pypirc",
        "**/*secret*",
        "**/*credential*",
        "**/*token*",
        "**/auth/**",
        "**/billing/**",
        "**/payment/**",
        "**/payments/**",
        "**/infra/**",
        "**/terraform/**",
        "**/.github/workflows/**",
        "**/policy/**",
        "**/compliance/**",
    ],
    "approved_external_domains": [
        "api.github.com",
        "github.com",
        "api.openai.com",
        "api.anthropic.com",
        "registry.npmjs.org",
        "pypi.org",
        "files.pythonhosted.org",
    ],
    "approved_mcp_tools": [
        "js",
        "mcp__codex_apps__github",
        "mcp__computer_use__",
        "mcp__node_repl__",
    ],
}

COMMAND_FINDING_POINTS = {
    "critical": 35,
    "high": 20,
    "medium": 10,
}


def normalize_agent_risk_policy(raw: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = dict(DEFAULT_AGENT_RISK_POLICY)
    if isinstance(raw, dict):
        for key, value in raw.items():
            if key in policy:
                policy[key] = value
    for key in ("critical_threshold", "high_threshold", "medium_threshold", "full_access_score_floor", "dangerous_command_score_floor", "sensitive_path_score_floor", "unknown_external_score_floor", "unapproved_mcp_score_floor"):
        try:
            policy[key] = max(0, min(100, int(policy[key])))
        except (TypeError, ValueError):
            policy[key] = DEFAULT_AGENT_RISK_POLICY[key]
    policy["critical_requires_danger_signal"] = bool(policy.get("critical_requires_danger_signal"))
    for key in ("dangerous_command_patterns", "sensitive_path_patterns", "approved_external_domains", "approved_mcp_tools"):
        value = policy.get(key)
        policy[key] = [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else list(DEFAULT_AGENT_RISK_POLICY[key])
    return policy


def agent_risk_policy_from_settings(settings: dict[str, Any] | None) -> dict[str, Any]:
    raw = settings.get("agent_risk_policy") if isinstance(settings, dict) else None
    return normalize_agent_risk_policy(raw if isinstance(raw, dict) else None)


def agent_risk_policy_from_org(org: object | None) -> dict[str, Any]:
    settings = getattr(org, "settings", None)
    return agent_risk_policy_from_settings(settings if isinstance(settings, dict) else None)


def risk_level_for_score(score: int, policy: dict[str, Any] | None = None, *, danger_signal: bool = False) -> str:
    config = normalize_agent_risk_policy(policy)
    if score >= int(config["critical_threshold"]) and (danger_signal or not config["critical_requires_danger_signal"]):
        return "critical"
    if score >= int(config["high_threshold"]):
        return "high"
    if score >= int(config["medium_threshold"]):
        return "medium"
    return "low"


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in {None, ""}]
    if isinstance(value, str) and value:
        return [value]
    return []


def _command_matches(command: str, pattern: str) -> bool:
    normalized = " ".join(command.lower().split())
    candidate = " ".join(pattern.lower().split())
    return fnmatch(normalized, candidate) or candidate in normalized


def _path_matches(path: str, pattern: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    candidate = pattern.replace("\\", "/").lower()
    return fnmatch(normalized, candidate) or fnmatch(normalized.lstrip("./"), candidate)


def _domain_approved(domain: str, approved_domains: list[str]) -> bool:
    normalized = domain.strip().lower()
    return any(normalized == item.lower() or normalized.endswith(f".{item.lower()}") for item in approved_domains)


def _mcp_approved(tool: str, approved_tools: list[str]) -> bool:
    normalized = tool.strip().lower()
    return any(normalized == item.lower() or normalized.startswith(f"{item.lower()}.") or normalized.startswith(f"{item.lower()}__") for item in approved_tools)


def _shell_tokens(command: str) -> list[str]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = "#"
        return list(lexer)
    except ValueError:
        return command.split()


def _tokens_before_heredoc(tokens: list[str]) -> list[str]:
    for index, token in enumerate(tokens):
        if token.startswith("<<"):
            return tokens[:index]
    return tokens


def _contains_real_redirect(tokens: list[str]) -> bool:
    visible = _tokens_before_heredoc(tokens)
    for index, token in enumerate(visible):
        previous = visible[index - 1] if index > 0 else ""
        if token in {">", ">>"} and (previous == "" or previous.isdigit() or not previous.endswith("-")):
            return True
        if re.fullmatch(r"\d*>{1,2}", token):
            return True
    return False


def _writes_sensitive_with_tee(tokens: list[str]) -> bool:
    visible = _tokens_before_heredoc(tokens)
    for index, token in enumerate(visible):
        if token != "tee":
            continue
        targets = [item for item in visible[index + 1 : index + 4] if not item.startswith("-")]
        if any(re.search(r"(^|/)(\.env|id_rsa|id_ed25519)|\.pem$|\.key$|secret|token|credential", target, re.I) for target in targets):
            return True
    return False


def _has_command(tokens: list[str], names: set[str]) -> bool:
    return any(token.split("/")[-1].lower() in names for token in _tokens_before_heredoc(tokens))


def classify_agent_command_danger(command: str) -> list[dict[str, str]]:
    normalized = " ".join(command.strip().lower().split())
    tokens = _shell_tokens(command)
    visible_tokens = _tokens_before_heredoc(tokens)
    lowered_tokens = [token.lower() for token in visible_tokens]
    findings: list[dict[str, str]] = []

    def add(severity: str, title: str, reason: str, pattern: str) -> None:
        finding = {"severity": severity, "title": title, "reason": reason, "matchedPattern": pattern, "command": command}
        if finding not in findings:
            findings.append(finding)

    sensitive_terms = r"api[_-]?key|token|secret|password|database_url|postgres|next_public_api_url|skillayer"
    if (
        lowered_tokens[:1] in (["env"], ["printenv"])
        or "printenv" in lowered_tokens
        or any(token in {".env", ".env.local"} for token in lowered_tokens)
        or re_search(r"/api[-_/]?key\b", normalized)
        or re_search(rf"\b(select|grep|rg|cat|sed)\b.*\b({sensitive_terms})\b", normalized)
    ):
        add("critical", "Credential or secret access", "The command can expose environment variables, API keys, tokens, secrets, or passwords.", "secret-access")
    if re_search(r"\b(cat|sed|awk)\b.*(\.env|\.pem|id_rsa|id_ed25519)", normalized) or re_search(r"\bselect\b.*\b(api[_-]?key|token|secret|password)\b", normalized):
        add("critical", "Sensitive file or column read", "The command reads credential-bearing files or sensitive database columns.", "sensitive-read")
    if re_search(r"\brm\s+-[a-z]*r[f]?\b|\brm\s+-[a-z]*f[a-z]*r\b|\bchmod\s+(-r\s+)?777\b|\bdd\s+|\bmkfs\b", normalized) or _contains_real_redirect(tokens) or _writes_sensitive_with_tee(tokens):
        add("critical", "Destructive filesystem operation", "The command can delete, overwrite, re-permission, or truncate files.", "destructive-filesystem")
    if re_search(r"git\s+push\s+.*(--force|-f)\b", normalized):
        add("high", "Force push", "The command can rewrite shared Git history.", "git-force-push")
    if re_search(r"(curl|wget)\b.*\|\s*(sh|bash)|\beval\b.*(curl|wget)", normalized):
        add("critical", "Remote code execution", "Fetched remote content is executed by the shell.", "remote-code-execution")
    if re_search(r"\b(cp|scp|rsync)\b.*(\.db|\.sqlite|\.sqlite3|dump|backup)", normalized):
        add("high", "Database file movement", "The command moves database or backup files and may exfiltrate data.", "data-movement")
    if _has_command(tokens, {"playwright", "puppeteer", "chromium", "chrome", "sudo", "uvicorn"}) or re_search(r"\b(playwright|puppeteer|chromium|chrome)\b|next dev|npm run dev|sudo\b", normalized):
        add("medium", "Process or automation launch", "The command starts automation, browser control, servers, or privileged execution.", "process-automation")
    return findings


def re_search(pattern: str, value: str) -> bool:
    return re.search(pattern, value) is not None


def agent_danger_signals(metadata: dict[str, Any], policy: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    config = normalize_agent_risk_policy(policy)
    details = metadata.get("activity_details") if isinstance(metadata.get("activity_details"), dict) else {}
    commands = _string_list(details.get("commands")) + _string_list(metadata.get("commands"))
    files = _string_list(metadata.get("file_targets")) + _string_list(details.get("edited_files"))
    mcp_tools = _string_list(metadata.get("mcp_tools"))
    external_calls = metadata.get("external_api_calls") if isinstance(metadata.get("external_api_calls"), list) else []

    matched_commands = list(dict.fromkeys(
        command
        for command in commands
        if any(_command_matches(command, pattern) for pattern in config["dangerous_command_patterns"])
    ))
    command_findings: list[dict[str, str]] = []
    for command in commands:
        command_findings.extend(classify_agent_command_danger(command))
    if command_findings:
        matched_commands = list(dict.fromkeys([*matched_commands, *(finding["command"] for finding in command_findings)]))
    sensitive_paths = list(dict.fromkeys(
        path
        for path in files
        if any(_path_matches(path, pattern) for pattern in config["sensitive_path_patterns"])
    ))
    unknown_domains = []
    for item in external_calls:
        if not isinstance(item, dict):
            continue
        domain = str(item.get("domain") or "").strip()
        if domain and not _domain_approved(domain, config["approved_external_domains"]):
            unknown_domains.append(domain)
    unknown_domains = list(dict.fromkeys(unknown_domains))
    unapproved_mcp = list(dict.fromkeys(tool for tool in mcp_tools if tool and not _mcp_approved(tool, config["approved_mcp_tools"])))

    reasons: list[str] = []
    if matched_commands:
        title = command_findings[0]["title"] if command_findings else "dangerous command matched"
        reasons.append(f"dangerous command - {title}: {matched_commands[0][:96]}")
    if sensitive_paths:
        reasons.append(f"sensitive path touched: {sensitive_paths[0]}")
    if unknown_domains:
        reasons.append(f"unapproved external API domain: {unknown_domains[0]}")
    if unapproved_mcp:
        reasons.append(f"unapproved MCP/tool call: {unapproved_mcp[0]}")
    return reasons, {
        "dangerous_commands": matched_commands,
        "command_findings": command_findings,
        "sensitive_paths": sensitive_paths,
        "unknown_external_domains": unknown_domains,
        "unapproved_mcp_tools": unapproved_mcp,
    }


def _normalize_contributions(contributions: list[dict[str, Any]], score: int) -> list[dict[str, Any]]:
    positive = [item for item in contributions if int(item.get("points") or 0) > 0]
    total = sum(int(item["points"]) for item in positive)
    if total <= 0 or total == score:
        return positive
    scaled: list[dict[str, Any]] = []
    running = 0
    for index, item in enumerate(positive):
        if index == len(positive) - 1:
            points = max(0, score - running)
        else:
            points = max(0, round((int(item["points"]) / total) * score))
            running += points
        scaled.append({**item, "points": points})
    return [item for item in scaled if int(item.get("points") or 0) > 0]


def score_agent_run_risk_breakdown(metadata: dict[str, Any], *, sensitivity_tier: str = "internal", policy: dict[str, Any] | None = None) -> tuple[int, str, list[str], dict[str, list[str]], list[dict[str, Any]]]:
    config = normalize_agent_risk_policy(policy)
    metrics = metadata.get("activity_metrics") if isinstance(metadata.get("activity_metrics"), dict) else {}
    edited = int(metrics.get("edited_files") or metadata.get("edited_files") or 0)
    commands = int(metrics.get("commands") or 0)
    tool_permissions = metadata.get("tool_permissions") if isinstance(metadata.get("tool_permissions"), list) else []
    mcp_tools = metadata.get("mcp_tools") if isinstance(metadata.get("mcp_tools"), list) else []
    file_targets = metadata.get("file_targets") if isinstance(metadata.get("file_targets"), list) else []

    action_class = "write" if edited > 0 or file_targets else "exec" if commands > 0 else "network" if tool_permissions else "read"
    base = {"read": 8, "write": 34, "exec": 48, "network": 44}.get(action_class, 10)
    sensitivity = {
        "public": 0,
        "internal": 5,
        "confidential": 18,
        "restricted": 28,
        "regulated": 32,
        "sensitive": 18,
        "unknown": 5,
    }.get(str(sensitivity_tier or "internal").lower(), 5)
    scope = min(20, len({str(path) for path in file_targets if path}) * 3)
    score = base + sensitivity + scope
    contributions = [
        {"factor": "activity", "label": f"{action_class.title()} activity", "points": base},
    ]
    if sensitivity:
        contributions.append({"factor": "repo_sensitivity", "label": f"{str(sensitivity_tier or 'internal').title()} repository", "points": sensitivity})
    if scope:
        contributions.append({"factor": "file_scope", "label": f"{len({str(path) for path in file_targets if path})} file target(s)", "points": scope})
    reasons = [f"{action_class} activity"]
    if str(sensitivity_tier or "").strip().lower() not in {"", "public"}:
        reasons.append(f"{str(sensitivity_tier).lower()} repository")
    if file_targets:
        reasons.append(f"{len({str(path) for path in file_targets if path})} file target{'s' if len(file_targets) != 1 else ''}")

    if bool(metadata.get("full_access")):
        floor_delta = max(0, int(config["full_access_score_floor"]) - score)
        score = max(score, int(config["full_access_score_floor"]))
        if floor_delta:
            contributions.append({"factor": "full_filesystem_access", "label": "Full filesystem access", "points": floor_delta})
        reasons.append("full filesystem access granted")
    if str(metadata.get("access_scope") or "").strip().lower() == "full-access":
        floor_delta = max(0, int(config["full_access_score_floor"]) - score)
        score = max(score, int(config["full_access_score_floor"]))
        contributions.append({"factor": "full_access_scope", "label": "Full access scope", "points": floor_delta or 8})
        reasons.append("full access scope granted")
    approval_policy = str(metadata.get("approval_policy") or "").strip().lower()
    sandbox_policy = str(metadata.get("sandbox_policy") or "").strip().lower()
    policy_text = f"{approval_policy} {sandbox_policy}".strip()
    if any(token in policy_text for token in ("auto", "autonomous")):
        score += 12
        contributions.append({"factor": "auto_review", "label": "Auto-review policy", "points": 12})
        reasons.append("auto-review policy")
    if mcp_tools:
        points = min(20, 6 + len(mcp_tools) * 2)
        score += points
        contributions.append({"factor": "mcp_tools", "label": f"{len(mcp_tools)} MCP/tool call(s)", "points": points})
        reasons.append(f"{len(mcp_tools)} MCP/tool call(s)")
    if commands:
        points = min(15, commands * 2)
        score += points
        contributions.append({"factor": "shell_commands", "label": f"{commands} shell command(s)", "points": points})
        reasons.append(f"{commands} shell command(s)")
    if str(metadata.get("github_enrichment_status") or "") == "missing":
        score += 10
        contributions.append({"factor": "github_join", "label": "Missing GitHub join evidence", "points": 10})
        reasons.append("missing GitHub join evidence")
    coverage = metadata.get("skill_coverage") if isinstance(metadata.get("skill_coverage"), dict) else {}
    relevant_count = int(coverage.get("relevant_count") or 0)
    loaded_count = int(coverage.get("loaded_count") or 0)
    if action_class == "write" and relevant_count > 0 and loaded_count == 0:
        score += 10
        contributions.append({"factor": "skill_coverage", "label": "0 skill docs loaded", "points": 10})
        reasons.append("0 relevant skill docs loaded")

    danger_reasons, signals = agent_danger_signals(metadata, config)
    command_findings = signals.get("command_findings") if isinstance(signals.get("command_findings"), list) else []
    if command_findings:
        grouped_findings: dict[tuple[str, str], int] = {}
        for finding in command_findings:
            if not isinstance(finding, dict):
                continue
            severity = str(finding.get("severity") or "medium")
            title = str(finding.get("title") or "Flagged command")
            grouped_findings[(severity, title)] = grouped_findings.get((severity, title), 0) + 1
        for (severity, title), count in grouped_findings.items():
            points = int(COMMAND_FINDING_POINTS.get(severity, COMMAND_FINDING_POINTS["medium"])) * count
            score += points
            contributions.append({"factor": f"command_{severity}_{title.lower().replace(' ', '_')}", "label": f"{title}{f' x{count}' if count > 1 else ''}", "points": points})
    elif signals["dangerous_commands"]:
        points = int(COMMAND_FINDING_POINTS["high"])
        score += points
        contributions.append({"factor": "dangerous_command", "label": "Dangerous command matched", "points": points})
    if signals["sensitive_paths"]:
        floor_delta = max(0, int(config["sensitive_path_score_floor"]) - score)
        score = max(score, int(config["sensitive_path_score_floor"]))
        contributions.append({"factor": "sensitive_path", "label": "Sensitive path touched", "points": floor_delta or 12})
    if signals["unknown_external_domains"]:
        floor_delta = max(0, int(config["unknown_external_score_floor"]) - score)
        score = max(score, int(config["unknown_external_score_floor"]))
        contributions.append({"factor": "unknown_external_api", "label": "Unapproved external API", "points": floor_delta or 12})
    if signals["unapproved_mcp_tools"]:
        floor_delta = max(0, int(config["unapproved_mcp_score_floor"]) - score)
        score = max(score, int(config["unapproved_mcp_score_floor"]))
        contributions.append({"factor": "unapproved_mcp", "label": "Unapproved MCP/tool call", "points": floor_delta or 12})
    reasons.extend(danger_reasons)

    danger_signal = any(signals.values())
    if config["critical_requires_danger_signal"] and not danger_signal:
        score = min(score, int(config["critical_threshold"]) - 1)
    score = max(0, min(100, int(score)))
    contributions = _normalize_contributions(contributions, score)
    return score, risk_level_for_score(score, config, danger_signal=danger_signal), reasons, signals, contributions


def score_agent_run_risk(metadata: dict[str, Any], *, sensitivity_tier: str = "internal", policy: dict[str, Any] | None = None) -> tuple[int, str, list[str], dict[str, list[str]]]:
    score, level, reasons, signals, _contributions = score_agent_run_risk_breakdown(metadata, sensitivity_tier=sensitivity_tier, policy=policy)
    return score, level, reasons, signals
