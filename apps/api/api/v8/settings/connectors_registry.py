from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ConnectorDefinition:
    id: str
    label: str
    category: str
    status: str = "planned"
    source_type: str | None = None
    description: str | None = None
    capabilities: tuple[str, ...] = ()


CONNECTORS: tuple[ConnectorDefinition, ...] = (
    ConnectorDefinition(
        "openai-compliance",
        "OpenAI Compliance Platform",
        "compliance-telemetry",
        "planned",
        "openai_compliance",
        "ChatGPT Enterprise/Edu compliance logs and metadata for audit, DLP, SIEM, and eDiscovery workflows.",
        ("audit logs", "chat metadata", "user activity", "model usage"),
    ),
    ConnectorDefinition(
        "anthropic-compliance",
        "Anthropic Compliance API",
        "compliance-telemetry",
        "planned",
        "anthropic_compliance",
        "Claude Enterprise compliance activity, chat data, file content, and audit log records where the tenant has API access.",
        ("audit logs", "chat data", "file content", "user activity"),
    ),
    ConnectorDefinition(
        "claude-cowork-otel",
        "Claude Cowork OpenTelemetry",
        "compliance-telemetry",
        "planned",
        "claude_cowork_otel",
        "Real-time Cowork telemetry for prompts, tool/MCP calls, file access, approvals, model usage, and errors.",
        ("prompts", "tool calls", "file access", "approval decisions", "model usage"),
    ),
    ConnectorDefinition(
        "claude-code",
        "Claude Code",
        "coding-agent",
        "planned",
        "claude_code",
        "Coding-agent activity, tool use, file access, skills, and permission decisions from Claude Code hooks or supported telemetry.",
        ("agent sessions", "tool calls", "file access", "permission decisions"),
    ),
    ConnectorDefinition(
        "codex-cli",
        "Codex CLI",
        "coding-agent",
        "planned",
        "codex_cli",
        "Codex CLI sessions, model/intelligence tier, command/tool access, file access, and approval decisions from local hooks.",
        ("agent sessions", "model tier", "tool access", "file access"),
    ),
    ConnectorDefinition(
        "cursor",
        "Cursor",
        "coding-agent",
        "planned",
        "cursor",
        "Cursor agent usage, full-access grants, model tier, tool calls, and workspace/repo activity where enterprise telemetry is available.",
        ("agent sessions", "model tier", "full-access grants", "repo activity"),
    ),
    ConnectorDefinition(
        "windsurf",
        "Windsurf",
        "coding-agent",
        "planned",
        "windsurf",
        "Windsurf/Cascade coding-agent sessions, model tier, workspace actions, terminal/tool use, and file-target metadata where enterprise telemetry is available.",
        ("agent sessions", "model tier", "tool calls", "file access", "repo activity"),
    ),
    ConnectorDefinition(
        "aider",
        "Aider",
        "coding-agent",
        "planned",
        "aider",
        "Aider coding sessions, repository targets, model usage, git changes, and shell/tool activity from local or enterprise telemetry hooks.",
        ("agent sessions", "model usage", "git changes", "shell access", "file access"),
    ),
    ConnectorDefinition(
        "github-copilot",
        "GitHub Copilot",
        "coding-agent",
        "planned",
        "github_copilot",
        "GitHub Copilot Business/Enterprise coding-agent and chat activity with organization, repo, model, policy, seat, and usage metadata.",
        ("agent sessions", "chat activity", "repo activity", "policy metadata", "model usage"),
    ),
    ConnectorDefinition(
        "gitlab-duo",
        "GitLab Duo",
        "coding-agent",
        "planned",
        "gitlab_duo",
        "GitLab Duo assistant activity, project targets, model usage, merge-request context, and policy metadata from GitLab telemetry or audit exports.",
        ("agent sessions", "project activity", "merge requests", "policy metadata", "model usage"),
    ),
    ConnectorDefinition(
        "internal-mcp",
        "Internal MCP servers",
        "runtime",
        "planned",
        "internal_mcp",
        "Internal MCP server calls, tool names, resource scopes, approval decisions, latency, and error metadata for agent runtime governance.",
        ("mcp calls", "tool access", "resource scopes", "approval decisions", "latency"),
    ),
    ConnectorDefinition("github", "GitHub", "source-control", "available", "github"),
    ConnectorDefinition("gitlab", "GitLab", "source-control", "planned"),
    ConnectorDefinition("bitbucket", "Bitbucket", "source-control", "planned"),
    ConnectorDefinition("jira", "Jira", "work-management", "planned"),
    ConnectorDefinition("linear", "Linear", "work-management", "planned"),
    ConnectorDefinition("slack", "Slack", "notifications", "available"),
    ConnectorDefinition("pagerduty", "PagerDuty", "incident", "available", "pagerduty"),
    ConnectorDefinition("splunk", "Splunk", "siem", "planned"),
    ConnectorDefinition("datadog", "Datadog", "siem", "planned"),
    ConnectorDefinition("sentinel", "Microsoft Sentinel", "siem", "planned"),
    ConnectorDefinition("s3-worm", "S3 Object Lock", "worm-store", "planned"),
    ConnectorDefinition("gcs-worm", "GCS Bucket Lock", "worm-store", "planned"),
    ConnectorDefinition("azure-worm", "Azure Immutable Blob", "worm-store", "planned"),
    ConnectorDefinition("sigstore", "Sigstore", "provenance", "planned"),
)


def connector_registry() -> list[dict[str, str | None]]:
    return [asdict(connector) for connector in CONNECTORS]
