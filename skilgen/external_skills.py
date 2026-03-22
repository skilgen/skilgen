from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, UTC
import json
import shutil
import subprocess
from pathlib import Path


@dataclass(frozen=True)
class ExternalSkillSource:
    slug: str
    name: str
    ecosystem: str
    description: str
    repository_url: str
    source_path: str | None
    docs_url: str
    install_strategy: str = "git_clone"
    trust_level: str = "official"
    tags: tuple[str, ...] = ()


CATALOG: tuple[ExternalSkillSource, ...] = (
    ExternalSkillSource(
        slug="anthropic-skills",
        name="Anthropic Skills",
        ecosystem="anthropic",
        description="Official Anthropic skills collection for Claude-style agents and workflows.",
        repository_url="https://github.com/anthropics/skills.git",
        source_path="skills",
        docs_url="https://github.com/anthropics/skills/tree/main/skills",
        tags=("official", "claude", "skills"),
    ),
    ExternalSkillSource(
        slug="langchain-skills",
        name="LangChain Skills",
        ecosystem="langchain",
        description="LangChain and Deep Agents skill ecosystem for reusable agent capabilities.",
        repository_url="https://github.com/langchain-ai/langchain-skills.git",
        source_path=None,
        docs_url="https://github.com/langchain-ai/langchain-skills",
        tags=("official", "deep-agents", "langchain"),
    ),
    ExternalSkillSource(
        slug="huggingface-skills",
        name="Hugging Face Skills",
        ecosystem="huggingface",
        description="Official Hugging Face skills collection for portable agent workflows and tools.",
        repository_url="https://github.com/huggingface/skills.git",
        source_path=None,
        docs_url="https://github.com/huggingface/skills",
        tags=("official", "huggingface", "skills"),
    ),
    ExternalSkillSource(
        slug="n8n-agent-templates",
        name="n8n Agent Templates",
        ecosystem="n8n",
        description="High-signal n8n agent and workflow templates that can be adapted into Skilgen-managed skills.",
        repository_url="https://github.com/n8n-io/n8n.git",
        source_path="packages/@n8n/nodes-langchain",
        docs_url="https://docs.n8n.io/advanced-ai/",
        trust_level="adapter",
        tags=("n8n", "templates", "workflow"),
    ),
    ExternalSkillSource(
        slug="crewai-patterns",
        name="CrewAI Patterns",
        ecosystem="crewai",
        description="CrewAI-compatible tools, knowledge, and reusable patterns normalized through Skilgen.",
        repository_url="https://github.com/crewAIInc/crewAI.git",
        source_path=None,
        docs_url="https://docs.crewai.com/en/concepts/tools",
        trust_level="adapter",
        tags=("crewai", "tools", "knowledge"),
    ),
)


def _external_skills_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "external-skills"


def _manifest_path(project_root: str | Path) -> Path:
    return _external_skills_root(project_root) / "manifest.json"


def _sources_dir(project_root: str | Path) -> Path:
    return _external_skills_root(project_root) / "sources"


def _normalize_slug(name: str) -> str:
    return "-".join(part for part in "".join(ch.lower() if ch.isalnum() else "-" for ch in name).split("-") if part)


def _load_manifest(project_root: str | Path) -> dict[str, object]:
    path = _manifest_path(project_root)
    if not path.exists():
        return {"skills": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_manifest(project_root: str | Path, payload: dict[str, object]) -> None:
    root = _external_skills_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    _manifest_path(project_root).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _installed_by_slug(project_root: str | Path) -> dict[str, dict[str, object]]:
    manifest = _load_manifest(project_root)
    entries = manifest.get("skills", [])
    if not isinstance(entries, list):
        return {}
    return {
        str(entry.get("slug")): entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("slug")
    }


def _catalog_entry(slug: str) -> ExternalSkillSource | None:
    for entry in CATALOG:
        if entry.slug == slug:
            return entry
    return None


def list_external_skills(
    project_root: str | Path = ".",
    *,
    ecosystem: str | None = None,
    search: str | None = None,
) -> dict[str, object]:
    installed = _installed_by_slug(project_root)
    items: list[dict[str, object]] = []
    needle = search.lower() if search else None
    for entry in CATALOG:
        if ecosystem and entry.ecosystem != ecosystem:
            continue
        haystack = " ".join((entry.slug, entry.name, entry.ecosystem, entry.description, " ".join(entry.tags))).lower()
        if needle and needle not in haystack:
            continue
        payload = asdict(entry)
        payload["installed"] = entry.slug in installed
        payload["install_path"] = installed.get(entry.slug, {}).get("install_path")
        items.append(payload)
    return {
        "skills": items,
        "ecosystems": sorted({entry["ecosystem"] for entry in items}),
        "count": len(items),
    }


def get_external_skill(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    entry = _catalog_entry(slug)
    if entry is None:
        raise KeyError(f"Unknown external skill source: {slug}")
    installed = _installed_by_slug(project_root).get(slug)
    payload = asdict(entry)
    payload["installed"] = installed is not None
    payload["install_path"] = installed.get("install_path") if installed else None
    payload["installed_metadata"] = installed
    return payload


def install_external_skill(
    *,
    project_root: str | Path = ".",
    slug: str | None = None,
    git_url: str | None = None,
    name: str | None = None,
    force: bool = False,
) -> dict[str, object]:
    if slug is None and git_url is None:
        raise ValueError("Provide either a catalog slug or a git_url.")

    if slug is not None:
        entry = _catalog_entry(slug)
        if entry is None:
            raise KeyError(f"Unknown external skill source: {slug}")
        resolved_slug = entry.slug
        resolved_name = entry.name
        repository_url = entry.repository_url
        ecosystem = entry.ecosystem
        source_path = entry.source_path
        docs_url = entry.docs_url
        trust_level = entry.trust_level
        description = entry.description
    else:
        assert git_url is not None
        resolved_name = name or Path(git_url.rstrip("/")).stem or "external-skill"
        resolved_slug = _normalize_slug(resolved_name)
        repository_url = git_url
        ecosystem = "custom"
        source_path = None
        docs_url = git_url
        trust_level = "custom"
        description = f"Custom external skill source installed from {git_url}."

    sources_dir = _sources_dir(project_root)
    sources_dir.mkdir(parents=True, exist_ok=True)
    install_path = sources_dir / resolved_slug
    if install_path.exists():
        if not force:
            installed = _installed_by_slug(project_root).get(resolved_slug)
            if installed is not None:
                return installed
            raise FileExistsError(f"{install_path} already exists. Use force=True to reinstall.")
        shutil.rmtree(install_path)

    subprocess.run(
        ["git", "clone", "--depth", "1", repository_url, str(install_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    metadata = {
        "slug": resolved_slug,
        "name": resolved_name,
        "ecosystem": ecosystem,
        "repository_url": repository_url,
        "source_path": source_path,
        "docs_url": docs_url,
        "trust_level": trust_level,
        "description": description,
        "install_path": str(install_path),
        "installed_at": datetime.now(UTC).isoformat(),
    }
    (install_path / "skilgen-source.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    manifest = _load_manifest(project_root)
    skills = [entry for entry in manifest.get("skills", []) if isinstance(entry, dict) and entry.get("slug") != resolved_slug]
    skills.append(metadata)
    manifest["skills"] = sorted(skills, key=lambda entry: str(entry.get("slug", "")))
    _write_manifest(project_root, manifest)
    return metadata
