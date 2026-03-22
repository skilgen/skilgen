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
from skilgen.core.config import render_default_config
from skilgen.delivery import run_delivery, watch_delivery
from skilgen.external_skills import get_external_skill, install_external_skill, list_external_skills


def init_project(project_root: str | Path = ".") -> Path:
    root = Path(project_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    config_path = root / "skilgen.yml"
    if not config_path.exists():
        config_path.write_text(render_default_config(), encoding="utf-8")
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


def show_skill_source(slug: str, project_root: str | Path = ".") -> dict[str, object]:
    return {"skill": get_external_skill(slug, Path(project_root).resolve())}


def install_skill_source(
    project_root: str | Path = ".",
    *,
    slug: str | None = None,
    git_url: str | None = None,
    name: str | None = None,
    force: bool = False,
) -> dict[str, object]:
    return {
        "installed_skill": install_external_skill(
            project_root=Path(project_root).resolve(),
            slug=slug,
            git_url=git_url,
            name=name,
            force=force,
        )
    }
