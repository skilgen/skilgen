from __future__ import annotations

import asyncio
from dataclasses import replace
import json
import os
import time
import uuid
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from skilgen.agents import build_agent_decision, fingerprint_project
from skilgen.agents.codebase_signals import clear_codebase_signal_caches, is_ignored_path_parts, is_internal_skillayer_monorepo
from skilgen.agents.source_graphs import clear_source_graph_caches
from skilgen.core.audit import append_audit_event
from skilgen.core.analytics import log_skill_usage
from skilgen.core.config import load_config
from skilgen.core.context import build_codebase_context
from skilgen.core.corpus_index import ensure_corpus_index
from skilgen.core.freshness import compute_freshness_report, load_freshness_state, save_freshness_state, snapshot_freshness_state
from skilgen.core.generated_outputs import is_generated_output_path
from skilgen.core.models import RunMemory
from skilgen.core.repo_state import classify_repo_change, git_repo_state
from skilgen.core.run_memory import append_run_event, create_run_memory, finalize_run_memory
from skilgen.core.runtime_data import prune_runtime_data
from skilgen.core.score import record_score_history
from skilgen.deep_agents_core import current_runtime_mode
from skilgen.enterprise_skills import ensure_enterprise_skills_for_project
from skilgen.external_skills import ensure_external_skills_for_project
from skilgen.core.requirements import load_project_context
from skilgen.generators.package import project_doc_paths, write_dashboard_doc, write_project_docs
from skilgen.generators.skills import planned_skill_paths, write_skills


ProgressCallback = Callable[[str], None]


def _emit(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _write_claude_code_hook(project_root: str | Path) -> Path | None:
    """Write Claude Code hook config so skill reads are auto-tracked."""
    root = Path(project_root).resolve()
    settings_path = root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    hook_command = 'python -m skilgen.hooks.claude_code_hook "$CLAUDE_TOOL_INPUT_FILE_PATH"'

    existing: dict[str, object] = {}
    if settings_path.exists():
        try:
            loaded = json.loads(settings_path.read_text(encoding="utf-8"))
            existing = loaded if isinstance(loaded, dict) else {}
        except (json.JSONDecodeError, OSError):
            existing = {}

    hooks = existing.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    pre_tool_use = hooks.get("PreToolUse")
    if not isinstance(pre_tool_use, list):
        pre_tool_use = []
    post_tool_use = hooks.get("PostToolUse")
    if not isinstance(post_tool_use, list):
        post_tool_use = []

    def _has_skilgen_hook(entries: list[object], matcher: str) -> bool:
        return any(
            isinstance(entry, dict)
            and entry.get("matcher") == matcher
            and any(
                isinstance(hook, dict) and "skilgen.hooks.claude_code_hook" in str(hook.get("command", ""))
                for hook in entry.get("hooks", [])
            )
            for entry in entries
        )

    skilgen_hook_exists = _has_skilgen_hook(pre_tool_use, "Edit|Write|NotebookEdit") and _has_skilgen_hook(post_tool_use, "Read|Edit|Write|NotebookEdit")
    if skilgen_hook_exists:
        return None

    if not _has_skilgen_hook(pre_tool_use, "Edit|Write|NotebookEdit"):
        pre_tool_use.append(
            {
                "matcher": "Edit|Write|NotebookEdit",
                "hooks": [{"type": "command", "command": hook_command}],
            }
        )
    if not _has_skilgen_hook(post_tool_use, "Read|Edit|Write|NotebookEdit"):
        post_tool_use.append(
            {
                "matcher": "Read|Edit|Write|NotebookEdit",
                "hooks": [{"type": "command", "command": hook_command}],
            }
        )
    hooks["PreToolUse"] = pre_tool_use
    hooks["PostToolUse"] = post_tool_use
    existing["hooks"] = hooks
    settings_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print("✓ Configured Claude Code skill load tracking (.claude/settings.json)")
    return settings_path


def _local_analytics_events(project_root: Path) -> list[dict[str, object]]:
    usage_path = project_root / ".skilgen" / "analytics" / "usage.jsonl"
    if not usage_path.exists():
        return []
    events: list[dict[str, object]] = []
    for line in usage_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        skill = str(entry.get("skill", "")).strip()
        if not skill or str(entry.get("context", "")) == "decision_planner":
            continue
        events.append(
            {
                "skill_path": skill,
                "agent_runtime": str(entry.get("agent_runtime", "unknown")).strip() or "unknown",
                "session_id": str(entry.get("session_id") or ""),
                "timestamp": str(entry.get("timestamp", "")),
            }
        )
    return events


async def _upload_analytics(api_url: str, repo_id: str, api_key: str, project_root: str | Path = ".") -> dict[str, int]:
    """Upload local analytics events to Skillayer without blocking callers on sync I/O."""
    root = Path(project_root).resolve()
    body = json.dumps({"repo_id": repo_id, "events": _local_analytics_events(root)}).encode("utf-8")
    request = Request(
        f"{api_url.rstrip('/')}/repos/{repo_id}/sync-analytics",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    def _send() -> dict[str, int]:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return {"synced": int(payload.get("synced", 0)), "skipped": int(payload.get("skipped", 0))}

    return await asyncio.to_thread(_send)


async def _auto_sync_to_skillayer(repo_root: str | Path, skills_delivered: list[str | Path]) -> bool:
    """
    After delivery, auto-upload fresh skill events to Skillayer.

    Silently no-ops if SKILLAYER_API_KEY or SKILLAYER_REPO_ID is not set.
    """
    api_key = os.environ.get("SKILLAYER_API_KEY")
    repo_id = os.environ.get("SKILLAYER_REPO_ID")
    api_url = os.environ.get("SKILLAYER_API_URL", "https://api.skillayer.com")
    if not api_key or not repo_id:
        return False

    root = Path(repo_root).resolve()
    skill_paths = []
    for skill_path in skills_delivered:
        path = Path(skill_path)
        if path.name != "SKILL.md":
            continue
        try:
            skill_paths.append(path.resolve().relative_to(root).as_posix())
        except ValueError:
            skill_paths.append(path.as_posix())
    if not skill_paths:
        return False

    for skill_path in skill_paths:
        log_skill_usage(
            root,
            [skill_path],
            event="delivered",
            context="skilgen_deliver",
            session_id=str(uuid.uuid4()),
        )

    try:
        await _upload_analytics(api_url, repo_id, api_key, root)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return False
    return True


def sync_to_skillayer_after_delivery(repo_root: str | Path, skills_delivered: list[str | Path]) -> bool:
    """Synchronous wrapper used by the CLI after a successful deliver."""
    if not os.environ.get("SKILLAYER_API_KEY") or not os.environ.get("SKILLAYER_REPO_ID"):
        return False
    _write_claude_code_hook(repo_root)
    try:
        return asyncio.run(_auto_sync_to_skillayer(repo_root, skills_delivered))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_auto_sync_to_skillayer(repo_root, skills_delivered))
        finally:
            loop.close()


def run_delivery(
    requirements_path: str | Path | None = None,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    dry_run: bool = False,
    skip_index: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    root = Path(project_root).resolve()
    clear_codebase_signal_caches()
    clear_source_graph_caches()
    input_mode = "codebase and requirements" if requirements_path is not None else "codebase only"
    _emit(progress_callback, f"Reading your {input_mode} and loading the Skilgen project configuration.")
    config = load_config(root)
    prune_runtime_data(root)
    if not skip_index and config.corpus.enabled:
        _emit(progress_callback, "Indexing the full repository corpus so evidence selection covers every subsystem, config, and architecture doc.")
        ensure_corpus_index(root, config)
    if config.auto_install_external_skills:
        _emit(progress_callback, "Scanning the repository for known external skill ecosystems that Skilgen can auto-install.")
        external_skill_summary = ensure_external_skills_for_project(root)
        if external_skill_summary["newly_installed"]:
            names = ", ".join(entry["slug"] for entry in external_skill_summary["newly_installed"])
            _emit(progress_callback, f"Installed matching external skill packs: {names}.")
        elif external_skill_summary["already_installed"]:
            names = ", ".join(entry["slug"] for entry in external_skill_summary["already_installed"][:4])
            _emit(progress_callback, f"Using already-installed external skill packs: {names}.")
    enterprise_summary = ensure_enterprise_skills_for_project(root)
    if enterprise_summary["installed_skills"]:
        names = ", ".join(entry["slug"] for entry in enterprise_summary["installed_skills"][:4])
        _emit(progress_callback, f"Ingested configured enterprise skill packs: {names}.")
    elif enterprise_summary["already_present_skills"]:
        names = ", ".join(entry["slug"] for entry in enterprise_summary["already_present_skills"][:4])
        _emit(progress_callback, f"Using configured enterprise skill packs: {names}.")
    if enterprise_summary["auto_activated_connectors"]:
        names = ", ".join(entry["slug"] for entry in enterprise_summary["auto_activated_connectors"][:4])
        _emit(progress_callback, f"Activated recommended MCP connectors: {names}.")
    _emit(progress_callback, "Building project context so agents can understand the repo structure and delivery scope.")
    context = load_project_context(root, Path(requirements_path).resolve() if requirements_path is not None else None)
    _emit(progress_callback, "Inspecting the codebase to identify frameworks, domains, and implementation patterns.")
    fingerprint_project(root)
    codebase_context = build_codebase_context(root, context)
    previous_state = load_freshness_state(root)
    freshness = compute_freshness_report(root, context, codebase_context.domain_graph, previous_state)
    decision = build_agent_decision(root, context, codebase_context.domain_graph, codebase_context.skill_tree)
    explicit_domains = set(domains)
    selected_domains = set(explicit_domains or decision.prioritized_domains)
    selected_skill_paths = sorted(
        node.path for node in codebase_context.skill_tree if not selected_domains or node.domain in selected_domains
    )
    run_memory = create_run_memory(
        root,
        Path(requirements_path).resolve() if requirements_path is not None else None,
        current_runtime_mode(root),
        freshness,
        sorted(selected_domains),
        selected_skill_paths,
    )
    if not decision.should_refresh and not explicit_domains:
        run_memory = replace(
            run_memory,
            resumable_steps=[
                "Reuse the current skill tree and start from the prioritized parent skills.",
                "Load the current run memory before making implementation changes.",
                "Only rerun skill refresh if new source changes appear.",
            ],
        )
    elif decision.next_actions:
        run_memory = replace(run_memory, resumable_steps=decision.next_actions)
    if freshness.reason == "no_source_changes":
        message = "No source changes were detected since the last skill snapshot. Skilgen will keep the existing skill tree stable."
        run_memory = append_run_event(root, run_memory, message)
        _emit(progress_callback, message)
    else:
        changed_preview = ", ".join(freshness.changed_files[:4]) if freshness.changed_files else "the inferred domain graph"
        impacted_preview = ", ".join(freshness.impacted_domains) if freshness.impacted_domains else "all domains"
        message = f"Detected changes in {changed_preview}. Refreshing the impacted skill domains: {impacted_preview}."
        run_memory = append_run_event(root, run_memory, message)
        _emit(progress_callback, message)
    decision_message = (
        f"Decision planner selected domains: {', '.join(decision.prioritized_domains) or 'none'}; "
        f"prioritized skills: {', '.join(decision.prioritized_skill_paths[:4]) or 'none'}."
    )
    log_skill_usage(root, decision.prioritized_skill_paths, context="decision_planner")
    run_memory = append_run_event(root, run_memory, decision_message)
    _emit(progress_callback, decision_message)
    generated = []
    if "docs" in targets:
        if dry_run:
            message = "Previewing the generated project docs without writing files."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
            generated.extend(project_doc_paths(root))
        else:
            message = "Generating project docs so coding agents have clear context, traceability, and operating guidance."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
            generated.extend(write_project_docs(context, root, progress_callback=progress_callback))
    if "skills" in targets:
        if not explicit_domains and not decision.should_refresh:
            message = "Decision planner recommends reusing the current skills. Skipping skill regeneration for this run."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
        elif not selected_domains:
            message = "Decision planner did not identify any concrete domains to refresh, so the existing skills will be reused."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
        if dry_run:
            message = "Previewing the skill tree that would be materialized for this repository."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
            if explicit_domains or decision.should_refresh:
                generated.extend(planned_skill_paths(context, root / "skills", selected_domains))
        elif explicit_domains or decision.should_refresh:
            message = "Materializing backend, frontend, requirements, and roadmap skills for coding agents."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
            generated.extend(write_skills(context, root / "skills", selected_domains, progress_callback=progress_callback))
    if not dry_run:
        saved_context = load_project_context(root, Path(requirements_path).resolve() if requirements_path is not None else None)
        save_freshness_state(root, snapshot_freshness_state(root, saved_context, codebase_context.domain_graph))
        record_score_history(root, source="delivery")
        if "docs" in targets:
            message = "Rendering the final dashboard HTML surface with graphs, score, freshness, and capability context."
            run_memory = append_run_event(root, run_memory, message)
            _emit(progress_callback, message)
            generated.append(write_dashboard_doc(saved_context, root, progress_callback=progress_callback))
    run_memory = finalize_run_memory(root, run_memory, generated, "completed")
    append_audit_event(
        root,
        action="deliver",
        outcome="success",
        source="delivery",
        details={
            "requirements_path": str(Path(requirements_path).resolve()) if requirements_path is not None else None,
            "targets": list(targets),
            "domains": list(domains),
            "generated_files": [str(path) for path in generated],
        },
    )
    message = f"Finished delivery. Generated or refreshed {len(generated)} files."
    run_memory = append_run_event(root, run_memory, message)
    _emit(progress_callback, message)
    return generated


def watch_delivery(
    requirements_path: str | Path | None = None,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    interval_seconds: float = 2.0,
    cycles: int = 0,
    once: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> list[list[Path]]:
    root = Path(project_root).resolve()

    def snapshot() -> dict[str, object]:
        tracked: dict[str, int] = {}
        internal_monorepo = is_internal_skillayer_monorepo(root)
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            relative_parts = Path(relative).parts
            if is_ignored_path_parts(relative_parts, internal_monorepo=internal_monorepo):
                continue
            if is_generated_output_path(relative):
                continue
            tracked[relative] = path.stat().st_mtime_ns
        return {
            "project_root": str(root),
            "files": tracked,
            "git": git_repo_state(root),
        }

    results = [
        run_delivery(
            requirements_path,
            root,
            targets=targets,
            domains=domains,
            progress_callback=progress_callback,
        ),
    ]
    if once:
        return results

    previous = snapshot()
    completed_cycles = 0
    while cycles == 0 or completed_cycles < cycles:
        time.sleep(interval_seconds)
        current = snapshot()
        if current != previous:
            clear_codebase_signal_caches()
            clear_source_graph_caches()
            change = classify_repo_change(previous, current)
            _emit(progress_callback, f"Detected {change['event_type'].replace('_', ' ')}. Refreshing the generated docs and skills.")
            results.append(
                run_delivery(
                    requirements_path,
                    root,
                    targets=targets,
                    domains=domains,
                    progress_callback=progress_callback,
                )
            )
            previous = current
        completed_cycles += 1
    return results
