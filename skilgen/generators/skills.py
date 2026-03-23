from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from skilgen.agents.codebase_signals import analyze_codebase
from skilgen.agents.requirements_parser import parse_project_intent
from skilgen.agents.roadmap_planner import build_roadmap_plan
from skilgen.core.config import load_config
from skilgen.core.context import build_codebase_context
from skilgen.core.models import RequirementsContext, SkillSpec
from skilgen.deep_agents_core import run_deep_text


TODAY = date.today().isoformat()


def _signal_bullets(items: list[str], fallback: str, limit: int = 5) -> list[str]:
    if not items:
        return [fallback]
    bullets = [f"Detected: `{item}`" for item in items[:limit]]
    if len(items) > limit:
        bullets.append(f"Detected {len(items) - limit} more matching files elsewhere in the repo.")
    return bullets


def _slug_name(name: str) -> str:
    return name.replace(" ", "-").lower()


def _relative_skill_ref(from_skill_path: str, to_skill_path: str) -> str:
    return os.path.relpath(to_skill_path, Path(from_skill_path).parent).replace("\\", "/")


def _parent_reference_map(context: RequirementsContext, project_root: Path) -> dict[str, str]:
    codebase_context = build_codebase_context(project_root, context)
    return {
        node.domain: node.path
        for node in codebase_context.skill_tree
        if node.parent_skill is None
    }


def _dynamic_parent_specs(context: RequirementsContext, project_root: Path) -> list[SkillSpec]:
    codebase_context = build_codebase_context(project_root, context)
    parent_nodes = [node for node in codebase_context.domain_graph.nodes if node.parent_domain is None and node.skill_path]
    specs: list[SkillSpec] = []
    for node in parent_nodes:
        references = []
        for related in node.related_domains:
            related_node = next((item for item in codebase_context.domain_graph.nodes if item.name == related and item.skill_path), None)
            if related_node is not None and related_node.skill_path != node.skill_path:
                references.append(_relative_skill_ref(node.skill_path, related_node.skill_path))
        for child_name in node.child_domains:
            child_node = next((item for item in codebase_context.domain_graph.nodes if item.name == child_name and item.skill_path), None)
            if child_node is not None:
                references.append(_relative_skill_ref(node.skill_path, child_node.skill_path))
        references = list(dict.fromkeys(references))
        specs.append(
            SkillSpec(
                path=node.skill_path.removeprefix("skills/"),
                name=_slug_name(node.name),
                domain=node.name,
                sub_domain="platform",
                overview=node.summary,
                checks=[f"{{{{project_root}}}}/{Path(item).parts[0]}/" if "/" in item else f"{{{{project_root}}}}/{item}" for item in node.key_files[:3]] or ["{{project_root}}/"],
                patterns=[
                    ("Inferred domain patterns", node.key_patterns or ["Use the inferred project structure before introducing a new top-level convention."]),
                    ("Dynamic topology", ["This parent skill was inferred from the current repo and may expand or contract as the codebase evolves."]),
                ],
                how_to=[
                    "Start from the nearest evidence file in this inferred domain.",
                    "Reuse the current structure before creating a new sibling domain or folder.",
                    "Refresh this parent skill when the planner says the domain topology has changed.",
                ],
                references=references,
            )
        )
    return specs


def _legacy_child_specs(context: RequirementsContext, project_root: Path) -> list[SkillSpec]:
    signals = analyze_codebase(project_root)
    references = _parent_reference_map(context, project_root)
    specs: list[SkillSpec] = []

    if "backend" in references:
        specs.extend(
            [
                SkillSpec(
                    path="backend/api/SKILL.md",
                    name="backend-api",
                    domain="backend",
                    sub_domain="api",
                    overview="Focused guidance for defining or changing API endpoints.",
                    checks=["{{project_root}}/backend/api/", "{{project_root}}/server/routes/", "{{project_root}}/tests/"],
                    patterns=[("Endpoint lifecycle", ["Define the request contract, validate inputs, delegate to services, and map stable responses."])],
                    how_to=[
                        "List all endpoints created or changed by the feature.",
                        "Define request and response contracts.",
                        "Implement the route or controller layer.",
                        "Add tests for every impacted endpoint.",
                    ],
                    references=["../SKILL.md", "../../requirements/SKILL.md"],
                ),
                SkillSpec(
                    path="backend/testing/SKILL.md",
                    name="backend-testing",
                    domain="backend",
                    sub_domain="testing",
                    overview="Verification rules for backend work, especially endpoint coverage.",
                    checks=["{{project_root}}/tests/", "{{project_root}}/backend/tests/", "{{project_root}}/server/tests/"],
                    patterns=[("Endpoint-first verification", ["Test happy paths and failure modes for each impacted endpoint."])],
                    how_to=[
                        "Enumerate every endpoint touched by the feature.",
                        "Add or update tests for success and failure cases.",
                        "Run the relevant test suite before closing the work.",
                    ],
                    references=["../SKILL.md", "../api/SKILL.md"],
                ),
            ]
        )
        if signals.backend_routes:
            specs.append(
                SkillSpec(
                    path="backend/routes/SKILL.md",
                    name="backend-routes",
                    domain="backend",
                    sub_domain="routes",
                    overview="Code-aware guidance for backend routes and handlers already present in the scanned project.",
                    checks=["{{project_root}}/backend/", "{{project_root}}/server/", "{{project_root}}/api/"],
                    patterns=[
                        ("Detected route files", _signal_bullets(signals.backend_routes, "No backend route files were detected.")),
                        ("Route extension pattern", ["Keep request parsing at the edge and move business logic into services."]),
                    ],
                    how_to=[
                        "Start with the closest existing route file from the detected list.",
                        "Trace the handler to the service or use-case layer before making changes.",
                        "Add endpoint tests for every touched success and failure path.",
                    ],
                    references=["../SKILL.md", "../api/SKILL.md", "../testing/SKILL.md"],
                )
            )
        if signals.services:
            specs.append(
                SkillSpec(
                    path="backend/services/SKILL.md",
                    name="backend-services",
                    domain="backend",
                    sub_domain="services",
                    overview="Code-aware guidance for service and use-case modules already present in the scanned project.",
                    checks=["{{project_root}}/backend/services/", "{{project_root}}/services/", "{{project_root}}/src/services/"],
                    patterns=[
                        ("Detected service files", _signal_bullets(signals.services, "No service files were detected.")),
                        ("Service boundary pattern", ["Keep orchestration, validation, and transport concerns separate from business logic."]),
                    ],
                    how_to=[
                        "Start from the closest service file in the detected list.",
                        "Reuse the current service naming and return-shape conventions.",
                        "Add endpoint or unit coverage for the service path you change.",
                    ],
                    references=["../SKILL.md", "../api/SKILL.md", "../testing/SKILL.md"],
                )
            )
        if signals.data_models or signals.persistence_layers:
            specs.append(
                SkillSpec(
                    path="backend/data/SKILL.md",
                    name="backend-data",
                    domain="backend",
                    sub_domain="data",
                    overview="Guidance for models, repositories, persistence layers, and data contracts detected in the project.",
                    checks=["{{project_root}}/models/", "{{project_root}}/repository/", "{{project_root}}/db/", "{{project_root}}/prisma/"],
                    patterns=[
                        ("Detected data model files", _signal_bullets(signals.data_models, "No data model files were detected.")),
                        ("Detected persistence files", _signal_bullets(signals.persistence_layers, "No persistence-layer files were detected.")),
                    ],
                    how_to=[
                        "Start from the nearest model or repository file in the detected list.",
                        "Confirm how data contracts flow between handlers, services, and persistence.",
                        "Keep schema or repository changes aligned with backend route and service guidance.",
                    ],
                    references=["../SKILL.md", "../services/SKILL.md", "../api/SKILL.md"],
                )
            )
        if signals.auth_files:
            specs.append(
                SkillSpec(
                    path="backend/auth/SKILL.md",
                    name="backend-auth",
                    domain="backend",
                    sub_domain="auth",
                    overview="Guidance for authentication, authorization, permission checks, and session handling patterns already present in the repo.",
                    checks=["{{project_root}}/auth/", "{{project_root}}/security/", "{{project_root}}/backend/"],
                    patterns=[("Detected auth files", _signal_bullets(signals.auth_files, "No auth files were detected."))],
                    how_to=[
                        "Trace the current user/session/permission path before making auth changes.",
                        "Validate both authorized and unauthorized backend responses.",
                        "Update endpoint and service tests for every changed auth path.",
                    ],
                    references=["../SKILL.md", "../api/SKILL.md", "../testing/SKILL.md"],
                )
            )
        if signals.background_jobs:
            specs.append(
                SkillSpec(
                    path="backend/jobs/SKILL.md",
                    name="backend-jobs",
                    domain="backend",
                    sub_domain="jobs",
                    overview="Guidance for background workers, cron tasks, queue processors, and offline execution paths detected in the project.",
                    checks=["{{project_root}}/jobs/", "{{project_root}}/workers/", "{{project_root}}/tasks/"],
                    patterns=[("Detected background job files", _signal_bullets(signals.background_jobs, "No background job files were detected."))],
                    how_to=[
                        "Start from the nearest existing job or worker file.",
                        "Identify the shared services or persistence paths the job relies on.",
                        "Add tests or smoke checks for success and failure execution paths.",
                    ],
                    references=["../SKILL.md", "../services/SKILL.md", "../testing/SKILL.md"],
                )
            )

    if "frontend" in references:
        specs.append(
            SkillSpec(
                path="frontend/components/SKILL.md",
                name="frontend-components",
                domain="frontend",
                sub_domain="components",
                overview="Guidance for reusable components and UI composition.",
                checks=["{{project_root}}/frontend/components/", "{{project_root}}/src/components/", "{{project_root}}/app/components/"],
                patterns=[
                    ("Dynamic location awareness", ["Resolve the nearest existing component folder before creating a new one."]),
                    ("Detected component files", _signal_bullets(signals.components, "No reusable component files were detected.")),
                ],
                how_to=[
                    "Find the nearest existing feature or shared component folder.",
                    "Match naming and export conventions for that area.",
                    "Add tests or story coverage if the project uses them.",
                ],
                references=["../SKILL.md", "../../requirements/SKILL.md"],
            )
        )
        if signals.frontend_routes:
            specs.append(
                SkillSpec(
                    path="frontend/routes/SKILL.md",
                    name="frontend-routes",
                    domain="frontend",
                    sub_domain="routes",
                    overview="Code-aware guidance for pages, screens, and route modules already present in the scanned project.",
                    checks=["{{project_root}}/frontend/", "{{project_root}}/src/", "{{project_root}}/app/"],
                    patterns=[
                        ("Detected route files", _signal_bullets(signals.frontend_routes, "No frontend route files were detected.")),
                        ("Route composition", ["Keep route-level data orchestration close to the page and move reusable UI into components."]),
                    ],
                    how_to=[
                        "Start with the closest existing route or page file from the detected list.",
                        "Reuse nearby components and shared state patterns before introducing new abstractions.",
                        "Update tests or route smoke checks if the project already has them.",
                    ],
                    references=["../SKILL.md", "../components/SKILL.md", "../../requirements/SKILL.md"],
                )
            )
        if signals.state_files:
            specs.append(
                SkillSpec(
                    path="frontend/state/SKILL.md",
                    name="frontend-state",
                    domain="frontend",
                    sub_domain="state",
                    overview="Guidance for client state, stores, contexts, reducers, and data-view synchronization patterns detected in the codebase.",
                    checks=["{{project_root}}/src/state/", "{{project_root}}/src/store/", "{{project_root}}/src/context/"],
                    patterns=[("Detected state files", _signal_bullets(signals.state_files, "No state files were detected."))],
                    how_to=[
                        "Start from the nearest existing state/store file in the detected list.",
                        "Trace how routes and components consume that state before changing it.",
                        "Update route or component tests when state behavior changes user-visible flows.",
                    ],
                    references=["../SKILL.md", "../routes/SKILL.md", "../components/SKILL.md", "../../requirements/SKILL.md"],
                )
            )
        if signals.design_system_files:
            specs.append(
                SkillSpec(
                    path="frontend/design-system/SKILL.md",
                    name="frontend-design-system",
                    domain="frontend",
                    sub_domain="design-system",
                    overview="Guidance for themes, tokens, UI kit modules, and design-system conventions already present in the repo.",
                    checks=["{{project_root}}/src/theme/", "{{project_root}}/src/tokens/", "{{project_root}}/src/ui/"],
                    patterns=[("Detected design system files", _signal_bullets(signals.design_system_files, "No design-system files were detected."))],
                    how_to=[
                        "Start from the nearest theme, token, or UI system file in the detected list.",
                        "Trace which components and routes depend on those primitives.",
                        "Update components and tests together when shared design primitives change.",
                    ],
                    references=["../SKILL.md", "../components/SKILL.md", "../../requirements/SKILL.md"],
                )
            )

    plan = build_roadmap_plan(load_config(project_root), parse_project_intent(project_root, context.requirements_path if context.requirements_path.exists() else None))
    if "roadmap" in references:
        phase_paths: list[str] = []
        seen_phases: set[str] = set()
        for step in plan.steps:
            if step.phase in seen_phases:
                continue
            seen_phases.add(step.phase)
            phase_paths.append(f"./{step.phase}/SKILL.md")
            specs.append(
                SkillSpec(
                    path=f"roadmap/{step.phase}/SKILL.md",
                    name=f"roadmap-{step.phase}",
                    domain="roadmap",
                    sub_domain=step.phase,
                    overview=f"Roadmap guidance for {step.title}.",
                    checks=["{{project_root}}/README.md", "{{project_root}}/FEATURES.md", "{{project_root}}/skills/roadmap/"],
                    patterns=[("Roadmap step", [step.description]), ("Status tracking", [f"Current status: {step.status}."])],
                    how_to=[
                        "Read the current step description.",
                        "Use the phase status to decide whether the work is in progress or pending.",
                        "Reflect completed work back into the roadmap tree.",
                    ],
                    references=["../SKILL.md", "../../requirements/SKILL.md"],
                )
            )
    return specs


def build_skill_specs(context: RequirementsContext, output_dir: Path) -> list[SkillSpec]:
    project_root = output_dir.parent
    specs = _dynamic_parent_specs(context, project_root)
    specs.extend(_legacy_child_specs(context, project_root))
    seen: set[str] = set()
    unique: list[SkillSpec] = []
    for spec in specs:
        if spec.path in seen:
            continue
        seen.add(spec.path)
        unique.append(spec)
    return unique


def _render_skill_native(spec: SkillSpec, source_hash: str) -> str:
    depth = len(Path(spec.path).parts)
    traceability_ref = "/".join([".."] * depth + ["TRACEABILITY.md"])
    pattern_sections = []
    for title, bullets in spec.patterns:
        block = [f"### {title}"]
        block.extend(f"- {item}" for item in bullets)
        pattern_sections.append("\n".join(block))

    sections = [
        "---",
        f"name: {spec.name}",
        "version: 0.3.0",
        f"domain: {spec.domain}",
        f"sub_domain: {spec.sub_domain}",
        f"last_updated: {TODAY}",
        "triggered_by: requirements_pipeline",
        f"source_hash: {source_hash}",
        "references:",
        *[f"  - {item}" for item in spec.references],
        "status: active",
        "---",
        "",
        f"# {spec.name.replace('-', ' ').title()} Skill",
        "",
        "## Overview",
        spec.overview,
        "",
        "## Check These Paths First",
        *[f"- {item}" for item in spec.checks],
        "",
        "## Patterns",
        "\n".join(pattern_sections),
        "",
        "## How-To",
        *[f"{index}. {step}" for index, step in enumerate(spec.how_to, start=1)],
        "",
        "## Traceability",
        f"- Generated from requirements source hash: `{source_hash}`",
        f"- Domain path: `{spec.domain}/{spec.sub_domain}`",
        f"- Read `{traceability_ref}` for full requirement-to-output mapping.",
        "- Use the detected file patterns in this skill before creating new structure.",
        "",
        "## References",
        *[f"- {item}" for item in spec.references],
        "",
    ]
    return "\n".join(sections)


def render_skill(spec: SkillSpec, source_hash: str, project_root: Path | str = ".") -> str:
    if spec.path.count("/") >= 2:
        return _render_skill_native(spec, source_hash)
    return run_deep_text(
        "skill guidance synthesis",
        (
            "Write a markdown SKILL.md file with YAML frontmatter for Skilgen. "
            "Use the provided skill spec to generate higher-level reusable guidance while preserving references and "
            "traceability. Optimize for coding agents that need actionable, reusable execution guidance rather than "
            "generic prose. Preserve the intent of the domain, keep the path references stable, and make the How-To "
            "section operational enough that an agent can decide what to inspect, change, and validate next.\n\n"
            f"Skill spec JSON:\n{spec}\nSource hash: {source_hash}"
        ),
        lambda: _render_skill_native(spec, source_hash),
        project_root=project_root,
    )


def render_manifest(specs: list[SkillSpec], source_hash: str) -> str:
    lines = [
        "# Skill Manifest",
        "",
        "This manifest is the entry point for agents discovering the skill tree.",
        "",
        "| Skill Path | Version | Domain | Last Updated | Triggered By | Source Hash |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for spec in specs:
        lines.append(f"| `{spec.path}` | `0.3.0` | `{spec.domain}` | `{TODAY}` | `requirements_pipeline` | `{source_hash}` |")
    lines.append("")
    return "\n".join(lines)


def render_graph(specs: list[SkillSpec]) -> str:
    lines = [
        "# Skill Graph",
        "",
        "This file summarizes the generated skill tree and cross references.",
        "",
    ]
    for spec in specs:
        lines.append(f"## {spec.path}")
        lines.append(f"- domain: `{spec.domain}`")
        lines.append(f"- sub_domain: `{spec.sub_domain}`")
        if spec.references:
            lines.append("- references:")
            lines.extend(f"  - `{reference}`" for reference in spec.references)
        else:
            lines.append("- references: none")
        lines.append("")
    return "\n".join(lines)


def render_summary(context: RequirementsContext) -> str:
    lines = ["# Requirements Summary", ""]
    if context.summary:
        lines.extend(f"- {line}" for line in context.summary)
    else:
        lines.append("- No major summary lines were extracted.")
    lines.append("")
    return "\n".join(lines)


def render_domain_summary(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]
    for heading, items in sections:
        lines.append(f"## {heading}")
        if items:
            lines.extend(f"- {item}" for item in items)
        else:
            lines.append("- No matching files detected.")
        lines.append("")
    return "\n".join(lines)


def _select_specs(specs: list[SkillSpec], selected_domains: set[str]) -> list[SkillSpec]:
    if not selected_domains:
        return specs
    return [spec for spec in specs if spec.domain in selected_domains]


def _dynamic_summary_paths(context: RequirementsContext, output_dir: Path, selected: set[str]) -> list[Path]:
    codebase_context = build_codebase_context(output_dir.parent, context)
    paths: list[Path] = []
    for node in codebase_context.domain_graph.nodes:
        if node.parent_domain is not None or not node.skill_path:
            continue
        if selected and node.name not in selected:
            continue
        skill_rel = Path(node.skill_path.removeprefix("skills/"))
        paths.append(output_dir / skill_rel.parent / "SUMMARY.md")
    return paths


def planned_skill_paths(context: RequirementsContext, output_dir: Path, selected_domains: set[str] | None = None) -> list[Path]:
    selected = selected_domains or set()
    specs = _select_specs(build_skill_specs(context, output_dir), selected)
    planned = [output_dir / spec.path for spec in specs]
    planned.append(output_dir / "MANIFEST.md")
    planned.append(output_dir / "GRAPH.md")
    planned.extend(_dynamic_summary_paths(context, output_dir, selected))
    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for path in planned:
        if path in seen:
            continue
        seen.add(path)
        unique_paths.append(path)
    return unique_paths


def write_skills(context: RequirementsContext, output_dir: Path, selected_domains: set[str] | None = None) -> list[Path]:
    selected = selected_domains or set()
    specs = _select_specs(build_skill_specs(context, output_dir), selected)
    signals = analyze_codebase(output_dir.parent)
    written: list[Path] = []
    for spec in specs:
        target = output_dir / spec.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_skill(spec, context.source_hash, output_dir.parent), encoding="utf-8")
        written.append(target)

    manifest = output_dir / "MANIFEST.md"
    manifest.write_text(render_manifest(specs, context.source_hash), encoding="utf-8")
    written.append(manifest)

    graph = output_dir / "GRAPH.md"
    graph.write_text(render_graph(specs), encoding="utf-8")
    written.append(graph)

    summary_map: dict[str, list[tuple[str, list[str]]]] = {
        "requirements": [("Planning Inputs", context.summary)],
        "backend": [("Detected Route Files", signals.backend_routes), ("Detected Service Files", signals.services), ("Detected Test Files", signals.tests)],
        "frontend": [("Detected Route Files", signals.frontend_routes), ("Detected Component Files", signals.components), ("Detected Test Files", signals.tests)],
        "design-system": [("Detected Design System Files", signals.design_system_files)],
        "security": [("Detected Auth Files", signals.auth_files)],
        "operations": [("Detected Background Job Files", signals.background_jobs)],
        "data-platform": [("Detected Data Model Files", signals.data_models), ("Detected Persistence Files", signals.persistence_layers)],
        "roadmap": [("Roadmap Context", context.summary)],
    }
    codebase_context = build_codebase_context(output_dir.parent, context)
    for node in codebase_context.domain_graph.nodes:
        if node.parent_domain is not None or not node.skill_path:
            continue
        if selected and node.name not in selected:
            continue
        summary_path = output_dir / Path(node.skill_path.removeprefix("skills/")).parent / "SUMMARY.md"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            render_domain_summary(f"{node.name.replace('-', ' ').title()} Summary", summary_map.get(node.name, [("Key Files", node.key_files)])),
            encoding="utf-8",
        )
        written.append(summary_path)

    if "frontend" in {node.name for node in codebase_context.domain_graph.nodes if node.parent_domain is None} and (
        not selected or "frontend" in selected
    ):
        component_summary = output_dir / "frontend" / "components" / "SUMMARY.md"
        component_summary.parent.mkdir(parents=True, exist_ok=True)
        component_summary.write_text(
            render_domain_summary("Frontend Components Summary", [("Detected Component Files", signals.components)]),
            encoding="utf-8",
        )
        written.append(component_summary)

    if "backend" in {node.name for node in codebase_context.domain_graph.nodes if node.parent_domain is None} and signals.services and (
        not selected or "backend" in selected
    ):
        service_summary = output_dir / "backend" / "services" / "SUMMARY.md"
        service_summary.parent.mkdir(parents=True, exist_ok=True)
        service_summary.write_text(
            render_domain_summary("Backend Services Summary", [("Detected Service Files", signals.services)]),
            encoding="utf-8",
        )
        written.append(service_summary)

    return written
