from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import shutil
import subprocess
from pathlib import Path


@dataclass(frozen=True)
class ExternalSkillSource:
    slug: str
    name: str
    ecosystem: str
    publisher: str
    description: str
    repository_url: str
    source_path: str | None
    docs_url: str
    category: str = "official"
    trust_level: str = "official"
    supported_agents: tuple[str, ...] = ()
    install_strategy: str = "git_clone"
    tags: tuple[str, ...] = ()


CATALOG: tuple[ExternalSkillSource, ...] = (
    ExternalSkillSource(
        slug="anthropic-skills",
        name="Anthropic Skills",
        ecosystem="anthropic",
        publisher="Anthropic",
        description="Official Anthropic skills collection with reference skills and SKILL template patterns.",
        repository_url="https://github.com/anthropics/skills.git",
        source_path="skills",
        docs_url="https://github.com/anthropics/skills/tree/main/skills",
        supported_agents=("Claude Code",),
        tags=("official", "claude", "skills"),
    ),
    ExternalSkillSource(
        slug="langchain-skills",
        name="LangChain Skills",
        ecosystem="langchain",
        publisher="LangChain AI",
        description="Official LangChain skills for LangChain, LangGraph, Deep Agents, RAG, and orchestration flows.",
        repository_url="https://github.com/langchain-ai/langchain-skills.git",
        source_path=None,
        docs_url="https://github.com/langchain-ai/langchain-skills",
        supported_agents=("Claude Code", "Cursor", "Windsurf", "Codex"),
        tags=("official", "deep-agents", "langchain"),
    ),
    ExternalSkillSource(
        slug="langsmith-skills",
        name="LangSmith Skills",
        ecosystem="langchain",
        publisher="LangChain AI",
        description="Official LangSmith skills for observability, evaluation, prompt engineering, and tracing workflows.",
        repository_url="https://github.com/langchain-ai/langsmith-skills.git",
        source_path=None,
        docs_url="https://github.com/langchain-ai/langsmith-skills",
        supported_agents=("Claude Code", "Cursor", "Codex"),
        tags=("official", "langsmith", "evaluation", "observability"),
    ),
    ExternalSkillSource(
        slug="huggingface-skills",
        name="Hugging Face Skills",
        ecosystem="huggingface",
        publisher="Hugging Face",
        description="Official Hugging Face skills collection for hub, datasets, jobs, trainers, and evaluation workflows.",
        repository_url="https://github.com/huggingface/skills.git",
        source_path=None,
        docs_url="https://github.com/huggingface/skills",
        supported_agents=("Claude Code", "Codex", "Gemini CLI", "Cursor"),
        tags=("official", "huggingface", "skills"),
    ),
    ExternalSkillSource(
        slug="huggingface-upskill",
        name="Hugging Face Upskill",
        ecosystem="huggingface",
        publisher="Hugging Face",
        description="Official Hugging Face tool for auto-generating and benchmarking skills with teacher-student approaches.",
        repository_url="https://github.com/huggingface/upskill.git",
        source_path=None,
        docs_url="https://github.com/huggingface/upskill",
        supported_agents=("Claude Code", "Codex", "Gemini CLI"),
        tags=("official", "huggingface", "generation", "benchmarking"),
    ),
    ExternalSkillSource(
        slug="awesome-copilot",
        name="Awesome Copilot",
        ecosystem="github",
        publisher="GitHub / Microsoft",
        description="Official GitHub Copilot skill and workflow examples for Azure, AWS, BigQuery, IAM, and VS Code.",
        repository_url="https://github.com/github/awesome-copilot.git",
        source_path=None,
        docs_url="https://github.com/github/awesome-copilot",
        supported_agents=("GitHub Copilot", "VS Code"),
        tags=("official", "copilot", "workflows"),
    ),
    ExternalSkillSource(
        slug="agentskills-spec",
        name="AgentSkills Spec",
        ecosystem="spec",
        publisher="agentskills.io",
        description="Open standard specification and documentation for the SKILL.md format.",
        repository_url="https://github.com/agentskills/agentskills.git",
        source_path=None,
        docs_url="https://github.com/agentskills/agentskills",
        category="spec",
        trust_level="spec",
        supported_agents=("All agents",),
        tags=("spec", "skill-md", "standard"),
    ),
    ExternalSkillSource(
        slug="n8n-mcp-patterns",
        name="n8n MCP Patterns",
        ecosystem="n8n",
        publisher="czlonkowski",
        description="n8n skills for code nodes, expressions, MCP tooling, workflow patterns, and validation.",
        repository_url="https://github.com/czlonkowski/n8n-mcp.git",
        source_path=None,
        docs_url="https://github.com/czlonkowski/n8n-mcp",
        category="framework",
        trust_level="community",
        supported_agents=("Claude Code", "Cursor", "Windsurf"),
        tags=("n8n", "mcp", "workflow"),
    ),
    ExternalSkillSource(
        slug="ai-research-skills",
        name="AI Research Skills",
        ecosystem="multi-framework",
        publisher="Orchestra Research",
        description="83+ research and coding skills for LangChain, LlamaIndex, CrewAI, fine-tuning, RLHF, and RAG.",
        repository_url="https://github.com/Orchestra-Research/AI-Research-SKILLS.git",
        source_path=None,
        docs_url="https://github.com/Orchestra-Research/AI-Research-SKILLS",
        category="framework",
        trust_level="community",
        supported_agents=("Claude Code", "Codex", "Cursor", "Gemini CLI"),
        tags=("research", "multi-framework", "rag"),
    ),
    ExternalSkillSource(
        slug="context-engineering-skills",
        name="Context Engineering Skills",
        ecosystem="framework",
        publisher="muratcankoylan",
        description="Context engineering, multi-agent architecture, memory patterns, and LLM-as-judge skills.",
        repository_url="https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering.git",
        source_path=None,
        docs_url="https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering",
        category="framework",
        trust_level="community",
        supported_agents=("Claude Code", "Codex", "Gemini CLI"),
        tags=("context-engineering", "memory", "multi-agent"),
    ),
    ExternalSkillSource(
        slug="skill-seekers",
        name="Skill Seekers",
        ecosystem="tooling",
        publisher="yusufkaraaslan",
        description="Tooling to convert docs, sites, repos, and PDFs into SKILL.md with RAG assets.",
        repository_url="https://github.com/yusufkaraaslan/Skill_Seekers.git",
        source_path=None,
        docs_url="https://github.com/yusufkaraaslan/Skill_Seekers",
        category="tooling",
        trust_level="community",
        supported_agents=("All agents",),
        tags=("tooling", "conversion", "rag"),
    ),
    ExternalSkillSource(
        slug="awesome-agent-skills-voltagent",
        name="Awesome Agent Skills (VoltAgent)",
        ecosystem="directory",
        publisher="VoltAgent",
        description="Large directory of official and community agent skills across Anthropic, Codex, LangChain, and n8n.",
        repository_url="https://github.com/VoltAgent/awesome-agent-skills.git",
        source_path=None,
        docs_url="https://github.com/VoltAgent/awesome-agent-skills",
        category="directory",
        trust_level="directory",
        supported_agents=("Claude Code", "Codex", "Gemini CLI", "Cursor"),
        tags=("directory", "aggregator", "awesome-list"),
    ),
    ExternalSkillSource(
        slug="awesome-agent-skills-skillmatic",
        name="Awesome Agent Skills (skillmatic-ai)",
        ecosystem="directory",
        publisher="skillmatic-ai",
        description="Directory of agent skills, authoring guides, scanners, and marketplace-style discovery links.",
        repository_url="https://github.com/skillmatic-ai/awesome-agent-skills.git",
        source_path=None,
        docs_url="https://github.com/skillmatic-ai/awesome-agent-skills",
        category="directory",
        trust_level="directory",
        supported_agents=("All agents",),
        tags=("directory", "aggregator", "marketplace"),
    ),
    ExternalSkillSource(
        slug="awesome-agent-skills-heilcheng",
        name="Awesome Agent Skills (heilcheng)",
        ecosystem="directory",
        publisher="heilcheng",
        description="Directory of skills for Claude, Codex, GitHub Copilot, VS Code, and Google Workspace agent workflows.",
        repository_url="https://github.com/heilcheng/awesome-agent-skills.git",
        source_path=None,
        docs_url="https://github.com/heilcheng/awesome-agent-skills",
        category="directory",
        trust_level="directory",
        supported_agents=("Claude Code", "Codex", "Copilot"),
        tags=("directory", "workspace", "copilot"),
    ),
    ExternalSkillSource(
        slug="awesome-llm-skills",
        name="Awesome LLM Skills",
        ecosystem="directory",
        publisher="Prat011",
        description="Directory covering Notion, Google Workspace, multi-agent, Gemini CLI, OpenCode, and Qwen-ready skills.",
        repository_url="https://github.com/Prat011/awesome-llm-skills.git",
        source_path=None,
        docs_url="https://github.com/Prat011/awesome-llm-skills",
        category="directory",
        trust_level="directory",
        supported_agents=("All agents",),
        tags=("directory", "multi-agent", "workspace"),
    ),
    ExternalSkillSource(
        slug="curated-ai-agent-skills",
        name="Curated AI Agent Skills",
        ecosystem="curated",
        publisher="MoizIbnYousaf",
        description="Curated personal library with trust metadata, provenance, and universal installation ideas.",
        repository_url="https://github.com/MoizIbnYousaf/AI-Agent-Skills.git",
        source_path=None,
        docs_url="https://github.com/MoizIbnYousaf/AI-Agent-Skills",
        category="curated",
        trust_level="curated",
        supported_agents=("Claude Code", "Codex", "cross-agent"),
        tags=("curated", "provenance", "trust"),
    ),
    ExternalSkillSource(
        slug="skills-benchmarks",
        name="Skills Benchmarks",
        ecosystem="benchmarks",
        publisher="LangChain AI",
        description="Benchmark suite for measuring skill quality and performance across LangChain and LangSmith tasks.",
        repository_url="https://github.com/langchain-ai/skills-benchmarks.git",
        source_path=None,
        docs_url="https://github.com/langchain-ai/skills-benchmarks",
        category="benchmarks",
        trust_level="official",
        supported_agents=("Claude Code", "Codex"),
        tags=("benchmarks", "langchain", "evaluation"),
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


def _serialize_entry(entry: ExternalSkillSource, installed: dict[str, object] | None) -> dict[str, object]:
    payload = asdict(entry)
    payload["installed"] = installed is not None
    payload["install_path"] = installed.get("install_path") if installed else None
    payload["installed_metadata"] = installed
    return payload


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
        haystack = " ".join(
            (
                entry.slug,
                entry.name,
                entry.ecosystem,
                entry.publisher,
                entry.description,
                " ".join(entry.tags),
                " ".join(entry.supported_agents),
            )
        ).lower()
        if needle and needle not in haystack:
            continue
        items.append(_serialize_entry(entry, installed.get(entry.slug)))
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
    return _serialize_entry(entry, installed)


def _build_install_metadata(
    *,
    slug: str,
    name: str,
    ecosystem: str,
    repository_url: str,
    source_path: str | None,
    docs_url: str,
    trust_level: str,
    description: str,
    install_path: Path,
) -> dict[str, object]:
    return {
        "slug": slug,
        "name": name,
        "ecosystem": ecosystem,
        "repository_url": repository_url,
        "source_path": source_path,
        "docs_url": docs_url,
        "trust_level": trust_level,
        "description": description,
        "install_path": str(install_path),
        "installed_at": datetime.now(UTC).isoformat(),
    }


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

    metadata = _build_install_metadata(
        slug=resolved_slug,
        name=resolved_name,
        ecosystem=ecosystem,
        repository_url=repository_url,
        source_path=source_path,
        docs_url=docs_url,
        trust_level=trust_level,
        description=description,
        install_path=install_path,
    )
    (install_path / "skilgen-source.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    manifest = _load_manifest(project_root)
    skills = [entry for entry in manifest.get("skills", []) if isinstance(entry, dict) and entry.get("slug") != resolved_slug]
    skills.append(metadata)
    manifest["skills"] = sorted(skills, key=lambda entry: str(entry.get("slug", "")))
    _write_manifest(project_root, manifest)
    return metadata


def sync_external_skill(*, project_root: str | Path = ".", slug: str) -> dict[str, object]:
    installed = _installed_by_slug(project_root).get(slug)
    if installed is None:
        raise KeyError(f"External skill source is not installed: {slug}")
    install_path = Path(str(installed["install_path"]))
    result = subprocess.run(
        ["git", "-C", str(install_path), "pull", "--ff-only"],
        check=True,
        capture_output=True,
        text=True,
    )
    installed["synced_at"] = datetime.now(UTC).isoformat()
    installed["sync_stdout"] = result.stdout.strip()
    installed["sync_stderr"] = result.stderr.strip()
    manifest = _load_manifest(project_root)
    manifest["skills"] = sorted(
        [
            installed if isinstance(entry, dict) and entry.get("slug") == slug else entry
            for entry in manifest.get("skills", [])
            if isinstance(entry, dict)
        ],
        key=lambda entry: str(entry.get("slug", "")),
    )
    _write_manifest(project_root, manifest)
    (install_path / "skilgen-source.json").write_text(json.dumps(installed, indent=2), encoding="utf-8")
    return installed


def remove_external_skill(*, project_root: str | Path = ".", slug: str) -> dict[str, object]:
    installed = _installed_by_slug(project_root).get(slug)
    if installed is None:
        raise KeyError(f"External skill source is not installed: {slug}")
    install_path = Path(str(installed["install_path"]))
    if install_path.exists():
        shutil.rmtree(install_path)
    manifest = _load_manifest(project_root)
    manifest["skills"] = [
        entry
        for entry in manifest.get("skills", [])
        if isinstance(entry, dict) and entry.get("slug") != slug
    ]
    _write_manifest(project_root, manifest)
    return {
        "slug": slug,
        "removed": True,
        "install_path": str(install_path),
    }
