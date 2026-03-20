from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from skilgen.core.models import DomainGraph, FreshnessReport, FreshnessState, RequirementsContext


IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}
IGNORED_FILES = {
    "AGENTS.md",
    "ANALYSIS.md",
    "FEATURES.md",
    "REPORT.md",
    "TRACEABILITY.md",
}


def _state_dir(project_root: Path) -> Path:
    return project_root.resolve() / ".skilgen" / "state"


def _state_path(project_root: Path) -> Path:
    return _state_dir(project_root) / "freshness.json"


def _iter_source_files(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if set(relative.parts) & IGNORED_PARTS:
            continue
        if relative.parts and relative.parts[0] == "skills":
            continue
        if relative.parts and relative.parts[0] == ".skilgen":
            continue
        if path.name in IGNORED_FILES:
            continue
        files.append(path)
    return sorted(files)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _top_level_domains(domain_graph: DomainGraph) -> list[str]:
    return [node.name for node in domain_graph.nodes if node.parent_domain is None and node.skill_path]


def snapshot_freshness_state(
    project_root: Path,
    requirements: RequirementsContext,
    domain_graph: DomainGraph,
) -> FreshnessState:
    root = project_root.resolve()
    source_hashes = {path.relative_to(root).as_posix(): _hash_file(path) for path in _iter_source_files(root)}
    return FreshnessState(
        source_hashes=source_hashes,
        requirements_source_hash=requirements.source_hash,
        domain_graph_nodes=[asdict(node) for node in domain_graph.nodes],
        top_level_domains=_top_level_domains(domain_graph),
    )


def load_freshness_state(project_root: Path) -> FreshnessState | None:
    path = _state_path(project_root)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return FreshnessState(
        source_hashes={str(key): str(value) for key, value in payload.get("source_hashes", {}).items()},
        requirements_source_hash=str(payload.get("requirements_source_hash", "")),
        domain_graph_nodes=list(payload.get("domain_graph_nodes", [])),
        top_level_domains=[str(item) for item in payload.get("top_level_domains", [])],
    )


def save_freshness_state(project_root: Path, state: FreshnessState) -> Path:
    path = _state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2, sort_keys=True), encoding="utf-8")
    return path


def compute_freshness_report(
    project_root: Path,
    requirements: RequirementsContext,
    domain_graph: DomainGraph,
    previous_state: FreshnessState | None,
) -> FreshnessReport:
    current_state = snapshot_freshness_state(project_root, requirements, domain_graph)
    top_level_domains = current_state.top_level_domains
    if previous_state is None:
        stale_paths = [node.skill_path for node in domain_graph.nodes if node.skill_path]
        return FreshnessReport(
            changed_files=sorted(current_state.source_hashes),
            impacted_domains=top_level_domains,
            stale_skill_paths=sorted(path for path in stale_paths if path),
            top_level_domains=top_level_domains,
            reason="initial_generation",
        )

    changed_files = sorted(
        path
        for path in set(previous_state.source_hashes) | set(current_state.source_hashes)
        if previous_state.source_hashes.get(path) != current_state.source_hashes.get(path)
    )

    if previous_state.requirements_source_hash != current_state.requirements_source_hash:
        changed_files.append("requirements")
    changed_files = sorted(set(changed_files))

    if not changed_files:
        return FreshnessReport(
            changed_files=[],
            impacted_domains=[],
            stale_skill_paths=[],
            top_level_domains=top_level_domains,
            reason="no_source_changes",
        )

    nodes_by_name = {node.name: node for node in domain_graph.nodes}
    impacted: set[str] = set()
    stale_paths: set[str] = set()

    if "requirements" in changed_files:
        stale_paths.update(node.skill_path for node in domain_graph.nodes if node.skill_path)
        return FreshnessReport(
            changed_files=changed_files,
            impacted_domains=top_level_domains,
            stale_skill_paths=sorted(path for path in stale_paths if path),
            top_level_domains=top_level_domains,
            reason="requirements_changed",
        )

    for node in domain_graph.nodes:
        if not node.skill_path:
            continue
        evidence = set(node.key_files)
        if evidence and any(changed in evidence for changed in changed_files):
            stale_paths.add(node.skill_path)
            impacted.add(node.parent_domain or node.name)
            parent_name = node.parent_domain
            while parent_name:
                impacted.add(parent_name)
                parent = nodes_by_name.get(parent_name)
                if parent and parent.skill_path:
                    stale_paths.add(parent.skill_path)
                parent_name = parent.parent_domain if parent else None

    top_level_set = set(top_level_domains)
    impacted = {domain for domain in impacted if domain in top_level_set}

    if not impacted:
        impacted = top_level_set
        stale_paths.update(node.skill_path for node in domain_graph.nodes if node.skill_path)

    reason = "requirements_changed" if "requirements" in changed_files else "source_changes_detected"
    return FreshnessReport(
        changed_files=changed_files,
        impacted_domains=sorted(impacted),
            stale_skill_paths=sorted(path for path in stale_paths if path),
            top_level_domains=top_level_domains,
            reason=reason,
        )
