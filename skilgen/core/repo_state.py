from __future__ import annotations

import subprocess
from pathlib import Path


def _git_dir(project_root: Path) -> Path | None:
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "--git-dir"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    git_dir = Path(result.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = (project_root / git_dir).resolve()
    return git_dir


def _git_output(project_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _git_lines(project_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(project_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def git_repo_state(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    git_dir = _git_dir(root)
    if git_dir is None:
        return {
            "is_git_repo": False,
            "head": None,
            "branch": None,
            "merge_in_progress": False,
            "rebase_in_progress": False,
            "staged_changes": 0,
            "unstaged_changes": 0,
            "untracked_files": 0,
            "head_parent_count": 0,
        }

    status_lines = _git_lines(root, "status", "--porcelain=v1")
    staged_changes = 0
    unstaged_changes = 0
    untracked_files = 0
    for line in status_lines:
        if not line:
            continue
        if line.startswith("??"):
            untracked_files += 1
            continue
        if len(line) >= 2:
            if line[0] != " ":
                staged_changes += 1
            if line[1] != " ":
                unstaged_changes += 1

    head = _git_output(root, "rev-parse", "HEAD") or None
    branch = _git_output(root, "rev-parse", "--abbrev-ref", "HEAD") or None
    parents = _git_output(root, "rev-list", "--parents", "-n", "1", "HEAD").split()
    head_parent_count = max(0, len(parents) - 1)
    rebase_in_progress = (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()
    merge_in_progress = (git_dir / "MERGE_HEAD").exists()
    return {
        "is_git_repo": True,
        "head": head,
        "branch": branch,
        "merge_in_progress": merge_in_progress,
        "rebase_in_progress": rebase_in_progress,
        "staged_changes": staged_changes,
        "unstaged_changes": unstaged_changes,
        "untracked_files": untracked_files,
        "head_parent_count": head_parent_count,
    }


def classify_repo_change(previous: dict[str, object], current: dict[str, object]) -> dict[str, object]:
    prev_git = previous.get("git", {}) if isinstance(previous.get("git"), dict) else {}
    curr_git = current.get("git", {}) if isinstance(current.get("git"), dict) else {}

    prev_files = previous.get("files", {})
    curr_files = current.get("files", {})
    changed_paths = sorted(
        set(prev_files) ^ set(curr_files)
        | {path for path in set(prev_files) & set(curr_files) if prev_files[path] != curr_files[path]}
    )
    head_changed = prev_git.get("head") != curr_git.get("head")
    branch_changed = prev_git.get("branch") != curr_git.get("branch")

    if curr_git.get("merge_in_progress") or prev_git.get("merge_in_progress"):
        event_type = "merge_in_progress"
    elif curr_git.get("rebase_in_progress") or prev_git.get("rebase_in_progress"):
        event_type = "rebase_in_progress"
    elif head_changed and curr_git.get("head_parent_count", 0) > 1:
        event_type = "merge_commit"
    elif head_changed and (branch_changed or prev_git.get("rebase_in_progress")):
        event_type = "rebase_or_history_rewrite"
    elif head_changed:
        event_type = "git_head_changed"
    elif curr_git.get("staged_changes", 0) != prev_git.get("staged_changes", 0):
        event_type = "staged_changes"
    elif curr_git.get("unstaged_changes", 0) != prev_git.get("unstaged_changes", 0):
        event_type = "manual_edit"
    elif curr_git.get("untracked_files", 0) != prev_git.get("untracked_files", 0):
        event_type = "new_untracked_files"
    else:
        event_type = "file_change"

    return {
        "event_type": event_type,
        "head_changed": head_changed,
        "branch_changed": branch_changed,
        "changed_paths": changed_paths[:25],
        "changed_path_count": len(changed_paths),
        "git": curr_git,
    }
