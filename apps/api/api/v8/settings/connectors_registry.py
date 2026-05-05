from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ConnectorDefinition:
    id: str
    label: str
    category: str
    status: str = "planned"
    source_type: str | None = None


CONNECTORS: tuple[ConnectorDefinition, ...] = (
    ConnectorDefinition("claude-code", "Claude Code", "coding-agent", "planned"),
    ConnectorDefinition("codex-cli", "Codex CLI", "coding-agent", "planned"),
    ConnectorDefinition("cursor", "Cursor", "coding-agent", "planned"),
    ConnectorDefinition("windsurf", "Windsurf", "coding-agent", "planned"),
    ConnectorDefinition("aider", "Aider", "coding-agent", "planned"),
    ConnectorDefinition("github-copilot", "GitHub Copilot", "coding-agent", "planned"),
    ConnectorDefinition("gitlab-duo", "GitLab Duo", "coding-agent", "planned"),
    ConnectorDefinition("internal-mcp", "Internal MCP servers", "runtime", "planned"),
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
