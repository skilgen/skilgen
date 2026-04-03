from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from skilgen.agents import build_agent_decision, fingerprint_project
from skilgen.core.config import load_config
from skilgen.core.context import build_codebase_context
from skilgen.core.freshness import compute_freshness_report, load_freshness_state, save_freshness_state, snapshot_freshness_state
from skilgen.core.models import RunMemory
from skilgen.core.repo_state import classify_repo_change, git_repo_state
from skilgen.core.run_memory import append_run_event, create_run_memory, finalize_run_memory
from skilgen.deep_agents_core import current_runtime_mode
from skilgen.enterprise_skills import ensure_enterprise_skills_for_project
from skilgen.external_skills import ensure_external_skills_for_project
from skilgen.core.requirements import load_project_context
from skilgen.generators.package import project_doc_paths, write_project_docs
from skilgen.generators.skills import planned_skill_paths, write_skills


ProgressCallback = Callable[[str], None]


def _emit(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def run_delivery(
    requirements_path: str | Path | None = None,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    dry_run: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    root = Path(project_root).resolve()
    input_mode = "codebase and requirements" if requirements_path is not None else "codebase only"
    _emit(progress_callback, f"Reading your {input_mode} and loading the Skilgen project configuration.")
    config = load_config(root)
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
        run_memory = RunMemory(
            run_id=run_memory.run_id,
            status=run_memory.status,
            project_root=run_memory.project_root,
            requirements_path=run_memory.requirements_path,
            objective=run_memory.objective,
            runtime=run_memory.runtime,
            impacted_domains=run_memory.impacted_domains,
            selected_domains=run_memory.selected_domains,
            selected_skill_paths=run_memory.selected_skill_paths,
            changed_files=run_memory.changed_files,
            generated_files=run_memory.generated_files,
            active_file_focus=run_memory.active_file_focus,
            unresolved_questions=run_memory.unresolved_questions,
            pending_validations=run_memory.pending_validations,
            resumable_steps=[
                "Reuse the current skill tree and start from the prioritized parent skills.",
                "Load the current run memory before making implementation changes.",
                "Only rerun skill refresh if new source changes appear.",
            ],
            recent_events=run_memory.recent_events,
        )
    elif decision.next_actions:
        run_memory = RunMemory(
            run_id=run_memory.run_id,
            status=run_memory.status,
            project_root=run_memory.project_root,
            requirements_path=run_memory.requirements_path,
            objective=run_memory.objective,
            runtime=run_memory.runtime,
            impacted_domains=run_memory.impacted_domains,
            selected_domains=run_memory.selected_domains,
            selected_skill_paths=run_memory.selected_skill_paths,
            changed_files=run_memory.changed_files,
            generated_files=run_memory.generated_files,
            active_file_focus=run_memory.active_file_focus,
            unresolved_questions=run_memory.unresolved_questions,
            pending_validations=run_memory.pending_validations,
            resumable_steps=decision.next_actions,
            recent_events=run_memory.recent_events,
        )
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
            generated.extend(write_project_docs(context, root))
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
            generated.extend(write_skills(context, root / "skills", selected_domains))
    if not dry_run:
        saved_context = load_project_context(root, Path(requirements_path).resolve() if requirements_path is not None else None)
        saved_codebase_context = build_codebase_context(root, saved_context)
        save_freshness_state(root, snapshot_freshness_state(root, saved_context, saved_codebase_context.domain_graph))
    run_memory = finalize_run_memory(root, run_memory, generated, "completed")
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
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative.startswith((".git/", "skills/", "__pycache__/")):
                continue
            if path.name in {"ANALYSIS.md", "FEATURES.md", "REPORT.md"}:
                continue
            tracked[relative] = path.stat().st_mtime_ns
        return {
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
