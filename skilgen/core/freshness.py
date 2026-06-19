from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from skilgen.core.generated_outputs import is_generated_output_path
from skilgen.core.models import DomainGraph, FreshnessReport, FreshnessState, RequirementsContext


IGNORED_PARTS = {
    ".git",
    ".skilgen",
    ".vercel",
    ".venv",
    ".venv-api",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    "skills",
}
IGNORED_FILE_NAMES = {".ds_store", "thumbs.db"}
INTERNAL_MONOREPO_PARTS = {"apps", "packages", "infra"}


def _is_internal_skillayer_monorepo(project_root: Path) -> bool:
    """Return whether Skilgen is running inside its product monorepo wrapper."""
    return project_root.name == "skilgen-upstream-work" or (
        (project_root / "skilgen").is_dir()
        and (project_root / "apps").is_dir()
        and (project_root / "packages").is_dir()
    )


def _is_ignored(relative: Path, *, internal_monorepo: bool = False) -> bool:
    """Return whether a path should be ignored for source freshness."""
    lowered = [part.lower() for part in relative.parts]
    if internal_monorepo and lowered and lowered[0] in INTERNAL_MONOREPO_PARTS:
        return True
    return any(
        part in IGNORED_PARTS
        or part.startswith(".venv")
        or part.endswith(".egg-info")
        or part in IGNORED_FILE_NAMES
        for part in lowered
    )


def _is_trackable_source_path(relative: Path, *, internal_monorepo: bool = False) -> bool:
    """Return whether a relative path belongs in freshness source state."""
    return not _is_ignored(relative, internal_monorepo=internal_monorepo) and not is_generated_output_path(relative)


def _filter_source_hashes(source_hashes: dict[str, str], *, internal_monorepo: bool = False) -> dict[str, str]:
    """Remove stale entries for ignored/generated files from persisted state."""
    return {
        path: digest
        for path, digest in source_hashes.items()
        if _is_trackable_source_path(Path(path), internal_monorepo=internal_monorepo)
    }


def _state_dir(project_root: Path) -> Path:
    return project_root.resolve() / ".skilgen" / "state"


def _state_path(project_root: Path) -> Path:
    return _state_dir(project_root) / "freshness.json"


def _iter_source_files(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    internal_monorepo = _is_internal_skillayer_monorepo(root)
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if not _is_trackable_source_path(relative, internal_monorepo=internal_monorepo):
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
    internal_monorepo = _is_internal_skillayer_monorepo(project_root.resolve())
    return FreshnessState(
        source_hashes=_filter_source_hashes(
            {str(key): str(value) for key, value in payload.get("source_hashes", {}).items()},
            internal_monorepo=internal_monorepo,
        ),
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
    if previous_state is not None:
        internal_monorepo = _is_internal_skillayer_monorepo(project_root.resolve())
        previous_state = FreshnessState(
            source_hashes=_filter_source_hashes(previous_state.source_hashes, internal_monorepo=internal_monorepo),
            requirements_source_hash=previous_state.requirements_source_hash,
            domain_graph_nodes=previous_state.domain_graph_nodes,
            top_level_domains=previous_state.top_level_domains,
        )
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
