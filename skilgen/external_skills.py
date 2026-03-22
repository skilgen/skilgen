from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import re
import shutil
import subprocess
from pathlib import Path

from skilgen.core.config import load_config


TRUST_SCORES = {
    "official": 5,
    "spec": 4,
    "curated": 3,
    "community": 2,
    "directory": 1,
    "custom": 1,
}


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


def _lock_path(project_root: str | Path) -> Path:
    return _external_skills_root(project_root) / "lock.json"


def _sources_dir(project_root: str | Path) -> Path:
    return _external_skills_root(project_root) / "sources"


def _normalized_dir(project_root: str | Path) -> Path:
    return _external_skills_root(project_root) / "normalized"


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


def _load_lock(project_root: str | Path) -> dict[str, object]:
    path = _lock_path(project_root)
    if not path.exists():
        return {"skills": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_lock(project_root: str | Path, payload: dict[str, object]) -> None:
    root = _external_skills_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    _lock_path(project_root).write_text(json.dumps(payload, indent=2), encoding="utf-8")


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


def _lock_by_slug(project_root: str | Path) -> dict[str, dict[str, object]]:
    lock = _load_lock(project_root)
    entries = lock.get("skills", [])
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
    payload["trust_score"] = TRUST_SCORES.get(entry.trust_level, 0)
    return payload


def installed_external_skills(project_root: str | Path = ".") -> list[dict[str, object]]:
    return sorted(_installed_by_slug(project_root).values(), key=lambda entry: str(entry.get("slug", "")))


def external_skill_lock(project_root: str | Path = ".") -> dict[str, object]:
    return _load_lock(project_root)


def active_external_skills(project_root: str | Path = ".") -> list[dict[str, object]]:
    installed = _installed_by_slug(project_root)
    locked = _lock_by_slug(project_root)
    active: list[dict[str, object]] = []
    for slug, entry in installed.items():
        lock_entry = locked.get(slug, {})
        if lock_entry.get("active"):
            active.append({**entry, "lock_metadata": lock_entry})
    return sorted(active, key=lambda entry: str(entry.get("slug", "")))


def _repo_keyword_profile(project_root: str | Path) -> set[str]:
    _, text = _repo_text_snapshot(Path(project_root).resolve())
    keywords: set[str] = set()
    keyword_map = {
        "claude": ("claude", "anthropic"),
        "langchain": ("langchain", "langgraph", "deep agents", "deepagents"),
        "langsmith": ("langsmith", "evaluation", "observability", "tracing"),
        "huggingface": ("huggingface", "hugging face", "transformers", "datasets", "diffusers"),
        "copilot": ("copilot", "github copilot", "copilot-instructions"),
        "n8n": ("n8n", "workflow"),
        "research": ("rag", "crewai", "llamaindex", "rlhf", "fine-tuning", "finetuning"),
        "benchmark": ("benchmark", "benchmarks"),
        "context": ("memory", "multi-agent", "context engineering"),
    }
    for label, needles in keyword_map.items():
        if any(needle in text for needle in needles):
            keywords.add(label)
    return keywords


def _catalog_tags(entry: ExternalSkillSource) -> set[str]:
    values = {
        entry.ecosystem.lower(),
        entry.publisher.lower(),
        entry.category.lower(),
        entry.trust_level.lower(),
        *(tag.lower() for tag in entry.tags),
        *(agent.lower() for agent in entry.supported_agents),
    }
    return {value for value in values if value}


def prioritized_active_external_skills(project_root: str | Path = ".") -> list[dict[str, object]]:
    root = Path(project_root).resolve()
    active = active_external_skills(root)
    detection_map = {
        str(entry["slug"]): entry for entry in detect_external_skill_sources(root).get("detected_skills", [])
    }
    keywords = _repo_keyword_profile(root)
    ranked: list[dict[str, object]] = []
    for entry in active:
        slug = str(entry["slug"])
        lock_metadata = entry.get("lock_metadata", {}) if isinstance(entry.get("lock_metadata"), dict) else {}
        source = _catalog_entry(slug)
        tags = _catalog_tags(source) if source is not None else set()
        matched_keywords = sorted(keyword for keyword in keywords if keyword in tags)
        detection = detection_map.get(slug)
        trust_level = str(entry.get("trust_level", source.trust_level if source else "custom"))
        trust_score = TRUST_SCORES.get(trust_level, 0)
        score = trust_score * 10
        score += len(matched_keywords) * 5
        if detection is not None:
            score += 12
        normalized = lock_metadata.get("normalized", {}) if isinstance(lock_metadata, dict) else {}
        score += min(int(normalized.get("entry_count", 0) or 0), 20)
        ranked.append(
            {
                **entry,
                "priority_score": score,
                "priority_reason": (
                    detection["reasons"][0]
                    if isinstance(detection, dict) and detection.get("reasons")
                    else f"Trust level `{trust_level}` and ecosystem fit for this repo."
                ),
                "matched_keywords": matched_keywords,
                "trust_score": trust_score,
            }
        )
    return sorted(ranked, key=lambda item: (-int(item["priority_score"]), str(item["slug"])))


def _repo_text_snapshot(project_root: Path) -> tuple[list[str], str]:
    ignored_parts = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".next", ".skilgen", "skills"}
    ignored_files = {"AGENTS.md", "ANALYSIS.md", "FEATURES.md", "REPORT.md", "TRACEABILITY.md"}
    text_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".toml", ".yml", ".yaml", ".md", ".txt"}
    paths: list[str] = []
    snippets: list[str] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in ignored_files:
            continue
        relative = path.relative_to(project_root)
        if set(relative.parts) & ignored_parts:
            continue
        rel = relative.as_posix()
        paths.append(rel.lower())
        if path.suffix.lower() in text_extensions and len(snippets) < 80:
            try:
                snippets.append(path.read_text(encoding="utf-8", errors="ignore")[:12000].lower())
            except OSError:
                continue
    return paths, "\n".join(snippets)


def detect_external_skill_sources(project_root: str | Path = ".") -> dict[str, object]:
    root = Path(project_root).resolve()
    lower_paths, text = _repo_text_snapshot(root)
    installed = _installed_by_slug(root)
    detected: list[dict[str, object]] = []
    manual_recommendations: list[dict[str, object]] = []

    def has_path(fragment: str) -> bool:
        needle = fragment.lower()
        return any(needle in path for path in lower_paths)

    def has_text(*needles: str) -> bool:
        return any(needle.lower() in text for needle in needles)

    def has_pattern(pattern: str) -> bool:
        return re.search(pattern, text, re.IGNORECASE) is not None

    def add_detected(slug: str, reason: str) -> None:
        entry = _catalog_entry(slug)
        if entry is None:
            return
        for existing in detected:
            if existing["slug"] == slug:
                existing["reasons"].append(reason)
                return
        detected.append(
            {
                "slug": slug,
                "name": entry.name,
                "ecosystem": entry.ecosystem,
                "installed": slug in installed,
                "reasons": [reason],
            }
        )

    def add_manual(slug: str, reason: str) -> None:
        entry = _catalog_entry(slug)
        if entry is None:
            return
        for existing in manual_recommendations:
            if existing["slug"] == slug:
                existing["reasons"].append(reason)
                return
        manual_recommendations.append(
            {
                "slug": slug,
                "name": entry.name,
                "ecosystem": entry.ecosystem,
                "reasons": [reason],
            }
        )

    if has_path("claude.md") or (root / ".claude").exists() or has_text("claude code", "anthropic"):
        add_detected("anthropic-skills", "Detected Claude/Anthropic repo hints.")
    if has_text("langchain", "langgraph", "deepagents", "deep agents", "langchain_openai", "langchain_anthropic"):
        add_detected("langchain-skills", "Detected LangChain/LangGraph/Deep Agents dependencies.")
    if has_text("langsmith", "langsmith_project", "langsmith tracing", "langsmith sdk"):
        add_detected("langsmith-skills", "Detected LangSmith observability or tracing usage.")
    if has_text("huggingface_hub", "transformers", "diffusers", "datasets", "trl", "sentence_transformers", "hugging face"):
        add_detected("huggingface-skills", "Detected Hugging Face package usage.")
        if has_text("benchmark", "teacher", "student", "evaluation", "trainer", "upskill"):
            add_detected("huggingface-upskill", "Detected Hugging Face evaluation or teacher/student workflow hints.")
    if has_path(".github/copilot-instructions.md") or (root / ".copilot").exists() or has_text("github copilot", "copilot-instructions"):
        add_detected("awesome-copilot", "Detected GitHub Copilot instructions or workspace setup.")
    if has_text("n8n-nodes", "n8n workflow") or has_path("n8n"):
        add_detected("n8n-mcp-patterns", "Detected n8n workflow or MCP-style repo signals.")
    if has_text("llamaindex", "crewai", "rlhf", "fine-tuning", "finetuning") or (
        has_text("pinecone", "qdrant", "chroma") and has_pattern(r"\brag\b")
    ):
        add_detected("ai-research-skills", "Detected research-stack or retrieval workflow dependencies.")
    if has_text("context engineering", "llm-as-judge", "memory strategy") or (
        has_pattern(r"\bmulti-agent\b") and has_pattern(r"\bmemory\b")
    ):
        add_detected("context-engineering-skills", "Detected context engineering or multi-agent memory patterns.")
    if has_path("skill.md") or has_path("skills/"):
        add_detected("agentskills-spec", "Detected SKILL.md-style files or an existing skills tree.")

    if any(entry["slug"] in {"langchain-skills", "langsmith-skills"} for entry in detected):
        add_manual("skills-benchmarks", "Recommended because LangChain/LangSmith was detected.")
    if detected:
        add_manual("awesome-agent-skills-voltagent", "Recommended directory of adjacent agent skills.")
        add_manual("awesome-agent-skills-skillmatic", "Recommended directory of adjacent agent skills.")
        add_manual("awesome-agent-skills-heilcheng", "Recommended directory of adjacent agent skills.")
        add_manual("awesome-llm-skills", "Recommended directory of adjacent agent skills.")
        add_manual("curated-ai-agent-skills", "Recommended curated cross-agent collection.")
        add_manual("skill-seekers", "Recommended tooling for converting docs and repos into skills.")

    return {
        "detected_skills": sorted(detected, key=lambda entry: entry["slug"]),
        "manual_recommendations": sorted(manual_recommendations, key=lambda entry: entry["slug"]),
        "installed_skills": installed_external_skills(root),
        "auto_install_count": len(detected),
    }


def _git_revision(install_path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(install_path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def _git_remote_url(install_path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(install_path), "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def _detect_license(install_path: Path) -> dict[str, str] | None:
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md", "COPYING"):
        path = install_path / name
        if not path.exists():
            continue
        try:
            first_line = next(
                (line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()),
                "",
            )
        except OSError:
            first_line = ""
        return {
            "path": path.relative_to(install_path).as_posix(),
            "summary": first_line or "License file present",
        }
    return None


def _adapter_for_source(source: ExternalSkillSource) -> str:
    if source.slug == "anthropic-skills":
        return "anthropic-skills"
    if source.slug in {"langchain-skills", "langsmith-skills"}:
        return "langchain-skills"
    if source.ecosystem == "huggingface":
        return "huggingface-skills"
    if source.category in {"directory", "curated"}:
        return "catalog-directory"
    if source.category == "spec":
        return "skill-spec"
    if source.category == "benchmarks":
        return "benchmarks"
    return "generic-repo"


def _title_from_path(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ")


def _entry_score(adapter: str, relative: str, entry_type: str) -> tuple[int, int]:
    lower = relative.lower()
    entrypoint_score = 0
    keyword_score = 0
    if entry_type == "skill":
        entrypoint_score += 40
    elif entry_type == "readme":
        entrypoint_score += 20
    elif entry_type == "doc":
        entrypoint_score += 5

    if adapter == "anthropic-skills":
        if "/skills/" in f"/{lower}" or lower.startswith("skills/"):
            keyword_score += 30
        if lower.endswith("/skill.md"):
            keyword_score += 20
        if "template" in lower:
            keyword_score += 10
    elif adapter == "langchain-skills":
        if any(token in lower for token in ("langgraph", "deep-agent", "deep_agents", "langsmith", "rag")):
            keyword_score += 25
        if lower.endswith("readme.md"):
            keyword_score += 10
    elif adapter == "huggingface-skills":
        if any(token in lower for token in ("dataset", "trainer", "evaluation", "hub", "benchmark")):
            keyword_score += 25
    elif adapter == "catalog-directory":
        if "awesome" in lower or "index" in lower:
            keyword_score += 20
    elif adapter == "skill-spec":
        if "skill" in lower or "spec" in lower:
            keyword_score += 30
    elif adapter == "benchmarks":
        if "benchmark" in lower or "eval" in lower:
            keyword_score += 30
    elif adapter == "generic-repo":
        if lower.endswith("/skill.md") or lower.endswith("readme.md"):
            keyword_score += 10

    depth_penalty = lower.count("/")
    return entrypoint_score + keyword_score - depth_penalty, depth_penalty


def _collect_normalized_entries(
    install_path: Path,
    source_path: str | None,
    *,
    adapter: str,
) -> list[dict[str, object]]:
    root = install_path / source_path if source_path else install_path
    if not root.exists():
        root = install_path
    entries: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(install_path).as_posix()
        lower = path.name.lower()
        if lower == "skill.md":
            entries.append(
                {
                    "path": relative,
                    "type": "skill",
                    "title": path.parent.name,
                    "entrypoint": True,
                    "adapter_hint": adapter,
                }
            )
        elif lower == "readme.md":
            entries.append(
                {
                    "path": relative,
                    "type": "readme",
                    "title": path.parent.name if path.parent != install_path else path.stem,
                    "entrypoint": len(path.relative_to(root).parts) <= 2,
                    "adapter_hint": adapter,
                }
            )
        elif path.suffix.lower() == ".md" and len(entries) < 50:
            entries.append(
                {
                    "path": relative,
                    "type": "doc",
                    "title": _title_from_path(path),
                    "entrypoint": False,
                    "adapter_hint": adapter,
                }
            )
    decorated = [
        (
            *_entry_score(adapter, str(entry["path"]), str(entry["type"])),
            entry,
        )
        for entry in entries
    ]
    decorated.sort(key=lambda item: (-item[0], item[1], str(item[2]["path"])))
    return [entry for _, _, entry in decorated]


def _normalize_external_skill_install(
    project_root: str | Path,
    *,
    source: ExternalSkillSource,
    install_path: Path,
) -> dict[str, object]:
    normalized_root = _normalized_dir(project_root) / source.slug
    normalized_root.mkdir(parents=True, exist_ok=True)
    adapter = _adapter_for_source(source)
    entries = _collect_normalized_entries(install_path, source.source_path, adapter=adapter)
    entry_type_counts: dict[str, int] = {}
    for entry in entries:
        entry_type_counts[str(entry["type"])] = entry_type_counts.get(str(entry["type"]), 0) + 1
    payload = {
        "slug": source.slug,
        "adapter": adapter,
        "ecosystem": source.ecosystem,
        "publisher": source.publisher,
        "trust_level": source.trust_level,
        "trust_score": TRUST_SCORES.get(source.trust_level, 0),
        "supported_agents": list(source.supported_agents),
        "repository_url": source.repository_url,
        "docs_url": source.docs_url,
        "entry_count": len(entries),
        "entry_type_counts": entry_type_counts,
        "entrypoints": [entry["path"] for entry in entries if entry["entrypoint"]][:12],
        "entries": entries[:100],
    }
    index_path = normalized_root / "index.json"
    index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary_path = normalized_root / "SUMMARY.md"
    entrypoint_lines = [f"- `{path}`" for path in payload["entrypoints"]] or [
        "- No obvious entrypoints were indexed."
    ]
    summary_lines = [
        f"# {source.name}",
        "",
        f"- Adapter: `{payload['adapter']}`",
        f"- Ecosystem: `{payload['ecosystem']}`",
        f"- Publisher: `{payload['publisher']}`",
        f"- Trust level: `{payload['trust_level']}` (score: {payload['trust_score']})",
        f"- Repository: {payload['repository_url']}",
        f"- Docs: {payload['docs_url']}",
        f"- Entrypoints indexed: {len(payload['entrypoints'])}",
        f"- Entry types: {', '.join(f'{name}={count}' for name, count in sorted(entry_type_counts.items())) or 'none'}",
        f"- Supported agents: {', '.join(payload['supported_agents']) or 'unknown'}",
        "",
        "## Entrypoints",
        *entrypoint_lines,
    ]
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    return {
        "adapter": payload["adapter"],
        "entry_count": payload["entry_count"],
        "entry_type_counts": payload["entry_type_counts"],
        "entrypoints": payload["entrypoints"],
        "publisher": payload["publisher"],
        "trust_level": payload["trust_level"],
        "trust_score": payload["trust_score"],
        "supported_agents": payload["supported_agents"],
        "repository_url": payload["repository_url"],
        "docs_url": payload["docs_url"],
        "index_path": str(index_path),
        "summary_path": str(summary_path),
    }


def _policy_allows_source(project_root: str | Path, source: ExternalSkillSource) -> tuple[bool, str | None]:
    config = load_config(Path(project_root).resolve())
    allowlist = {slug for slug in config.external_skills_allowlist}
    denylist = {slug for slug in config.external_skills_denylist}
    allowed_trust = {trust for trust in config.external_skills_allowed_trust_levels}
    policy_mode = config.external_skills_policy_mode
    if source.slug in denylist:
        return False, "source is denylisted by config"
    if allowlist and source.slug not in allowlist:
        return False, "source is not allowlisted by config"
    if allowed_trust and source.trust_level not in allowed_trust:
        return False, f"trust level '{source.trust_level}' is blocked by config"
    if policy_mode == "official_only" and source.trust_level not in {"official", "spec"}:
        return False, "policy mode official_only only permits official/spec sources"
    return True, None


def _upsert_lock_entry(project_root: str | Path, entry: dict[str, object]) -> None:
    lock = _load_lock(project_root)
    skills = [item for item in lock.get("skills", []) if isinstance(item, dict) and item.get("slug") != entry.get("slug")]
    skills.append(entry)
    lock["skills"] = sorted(skills, key=lambda item: str(item.get("slug", "")))
    _write_lock(project_root, lock)


def list_external_skills(
    project_root: str | Path = ".",
    *,
    ecosystem: str | None = None,
    search: str | None = None,
) -> dict[str, object]:
    installed = _installed_by_slug(project_root)
    locked = _lock_by_slug(project_root)
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
        payload = _serialize_entry(entry, installed.get(entry.slug))
        payload["lock_metadata"] = locked.get(entry.slug)
        payload["active"] = bool(locked.get(entry.slug, {}).get("active", False))
        items.append(payload)
    return {
        "skills": items,
        "ecosystems": sorted({entry["ecosystem"] for entry in items}),
        "count": len(items),
    }


def ranked_external_skills(project_root: str | Path = ".") -> dict[str, object]:
    items = prioritized_active_external_skills(project_root)
    return {
        "skills": items,
        "count": len(items),
    }


def external_skill_policy(project_root: str | Path = ".") -> dict[str, object]:
    config = load_config(Path(project_root).resolve())
    return {
        "policy_mode": config.external_skills_policy_mode,
        "auto_install_enabled": config.auto_install_external_skills,
        "auto_activate_enabled": config.external_skills_auto_activate,
        "allowed_trust_levels": list(config.external_skills_allowed_trust_levels),
        "allowlist": list(config.external_skills_allowlist),
        "denylist": list(config.external_skills_denylist),
        "review_required_for_auto_activation": config.external_skills_policy_mode == "review_required",
    }


def get_external_skill(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    entry = _catalog_entry(slug)
    if entry is None:
        raise KeyError(f"Unknown external skill source: {slug}")
    installed = _installed_by_slug(project_root).get(slug)
    payload = _serialize_entry(entry, installed)
    payload["lock_metadata"] = _lock_by_slug(project_root).get(slug)
    payload["active"] = bool(payload["lock_metadata"].get("active", False)) if isinstance(payload["lock_metadata"], dict) else False
    return payload


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
    install_mode: str = "manual",
    detection_reasons: list[str] | None = None,
) -> dict[str, object]:
    source = _catalog_entry(slug)
    return {
        "slug": slug,
        "name": name,
        "ecosystem": ecosystem,
        "publisher": source.publisher if source is not None else "Custom",
        "category": source.category if source is not None else "custom",
        "supported_agents": list(source.supported_agents) if source is not None else [],
        "repository_url": repository_url,
        "source_path": source_path,
        "docs_url": docs_url,
        "trust_level": trust_level,
        "trust_score": TRUST_SCORES.get(trust_level, 0),
        "description": description,
        "install_path": str(install_path),
        "installed_at": datetime.now(UTC).isoformat(),
        "install_mode": install_mode,
        "detection_reasons": detection_reasons or [],
    }


def install_external_skill(
    *,
    project_root: str | Path = ".",
    slug: str | None = None,
    git_url: str | None = None,
    name: str | None = None,
    force: bool = False,
    install_mode: str = "manual",
    detection_reasons: list[str] | None = None,
    ref: str | None = None,
    active: bool | None = None,
) -> dict[str, object]:
    if slug is None and git_url is None:
        raise ValueError("Provide either a catalog slug or a git_url.")

    if slug is not None:
        entry = _catalog_entry(slug)
        if entry is None:
            raise KeyError(f"Unknown external skill source: {slug}")
        allowed, reason = _policy_allows_source(project_root, entry)
        if not allowed:
            raise PermissionError(f"Cannot install {entry.slug}: {reason}")
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
        install_mode=install_mode,
        detection_reasons=detection_reasons,
    )
    metadata["requested_ref"] = ref
    (install_path / "skilgen-source.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if ref:
        subprocess.run(
            ["git", "-C", str(install_path), "checkout", ref],
            check=True,
            capture_output=True,
            text=True,
        )

    resolved_revision = _git_revision(install_path)
    if resolved_revision is not None:
        metadata["resolved_revision"] = resolved_revision
    remote_url = _git_remote_url(install_path)
    if remote_url is not None:
        metadata["repository_url"] = remote_url
    license_info = _detect_license(install_path)
    if license_info is not None:
        metadata["license"] = license_info

    source = entry if slug is not None and entry is not None else ExternalSkillSource(
        slug=resolved_slug,
        name=resolved_name,
        ecosystem=ecosystem,
        publisher="Custom",
        description=description,
        repository_url=repository_url,
        source_path=source_path,
        docs_url=docs_url,
        category="custom",
        trust_level=trust_level,
    )
    normalization = _normalize_external_skill_install(project_root, source=source, install_path=install_path)
    config = load_config(Path(project_root).resolve())
    auto_activate_allowed = config.external_skills_auto_activate and config.external_skills_policy_mode != "review_required"
    active_value = auto_activate_allowed if active is None else active
    metadata["normalized"] = normalization
    metadata["active"] = active_value

    manifest = _load_manifest(project_root)
    skills = [entry for entry in manifest.get("skills", []) if isinstance(entry, dict) and entry.get("slug") != resolved_slug]
    skills.append(metadata)
    manifest["skills"] = sorted(skills, key=lambda entry: str(entry.get("slug", "")))
    _write_manifest(project_root, manifest)
    _upsert_lock_entry(
        project_root,
        {
            "slug": resolved_slug,
            "name": resolved_name,
            "publisher": metadata.get("publisher"),
            "category": metadata.get("category"),
            "repository_url": metadata["repository_url"],
            "requested_ref": ref,
            "resolved_revision": resolved_revision,
            "active": active_value,
            "normalized": normalization,
            "license": metadata.get("license"),
            "trust_level": trust_level,
            "trust_score": TRUST_SCORES.get(trust_level, 0),
            "supported_agents": metadata.get("supported_agents", []),
            "install_mode": install_mode,
            "updated_at": datetime.now(UTC).isoformat(),
        },
    )
    (install_path / "skilgen-source.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def ensure_external_skills_for_project(project_root: str | Path = ".") -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    detections = detect_external_skill_sources(root)
    installed = _installed_by_slug(root)
    locked = _lock_by_slug(root)
    newly_installed: list[dict[str, object]] = []
    already_installed: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    blocked: list[dict[str, str]] = []
    for detection in detections["detected_skills"]:
        slug = str(detection["slug"])
        source = _catalog_entry(slug)
        if source is None:
            continue
        allowed, reason = _policy_allows_source(root, source)
        if not allowed:
            blocked.append({"slug": slug, "reason": reason or "blocked"})
            continue
        if slug in installed:
            auto_activate_allowed = config.external_skills_auto_activate and config.external_skills_policy_mode != "review_required"
            if auto_activate_allowed:
                lock_entry = locked.get(slug)
                if isinstance(lock_entry, dict) and not lock_entry.get("active"):
                    lock_entry["active"] = True
                    lock_entry["updated_at"] = datetime.now(UTC).isoformat()
                    _upsert_lock_entry(root, lock_entry)
            already_installed.append(installed[slug])
            continue
        try:
            metadata = install_external_skill(
                project_root=root,
                slug=slug,
                install_mode="auto",
                detection_reasons=[str(reason) for reason in detection.get("reasons", [])],
                active=config.external_skills_auto_activate and config.external_skills_policy_mode != "review_required",
            )
            newly_installed.append(metadata)
            installed[slug] = metadata
        except Exception as exc:  # pragma: no cover
            errors.append({"slug": slug, "error": str(exc)})
    return {
        **detections,
        "installed_skills": installed_external_skills(root),
        "newly_installed": newly_installed,
        "already_installed": already_installed,
        "errors": errors,
        "blocked": blocked,
    }


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
    source = _catalog_entry(slug) or ExternalSkillSource(
        slug=slug,
        name=str(installed.get("name", slug)),
        ecosystem=str(installed.get("ecosystem", "custom")),
        publisher="Custom",
        description=str(installed.get("description", "")),
        repository_url=str(installed.get("repository_url", "")),
        source_path=installed.get("source_path") if isinstance(installed.get("source_path"), str) or installed.get("source_path") is None else None,
        docs_url=str(installed.get("docs_url", installed.get("repository_url", ""))),
        category="custom",
        trust_level=str(installed.get("trust_level", "custom")),
    )
    normalization = _normalize_external_skill_install(project_root, source=source, install_path=install_path)
    installed["synced_at"] = datetime.now(UTC).isoformat()
    installed["sync_stdout"] = result.stdout.strip()
    installed["sync_stderr"] = result.stderr.strip()
    installed["resolved_revision"] = _git_revision(install_path)
    installed["normalized"] = normalization
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
    lock_entry = _lock_by_slug(project_root).get(slug, {"slug": slug})
    lock_entry.update(
        {
            "slug": slug,
            "name": installed.get("name"),
            "publisher": installed.get("publisher"),
            "category": installed.get("category"),
            "repository_url": installed.get("repository_url"),
            "requested_ref": installed.get("requested_ref"),
            "resolved_revision": installed.get("resolved_revision"),
            "active": lock_entry.get("active", False),
            "normalized": normalization,
            "license": installed.get("license"),
            "trust_level": installed.get("trust_level"),
            "trust_score": installed.get("trust_score", TRUST_SCORES.get(str(installed.get("trust_level", "custom")), 0)),
            "supported_agents": installed.get("supported_agents", []),
            "install_mode": installed.get("install_mode", "manual"),
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    _upsert_lock_entry(project_root, lock_entry)
    return installed


def sync_all_external_skills(*, project_root: str | Path = ".") -> dict[str, object]:
    synced: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    for installed in installed_external_skills(project_root):
        slug = str(installed["slug"])
        try:
            synced.append(sync_external_skill(project_root=project_root, slug=slug))
        except Exception as exc:  # pragma: no cover
            errors.append({"slug": slug, "error": str(exc)})
    return {"skills": synced, "errors": errors, "count": len(synced)}


def activate_external_skill(*, project_root: str | Path = ".", slug: str) -> dict[str, object]:
    installed = _installed_by_slug(project_root).get(slug)
    if installed is None:
        raise KeyError(f"External skill source is not installed: {slug}")
    lock_entry = _lock_by_slug(project_root).get(slug, {"slug": slug})
    lock_entry["active"] = True
    lock_entry["updated_at"] = datetime.now(UTC).isoformat()
    lock_entry.setdefault("publisher", installed.get("publisher"))
    lock_entry.setdefault("category", installed.get("category"))
    lock_entry.setdefault("license", installed.get("license"))
    lock_entry.setdefault("trust_level", installed.get("trust_level"))
    lock_entry.setdefault("trust_score", installed.get("trust_score", TRUST_SCORES.get(str(installed.get("trust_level", "custom")), 0)))
    lock_entry.setdefault("supported_agents", installed.get("supported_agents", []))
    if "normalized" not in lock_entry:
        install_path = Path(str(installed["install_path"]))
        source = _catalog_entry(slug) or ExternalSkillSource(
            slug=slug,
            name=str(installed.get("name", slug)),
            ecosystem=str(installed.get("ecosystem", "custom")),
            publisher="Custom",
            description=str(installed.get("description", "")),
            repository_url=str(installed.get("repository_url", "")),
            source_path=installed.get("source_path") if isinstance(installed.get("source_path"), str) or installed.get("source_path") is None else None,
            docs_url=str(installed.get("docs_url", installed.get("repository_url", ""))),
            category="custom",
            trust_level=str(installed.get("trust_level", "custom")),
        )
        lock_entry["normalized"] = _normalize_external_skill_install(project_root, source=source, install_path=install_path)
    _upsert_lock_entry(project_root, lock_entry)
    return {"slug": slug, "active": True, "lock_metadata": lock_entry}


def deactivate_external_skill(*, project_root: str | Path = ".", slug: str) -> dict[str, object]:
    installed = _installed_by_slug(project_root).get(slug)
    if installed is None:
        raise KeyError(f"External skill source is not installed: {slug}")
    lock_entry = _lock_by_slug(project_root).get(slug, {"slug": slug})
    lock_entry["active"] = False
    lock_entry["updated_at"] = datetime.now(UTC).isoformat()
    lock_entry.setdefault("publisher", installed.get("publisher"))
    lock_entry.setdefault("category", installed.get("category"))
    lock_entry.setdefault("license", installed.get("license"))
    lock_entry.setdefault("trust_level", installed.get("trust_level"))
    lock_entry.setdefault("trust_score", installed.get("trust_score", TRUST_SCORES.get(str(installed.get("trust_level", "custom")), 0)))
    lock_entry.setdefault("supported_agents", installed.get("supported_agents", []))
    _upsert_lock_entry(project_root, lock_entry)
    return {"slug": slug, "active": False, "lock_metadata": lock_entry}


def remove_external_skill(*, project_root: str | Path = ".", slug: str) -> dict[str, object]:
    installed = _installed_by_slug(project_root).get(slug)
    if installed is None:
        raise KeyError(f"External skill source is not installed: {slug}")
    install_path = Path(str(installed["install_path"]))
    if install_path.exists():
        shutil.rmtree(install_path)
    normalized_path = _normalized_dir(project_root) / slug
    if normalized_path.exists():
        shutil.rmtree(normalized_path)
    manifest = _load_manifest(project_root)
    manifest["skills"] = [
        entry
        for entry in manifest.get("skills", [])
        if isinstance(entry, dict) and entry.get("slug") != slug
    ]
    _write_manifest(project_root, manifest)
    lock = _load_lock(project_root)
    lock["skills"] = [
        entry
        for entry in lock.get("skills", [])
        if isinstance(entry, dict) and entry.get("slug") != slug
    ]
    _write_lock(project_root, lock)
    return {
        "slug": slug,
        "removed": True,
        "install_path": str(install_path),
    }
