from __future__ import annotations

import subprocess
from pathlib import Path
import re
import shutil

from skilgen.agents.language_parsers import parse_language_text


_CODE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".java",
    ".go",
    ".rs",
    ".cbl",
    ".cob",
    ".cpy",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cc",
    ".cxx",
    ".cs",
    ".rb",
    ".kt",
    ".kts",
    ".scala",
    ".php",
    ".swift",
    ".lua",
    ".zig",
    ".ps1",
    ".psm1",
    ".ex",
    ".exs",
    ".m",
    ".mm",
    ".dart",
    ".jl",
    ".sh",
    ".bash",
    ".r",
    ".hs",
    ".ml",
    ".fs",
}
_CONFIG_NAMES = {
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "Cargo.lock",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env",
    ".env.example",
}


def _semantic_path_kind(path_value: str) -> str:
    path = Path(path_value)
    lowered = path.as_posix().lower()
    if any(token in lowered for token in ("/tests/", "/test/", ".test.", ".spec.", "test_", "_test.")):
        return "test"
    if path.name in _CONFIG_NAMES or path.suffix.lower() in {".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}:
        return "config"
    if path.suffix.lower() in {".md", ".rst", ".txt"}:
        return "docs"
    if path.suffix.lower() in _CODE_SUFFIXES:
        return "code"
    return "other"


def _git_dir(project_root: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "--git-dir"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    git_dir = Path(result.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = (project_root / git_dir).resolve()
    return git_dir


def _git_output(project_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _git_lines(project_root: Path, *args: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def _git_show(project_root: Path, revision: str, path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "show", f"{revision}:{path}"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def _structural_signal_summary(path: Path, text: str) -> dict[str, int]:
    parsed = parse_language_text(path, text)
    return {
        "symbols": len(parsed.symbols),
        "calls": len(parsed.calls),
        "imports": len(parsed.imports),
        "relationships": len(parsed.relationships),
    }


def classify_commit_intent(project_root: Path, before_ref: str | None, after_ref: str | None) -> dict[str, object]:
    if shutil.which("git") is None:
        return {"intent": "unknown", "confidence": 0.0, "signals": []}
    if not before_ref or not after_ref:
        return {"intent": "unknown", "confidence": 0.0, "signals": ["missing_git_refs"]}
    changed_paths = _git_lines(project_root, "diff", "--name-only", before_ref, after_ref)
    if not changed_paths:
        return {"intent": "unknown", "confidence": 0.0, "signals": ["no_changed_paths"]}
    kinds = {_semantic_path_kind(path) for path in changed_paths}
    if kinds == {"test"}:
        return {"intent": "test_only", "confidence": 0.98, "signals": ["tests_only"]}
    if kinds <= {"config", "docs", "other"} and "config" in kinds:
        return {"intent": "config_change", "confidence": 0.95, "signals": ["config_only"]}

    added_code_files = 0
    removed_code_files = 0
    symbol_additions = 0
    symbol_removals = 0
    relationship_additions = 0
    import_delta = 0
    touched_code = 0
    api_paths = 0
    for raw_path in changed_paths[:80]:
        path = Path(raw_path)
        kind = _semantic_path_kind(raw_path)
        if kind != "code":
            continue
        touched_code += 1
        if re.search(r"(^|/)(api|routes?|controllers?|handlers?)(/|$)", raw_path.lower()):
            api_paths += 1
        before_text = _git_show(project_root, before_ref, raw_path)
        after_text = _git_show(project_root, after_ref, raw_path)
        if before_text and not after_text:
            removed_code_files += 1
        elif after_text and not before_text:
            added_code_files += 1
        before_summary = _structural_signal_summary(path, before_text)
        after_summary = _structural_signal_summary(path, after_text)
        symbol_additions += max(0, after_summary["symbols"] - before_summary["symbols"])
        symbol_removals += max(0, before_summary["symbols"] - after_summary["symbols"])
        relationship_additions += max(0, after_summary["relationships"] - before_summary["relationships"])
        import_delta += abs(after_summary["imports"] - before_summary["imports"])

    signals: list[str] = []
    if api_paths:
        signals.append("api_surface_changed")
    if added_code_files:
        signals.append("new_code_files")
    if symbol_additions:
        signals.append("symbol_additions")
    if relationship_additions:
        signals.append("relationship_additions")
    if import_delta:
        signals.append("dependency_structure_changed")

    if touched_code == 0 and "test" in kinds:
        return {"intent": "test_only", "confidence": 0.82, "signals": ["test_artifacts_changed"]}
    if touched_code == 0 and "config" in kinds:
        return {"intent": "config_change", "confidence": 0.82, "signals": ["config_artifacts_changed"]}
    if added_code_files > 0 or symbol_additions >= 1 or relationship_additions > 0:
        intent = "new_feature"
        if api_paths and touched_code <= 3:
            signals.append("api_only_slice")
        confidence = 0.78 if touched_code else 0.55
    elif import_delta >= max(2, touched_code) or symbol_removals >= 2:
        intent = "refactor"
        confidence = 0.72
    elif touched_code > 0:
        intent = "bug_fix"
        confidence = 0.68
    else:
        intent = "unknown"
        confidence = 0.35
    return {"intent": intent, "confidence": round(confidence, 2), "signals": signals}


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

    project_root_value = current.get("project_root") or previous.get("project_root")
    semantic_intent = {"intent": "unknown", "confidence": 0.0, "signals": ["project_root_unavailable"]}
    if project_root_value:
        project_root = Path(str(project_root_value)).resolve()
        semantic_intent = classify_commit_intent(
            project_root,
            str(prev_git.get("head")) if prev_git.get("head") else None,
            str(curr_git.get("head")) if curr_git.get("head") else None,
        )

    return {
        "event_type": event_type,
        "head_changed": head_changed,
        "branch_changed": branch_changed,
        "changed_paths": changed_paths[:25],
        "changed_path_count": len(changed_paths),
        "semantic_intent": semantic_intent["intent"],
        "semantic_confidence": semantic_intent["confidence"],
        "semantic_signals": semantic_intent["signals"],
        "git": curr_git,
    }
