from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from skilgen.core.models import ProjectMemory, RequirementsContext


def _memory_dir(project_root: Path) -> Path:
    return project_root.resolve() / ".skilgen" / "memory"


def _project_memory_path(project_root: Path) -> Path:
    return _memory_dir(project_root) / "project_memory.json"


def build_project_memory(
    project_root: Path,
    context: RequirementsContext,
    codebase_context,
    decision,
    generated_files: list[Path] | None = None,
) -> ProjectMemory:
    input_mode = "requirements + codebase" if context.requirements_path.exists() else "codebase only"
    top_level_domains = [
        node.name
        for node in codebase_context.domain_graph.nodes
        if node.parent_domain is None
    ]
    generated_doc_names = sorted(
        path.name
        for path in (generated_files or [])
        if path.suffix == ".md" and path.parent == project_root.resolve()
    )
    if not generated_doc_names:
        generated_doc_names = ["AGENTS.md", "ANALYSIS.md", "FEATURES.md", "REPORT.md", "TRACEABILITY.md"]
    refresh_policy = [
        "Refresh only the domains impacted by source or requirements changes.",
        "Reuse the existing skill tree when no meaningful source changes are detected.",
        "Rebuild AGENTS.md whenever prioritized skills or parent entry points change.",
    ]
    architectural_notes = [
        f"Dynamic top-level domains: {', '.join(top_level_domains) or 'none detected'}",
        f"Prioritized skills: {', '.join(decision.prioritized_skill_paths[:4]) or 'none'}",
        "Use project memory for stable repo context and current run memory for in-flight execution continuity.",
    ]
    memory_files = [
        ".skilgen/memory/project_memory.json",
        ".skilgen/memory/current_run.json",
        ".skilgen/state/freshness.json",
    ]
    return ProjectMemory(
        project_root=str(project_root.resolve()),
        input_mode=input_mode,
        top_level_domains=top_level_domains,
        prioritized_skill_paths=list(decision.prioritized_skill_paths),
        generated_docs=generated_doc_names,
        refresh_policy=refresh_policy,
        recent_objectives=[
            f"Keep the dynamic skill tree aligned with {input_mode}.",
            "Load AGENTS.md and prioritized parent skills before implementation work.",
        ],
        architectural_notes=architectural_notes,
        memory_files=memory_files,
    )


def save_project_memory(project_root: Path, project_memory: ProjectMemory) -> Path:
    memory_dir = _memory_dir(project_root)
    memory_dir.mkdir(parents=True, exist_ok=True)
    path = _project_memory_path(project_root)
    path.write_text(json.dumps(asdict(project_memory), indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_project_memory(project_root: Path) -> ProjectMemory | None:
    path = _project_memory_path(project_root)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ProjectMemory(
        project_root=str(payload.get("project_root", "")),
        input_mode=str(payload.get("input_mode", "")),
        top_level_domains=[str(item) for item in payload.get("top_level_domains", [])],
        prioritized_skill_paths=[str(item) for item in payload.get("prioritized_skill_paths", [])],
        generated_docs=[str(item) for item in payload.get("generated_docs", [])],
        refresh_policy=[str(item) for item in payload.get("refresh_policy", [])],
        recent_objectives=[str(item) for item in payload.get("recent_objectives", [])],
        architectural_notes=[str(item) for item in payload.get("architectural_notes", [])],
        memory_files=[str(item) for item in payload.get("memory_files", [])],
    )
