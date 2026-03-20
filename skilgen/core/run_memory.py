from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from pathlib import Path

from skilgen.core.models import FreshnessReport, RunMemory


def _memory_dir(project_root: Path) -> Path:
    return project_root.resolve() / ".skilgen" / "memory"


def _runs_dir(project_root: Path) -> Path:
    return _memory_dir(project_root) / "runs"


def _current_run_path(project_root: Path) -> Path:
    return _memory_dir(project_root) / "current_run.json"


def create_run_memory(
    project_root: Path,
    requirements_path: Path | None,
    runtime: str,
    freshness: FreshnessReport,
    selected_domains: list[str],
    selected_skill_paths: list[str],
) -> RunMemory:
    objective_mode = "codebase and requirements" if requirements_path is not None else "codebase only"
    active_file_focus = freshness.changed_files[:8]
    pending_validations: list[str] = []
    if "backend" in selected_domains:
        pending_validations.append("Validate all touched backend endpoints for both happy and failure paths.")
    if "frontend" in selected_domains:
        pending_validations.append("Check affected UI flows, routes, and reusable component paths.")
    unresolved_questions = []
    if not selected_domains:
        unresolved_questions.append("No impacted domains were selected yet; confirm whether the current skill tree should be reused.")
    resumable_steps = [
        "Load AGENTS.md and MANIFEST.md.",
        "Load prioritized parent skills and the freshest run memory.",
        "Refresh stale skills if the planner recommends it.",
        "Validate changed backend/frontend flows before finishing.",
    ]
    return RunMemory(
        run_id=f"run-{uuid.uuid4().hex[:12]}",
        status="running",
        project_root=str(project_root.resolve()),
        requirements_path=str(requirements_path.resolve()) if requirements_path is not None else None,
        objective=f"Generate and refresh Skilgen outputs from {objective_mode}.",
        runtime=runtime,
        impacted_domains=freshness.impacted_domains,
        selected_domains=selected_domains,
        selected_skill_paths=selected_skill_paths,
        changed_files=freshness.changed_files,
        generated_files=[],
        active_file_focus=active_file_focus,
        unresolved_questions=unresolved_questions,
        pending_validations=pending_validations,
        resumable_steps=resumable_steps,
        recent_events=[],
    )


def save_run_memory(project_root: Path, memory: RunMemory) -> Path:
    runs_dir = _runs_dir(project_root)
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_path = runs_dir / f"{memory.run_id}.json"
    payload = asdict(memory)
    run_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _current_run_path(project_root).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return run_path


def append_run_event(project_root: Path, memory: RunMemory, message: str) -> RunMemory:
    events = [*memory.recent_events, message][-12:]
    updated = RunMemory(
        run_id=memory.run_id,
        status=memory.status,
        project_root=memory.project_root,
        requirements_path=memory.requirements_path,
        objective=memory.objective,
        runtime=memory.runtime,
        impacted_domains=memory.impacted_domains,
        selected_domains=memory.selected_domains,
        selected_skill_paths=memory.selected_skill_paths,
        changed_files=memory.changed_files,
        generated_files=memory.generated_files,
        active_file_focus=memory.active_file_focus,
        unresolved_questions=memory.unresolved_questions,
        pending_validations=memory.pending_validations,
        resumable_steps=memory.resumable_steps,
        recent_events=events,
    )
    save_run_memory(Path(memory.project_root), updated)
    return updated


def finalize_run_memory(project_root: Path, memory: RunMemory, generated_files: list[Path], status: str = "completed") -> RunMemory:
    updated = RunMemory(
        run_id=memory.run_id,
        status=status,
        project_root=memory.project_root,
        requirements_path=memory.requirements_path,
        objective=memory.objective,
        runtime=memory.runtime,
        impacted_domains=memory.impacted_domains,
        selected_domains=memory.selected_domains,
        selected_skill_paths=memory.selected_skill_paths,
        changed_files=memory.changed_files,
        generated_files=[str(path.resolve()) for path in generated_files],
        active_file_focus=memory.active_file_focus,
        unresolved_questions=memory.unresolved_questions,
        pending_validations=memory.pending_validations,
        resumable_steps=memory.resumable_steps,
        recent_events=memory.recent_events,
    )
    save_run_memory(project_root, updated)
    return updated


def load_current_run_memory(project_root: Path) -> RunMemory | None:
    path = _current_run_path(project_root)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return RunMemory(
        run_id=str(payload.get("run_id", "")),
        status=str(payload.get("status", "unknown")),
        project_root=str(payload.get("project_root", "")),
        requirements_path=str(payload.get("requirements_path")) if payload.get("requirements_path") is not None else None,
        objective=str(payload.get("objective", "")),
        runtime=str(payload.get("runtime", "")),
        impacted_domains=[str(item) for item in payload.get("impacted_domains", [])],
        selected_domains=[str(item) for item in payload.get("selected_domains", [])],
        selected_skill_paths=[str(item) for item in payload.get("selected_skill_paths", [])],
        changed_files=[str(item) for item in payload.get("changed_files", [])],
        generated_files=[str(item) for item in payload.get("generated_files", [])],
        active_file_focus=[str(item) for item in payload.get("active_file_focus", [])],
        unresolved_questions=[str(item) for item in payload.get("unresolved_questions", [])],
        pending_validations=[str(item) for item in payload.get("pending_validations", [])],
        resumable_steps=[str(item) for item in payload.get("resumable_steps", [])],
        recent_events=[str(item) for item in payload.get("recent_events", [])],
    )
