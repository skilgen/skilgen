from __future__ import annotations

from pathlib import Path

from skilgen.core.context import build_codebase_context
from skilgen.core.freshness import compute_freshness_report, load_freshness_state, snapshot_freshness_state
from skilgen.core.repo_state import git_repo_state
from skilgen.core.requirements import load_project_context
from skilgen.core.score import freshness_subscore


def _current_git_event_from_state(state: dict[str, object]) -> str:
    if not state.get("is_git_repo"):
        return "not_git_repo"
    if state.get("merge_in_progress"):
        return "merge_in_progress"
    if state.get("rebase_in_progress"):
        return "rebase_in_progress"
    if state.get("unstaged_changes", 0) > 0:
        return "manual_edit"
    if state.get("staged_changes", 0) > 0:
        return "staged_changes"
    if state.get("untracked_files", 0) > 0:
        return "new_untracked_files"
    return "clean"


def _classify_changed_files(previous_hashes: dict[str, str], current_hashes: dict[str, str]) -> list[dict[str, str]]:
    changed: list[dict[str, str]] = []
    all_paths = sorted(set(previous_hashes) | set(current_hashes))
    for path in all_paths:
        previous_hash = previous_hashes.get(path)
        current_hash = current_hashes.get(path)
        if previous_hash is None and current_hash is not None:
            changed.append({"path": path, "change_type": "added"})
        elif previous_hash is not None and current_hash is None:
            changed.append({"path": path, "change_type": "deleted"})
        elif previous_hash != current_hash:
            changed.append({"path": path, "change_type": "modified"})
    return changed


def compute_diff(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    context = load_project_context(root, None)
    codebase_context = build_codebase_context(root, context)
    previous_state = load_freshness_state(root)
    current_state = snapshot_freshness_state(root, context, codebase_context.domain_graph)
    freshness = compute_freshness_report(root, context, codebase_context.domain_graph, previous_state)
    freshness_score, freshness_payload = freshness_subscore(root)
    git_state = git_repo_state(root)

    top_level_domains = freshness.top_level_domains
    nodes_by_name = {node.name: node for node in codebase_context.domain_graph.nodes}
    impacted_domain_details = [
        {
            "domain": domain,
            "skill_path": nodes_by_name.get(domain).skill_path if nodes_by_name.get(domain) is not None else None,
            "stale": any(path == (nodes_by_name.get(domain).skill_path if nodes_by_name.get(domain) is not None else None) for path in freshness.stale_skill_paths),
        }
        for domain in freshness.impacted_domains
    ]

    if previous_state is None:
        return {
            "changed_files": [],
            "changed_file_count": 0,
            "impacted_domains": top_level_domains,
            "impacted_domain_details": impacted_domain_details,
            "stale_skill_paths": freshness.stale_skill_paths,
            "current_domains": [],
            "reason": "missing_freshness_state",
            "freshness_score": freshness_score,
            "freshness_max": freshness_payload["max_score"],
            "git": {
                "is_git_repo": git_state.get("is_git_repo", False),
                "head": git_state.get("head"),
                "branch": git_state.get("branch"),
                "event_type": _current_git_event_from_state(git_state),
            },
        }

    changed_files = _classify_changed_files(previous_state.source_hashes, current_state.source_hashes)
    if freshness.reason == "no_source_changes":
        changed_files = []
        impacted_domains: list[str] = []
        stale_skill_paths: list[str] = []
        current_domains = top_level_domains
    else:
        impacted_domains = freshness.impacted_domains
        stale_skill_paths = freshness.stale_skill_paths
        current_domains = [domain for domain in top_level_domains if domain not in set(impacted_domains)]

    return {
        "changed_files": changed_files,
        "changed_file_count": len(changed_files),
        "impacted_domains": impacted_domains,
        "impacted_domain_details": impacted_domain_details,
        "stale_skill_paths": stale_skill_paths,
        "current_domains": current_domains,
        "reason": freshness.reason,
        "freshness_score": freshness_score,
        "freshness_max": freshness_payload["max_score"],
        "git": {
            "is_git_repo": git_state.get("is_git_repo", False),
            "head": git_state.get("head"),
            "branch": git_state.get("branch"),
            "event_type": _current_git_event_from_state(git_state),
        },
    }
