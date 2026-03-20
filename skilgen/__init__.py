"""Skilgen package."""

from skilgen.agents import fingerprint_project
from skilgen.delivery import run_delivery
from skilgen.sdk import (
    analyze_project,
    cancel_job,
    deliver_project,
    get_job_status,
    init_project,
    list_project_jobs,
    map_codebase,
    plan_project,
    preview_project,
    project_report,
    project_status,
    resume_job,
    start_deliver_job,
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
    "list_project_jobs",
    "map_codebase",
    "plan_project",
    "preview_project",
    "project_report",
    "project_status",
    "resume_job",
    "run_delivery",
    "start_deliver_job",
    "update_project",
    "validate_project_outputs",
    "watch_project",
]
