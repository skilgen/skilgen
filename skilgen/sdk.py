from __future__ import annotations

from pathlib import Path

from skilgen.api.service import (
    analyze_payload,
    cancel_job_payload,
    decision_payload,
    create_deliver_job,
    features_payload,
    fingerprint_payload,
    intent_payload,
    job_status_payload,
    jobs_payload,
    map_payload,
    plan_payload,
    preview_payload,
    resume_job_payload,
    report_payload,
    status_payload,
    validate_payload,
)
from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, stop_auto_update_worker
from skilgen.core.config import render_default_config
from skilgen.delivery import run_delivery, watch_delivery
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
from skilgen.external_skills import (
    activate_external_skill,
    active_external_skills,
    detect_external_skill_sources,
    external_skill_lock,
    external_skill_policy,
    deactivate_external_skill,
    export_external_skill_lock,
    get_external_skill,
    import_external_skill_candidates,
    import_external_skill_lock,
    install_external_skill,
    list_external_skills,
    ranked_external_skills,
    remove_external_skill,
    sync_all_external_skills,
    sync_external_skill,
)


def init_project(project_root: str | Path = ".") -> Path:
    root = Path(project_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "skilgen.yml"
    if not config_path.exists():
        config_path.write_text(render_default_config(), encoding="utf-8")
    ensure_auto_update_worker(root)
    return config_path


def fingerprint_codebase(project_root: str | Path = ".") -> dict[str, object]:
    return fingerprint_payload(Path(project_root).resolve())


def map_codebase(project_root: str | Path = ".") -> dict[str, object]:
    return map_payload(Path(project_root).resolve())


def analyze_project(project_root: str | Path = ".", requirements: str | Path | None = None) -> dict[str, object]:
    resolved_requirements = Path(requirements).resolve() if requirements is not None else None
    return analyze_payload(Path(project_root).resolve(), resolved_requirements)


def decide_project(project_root: str | Path = ".", requirements: str | Path | None = None) -> dict[str, object]:
    resolved_requirements = Path(requirements).resolve() if requirements is not None else None
    return decision_payload(Path(project_root).resolve(), resolved_requirements)


def parse_intent(requirements: str | Path) -> dict[str, object]:
    return intent_payload(Path(requirements).resolve())


def extract_feature_inventory(requirements: str | Path, project_root: str | Path = ".") -> dict[str, object]:
    return features_payload(Path(requirements).resolve(), Path(project_root).resolve())


def plan_project(requirements: str | Path, project_root: str | Path = ".") -> dict[str, object]:
    return plan_payload(Path(requirements).resolve(), Path(project_root).resolve())


def deliver_project(
    requirements: str | Path,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    dry_run: bool = False,
) -> list[Path]:
    return run_delivery(requirements, project_root, targets=targets, domains=domains, dry_run=dry_run)


def preview_project(
    requirements: str | Path,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
) -> dict[str, object]:
    return preview_payload(requirements, project_root, targets=targets, domains=domains)


def update_project(
    requirements: str | Path,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    dry_run: bool = False,
) -> list[Path]:
    return run_delivery(requirements, project_root, targets=targets, domains=domains, dry_run=dry_run)


def watch_project(
    requirements: str | Path,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    interval_seconds: float = 2.0,
    cycles: int = 0,
    once: bool = False,
) -> list[list[Path]]:
    return watch_delivery(
        requirements,
        project_root,
        targets=targets,
        domains=domains,
        interval_seconds=interval_seconds,
        cycles=cycles,
        once=once,
    )


def project_status(project_root: str | Path = ".") -> dict[str, object]:
    return status_payload(Path(project_root).resolve())


def start_auto_update(project_root: str | Path = ".", requirements: str | Path | None = None) -> dict[str, object]:
    resolved_requirements = Path(requirements).resolve() if requirements is not None else None
    return ensure_auto_update_worker(Path(project_root).resolve(), requirements_path=resolved_requirements)


def stop_auto_update(project_root: str | Path = ".") -> dict[str, object]:
    return stop_auto_update_worker(Path(project_root).resolve())


def get_auto_update_status(project_root: str | Path = ".") -> dict[str, object]:
    return auto_update_status(Path(project_root).resolve())


def project_report(project_root: str | Path = ".") -> dict[str, object]:
    return report_payload(Path(project_root).resolve())


def validate_project_outputs(project_root: str | Path = ".") -> dict[str, object]:
    return validate_payload(Path(project_root).resolve())


def start_deliver_job(requirements: str | Path, project_root: str | Path = ".") -> dict[str, object]:
    return create_deliver_job(requirements, project_root)


def cancel_job(job_id: str, project_root: str | Path | None = None) -> dict[str, object]:
    return cancel_job_payload(job_id, Path(project_root).resolve() if project_root is not None else None)


def resume_job(job_id: str, project_root: str | Path | None = None) -> dict[str, object]:
    return resume_job_payload(job_id, Path(project_root).resolve() if project_root is not None else None)


def get_job_status(job_id: str, project_root: str | Path | None = None) -> dict[str, object]:
    return job_status_payload(job_id, Path(project_root).resolve() if project_root is not None else None)


def list_project_jobs(project_root: str | Path | None = None) -> dict[str, object]:
    return jobs_payload(Path(project_root).resolve() if project_root is not None else None)


def list_skill_sources(
    project_root: str | Path = ".",
    *,
    ecosystem: str | None = None,
    search: str | None = None,
) -> dict[str, object]:
    return list_external_skills(Path(project_root).resolve(), ecosystem=ecosystem, search=search)


def detect_skill_sources(project_root: str | Path = ".") -> dict[str, object]:
    return detect_external_skill_sources(Path(project_root).resolve())


def list_active_skill_sources(project_root: str | Path = ".") -> dict[str, object]:
    return {"skills": active_external_skills(Path(project_root).resolve())}


def skill_source_lock(project_root: str | Path = ".") -> dict[str, object]:
    return external_skill_lock(Path(project_root).resolve())


def export_skill_source_lock(project_root: str | Path = ".", output_path: str | Path | None = None) -> dict[str, object]:
    return export_external_skill_lock(project_root=Path(project_root).resolve(), output_path=output_path)


def import_skill_source_lock(
    project_root: str | Path = ".",
    input_path: str | Path = ".",
    *,
    sync_existing: bool = False,
) -> dict[str, object]:
    return import_external_skill_lock(project_root=Path(project_root).resolve(), input_path=input_path, sync_existing=sync_existing)


def import_skill_source_candidates(
    slug: str,
    project_root: str | Path = ".",
    *,
    limit: int = 5,
    active: bool | None = None,
) -> dict[str, object]:
    return import_external_skill_candidates(project_root=Path(project_root).resolve(), slug=slug, limit=limit, active=active)


def rank_skill_sources(project_root: str | Path = ".") -> dict[str, object]:
    return ranked_external_skills(Path(project_root).resolve())


def skill_source_policy(project_root: str | Path = ".") -> dict[str, object]:
    return external_skill_policy(Path(project_root).resolve())


def list_enterprise_skill_sources(project_root: str | Path = ".") -> dict[str, object]:
    return {"skills": list_enterprise_skills(Path(project_root).resolve())}


def ingest_enterprise_skill_source(
    name: str,
    project_root: str | Path = ".",
    *,
    path: str | Path | None = None,
    git_url: str | None = None,
    ref: str | None = None,
    activate: bool | None = None,
    kind: str = "enterprise",
) -> dict[str, object]:
    return {
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


def generate_enterprise_skill_source(
    name: str,
    source_paths: list[str | Path],
    project_root: str | Path = ".",
    *,
    kind: str = "domain",
    activate: bool = True,
) -> dict[str, object]:
    return {
        "enterprise_skill": generate_enterprise_skill(
            Path(project_root).resolve(),
            name=name,
            source_paths=source_paths,
            kind=kind,
            activate=activate,
        )
    }


def list_mcp_connectors(*, system: str | None = None, search: str | None = None) -> dict[str, object]:
    return connector_catalog(system=system, search=search)


def recommend_project_mcp_connectors(project_root: str | Path = ".") -> dict[str, object]:
    return recommend_mcp_connectors(Path(project_root).resolve())


def list_active_mcp_connectors(project_root: str | Path = ".") -> dict[str, object]:
    return {"connectors": active_mcp_connectors(Path(project_root).resolve())}


def activate_project_mcp_connector(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"connector": activate_mcp_connector(Path(project_root).resolve(), slug)}


def deactivate_project_mcp_connector(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"connector": deactivate_mcp_connector(Path(project_root).resolve(), slug)}


def show_skill_source(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"skill": get_external_skill(slug, Path(project_root).resolve())}


def install_skill_source(
    project_root: str | Path = ".",
    *,
    slug: str | None = None,
    git_url: str | None = None,
    name: str | None = None,
    force: bool = False,
    ref: str | None = None,
    active: bool | None = None,
) -> dict[str, object]:
    return {
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


def sync_skill_source(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"synced_skill": sync_external_skill(project_root=Path(project_root).resolve(), slug=slug)}


def sync_all_skill_sources(project_root: str | Path = ".") -> dict[str, object]:
    return sync_all_external_skills(project_root=Path(project_root).resolve())


def remove_skill_source(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"removed_skill": remove_external_skill(project_root=Path(project_root).resolve(), slug=slug)}


def activate_skill_source(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"activated_skill": activate_external_skill(project_root=Path(project_root).resolve(), slug=slug)}


def deactivate_skill_source(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"deactivated_skill": deactivate_external_skill(project_root=Path(project_root).resolve(), slug=slug)}
