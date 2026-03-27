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


CONNECTOR_CATALOG: tuple[MCPConnector, ...] = (
    MCPConnector("jira", "Jira", "Atlassian", "Track issues, delivery state, and engineering workflows.", ("tickets", "planning", "enterprise")),
    MCPConnector("confluence", "Confluence", "Atlassian", "Search and read internal documentation, playbooks, and architecture notes.", ("docs", "wiki", "enterprise")),
    MCPConnector("slack", "Slack", "Slack", "Read team communication context and incident coordination threads.", ("chat", "incident", "ops")),
    MCPConnector("servicenow", "ServiceNow", "ServiceNow", "Work with enterprise tickets, service requests, and incident records.", ("itsm", "incident", "enterprise")),
    MCPConnector("datadog", "Datadog", "Datadog", "Inspect metrics, traces, monitors, and production signals.", ("observability", "metrics", "ops")),
    MCPConnector("sentry", "Sentry", "Sentry", "Inspect application errors, releases, and issue trends.", ("errors", "observability", "ops")),
    MCPConnector("github-enterprise", "GitHub Enterprise", "GitHub", "Read enterprise repositories, pull requests, and actions state.", ("code", "git", "devex")),
    MCPConnector("gitlab", "GitLab", "GitLab", "Read merge requests, CI pipelines, and source repos.", ("code", "ci", "devex")),
    MCPConnector("kubernetes", "Kubernetes", "Cloud Native", "Inspect cluster resources, workloads, rollout state, and runtime incidents.", ("infra", "ops", "deployments")),
    MCPConnector("terraform", "Terraform", "HashiCorp", "Inspect infrastructure definitions, plans, and cloud rollout workflows.", ("infra", "iac", "cloud")),
    MCPConnector("snowflake", "Snowflake", "Snowflake", "Work with enterprise data warehouse context and SQL operations.", ("data", "warehouse", "analytics")),
    MCPConnector("postgres", "Postgres", "PostgreSQL", "Inspect schemas, queries, and transactional application data.", ("database", "sql", "data")),
    MCPConnector("notion", "Notion", "Notion", "Read shared docs, product specs, and operational notes.", ("docs", "planning", "workspace")),
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


def _connector_keywords() -> dict[str, tuple[str, ...]]:
    return {
        "jira": ("jira", "atlassian"),
        "confluence": ("confluence",),
        "slack": ("slack",),
        "servicenow": ("servicenow", "service-now"),
        "datadog": ("datadog",),
        "sentry": ("sentry",),
        "github-enterprise": ("github", "github enterprise"),
        "gitlab": ("gitlab",),
        "kubernetes": ("k8s", "kubernetes", "kubectl"),
        "terraform": ("terraform", "tfstate", "hashicorp"),
        "snowflake": ("snowflake",),
        "postgres": ("postgres", "postgresql", "psycopg"),
        "notion": ("notion",),
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
        matches = [keyword for keyword in _connector_keywords().get(connector.slug, ()) if keyword in blob]
        if matches:
            detected.append({**asdict(connector), "reasons": [f"Detected connector keywords: {', '.join(matches[:3])}."]})
    return {"connectors": detected, "count": len(detected)}


def active_mcp_connectors(project_root: str | Path) -> list[dict[str, object]]:
    manifest = _load_connector_manifest(project_root)
    return [entry for entry in manifest.get("connectors", []) if entry.get("active")]


def activate_mcp_connector(project_root: str | Path, slug: str) -> dict[str, object]:
    root = Path(project_root).resolve()
    now = datetime.now(UTC).isoformat()
    connector = next((asdict(item) for item in CONNECTOR_CATALOG if item.slug == slug), None)
    if connector is None:
        raise ValueError(f"Unknown MCP connector: {slug}")
    manifest = _load_connector_manifest(root)
    connectors = [entry for entry in manifest.get("connectors", []) if entry.get("slug") != slug]
    connector["active"] = True
    connector["activated_at"] = now
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
