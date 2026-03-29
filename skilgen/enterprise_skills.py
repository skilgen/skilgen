from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import re
import shutil
import subprocess
from pathlib import Path

from skilgen.core.config import load_config


@dataclass(frozen=True)
class MCPConnector:
    slug: str
    name: str
    system: str
    description: str
    tags: tuple[str, ...] = ()
    default_mode: str = "read-only"
    official_source_url: str | None = None
    official_source_label: str | None = None
    auth_scheme: str = "manual"
    oauth_supported: bool = False
    oauth_principles: tuple[str, ...] = ()
    enterprise_ready: bool = False
    setup_notes: tuple[str, ...] = ()
    source_status: str = "official"
    recommended_source_url: str | None = None
    recommended_source_label: str | None = None


CONNECTOR_CATALOG: tuple[MCPConnector, ...] = (
    MCPConnector(
        "chrome-devtools",
        "Chrome DevTools MCP",
        "Google Chrome",
        "Inspect, debug, and automate browser behavior with the official Chrome DevTools MCP server.",
        ("browser", "debugging", "frontend"),
        official_source_url="https://github.com/mcp/ChromeDevTools/chrome-devtools-mcp",
        official_source_label="MCP Registry · Chrome DevTools MCP",
        auth_scheme="local",
        oauth_supported=False,
        enterprise_ready=True,
        setup_notes=("Use the official Chrome DevTools MCP package from the MCP Registry.",),
    ),
    MCPConnector(
        "playwright",
        "Playwright",
        "Microsoft",
        "Automate browsers for testing, accessibility inspection, and web data extraction.",
        ("browser", "testing", "automation"),
        official_source_url="https://github.com/microsoft/playwright-mcp",
        official_source_label="Microsoft Playwright MCP",
        auth_scheme="local",
        oauth_supported=False,
        enterprise_ready=True,
        setup_notes=("Best for controlled browser automation inside approved test or staging environments.",),
    ),
    MCPConnector(
        "jira",
        "Jira",
        "Atlassian",
        "Track issues, delivery state, and engineering workflows.",
        ("tickets", "planning", "enterprise"),
        official_source_url="https://www.atlassian.com/platform/remote-mcp-server",
        official_source_label="Atlassian Remote MCP Server",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("least-privilege scopes", "workspace-bound consent", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Use Atlassian-managed remote MCP.", "Prefer read-only scopes unless a workflow explicitly requires writes."),
    ),
    MCPConnector(
        "confluence",
        "Confluence",
        "Atlassian",
        "Search and read internal documentation, playbooks, and architecture notes.",
        ("docs", "wiki", "enterprise"),
        official_source_url="https://www.atlassian.com/platform/remote-mcp-server",
        official_source_label="Atlassian Remote MCP Server",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("least-privilege scopes", "workspace-bound consent", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Use Atlassian-managed remote MCP.", "Prefer page-read scopes before enabling edits."),
    ),
    MCPConnector(
        "compass",
        "Atlassian Compass",
        "Atlassian",
        "Use the Atlassian MCP server to access Compass service ownership and software catalog context.",
        ("service-catalog", "platform", "enterprise"),
        official_source_url="https://github.com/atlassian/atlassian-mcp-server",
        official_source_label="Atlassian MCP Server",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("least-privilege scopes", "workspace-bound consent", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Compass access is part of Atlassian's official MCP surface alongside Jira and Confluence.",),
    ),
    MCPConnector(
        "slack",
        "Slack",
        "Slack",
        "Read team communication context and incident coordination threads.",
        ("chat", "incident", "ops"),
        official_source_url="https://api.slack.com/automation/mcp",
        official_source_label="Slack MCP",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("workspace consent", "scoped bot tokens", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Provision a Slack app with only the channels and read scopes your agent needs.",),
    ),
    MCPConnector("servicenow", "ServiceNow", "ServiceNow", "Work with enterprise tickets, service requests, and incident records.", ("itsm", "incident", "enterprise")),
    MCPConnector(
        "datadog",
        "Datadog",
        "Datadog",
        "Inspect metrics, traces, monitors, and production signals.",
        ("observability", "metrics", "ops"),
        official_source_url="https://docs.datadoghq.com/llm_observability/instrumentation/mcp/",
        official_source_label="Datadog MCP",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("org-scoped consent", "short-lived access tokens", "auditable scopes"),
        enterprise_ready=True,
        setup_notes=("Bind Datadog access to the minimum set of org permissions and dashboards needed by the agent.",),
    ),
    MCPConnector("sentry", "Sentry", "Sentry", "Inspect application errors, releases, and issue trends.", ("errors", "observability", "ops")),
    MCPConnector(
        "github-enterprise",
        "GitHub Enterprise",
        "GitHub",
        "Read enterprise repositories, pull requests, and actions state.",
        ("code", "git", "devex"),
        official_source_url="https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp",
        official_source_label="GitHub MCP integration docs",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("org approval", "repo-scoped access", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Use GitHub App or enterprise-approved OAuth app credentials.", "Limit repo and workflow scopes to the agent's duties."),
    ),
    MCPConnector(
        "gitlab",
        "GitLab",
        "GitLab",
        "Read merge requests, CI pipelines, and source repos.",
        ("code", "ci", "devex"),
        official_source_url="https://docs.gitlab.com/user/gitlab_duo/mcp_server/",
        official_source_label="GitLab Duo MCP Server",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("group-scoped consent", "least-privilege scopes", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Prefer group-level allowlists and read-only scopes for CI and repo inspection.",),
    ),
    MCPConnector(
        "azure",
        "Azure MCP Server",
        "Microsoft Azure",
        "Connect agents to Azure services with the official Azure MCP server.",
        ("cloud", "infra", "platform"),
        official_source_url="https://github.com/Azure/azure-mcp",
        official_source_label="Azure MCP Server",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("Entra ID tokens", "RBAC", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Use the official Azure Identity flows and RBAC-scoped service principals or user identities.",),
    ),
    MCPConnector(
        "azure-devops",
        "Azure DevOps",
        "Microsoft",
        "Interact with Azure DevOps repos, work items, pipelines, test plans, and wiki.",
        ("devops", "work-items", "pipelines"),
        official_source_url="https://github.com/mcp/microsoft/azure-devops-mcp",
        official_source_label="MCP Registry · Azure DevOps",
        auth_scheme="pat",
        oauth_supported=False,
        enterprise_ready=True,
        setup_notes=("Official Azure DevOps MCP is available, but the default enterprise OAuth gate will keep it inactive unless policy is relaxed.",),
    ),
    MCPConnector(
        "azure-kubernetes",
        "Azure Kubernetes",
        "Microsoft Azure",
        "Inspect Kubernetes clusters through Microsoft's official Azure-backed Kubernetes MCP server.",
        ("infra", "ops", "deployments", "kubernetes"),
        official_source_url="https://github.com/Azure/mcp-kubernetes",
        official_source_label="Azure mcp-kubernetes",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("Entra ID tokens", "cluster RBAC", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Prefer cluster-scoped read roles and namespace restrictions for production use.",),
    ),
    MCPConnector(
        "kubernetes",
        "Kubernetes",
        "Cloud Native",
        "Inspect cluster resources, workloads, rollout state, and runtime incidents.",
        ("infra", "ops", "deployments"),
        source_status="community",
        recommended_source_url="https://github.com/openshift/openshift-mcp-server",
        recommended_source_label="OpenShift MCP Server",
        setup_notes=("No single official upstream Kubernetes Foundation MCP source was verified; use approved vendor/community servers deliberately.",),
    ),
    MCPConnector(
        "terraform",
        "Terraform",
        "HashiCorp",
        "Inspect infrastructure definitions, plans, and cloud rollout workflows.",
        ("infra", "iac", "cloud"),
        official_source_url="https://github.com/mcp/hashicorp/terraform-mcp-server",
        official_source_label="MCP Registry · Terraform",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("least-privilege tokens", "workspace scoping", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Prefer Terraform Cloud/Enterprise workspace scoping and read-only workflows by default.",),
    ),
    MCPConnector(
        "snowflake",
        "Snowflake",
        "Snowflake",
        "Work with enterprise data warehouse context and SQL operations.",
        ("data", "warehouse", "analytics"),
        source_status="community",
        recommended_source_url="https://registry.modelcontextprotocol.io/",
        recommended_source_label="Track registry entries for Snowflake-capable MCPs",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("role-based access", "warehouse-scoped credentials", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Use approved Snowflake-native or registry-backed MCP servers with role-scoped OAuth before activation.",),
    ),
    MCPConnector("postgres", "Postgres", "PostgreSQL", "Inspect schemas, queries, and transactional application data.", ("database", "sql", "data"), source_status="community"),
    MCPConnector(
        "mongodb",
        "MongoDB",
        "MongoDB",
        "Connect to MongoDB databases and Atlas clusters through the official MongoDB MCP server.",
        ("database", "data", "analytics"),
        official_source_url="https://github.com/mcp/mongodb-js/mongodb-mcp-server",
        official_source_label="MCP Registry · MongoDB",
        auth_scheme="api_key",
        oauth_supported=False,
        enterprise_ready=True,
        setup_notes=("Prefer read-only mode for analysis workloads and service-account scoping for Atlas tools.",),
    ),
    MCPConnector(
        "notion",
        "Notion",
        "Notion",
        "Read shared docs, product specs, and operational notes.",
        ("docs", "planning", "workspace"),
        official_source_url="https://github.com/mcp/makenotion/notion-mcp-server",
        official_source_label="MCP Registry · Notion",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("workspace consent", "page/database scoping", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Prefer workspace-scoped read access for enterprise documentation retrieval.",),
    ),
    MCPConnector(
        "microsoft-learn",
        "Microsoft Learn",
        "MicrosoftDocs",
        "Bring trusted and current Microsoft documentation directly into the agent workflow.",
        ("docs", "reference", "microsoft"),
        official_source_url="https://github.com/mcp/microsoftdocs/mcp",
        official_source_label="MCP Registry · Microsoft Learn",
        auth_scheme="none",
        oauth_supported=False,
        enterprise_ready=True,
        setup_notes=("No auth required. Great for enterprise Microsoft stacks, but it remains outside the default OAuth activation gate.",),
    ),
    MCPConnector(
        "stripe",
        "Stripe",
        "Stripe",
        "Work with customers, products, payments, and billing through Stripe's official MCP endpoints.",
        ("payments", "billing", "commerce"),
        official_source_url="https://github.com/mcp/com.stripe/mcp",
        official_source_label="MCP Registry · Stripe",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("account-scoped consent", "least-privilege actions", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Prefer OAuth where available; fall back to secret keys only in tightly controlled environments.",),
    ),
    MCPConnector(
        "figma",
        "Figma MCP Server",
        "Figma",
        "Bring design context directly into coding workflows through Figma's official MCP server.",
        ("design", "frontend", "design-system"),
        official_source_url="https://github.com/mcp/com.figma.mcp/mcp",
        official_source_label="MCP Registry · Figma MCP Server",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("workspace consent", "seat-based access", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Supports remote and local desktop modes; prefer remote with enterprise-managed workspace access.",),
    ),
    MCPConnector(
        "elasticsearch",
        "Elasticsearch",
        "Elastic",
        "Search and inspect Elasticsearch indices and data through the official Elastic MCP server.",
        ("search", "analytics", "observability"),
        official_source_url="https://github.com/mcp/elastic/mcp-server-elasticsearch",
        official_source_label="MCP Registry · Elasticsearch",
        auth_scheme="api_key",
        oauth_supported=False,
        enterprise_ready=True,
        setup_notes=("Official Elastic MCP exists, but the current server is deprecated in favor of Elastic Agent Builder MCP endpoints.",),
    ),
    MCPConnector(
        "sentry",
        "Getsentry Sentry",
        "Sentry",
        "Inspect issues, releases, and debugging context through Sentry's official MCP server.",
        ("errors", "observability", "ops"),
        official_source_url="https://github.com/mcp/getsentry/sentry-mcp",
        official_source_label="MCP Registry · Sentry",
        auth_scheme="oauth2",
        oauth_supported=True,
        oauth_principles=("user-consented auth", "project scoping", "token rotation"),
        enterprise_ready=True,
        setup_notes=("Sentry supports OAuth-oriented remote flows and token-based local flows; prefer OAuth in shared enterprise setups.",),
    ),
    MCPConnector(
        "sharepoint",
        "SharePoint",
        "Microsoft 365",
        "Search and retrieve SharePoint content for enterprise knowledge retrieval.",
        ("docs", "files", "microsoft365"),
        source_status="community",
        recommended_source_url="https://github.com/sekops-ch/sharepoint-mcp-server",
        recommended_source_label="sharepoint-mcp-server",
        auth_scheme="oauth2",
        oauth_supported=True,
        enterprise_ready=True,
        setup_notes=("No official Microsoft SharePoint MCP server was verified from the MCP registry sources reviewed; use approved Microsoft Graph-based community servers only after security review.",),
    ),
    MCPConnector("okta", "Okta", "Okta", "Understand enterprise identity, auth, and access-management flows.", ("identity", "security", "enterprise")),
)


def _skills_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "enterprise-skills"


def _skills_manifest_path(project_root: str | Path) -> Path:
    return _skills_root(project_root) / "manifest.json"


def _connector_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "connectors"


def _connector_manifest_path(project_root: str | Path) -> Path:
    return _connector_root(project_root) / "manifest.json"


def _normalize_slug(value: str) -> str:
    return "-".join(part for part in "".join(ch.lower() if ch.isalnum() else "-" for ch in value).split("-") if part)


def _name_from_git_url(git_url: str) -> str:
    cleaned = git_url.rstrip("/").rsplit("/", 1)[-1]
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    return cleaned or "enterprise-skill"


def _load_json(path: Path, default: dict[str, object]) -> dict[str, object]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_skills_manifest(project_root: str | Path) -> dict[str, object]:
    return _load_json(_skills_manifest_path(project_root), {"skills": []})


def _write_skills_manifest(project_root: str | Path, payload: dict[str, object]) -> None:
    _write_json(_skills_manifest_path(project_root), payload)


def _load_connector_manifest(project_root: str | Path) -> dict[str, object]:
    return _load_json(_connector_manifest_path(project_root), {"connectors": []})


def _write_connector_manifest(project_root: str | Path, payload: dict[str, object]) -> None:
    _write_json(_connector_manifest_path(project_root), payload)


def _active_slug_set(project_root: str | Path) -> set[str]:
    manifest = _load_skills_manifest(project_root)
    return {str(entry.get("slug")) for entry in manifest.get("skills", []) if entry.get("active")}


def _detect_license_text(path: Path) -> dict[str, str] | None:
    for candidate in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        license_path = path / candidate
        if license_path.exists():
            first_line = next((line.strip() for line in license_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()), "License file")
            return {"path": candidate, "summary": first_line[:120]}
    return None


def _summarize_readme(path: Path) -> dict[str, str] | None:
    for candidate in ("README.md", "README", "readme.md"):
        readme_path = path / candidate
        if readme_path.exists():
            lines = [line.strip() for line in readme_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
            title = next((line.lstrip("# ").strip() for line in lines if line.startswith("#")), path.name)
            summary = next((line for line in lines if not line.startswith("#") and len(line) > 20), title)
            return {"path": candidate, "title": title[:120], "summary": summary[:280]}
    return None


def _copy_source(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination / source.name)


def _ingest_from_git(git_url: str, destination: Path, ref: str | None = None) -> str | None:
    if destination.exists():
        shutil.rmtree(destination)
    subprocess.run(["git", "clone", git_url, str(destination)], text=True, capture_output=True, check=True)
    if ref:
        subprocess.run(["git", "-C", str(destination), "checkout", ref], text=True, capture_output=True, check=True)
    result = subprocess.run(["git", "-C", str(destination), "rev-parse", "HEAD"], text=True, capture_output=True, check=True)
    return result.stdout.strip()


def list_enterprise_skills(project_root: str | Path) -> list[dict[str, object]]:
    manifest = _load_skills_manifest(project_root)
    return list(manifest.get("skills", []))


def active_enterprise_skills(project_root: str | Path) -> list[dict[str, object]]:
    return [entry for entry in list_enterprise_skills(project_root) if entry.get("active")]


def ingest_enterprise_skill(
    project_root: str | Path,
    *,
    name: str,
    path: str | Path | None = None,
    git_url: str | None = None,
    ref: str | None = None,
    activate: bool | None = None,
    kind: str = "enterprise",
) -> dict[str, object]:
    root = Path(project_root).resolve()
    slug = _normalize_slug(name)
    source_dir = _skills_root(root) / "sources" / slug
    resolved_revision = None
    install_mode = "path"
    if git_url:
        resolved_revision = _ingest_from_git(git_url, source_dir, ref=ref)
        install_mode = "git"
    elif path is not None:
        _copy_source(Path(path).resolve(), source_dir)
    else:
        raise ValueError("Either `path` or `git_url` is required to ingest an enterprise skill.")
    now = datetime.now(UTC).isoformat()
    entry = {
        "slug": slug,
        "name": name,
        "kind": kind,
        "install_path": str(source_dir),
        "source_path": str(Path(path).resolve()) if path is not None else None,
        "git_url": git_url,
        "requested_ref": ref,
        "resolved_revision": resolved_revision,
        "install_mode": install_mode,
        "license": _detect_license_text(source_dir),
        "readme": _summarize_readme(source_dir),
        "active": True if activate is None else bool(activate),
        "installed_at": now,
        "updated_at": now,
    }
    manifest = _load_skills_manifest(root)
    skills = [item for item in manifest.get("skills", []) if item.get("slug") != slug]
    skills.append(entry)
    manifest["skills"] = sorted(skills, key=lambda item: str(item.get("slug", "")))
    _write_skills_manifest(root, manifest)
    return entry


def generate_enterprise_skill(
    project_root: str | Path,
    *,
    name: str,
    source_paths: list[str | Path],
    kind: str = "domain",
    activate: bool = True,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    slug = _normalize_slug(name)
    destination = _skills_root(root) / "generated" / slug
    destination.mkdir(parents=True, exist_ok=True)
    resolved_sources = [Path(item).resolve() for item in source_paths]
    existing = [path for path in resolved_sources if path.exists()]
    evidence = [path.name for path in existing[:12]]
    sections = []
    for path in existing[:8]:
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            snippet = next((line for line in lines if not line.startswith("#")), "")[:220]
            sections.append(f"- `{path.name}`: {snippet or 'Source file included for enterprise context.'}")
        else:
            sections.append(f"- `{path.name}/`: directory included for enterprise context.")
    skill_text = "\n".join(
        [
            f"# {name}",
            "",
            "## Purpose",
            f"This is a Skilgen-generated enterprise skill for `{name}`. It consolidates reusable enterprise context for coding agents.",
            "",
            "## Source Inputs",
            *([f"- `{path}`" for path in existing] or ["- No source inputs were provided."]),
            "",
            "## Reusable Guidance",
            f"- Treat this as a `{kind}`-level enterprise skill.",
            "- Load it alongside project-local skills when the task crosses repo boundaries or relies on enterprise standards.",
            "- Prefer stable enterprise conventions over ad-hoc repo-specific assumptions when they conflict.",
            "",
            "## Evidence Snapshot",
            *(sections or ["- No detailed evidence snapshot was generated."]),
            "",
        ]
    )
    (destination / "SKILL.md").write_text(skill_text, encoding="utf-8")
    (destination / "SUMMARY.md").write_text(
        f"# {name}\n\nGenerated enterprise skill with {len(existing)} source inputs. Key evidence: {', '.join(evidence) or 'none'}.\n",
        encoding="utf-8",
    )
    entry = {
        "slug": slug,
        "name": name,
        "kind": kind,
        "install_path": str(destination),
        "source_path": None,
        "git_url": None,
        "requested_ref": None,
        "resolved_revision": None,
        "install_mode": "generated",
        "license": None,
        "readme": {"path": "SUMMARY.md", "title": name, "summary": f"Generated enterprise skill from {len(existing)} source inputs."},
        "active": activate,
        "installed_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        "generated_from": [str(path) for path in existing],
        "skill_path": str((destination / "SKILL.md")),
        "summary_path": str((destination / "SUMMARY.md")),
    }
    manifest = _load_skills_manifest(root)
    skills = [item for item in manifest.get("skills", []) if item.get("slug") != slug]
    skills.append(entry)
    manifest["skills"] = sorted(skills, key=lambda item: str(item.get("slug", "")))
    _write_skills_manifest(root, manifest)
    return entry


def connector_catalog(system: str | None = None, search: str | None = None) -> dict[str, object]:
    entries = [asdict(item) for item in CONNECTOR_CATALOG]
    if system:
        entries = [entry for entry in entries if entry["system"].lower() == system.lower()]
    if search:
        needle = search.lower()
        entries = [
            entry
            for entry in entries
            if needle in entry["slug"] or needle in entry["name"].lower() or any(needle in tag.lower() for tag in entry.get("tags", []))
        ]
    return {"connectors": entries, "count": len(entries)}


def _catalog_connector(slug: str) -> MCPConnector | None:
    return next((item for item in CONNECTOR_CATALOG if item.slug == slug), None)


def _connector_keywords() -> dict[str, tuple[str, ...]]:
    return {
        "chrome-devtools": ("chrome devtools", "devtools"),
        "playwright": ("playwright",),
        "jira": ("jira", "atlassian"),
        "confluence": ("confluence",),
        "compass": ("atlassian compass", "compass"),
        "slack": ("slack",),
        "servicenow": ("servicenow", "service-now"),
        "datadog": ("datadog",),
        "sentry": ("sentry",),
        "github-enterprise": ("github", "github enterprise"),
        "gitlab": ("gitlab",),
        "azure": ("azure", "azd", "azure subscription"),
        "azure-devops": ("azure devops", "ado", "pipelines"),
        "azure-kubernetes": ("aks", "azure kubernetes"),
        "kubernetes": ("k8s", "kubernetes", "kubectl"),
        "terraform": ("terraform", "tfstate", "hashicorp"),
        "snowflake": ("snowflake",),
        "postgres": ("postgres", "postgresql", "psycopg"),
        "mongodb": ("mongodb", "atlas"),
        "notion": ("notion",),
        "microsoft-learn": ("learn.microsoft.com", "microsoft docs", "azure docs"),
        "stripe": ("stripe",),
        "figma": ("figma",),
        "elasticsearch": ("elasticsearch", "esql"),
        "sharepoint": ("sharepoint", "microsoft graph"),
        "okta": ("okta",),
    }


def recommend_mcp_connectors(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    deny = set(config.mcp_connector_denylist)
    allow = set(config.mcp_connector_allowlist)
    haystacks: list[str] = []
    for path in list(root.rglob("*"))[:400]:
        if any(part in {".git", ".skilgen", "__pycache__", "node_modules"} for part in path.parts):
            continue
        haystacks.append(path.name.lower())
        if path.is_file() and path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".yml", ".yaml", ".json", ".tf"}:
            text = path.read_text(encoding="utf-8", errors="ignore")[:4000].lower()
            haystacks.append(text)
    blob = "\n".join(haystacks)
    detected: list[dict[str, object]] = []
    for connector in CONNECTOR_CATALOG:
        if connector.slug in deny:
            continue
        if allow and connector.slug not in allow:
            continue
        if config.mcp_connectors_require_official_source and not connector.official_source_url:
            continue
        if config.mcp_connectors_require_oauth and not connector.oauth_supported:
            continue
        matches = [keyword for keyword in _connector_keywords().get(connector.slug, ()) if keyword in blob]
        if matches:
            detected.append(
                {
                    **asdict(connector),
                    "official_source_verified": bool(connector.official_source_url),
                    "reasons": [f"Detected connector keywords: {', '.join(matches[:3])}."],
                }
            )
    return {"connectors": detected, "count": len(detected)}


def active_mcp_connectors(project_root: str | Path) -> list[dict[str, object]]:
    manifest = _load_connector_manifest(project_root)
    return [entry for entry in manifest.get("connectors", []) if entry.get("active")]


def activate_mcp_connector(project_root: str | Path, slug: str) -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    now = datetime.now(UTC).isoformat()
    catalog_connector = _catalog_connector(slug)
    if catalog_connector is None:
        raise ValueError(f"Unknown MCP connector: {slug}")
    if config.mcp_connectors_require_official_source and not catalog_connector.official_source_url:
        raise ValueError(f"MCP connector `{slug}` does not have a verified official source configured.")
    if config.mcp_connectors_require_oauth and not catalog_connector.oauth_supported:
        raise ValueError(f"MCP connector `{slug}` does not meet the project's OAuth requirements.")
    connector = asdict(catalog_connector)
    manifest = _load_connector_manifest(root)
    connectors = [entry for entry in manifest.get("connectors", []) if entry.get("slug") != slug]
    connector["active"] = True
    connector["activated_at"] = now
    connector["official_source_verified"] = bool(catalog_connector.official_source_url)
    connector["authorization"] = {
        "scheme": catalog_connector.auth_scheme,
        "oauth_supported": catalog_connector.oauth_supported,
        "status": "pending_oauth" if catalog_connector.oauth_supported else "manual_setup_required",
        "principles": list(catalog_connector.oauth_principles),
    }
    connector["runtime_ready"] = bool(catalog_connector.official_source_url and catalog_connector.oauth_supported)
    connectors.append(connector)
    manifest["connectors"] = sorted(connectors, key=lambda item: str(item.get("slug", "")))
    _write_connector_manifest(root, manifest)
    return connector


def deactivate_mcp_connector(project_root: str | Path, slug: str) -> dict[str, object]:
    root = Path(project_root).resolve()
    manifest = _load_connector_manifest(root)
    updated = None
    connectors: list[dict[str, object]] = []
    for entry in manifest.get("connectors", []):
        if entry.get("slug") == slug:
            item = dict(entry)
            item["active"] = False
            updated = item
            connectors.append(item)
        else:
            connectors.append(entry)
    if updated is None:
        raise ValueError(f"MCP connector is not active: {slug}")
    manifest["connectors"] = connectors
    _write_connector_manifest(root, manifest)
    return updated


def ensure_enterprise_skills_for_project(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    manifest = _load_skills_manifest(root)
    existing_skills = list(manifest.get("skills", []))
    existing_by_source = {
        str(entry.get("source_path")): entry for entry in existing_skills if entry.get("source_path")
    }
    existing_by_git = {
        str(entry.get("git_url")): entry for entry in existing_skills if entry.get("git_url")
    }
    installed: list[dict[str, object]] = []
    already_present: list[dict[str, object]] = []
    errors: list[str] = []

    for raw_path in config.enterprise_skill_paths:
        try:
            resolved = str(Path(raw_path).resolve())
            if resolved in existing_by_source:
                already_present.append(existing_by_source[resolved])
                continue
            entry = ingest_enterprise_skill(
                root,
                name=Path(raw_path).resolve().name,
                path=raw_path,
                activate=True,
                kind="enterprise",
            )
            installed.append(entry)
            existing_by_source[resolved] = entry
        except Exception as exc:  # pragma: no cover - defensive error collection
            errors.append(f"{raw_path}: {exc}")

    for git_url in config.enterprise_skill_git_urls:
        try:
            if git_url in existing_by_git:
                already_present.append(existing_by_git[git_url])
                continue
            entry = ingest_enterprise_skill(
                root,
                name=_name_from_git_url(git_url),
                git_url=git_url,
                activate=True,
                kind="enterprise",
            )
            installed.append(entry)
            existing_by_git[git_url] = entry
        except Exception as exc:  # pragma: no cover - defensive error collection
            errors.append(f"{git_url}: {exc}")

    recommended = recommend_mcp_connectors(root).get("connectors", [])
    active_slugs = {str(entry.get("slug")) for entry in active_mcp_connectors(root)}
    auto_activated: list[dict[str, object]] = []
    already_active: list[dict[str, object]] = []
    if config.auto_activate_mcp_connectors:
        for entry in recommended:
            slug = str(entry.get("slug", ""))
            if slug in active_slugs:
                already_active.append(entry)
                continue
            try:
                connector = activate_mcp_connector(root, slug)
                auto_activated.append(connector)
                active_slugs.add(slug)
            except Exception as exc:  # pragma: no cover - defensive error collection
                errors.append(f"{slug}: {exc}")

    return {
        "installed_skills": installed,
        "already_present_skills": already_present,
        "errors": errors,
        "recommended_connectors": recommended,
        "auto_activated_connectors": auto_activated,
        "already_active_connectors": already_active,
    }
