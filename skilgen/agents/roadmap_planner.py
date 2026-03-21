from __future__ import annotations

from pathlib import Path

from skilgen.deep_agents_core import run_deep_json
from skilgen.agents.model_registry import resolve_model_settings
from skilgen.core.models import PlanStep, ProjectIntent, RoadmapPlan, SkilgenConfig


def build_roadmap_plan_native(config: SkilgenConfig, intent: ProjectIntent) -> RoadmapPlan:
    model = resolve_model_settings(config)
    steps = [
        PlanStep(
            phase="phase-0",
            title="Lock contracts and output formats",
            description="Stabilize AGENTS.md, SKILL.md, MANIFEST.md, FEATURES.md, and config contracts.",
            status="completed",
        ),
        PlanStep(
            phase="phase-1",
            title="Strengthen analysis agents",
            description="Expand framework fingerprinting, requirements parsing, and codebase context generation.",
            status="completed",
        ),
        PlanStep(
            phase="phase-2",
            title="Generate richer skills from code and intent",
            description="Use project intent and codebase analysis to produce deeper, bidirectionally linked skills.",
            status="completed",
        ),
        PlanStep(
            phase="phase-3",
            title="Complete CLI and SDK ergonomics",
            description="Finish install, scan, validate, status, report, and watch flows with clear outputs.",
            status="pending",
        ),
    ]
    if intent.endpoints:
        steps.append(
            PlanStep(
                phase="phase-2",
                title="Add endpoint-aware feature extraction",
                description="Extract and track API endpoints, route mappings, and endpoint coverage expectations.",
                status="completed",
            )
        )
    if intent.ui_flows:
        steps.append(
            PlanStep(
                phase="phase-2",
                title="Add UI flow and route extraction",
                description="Track UI routes, page composition, and frontend flow coverage from requirements and code.",
                status="completed",
            )
        )
    return RoadmapPlan(model=model, steps=steps)


def build_roadmap_plan(config: SkilgenConfig, intent: ProjectIntent, project_root: Path | str = ".") -> RoadmapPlan:
    native_plan = build_roadmap_plan_native(config, intent)
    root = Path(project_root).resolve()
    payload = run_deep_json(
        "roadmap planning",
        (
            "Build a phase-based implementation roadmap for Skilgen. Return JSON with keys model and steps. "
            "model should include provider, model, api_key_env, api_key_present. steps should be a list of "
            "objects with phase, title, description, status. Optimize for execution order, dependency awareness, "
            "and clear agent handoff. Prefer phases that break the work into coherent capability slices rather than "
            "generic milestones. When endpoints or UI flows exist, reflect them in roadmap steps that strengthen "
            "coverage, validation, and skill generation quality.\n\n"
            f"Intent features: {intent.features}\n"
            f"Intent domain_concepts: {intent.domain_concepts}\n"
            f"Intent entities: {intent.entities}\n"
            f"Intent endpoints: {intent.endpoints}\n"
            f"Intent ui_flows: {intent.ui_flows}\n"
        ),
        lambda: {
            "model": native_plan.model.__dict__,
            "steps": [step.__dict__ for step in native_plan.steps],
        },
        project_root=root,
    )
    steps = [
        PlanStep(
            phase=str(step.get("phase", "phase-3")),
            title=str(step.get("title", "Roadmap step")),
            description=str(step.get("description", "")),
            status=str(step.get("status", "pending")),
        )
        for step in payload.get("steps", [])
    ]
    if not steps:
        steps = native_plan.steps
    return RoadmapPlan(model=resolve_model_settings(config), steps=steps)
