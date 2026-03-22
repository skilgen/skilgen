from __future__ import annotations

import json
from pathlib import Path

from skilgen.agents import analyze_codebase, build_agent_decision, build_import_graph, fingerprint_project
from skilgen.agents.feature_extractor import extract_features
from skilgen.agents.requirements_parser import parse_project_intent
from skilgen.deep_agents_core import run_deep_text
from skilgen.core.config import render_default_config
from skilgen.core.context import build_codebase_context
from skilgen.external_skills import active_external_skills, detect_external_skill_sources, installed_external_skills
from skilgen.core.models import RequirementsContext


def ensure_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def project_doc_paths(project_root: Path) -> list[Path]:
    return [
        project_root / "AGENTS.md",
        project_root / "ANALYSIS.md",
        project_root / "FEATURES.md",
        project_root / "REPORT.md",
        project_root / "TRACEABILITY.md",
        project_root / "skilgen.yml",
    ]


def _render_feature_inventory_native(context: RequirementsContext) -> str:
    project_root = context.requirements_path.parent.parent if context.requirements_path.exists() and context.requirements_path.parent.name == "docs" else context.requirements_path.parent
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    features = extract_features(requirements_path, project_root)
    lines = [
        "# Features",
        "",
        "Search this file before implementing any feature to avoid duplicating work.",
        "",
        "| Feature Name | Domain | Location | Description | Status | Last Modified |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for feature in features:
        lines.append(
            f"| {feature.name} | {feature.domain} | `{feature.location}` | {feature.description} | {feature.status} | {feature.last_modified} |"
        )
    lines.append("| HTTP API surface | api | `skilgen/api/server.py` | Exposes health, fingerprint, map, intent, features, plan, deliver, status, report, and validate endpoints. | active | current |")
    lines.append("")
    return "\n".join(lines)


def render_feature_inventory(context: RequirementsContext) -> str:
    project_root = context.requirements_path.parent.parent if context.requirements_path.exists() and context.requirements_path.parent.name == "docs" else context.requirements_path.parent
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    features = extract_features(requirements_path, project_root)
    return run_deep_text(
        "feature inventory markdown",
        (
            "Write a markdown feature inventory document for Skilgen. Keep the existing table format with columns "
            "Feature Name, Domain, Location, Description, Status, Last Modified. Preserve grounded engineering detail, "
            "favor concise but specific descriptions, and make the document useful to coding agents that need to decide "
            "what already exists before implementing more changes.\n\n"
            f"Features JSON:\n{json.dumps([feature.__dict__ for feature in features], indent=2)}"
        ),
        lambda: _render_feature_inventory_native(context),
        project_root=project_root,
    )


def render_analysis_report(context: RequirementsContext, project_root: Path) -> str:
    fingerprint = fingerprint_project(project_root)
    signals = analyze_codebase(project_root)
    import_graph = build_import_graph(project_root)
    codebase_context = build_codebase_context(project_root, context)
    payload = {
        "framework_fingerprint": {
            "frontend": fingerprint.frontend.__dict__ if fingerprint.frontend else None,
            "backend": fingerprint.backend.__dict__ if fingerprint.backend else None,
            "test_framework": fingerprint.test_framework.__dict__ if fingerprint.test_framework else None,
            "build_tool": fingerprint.build_tool.__dict__ if fingerprint.build_tool else None,
        },
        "signals": signals.__dict__,
        "domain_graph": {
            "nodes": [node.__dict__ for node in codebase_context.domain_graph.nodes],
            "recommendations": codebase_context.domain_graph.recommendations,
        },
        "detected_domains": [record.__dict__ for record in codebase_context.detected_domains],
        "skill_tree": [node.__dict__ for node in codebase_context.skill_tree],
        "import_graph": import_graph,
    }
    return "\n".join(["# Analysis", "", "```json", json.dumps(payload, indent=2), "```", ""])


def _render_traceability_report_native(context: RequirementsContext, project_root: Path) -> str:
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    intent = parse_project_intent(project_root, requirements_path)
    signals = analyze_codebase(project_root)
    codebase_context = build_codebase_context(project_root, context)
    evidence_map = {
        "backend": [*signals.backend_routes[:3], *signals.services[:2], *signals.data_models[:2], *signals.auth_files[:1]],
        "frontend": [*signals.frontend_routes[:3], *signals.components[:2], *signals.state_files[:2], *signals.design_system_files[:1]],
        "data": [*signals.data_models[:3], *signals.persistence_layers[:3]],
        "operations": [*signals.background_jobs[:3], *signals.tests[:2]],
    }

    lines = [
        "# Traceability",
        "",
        "This file maps requirements and detected code evidence to the generated Skilgen outputs.",
        "",
        "## Requirements Source",
        f"- Source file: `{context.requirements_path.name if requirements_path is not None else 'codebase-only input'}`",
        f"- Source hash: `{context.source_hash[:12]}`",
        "",
        "## Intent To Output Mapping",
    ]

    def append_mapping(title: str, items: list[str], domain: str, outputs: list[str]) -> None:
        lines.append(f"### {title}")
        if not items:
            lines.append("- No items extracted for this category.")
            lines.append("")
            return
        evidence = evidence_map.get(domain, [])
        for item in items[:6]:
            lines.append(f"- Intent: {item}")
            lines.append(f"  Domain: `{domain}`")
            lines.append(f"  Evidence: {', '.join(f'`{entry}`' for entry in evidence) if evidence else 'requirements-driven only'}")
            lines.append(f"  Generated output: {', '.join(f'`{entry}`' for entry in outputs)}")
        lines.append("")

    append_mapping("Endpoints", intent.endpoints, "backend", ["skills/backend/SKILL.md", "skills/backend/api/SKILL.md", "FEATURES.md"])
    append_mapping("UI Flows", intent.ui_flows, "frontend", ["skills/frontend/SKILL.md", "skills/frontend/components/SKILL.md", "FEATURES.md"])
    append_mapping(
        "Feature Planning",
        intent.features,
        "operations",
        ["skills/roadmap/SKILL.md", "skills/GRAPH.md", "REPORT.md"],
    )

    lines.extend(
        [
            "## Domain Evidence",
            "",
        ]
    )
    for record in codebase_context.detected_domains:
        lines.append(f"### {record.name}")
        lines.append(f"- Key files: {', '.join(f'`{item}`' for item in record.key_files) if record.key_files else 'none'}")
        lines.append(f"- Key patterns: {', '.join(record.key_patterns) if record.key_patterns else 'none'}")
        lines.append(f"- Sub-domains: {', '.join(record.sub_domains) if record.sub_domains else 'none'}")
        lines.append("")

    lines.extend(
        [
            "## Generated Outputs",
            "- `ANALYSIS.md` for full machine-readable project analysis",
            "- `FEATURES.md` for detected and planned feature inventory",
            "- `REPORT.md` for human-readable summary",
            "- `skills/MANIFEST.md` and `skills/GRAPH.md` for skill discovery",
            "- `skills/<domain>/SKILL.md` for domain-specific execution guidance",
            "",
        ]
    )
    gaps: list[str] = []
    if signals.backend_routes and not signals.tests:
        gaps.append("Backend routes exist but no tests were detected for endpoint validation.")
    if signals.frontend_routes and not signals.components:
        gaps.append("Frontend routes exist but reusable components were not strongly detected yet.")
    if not context.requirements_path.exists():
        gaps.append("This run was codebase-only, so roadmap and intent guidance came from implementation signals rather than a product spec.")
    lines.extend(["## Gaps And Next Actions"])
    if gaps:
        lines.extend(f"- {gap}" for gap in gaps)
    else:
        lines.append("- No major delivery gaps were inferred from the current codebase and requirement inputs.")
    lines.append("")
    return "\n".join(lines)


def render_traceability_report(context: RequirementsContext, project_root: Path) -> str:
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    intent = parse_project_intent(project_root, requirements_path)
    signals = analyze_codebase(project_root)
    codebase_context = build_codebase_context(project_root, context)
    return run_deep_text(
        "traceability explanation",
        (
            "Write a markdown traceability report for Skilgen that explains how requirements and code evidence map to generated outputs. "
            "Include sections for requirements source, intent to output mapping, domain evidence, generated outputs, and "
            "clear next actions or gaps. Keep the output grounded in the provided intent, signals, and detected domains. "
            "Optimize for a coding agent or maintainer who needs to understand why a skill exists and what evidence justifies it.\n\n"
            f"Intent JSON:\n{json.dumps(intent.__dict__, indent=2)}\n\n"
            f"Signals JSON:\n{json.dumps(signals.__dict__, indent=2)}\n\n"
            f"Detected domains JSON:\n{json.dumps([record.__dict__ for record in codebase_context.detected_domains], indent=2)}\n"
        ),
        lambda: _render_traceability_report_native(context, project_root),
        project_root=project_root,
    )


def _render_project_report_native(context: RequirementsContext, project_root: Path) -> str:
    signals = analyze_codebase(project_root)
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    features = extract_features(requirements_path, project_root)
    codebase_context = build_codebase_context(project_root, context)
    domain_names = ", ".join(record.name for record in codebase_context.detected_domains)
    lines = [
        "# Report",
        "",
        "## Summary",
        f"- Detected domains: {domain_names or 'none'}",
        f"- Feature inventory entries: {len(features)}",
        f"- Backend route files: {len(signals.backend_routes)}",
        f"- Frontend route files: {len(signals.frontend_routes)}",
        f"- Component files: {len(signals.components)}",
        f"- Service files: {len(signals.services)}",
        f"- Test files: {len(signals.tests)}",
        f"- Data model files: {len(signals.data_models)}",
        f"- Persistence files: {len(signals.persistence_layers)}",
        f"- Background job files: {len(signals.background_jobs)}",
        f"- Auth files: {len(signals.auth_files)}",
        f"- State files: {len(signals.state_files)}",
        f"- Design system files: {len(signals.design_system_files)}",
        "",
        "## Generated Outputs",
        "- ANALYSIS.md",
        "- FEATURES.md",
        "- REPORT.md",
        "- TRACEABILITY.md",
        "- skills/MANIFEST.md",
        "- skills/GRAPH.md",
        "- skills/<domain>/SKILL.md",
        "- skills/<domain>/SUMMARY.md",
        "",
        "## Recommended Starting Points",
    ]
    if signals.backend_routes:
        lines.append(f"- Backend: start from `{signals.backend_routes[0]}`")
    if signals.services:
        lines.append(f"- Services: start from `{signals.services[0]}`")
    if signals.frontend_routes:
        lines.append(f"- Frontend routes: start from `{signals.frontend_routes[0]}`")
    if signals.components:
        lines.append(f"- Components: start from `{signals.components[0]}`")
    if not any([signals.backend_routes, signals.services, signals.frontend_routes, signals.components]):
        lines.append("- No concrete route/service/component files were detected yet; start from the requirements and roadmap skills.")
    lines.append("")
    return "\n".join(lines)


def render_project_report(context: RequirementsContext, project_root: Path) -> str:
    signals = analyze_codebase(project_root)
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    features = extract_features(requirements_path, project_root)
    codebase_context = build_codebase_context(project_root, context)
    return run_deep_text(
        "project report synthesis",
        (
            "Write a concise markdown project report for Skilgen with sections Summary, Generated Outputs, and Recommended Starting Points.\n\n"
            f"Signals JSON:\n{json.dumps(signals.__dict__, indent=2)}\n\n"
            f"Features count: {len(features)}\n"
            f"Detected domains JSON:\n{json.dumps([record.__dict__ for record in codebase_context.detected_domains], indent=2)}"
        ),
        lambda: _render_project_report_native(context, project_root),
        project_root=project_root,
    )


def render_delivery_module() -> str:
    return """from __future__ import annotations

import time
from pathlib import Path

from skilgen.agents import fingerprint_project
from skilgen.core.config import load_config
from skilgen.core.context import build_codebase_context
from skilgen.core.requirements import load_requirements
from skilgen.generators.package import project_doc_paths, write_project_docs
from skilgen.generators.skills import planned_skill_paths, write_skills


def run_delivery(
    requirements_path: str | Path,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    dry_run: bool = False,
) -> list[Path]:
    root = Path(project_root).resolve()
    load_config(root)
    context = load_requirements(Path(requirements_path).resolve())
    fingerprint_project(root)
    build_codebase_context(root, context)
    generated = []
    if "docs" in targets:
        if dry_run:
            generated.extend(project_doc_paths(root))
        else:
            generated.extend(write_project_docs(context, root))
    if "skills" in targets:
        if dry_run:
            generated.extend(planned_skill_paths(context, root / "skills", set(domains)))
        else:
            generated.extend(write_skills(context, root / "skills", set(domains)))
    return generated


def watch_delivery(
    requirements_path: str | Path,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    interval_seconds: float = 2.0,
    cycles: int = 0,
    once: bool = False,
) -> list[list[Path]]:
    root = Path(project_root).resolve()

    def snapshot() -> dict[str, int]:
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
        return tracked

    results = [
        run_delivery(requirements_path, root, targets=targets, domains=domains),
    ]
    if once:
        return results

    previous = snapshot()
    completed_cycles = 0
    while cycles == 0 or completed_cycles < cycles:
        time.sleep(interval_seconds)
        current = snapshot()
        if current != previous:
            results.append(run_delivery(requirements_path, root, targets=targets, domains=domains))
            previous = current
        completed_cycles += 1
    return results
"""


def render_cli_main() -> str:
    return """from __future__ import annotations

import argparse
import json
from pathlib import Path

from skilgen.api.server import run_server
from skilgen.api.service import analyze_payload, preview_payload, report_payload, status_payload, validate_payload
from skilgen import __version__
from skilgen.agents import build_import_graph, build_roadmap_plan, extract_features, fingerprint_project
from skilgen.agents.requirements_parser import parse_requirements_file
from skilgen.delivery import run_delivery, watch_delivery
from skilgen.core.config import load_config, render_default_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skilgen", description="Requirements-driven skill and scaffold generator.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Write a default skilgen.yml to the project root.")
    init.add_argument("--project-root", default=".")

    scan = subparsers.add_parser("scan", help="Generate docs and skills from a requirements file.")
    scan.add_argument("--requirements", required=True)
    scan.add_argument("--project-root", default=".")
    scan.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    scan.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    scan.add_argument("--dry-run", action="store_true")

    deliver = subparsers.add_parser("deliver", help="Alias for scan for now; intended to grow into full delivery automation.")
    deliver.add_argument("--requirements", required=True)
    deliver.add_argument("--project-root", default=".")
    deliver.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    deliver.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    deliver.add_argument("--dry-run", action="store_true")

    update = subparsers.add_parser("update", help="Refresh generated outputs for all or selected domains.")
    update.add_argument("--requirements", required=True)
    update.add_argument("--project-root", default=".")
    update.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    update.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    update.add_argument("--dry-run", action="store_true")

    watch = subparsers.add_parser("watch", help="Watch the project and rerun generation when files change.")
    watch.add_argument("--requirements", required=True)
    watch.add_argument("--project-root", default=".")
    watch.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    watch.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    watch.add_argument("--interval", type=float, default=2.0)
    watch.add_argument("--cycles", type=int, default=0)
    watch.add_argument("--once", action="store_true")

    preview = subparsers.add_parser("preview", help="Preview which generated files would be written without changing the project.")
    preview.add_argument("--requirements", required=True)
    preview.add_argument("--project-root", default=".")
    preview.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    preview.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])

    fingerprint = subparsers.add_parser("fingerprint", help="Detect the current project's likely frameworks.")
    fingerprint.add_argument("--project-root", default=".")

    mapping = subparsers.add_parser("map", help="Build a simple import relationship map for the project.")
    mapping.add_argument("--project-root", default=".")

    analyze = subparsers.add_parser("analyze", help="Assemble framework, signal, and relationship analysis for the project.")
    analyze.add_argument("--project-root", default=".")
    analyze.add_argument("--requirements")

    intent = subparsers.add_parser("intent", help="Parse a requirements file into a structured project intent.")
    intent.add_argument("--requirements", required=True)
    features = subparsers.add_parser("features", help="Extract a feature inventory from requirements and project context.")
    features.add_argument("--requirements", required=True)
    features.add_argument("--project-root", default=".")
    plan = subparsers.add_parser("plan", help="Build a roadmap plan from requirements and model config.")
    plan.add_argument("--requirements", required=True)
    plan.add_argument("--project-root", default=".")

    status = subparsers.add_parser("status", help="Show the current generated output status for a project root.")
    status.add_argument("--project-root", default=".")

    report = subparsers.add_parser("report", help="Show a summary report for a project root.")
    report.add_argument("--project-root", default=".")

    validate = subparsers.add_parser("validate", help="Validate generated outputs and skill references.")
    validate.add_argument("--project-root", default=".")

    serve = subparsers.add_parser("serve", help="Run the HTTP API server.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        project_root = Path(args.project_root).resolve()
        project_root.mkdir(parents=True, exist_ok=True)
        config_path = project_root / "skilgen.yml"
        if not config_path.exists():
            config_path.write_text(render_default_config(), encoding="utf-8")
        print(json.dumps({"config_path": str(config_path)}, indent=2))
        return
    if args.command == "fingerprint":
        result = fingerprint_project(Path(args.project_root).resolve())
        print(
            json.dumps(
                {
                    "frontend": result.frontend.__dict__ if result.frontend else None,
                    "backend": result.backend.__dict__ if result.backend else None,
                    "test_framework": result.test_framework.__dict__ if result.test_framework else None,
                    "build_tool": result.build_tool.__dict__ if result.build_tool else None,
                },
                indent=2,
            )
        )
        return
    if args.command == "map":
        print(json.dumps({"import_graph": build_import_graph(Path(args.project_root).resolve())}, indent=2))
        return
    if args.command == "analyze":
        print(json.dumps(analyze_payload(Path(args.project_root).resolve(), Path(args.requirements).resolve() if args.requirements else None), indent=2))
        return
    if args.command == "intent":
        result = parse_requirements_file(Path(args.requirements).resolve())
        print(
            json.dumps(
                {
                    "features": result.features,
                    "domain_concepts": result.domain_concepts,
                    "entities": result.entities,
                    "endpoints": result.endpoints,
                    "ui_flows": result.ui_flows,
                },
                indent=2,
            )
        )
        return
    if args.command == "features":
        features = extract_features(Path(args.requirements).resolve(), Path(args.project_root).resolve())
        print(json.dumps({"features": [feature.__dict__ for feature in features]}, indent=2))
        return
    if args.command == "plan":
        config = load_config(Path(args.project_root).resolve())
        plan = build_roadmap_plan(config, parse_requirements_file(Path(args.requirements).resolve()))
        print(
            json.dumps(
                {
                    "model": plan.model.__dict__,
                    "steps": [step.__dict__ for step in plan.steps],
                },
                indent=2,
            )
        )
        return
    if args.command == "status":
        print(json.dumps(status_payload(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "report":
        print(json.dumps(report_payload(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "validate":
        print(json.dumps(validate_payload(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "serve":
        run_server(args.host, args.port)
        return

    targets = ("docs", "skills") if getattr(args, "target", "all") == "all" else (args.target,)
    domains = tuple(getattr(args, "domain", None) or [])

    if args.command == "preview":
        print(
            json.dumps(
                preview_payload(
                    args.requirements,
                    Path(args.project_root),
                    targets=targets,
                    domains=domains,
                ),
                indent=2,
            )
        )
        return

    if args.command == "watch":
        runs = watch_delivery(
            args.requirements,
            Path(args.project_root),
            targets=targets,
            domains=domains,
            interval_seconds=args.interval,
            cycles=args.cycles,
            once=args.once,
        )
        print(json.dumps({"runs": [[str(path) for path in generated] for generated in runs]}, indent=2))
        return

    generated = run_delivery(
        args.requirements,
        Path(args.project_root),
        targets=targets,
        domains=domains,
        dry_run=args.dry_run,
    )
    print(json.dumps({"generated_files": [str(path) for path in generated]}, indent=2))


if __name__ == "__main__":
    main()
"""


def render_init_files() -> dict[str, str]:
    return {
        "skilgen/core/__init__.py": "",
        "skilgen/generators/__init__.py": "",
        "skilgen/cli/__init__.py": "",
        "skilgen/api/__init__.py": "from skilgen.api.server import create_server, run_server\n\n__all__ = [\"create_server\", \"run_server\"]\n",
        "skilgen/agents/__init__.py": "from skilgen.agents.codebase_signals import analyze_codebase\nfrom skilgen.agents.feature_extractor import extract_features\nfrom skilgen.agents.framework_fingerprint import fingerprint_project\nfrom skilgen.agents.model_registry import resolve_model_settings\nfrom skilgen.agents.relationship_mapper import build_import_graph\nfrom skilgen.agents.requirements_parser import parse_requirements_file\nfrom skilgen.agents.roadmap_planner import build_roadmap_plan\n\n__all__ = [\"analyze_codebase\", \"build_import_graph\", \"extract_features\", \"fingerprint_project\", \"parse_requirements_file\", \"resolve_model_settings\", \"build_roadmap_plan\"]\n",
    }


def render_agents_contract(context: RequirementsContext, project_root: Path) -> str:
    input_mode = "requirements + codebase" if context.requirements_path.exists() else "codebase only"
    codebase_context = build_codebase_context(project_root, context)
    decision = build_agent_decision(project_root, context, codebase_context.domain_graph, codebase_context.skill_tree)
    parent_skills = [node for node in codebase_context.skill_tree if node.parent_skill is None]
    skill_refs = ["- `skills/MANIFEST.md`: Start here to discover the generated skill tree."]
    skill_refs.extend(
        f"- `{node.path}`: Parent skill for the inferred `{node.domain}` domain."
        for node in parent_skills
    )
    inferred_domains = [node for node in codebase_context.domain_graph.nodes if node.parent_domain is None]
    installed_skill_packs = installed_external_skills(project_root)
    active_skill_packs = active_external_skills(project_root)
    external_skill_lines = [
        f"- `{entry['slug']}` ({entry.get('ecosystem', 'unknown')}): installed at `{entry.get('install_path', '')}`"
        for entry in installed_skill_packs
    ] or ["- No external skill packs have been installed yet."]
    active_external_lines = [
        f"- `{entry['slug']}` ({entry.get('lock_metadata', {}).get('normalized', {}).get('adapter', 'raw')}): load from `{entry.get('install_path', '')}`"
        for entry in active_skill_packs
    ] or ["- No external skill packs are currently active."]
    recommended_external_lines = [
        f"- `{entry['slug']}`: {'; '.join(entry.get('reasons', []))}"
        for entry in detect_external_skill_sources(project_root).get("manual_recommendations", [])
    ] or ["- No additional external skill recommendations were inferred."]
    priority_lines = [
        f"- `{path}`"
        for path in decision.prioritized_skill_paths
    ] or ["- No prioritized skills were suggested for this run."]
    dynamic_domain_lines = [
        f"- `{node.name}` ({node.confidence:.2f}): {node.summary}"
        for node in inferred_domains
    ] or ["- No inferred domains were available."]

    return "\n".join(
        [
            "# Skilgen Agent Contract",
            "",
            "## Project Overview",
            "This repository was generated or refreshed by Skilgen to help coding agents work from project-specific context instead of generic prompts.",
            f"The current input mode was: `{input_mode}`.",
            "",
            "## How To Work In This Repo",
            "1. Open `skills/MANIFEST.md` first.",
            "2. Open the most specific inferred child skill before changing code.",
            "3. Use `FEATURES.md`, `REPORT.md`, and `TRACEABILITY.md` to understand intent, current shape, and evidence.",
            "4. Keep generated references relative so the skill tree stays portable across repos.",
            "5. When backend behavior changes, test every touched endpoint before closing the task.",
            "",
            "## Inferred Domains",
            *dynamic_domain_lines,
            "",
            "## Skill Entry Points",
            *skill_refs,
            "",
            "## External Skill Packs",
            *external_skill_lines,
            "",
            "## Active External Skill Packs",
            *active_external_lines,
            "",
            "## Suggested External Skill Packs",
            *recommended_external_lines,
            "",
            "## Recommended Start Order",
            f"- Input mode: `{input_mode}`",
            f"- Detected domains: {', '.join(record.name for record in codebase_context.detected_domains) or 'none'}",
            f"- Decision planner refresh recommendation: `{decision.should_refresh}`",
            f"- Decision planner reason: {decision.reason}",
            "- Load these prioritized skills first:",
            *priority_lines,
            "- Load decision memory in this order:",
            *[f"  - `{path}`" for path in decision.memory_to_load],
            "",
            "## Generated Docs",
            "- `ANALYSIS.md`: Machine-readable project analysis.",
            "- `FEATURES.md`: Feature inventory from codebase and optional requirements.",
            "- `REPORT.md`: Human-readable summary and suggested starting points.",
            "- `TRACEABILITY.md`: Why outputs were generated and what evidence they came from.",
            "",
            "## Execution Rules",
            "- Prefer the generated skill guidance over ad-hoc prompting.",
            "- If backend behavior changes, test all affected endpoints before closing the task.",
            "- When adding new reusable patterns, update the relevant skill file and manifest references.",
            "- Treat `AGENTS.md` as the top-level contract and the `skills/` tree as the operating system for coding agents.",
            "- Use `TRACEABILITY.md` whenever you need to explain why a generated skill or document exists.",
            "",
            "## Project Root",
            f"- `{project_root}`",
            "",
        ]
    )


def write_project_docs(context: RequirementsContext, project_root: Path) -> list[Path]:
    written = []
    agents = render_agents_contract(context, project_root)
    analysis = render_analysis_report(context, project_root)
    features = render_feature_inventory(context)
    report = render_project_report(context, project_root)
    traceability = render_traceability_report(context, project_root)
    written.append(ensure_file(project_root / "AGENTS.md", agents))
    written.append(ensure_file(project_root / "ANALYSIS.md", analysis))
    written.append(ensure_file(project_root / "FEATURES.md", features))
    written.append(ensure_file(project_root / "REPORT.md", report))
    written.append(ensure_file(project_root / "TRACEABILITY.md", traceability))
    written.append(ensure_file(project_root / "skilgen.yml", render_default_config()))
    return written
