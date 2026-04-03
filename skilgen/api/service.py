from __future__ import annotations

from pathlib import Path
from typing import Callable

from skilgen.api.jobs import get_job, job_payload, list_jobs, request_cancel, submit_job
from skilgen.agents.decision_planner import build_agent_decision
from skilgen.autoupdate import auto_update_status
from skilgen.deep_agents_core import current_runtime_mode, runtime_diagnostics
from skilgen.deep_agents_runtime import (
    DeepAgentsRuntime,
    native_analyze_payload,
    native_features_payload,
    native_fingerprint_payload,
    native_intent_payload,
    native_map_payload,
    native_plan_payload,
    native_preview_payload,
    native_report_payload,
    native_status_payload,
    native_validate_payload,
)
from skilgen.delivery import run_delivery
from skilgen.enterprise_skills import (
    activate_mcp_connector,
    active_enterprise_skills,
    active_mcp_connectors,
    connector_catalog,
    deactivate_mcp_connector,
    generate_enterprise_skill,
    ingest_enterprise_skill,
    list_enterprise_skills,
    recommend_mcp_connectors,
)
from skilgen.core.freshness import compute_freshness_report, load_freshness_state
from skilgen.core.context import build_codebase_context
from skilgen.core.score import compute_skillgen_score, render_score_badge_svg, write_score_badge
from skilgen.core.requirements import load_project_context
from skilgen.core.run_memory import load_current_run_memory
from skilgen.external_skills import (
    activate_external_skill,
    active_external_skills,
    deactivate_external_skill,
    detect_external_skill_sources,
    external_skill_lock,
    external_skill_policy,
    export_external_skill_lock,
    get_external_skill,
    import_external_skill_candidates,
    import_external_skill_lock,
    install_external_skill,
    installed_external_skills,
    list_external_skills,
    ranked_external_skills,
    remove_external_skill,
    sync_all_external_skills,
    sync_external_skill,
)


API_VERSION = "1.0"


def _with_api_meta(payload: dict[str, object]) -> dict[str, object]:
    return {"api_version": API_VERSION, **payload}


def health_payload() -> dict[str, object]:
    return _with_api_meta({"status": "ok", "service": "skilgen", "runtime": current_runtime_mode()})


def doctor_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta(runtime_diagnostics(Path(project_root).resolve()))


def decision_payload(project_root: str | Path, requirements: str | Path | None = None) -> dict[str, object]:
    root = Path(project_root).resolve()
    req = Path(requirements).resolve() if requirements is not None else None
    requirements_context = load_project_context(root, req)
    codebase_context = build_codebase_context(root, requirements_context)
    decision = build_agent_decision(root, requirements_context, codebase_context.domain_graph, codebase_context.skill_tree)
    return _with_api_meta(decision.__dict__)


def fingerprint_payload(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    runtime = DeepAgentsRuntime(root)
    return _with_api_meta(
        runtime.run(
            "fingerprint",
            f"Fingerprint the project at {root} and return framework_fingerprint JSON.",
            lambda: native_fingerprint_payload(root),
        )
    )


def intent_payload(requirements: str | Path) -> dict[str, object]:
    path = Path(requirements).resolve()
    runtime = DeepAgentsRuntime(path.parent)
    return _with_api_meta(
        runtime.run(
            "intent",
            f"Parse the requirements file at {path} and return structured project intent JSON.",
            lambda: native_intent_payload(path),
        )
    )


def plan_payload(requirements: str | Path | None, project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    req = Path(requirements).resolve() if requirements is not None else None
    runtime = DeepAgentsRuntime(root)
    events = [
        {"message": "Reading project scope and available inputs for roadmap planning."},
        {"message": "Synthesizing implementation phases and sequencing the next delivery steps."},
    ]
    result = runtime.run(
            "plan",
            f"Build a roadmap plan for project_root={root} using requirements={req}. Return JSON with model and steps.",
            lambda: native_plan_payload(req, root),
        )
    return _with_api_meta(
        {
            "runtime": current_runtime_mode(root),
            "runtime_diagnostics": runtime_diagnostics(root),
            "events": events,
            **result,
        }
    )


def analyze_payload(project_root: str | Path, requirements: str | Path | None = None) -> dict[str, object]:
    root = Path(project_root).resolve()
    req = Path(requirements).resolve() if requirements is not None else None
    runtime = DeepAgentsRuntime(root)
    return _with_api_meta(
        runtime.run(
            "analyze",
            f"Analyze project_root={root} requirements={req} and return JSON with project_root, framework_fingerprint, signals, import_graph, and optional detected_domains/skill_tree.",
            lambda: native_analyze_payload(root, req),
        )
    )


def deliver_payload(requirements: str | Path | None, project_root: str | Path) -> dict[str, object]:
    events: list[dict[str, object]] = []

    def report(message: str) -> None:
        events.append({"message": message})

    generated = run_delivery(
        Path(requirements).resolve() if requirements is not None else None,
        Path(project_root).resolve(),
        progress_callback=report,
    )
    return _with_api_meta(
        {
            "runtime": current_runtime_mode(Path(project_root).resolve()),
            "runtime_diagnostics": runtime_diagnostics(Path(project_root).resolve()),
            "events": events,
            "generated_files": [str(path) for path in generated],
        }
    )


def preview_payload(
    requirements: str | Path | None,
    project_root: str | Path,
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
) -> dict[str, object]:
    root = Path(project_root).resolve()
    req = Path(requirements).resolve() if requirements is not None else None
    runtime = DeepAgentsRuntime(root)
    return _with_api_meta(
        runtime.run(
            "preview",
            f"Preview delivery for project_root={root} requirements={req} targets={list(targets)} domains={list(domains)} without writing files.",
            lambda: native_preview_payload(req, root, targets=targets, domains=domains),
        )
    )


def create_deliver_job(requirements: str | Path | None, project_root: str | Path) -> dict[str, object]:
    resolved_requirements = str(Path(requirements).resolve()) if requirements is not None else None
    resolved_root = str(Path(project_root).resolve())

    def run_with_progress(report: Callable[[int, str], None]) -> dict[str, object]:
        report(10, "Starting delivery and loading project inputs.")
        report(25, "Reading the codebase and optional requirements.")
        report(45, "Building project context and identifying implementation patterns.")
        report(70, "Generating docs and skills for coding agents.")
        result = deliver_payload(resolved_requirements, resolved_root)
        report(90, "Finalizing generated outputs.")
        return result

    job = submit_job(
        "deliver",
        {"requirements": resolved_requirements, "project_root": resolved_root},
        run_with_progress,
    )
    return _with_api_meta(job_payload(job))


def cancel_job_payload(job_id: str, project_root: str | Path | None = None) -> dict[str, object]:
    job = request_cancel(job_id, project_root)
    if job is None:
        return _with_api_meta({"error": "not_found", "job_id": job_id})
    return _with_api_meta(job_payload(job))


def resume_job_payload(job_id: str, project_root: str | Path | None = None) -> dict[str, object]:
    job = get_job(job_id, project_root)
    if job is None:
        return _with_api_meta({"error": "not_found", "job_id": job_id})
    requirements = job.payload.get("requirements")
    resolved_root = job.payload.get("project_root")
    if job.job_type != "deliver" or not isinstance(requirements, str) or not isinstance(resolved_root, str):
        return _with_api_meta({"error": "unsupported_resume", "job_id": job_id})
    if job.status not in {"failed", "cancelled"}:
        return _with_api_meta({"error": "resume_not_allowed", "job_id": job_id, "status": job.status})
    return create_deliver_job(requirements, resolved_root)


def job_status_payload(job_id: str, project_root: str | Path | None = None) -> dict[str, object]:
    job = get_job(job_id, project_root)
    if job is None:
        return _with_api_meta({"error": "not_found", "job_id": job_id})
    return _with_api_meta(job_payload(job))


def jobs_payload(project_root: str | Path | None = None) -> dict[str, object]:
    return _with_api_meta({"jobs": [job_payload(job) for job in list_jobs(project_root)]})


def features_payload(requirements: str | Path | None, project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    req = Path(requirements).resolve() if requirements is not None else None
    runtime = DeepAgentsRuntime(root)
    events = [
        {"message": "Reading the codebase and optional requirements to identify product capabilities."},
        {"message": "Grouping detected backend, frontend, and planning signals into a feature inventory."},
    ]
    result = runtime.run(
            "features",
            f"Build the feature inventory for project_root={root} requirements={req}. Return JSON with features.",
            lambda: native_features_payload(req, root),
        )
    return _with_api_meta(
        {
            "runtime": current_runtime_mode(root),
            "runtime_diagnostics": runtime_diagnostics(root),
            "events": events,
            **result,
        }
    )


def map_payload(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    runtime = DeepAgentsRuntime(root)
    return _with_api_meta(
        runtime.run(
            "map",
            f"Build the import and relationship map for project_root={root}. Return JSON with import_graph.",
            lambda: native_map_payload(root),
        )
    )


def status_payload(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    runtime = DeepAgentsRuntime(root)
    requirements_context = load_project_context(root, None)
    codebase_context = build_codebase_context(root, requirements_context)
    freshness = compute_freshness_report(root, requirements_context, codebase_context.domain_graph, load_freshness_state(root))
    current_run = load_current_run_memory(root)
    external_skill_detection = detect_external_skill_sources(root)
    return _with_api_meta(
        {
            **runtime.run(
                "status",
                f"Summarize generated artifact status for project_root={root}.",
                lambda: native_status_payload(root),
            ),
            "freshness": freshness.__dict__,
            "current_run_memory": current_run.__dict__ if current_run is not None else None,
            "agent_decision": build_agent_decision(root, requirements_context, codebase_context.domain_graph, codebase_context.skill_tree).__dict__,
            "installed_external_skills": installed_external_skills(root),
            "active_external_skills": active_external_skills(root),
            "ranked_external_skills": ranked_external_skills(root),
            "external_skill_lock": external_skill_lock(root),
            "external_skill_policy": external_skill_policy(root),
            "external_skill_recommendations": external_skill_detection["manual_recommendations"],
            "enterprise_skills": list_enterprise_skills(root),
            "active_enterprise_skills": active_enterprise_skills(root),
            "recommended_mcp_connectors": recommend_mcp_connectors(root),
            "active_mcp_connectors": active_mcp_connectors(root),
            "auto_update": auto_update_status(root),
            "skilgen_score": compute_skillgen_score(root),
        }
    )


def score_payload(project_root: str | Path, badge_file: str | Path | None = None) -> dict[str, object]:
    root = Path(project_root).resolve()
    payload = compute_skillgen_score(root)
    if badge_file is not None:
        payload["badge_file"] = write_score_badge(root, badge_file)
    return _with_api_meta(payload)


def score_badge_payload(project_root: str | Path) -> str:
    return render_score_badge_svg(compute_skillgen_score(Path(project_root).resolve()))


def skills_list_payload(project_root: str | Path, ecosystem: str | None = None, search: str | None = None) -> dict[str, object]:
    return _with_api_meta(list_external_skills(Path(project_root).resolve(), ecosystem=ecosystem, search=search))


def skills_detect_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta(detect_external_skill_sources(Path(project_root).resolve()))


def skills_active_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta({"skills": active_external_skills(Path(project_root).resolve())})


def skills_lock_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta(external_skill_lock(Path(project_root).resolve()))


def skills_lock_export_payload(project_root: str | Path, output_path: str | Path | None = None) -> dict[str, object]:
    return _with_api_meta(export_external_skill_lock(project_root=Path(project_root).resolve(), output_path=output_path))


def skills_lock_import_payload(project_root: str | Path, input_path: str | Path, *, sync_existing: bool = False) -> dict[str, object]:
    return _with_api_meta(import_external_skill_lock(project_root=Path(project_root).resolve(), input_path=input_path, sync_existing=sync_existing))


def skills_rank_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta(ranked_external_skills(Path(project_root).resolve()))


def skills_policy_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta(external_skill_policy(Path(project_root).resolve()))


def skills_show_payload(slug: str, project_root: str | Path) -> dict[str, object]:
    return _with_api_meta({"skill": get_external_skill(slug, Path(project_root).resolve())})


def skills_install_payload(
    project_root: str | Path,
    *,
    slug: str | None = None,
    git_url: str | None = None,
    name: str | None = None,
    force: bool = False,
    ref: str | None = None,
    active: bool | None = None,
) -> dict[str, object]:
    return _with_api_meta(
        {
            "installed_skill": install_external_skill(
                project_root=Path(project_root).resolve(),
                slug=slug,
                git_url=git_url,
                name=name,
                force=force,
                ref=ref,
                active=active,
            )
        }
    )


def skills_import_payload(
    project_root: str | Path,
    slug: str,
    *,
    limit: int = 5,
    active: bool | None = None,
) -> dict[str, object]:
    return _with_api_meta(import_external_skill_candidates(project_root=Path(project_root).resolve(), slug=slug, limit=limit, active=active))


def skills_sync_payload(project_root: str | Path, slug: str | None = None, *, all_sources: bool = False) -> dict[str, object]:
    root = Path(project_root).resolve()
    if all_sources:
        return _with_api_meta(sync_all_external_skills(project_root=root))
    if slug is None:
        return _with_api_meta({"error": "missing_slug"})
    return _with_api_meta({"synced_skill": sync_external_skill(project_root=root, slug=slug)})


def skills_remove_payload(project_root: str | Path, slug: str) -> dict[str, object]:
    return _with_api_meta({"removed_skill": remove_external_skill(project_root=Path(project_root).resolve(), slug=slug)})


def skills_activate_payload(project_root: str | Path, slug: str) -> dict[str, object]:
    return _with_api_meta({"activated_skill": activate_external_skill(project_root=Path(project_root).resolve(), slug=slug)})


def skills_deactivate_payload(project_root: str | Path, slug: str) -> dict[str, object]:
    return _with_api_meta({"deactivated_skill": deactivate_external_skill(project_root=Path(project_root).resolve(), slug=slug)})


def enterprise_list_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta({"skills": list_enterprise_skills(Path(project_root).resolve())})


def enterprise_ingest_payload(
    project_root: str | Path,
    *,
    name: str,
    path: str | Path | None = None,
    git_url: str | None = None,
    ref: str | None = None,
    activate: bool | None = None,
    kind: str = "enterprise",
) -> dict[str, object]:
    return _with_api_meta(
        {
            "enterprise_skill": ingest_enterprise_skill(
                Path(project_root).resolve(),
                name=name,
                path=path,
                git_url=git_url,
                ref=ref,
                activate=activate,
                kind=kind,
            )
        }
    )


def enterprise_generate_payload(
    project_root: str | Path,
    *,
    name: str,
    source_paths: list[str | Path],
    kind: str = "domain",
    activate: bool = True,
) -> dict[str, object]:
    return _with_api_meta(
        {
            "enterprise_skill": generate_enterprise_skill(
                Path(project_root).resolve(),
                name=name,
                source_paths=source_paths,
                kind=kind,
                activate=activate,
            )
        }
    )


def connectors_list_payload(system: str | None = None, search: str | None = None) -> dict[str, object]:
    return _with_api_meta(connector_catalog(system=system, search=search))


def connectors_recommend_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta(recommend_mcp_connectors(Path(project_root).resolve()))


def connectors_active_payload(project_root: str | Path) -> dict[str, object]:
    return _with_api_meta({"connectors": active_mcp_connectors(Path(project_root).resolve())})


def connectors_activate_payload(project_root: str | Path, slug: str) -> dict[str, object]:
    return _with_api_meta({"connector": activate_mcp_connector(Path(project_root).resolve(), slug)})


def connectors_deactivate_payload(project_root: str | Path, slug: str) -> dict[str, object]:
    return _with_api_meta({"connector": deactivate_mcp_connector(Path(project_root).resolve(), slug)})


def report_payload(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    runtime = DeepAgentsRuntime(root)
    return _with_api_meta(
        runtime.run(
            "report",
            f"Build a project report for project_root={root}. Return JSON with status, domains, signal_counts, and summary.",
            lambda: native_report_payload(root),
        )
    )


def validate_payload(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    runtime = DeepAgentsRuntime(root)
    payload = runtime.run(
            "validate",
            f"Validate project_root={root}. Return JSON with valid, errors, warnings, coverage, and completeness_score.",
            lambda: native_validate_payload(root),
        )
    payload["skilgen_score"] = compute_skillgen_score(root)
    return _with_api_meta(payload)
