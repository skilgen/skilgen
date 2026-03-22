"""Skilgen package."""

from skilgen.agents import fingerprint_project
from skilgen.delivery import run_delivery
from skilgen.sdk import (
    analyze_project,
    cancel_job,
    deliver_project,
    get_job_status,
    init_project,
    install_skill_source,
    list_project_jobs,
    list_skill_sources,
    map_codebase,
    plan_project,
    preview_project,
    project_report,
    project_status,
    remove_skill_source,
    resume_job,
    show_skill_source,
    start_deliver_job,
    sync_skill_source,
    update_project,
    validate_project_outputs,
    watch_project,
)

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "analyze_project",
    "cancel_job",
    "deliver_project",
    "fingerprint_project",
    "get_job_status",
    "init_project",
    "install_skill_source",
    "list_project_jobs",
    "list_skill_sources",
    "map_codebase",
    "plan_project",
    "preview_project",
    "project_report",
    "project_status",
    "remove_skill_source",
    "resume_job",
    "run_delivery",
    "show_skill_source",
    "start_deliver_job",
    "sync_skill_source",
    "update_project",
    "validate_project_outputs",
    "watch_project",
]
