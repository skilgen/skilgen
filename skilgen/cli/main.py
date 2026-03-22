from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skilgen.api.server import run_server
from skilgen.api.service import analyze_payload, decision_payload, doctor_payload, preview_payload, report_payload, status_payload, validate_payload
from skilgen import __version__
from skilgen.agents import build_import_graph, build_roadmap_plan, extract_features, fingerprint_project
from skilgen.agents.requirements_parser import parse_project_intent, parse_requirements_file
from skilgen.deep_agents_core import current_runtime_mode, runtime_diagnostics
from skilgen.delivery import run_delivery, watch_delivery
from skilgen.core.config import load_config, render_default_config
from skilgen.external_skills import (
    activate_external_skill,
    active_external_skills,
    detect_external_skill_sources,
    external_skill_lock,
    deactivate_external_skill,
    get_external_skill,
    install_external_skill,
    list_external_skills,
    ranked_external_skills,
    remove_external_skill,
    sync_all_external_skills,
    sync_external_skill,
)


def emit_progress(message: str) -> None:
    print(f"[skilgen] {message}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skilgen", description="Requirements-driven skill and scaffold generator.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Write a default skilgen.yml to the project root.")
    init.add_argument("--project-root", default=".")
    init.add_argument(
        "--provider",
        choices=["openai", "anthropic", "gemini", "google", "google_genai", "huggingface", "hugging_face", "hf"],
        help="Optionally scaffold provider-specific model defaults instead of a neutral template.",
    )

    scan = subparsers.add_parser("scan", help="Generate docs and skills from a requirements file.")
    scan.add_argument("--requirements")
    scan.add_argument("--project-root", default=".")
    scan.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    scan.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    scan.add_argument("--dry-run", action="store_true")

    deliver = subparsers.add_parser("deliver", help="Alias for scan for now; intended to grow into full delivery automation.")
    deliver.add_argument("--requirements")
    deliver.add_argument("--project-root", default=".")
    deliver.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    deliver.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    deliver.add_argument("--dry-run", action="store_true")

    update = subparsers.add_parser("update", help="Refresh generated outputs for all or selected domains.")
    update.add_argument("--requirements")
    update.add_argument("--project-root", default=".")
    update.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    update.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    update.add_argument("--dry-run", action="store_true")

    watch = subparsers.add_parser("watch", help="Watch the project and rerun generation when files change.")
    watch.add_argument("--requirements")
    watch.add_argument("--project-root", default=".")
    watch.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    watch.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    watch.add_argument("--interval", type=float, default=2.0)
    watch.add_argument("--cycles", type=int, default=0)
    watch.add_argument("--once", action="store_true")

    preview = subparsers.add_parser("preview", help="Preview which generated files would be written without changing the project.")
    preview.add_argument("--requirements")
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

    decide = subparsers.add_parser("decide", help="Recommend whether to refresh skills, which skills to prioritize, and which run memory to load.")
    decide.add_argument("--project-root", default=".")
    decide.add_argument("--requirements")

    skills = subparsers.add_parser("skills", help="Discover and install external skill collections through Skilgen.")
    skills_subparsers = skills.add_subparsers(dest="skills_command", required=True)

    skills_list = skills_subparsers.add_parser("list", help="List curated external skill sources available through Skilgen.")
    skills_list.add_argument("--project-root", default=".")
    skills_list.add_argument("--ecosystem")
    skills_list.add_argument("--search")

    skills_show = skills_subparsers.add_parser("show", help="Show details for a curated external skill source.")
    skills_show.add_argument("slug")
    skills_show.add_argument("--project-root", default=".")

    skills_detect = skills_subparsers.add_parser("detect", help="Detect external skill ecosystems that match the current repository.")
    skills_detect.add_argument("--project-root", default=".")

    skills_active = skills_subparsers.add_parser("active", help="List the currently active external skill packs for this project.")
    skills_active.add_argument("--project-root", default=".")

    skills_lock = skills_subparsers.add_parser("lock", help="Show the resolved external-skills lockfile for this project.")
    skills_lock.add_argument("--project-root", default=".")

    skills_rank = skills_subparsers.add_parser("rank", help="Rank active external skill packs by trust and relevance for the current project.")
    skills_rank.add_argument("--project-root", default=".")

    skills_install = skills_subparsers.add_parser("install", help="Install a curated or custom external skill source into the local project.")
    skills_install.add_argument("slug", nargs="?")
    skills_install.add_argument("--git-url")
    skills_install.add_argument("--name")
    skills_install.add_argument("--project-root", default=".")
    skills_install.add_argument("--force", action="store_true")
    skills_install.add_argument("--ref")
    skills_install.add_argument("--activate", action=argparse.BooleanOptionalAction, default=None)

    skills_sync = skills_subparsers.add_parser("sync", help="Sync an installed external skill source with its upstream repository.")
    skills_sync.add_argument("slug", nargs="?")
    skills_sync.add_argument("--project-root", default=".")
    skills_sync.add_argument("--all", action="store_true")

    skills_remove = skills_subparsers.add_parser("remove", help="Remove an installed external skill source from the local project.")
    skills_remove.add_argument("slug")
    skills_remove.add_argument("--project-root", default=".")

    skills_activate = skills_subparsers.add_parser("activate", help="Mark an installed external skill source as active for agent loading.")
    skills_activate.add_argument("slug")
    skills_activate.add_argument("--project-root", default=".")

    skills_deactivate = skills_subparsers.add_parser("deactivate", help="Mark an installed external skill source as inactive for agent loading.")
    skills_deactivate.add_argument("slug")
    skills_deactivate.add_argument("--project-root", default=".")

    intent = subparsers.add_parser("intent", help="Parse a requirements file into a structured project intent.")
    intent.add_argument("--requirements", required=True)
    features = subparsers.add_parser("features", help="Extract a feature inventory from requirements and project context.")
    features.add_argument("--requirements")
    features.add_argument("--project-root", default=".")
    plan = subparsers.add_parser("plan", help="Build a roadmap plan from requirements and model config.")
    plan.add_argument("--requirements")
    plan.add_argument("--project-root", default=".")

    status = subparsers.add_parser("status", help="Show the current generated output status for a project root.")
    status.add_argument("--project-root", default=".")

    report = subparsers.add_parser("report", help="Show a summary report for a project root.")
    report.add_argument("--project-root", default=".")

    validate = subparsers.add_parser("validate", help="Validate generated outputs and skill references.")
    validate.add_argument("--project-root", default=".")

    doctor = subparsers.add_parser("doctor", help="Diagnose runtime readiness, model configuration, and API-key setup.")
    doctor.add_argument("--project-root", default=".")

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
            config_path.write_text(render_default_config(args.provider), encoding="utf-8")
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
    if args.command == "decide":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting agent decision planning with the {current_runtime_mode(root)} runtime. Skilgen is deciding whether the skill tree should refresh and what the agent should load first."
        )
        print(json.dumps(decision_payload(root, Path(args.requirements).resolve() if args.requirements else None), indent=2))
        return
    if args.command == "skills":
        root = Path(args.project_root).resolve()
        if args.skills_command == "list":
            emit_progress("Loading the curated Skilgen skills catalog across supported ecosystems.")
            print(json.dumps(list_external_skills(root, ecosystem=args.ecosystem, search=args.search), indent=2))
            return
        if args.skills_command == "show":
            emit_progress(f"Loading details for the external skill source '{args.slug}'.")
            print(json.dumps({"skill": get_external_skill(args.slug, root)}, indent=2))
            return
        if args.skills_command == "detect":
            emit_progress("Scanning the repository for supported external skill ecosystems.")
            print(json.dumps(detect_external_skill_sources(root), indent=2))
            return
        if args.skills_command == "active":
            emit_progress("Listing the currently active external skill packs for this project.")
            print(json.dumps({"skills": active_external_skills(root)}, indent=2))
            return
        if args.skills_command == "lock":
            emit_progress("Loading the resolved external-skills lockfile.")
            print(json.dumps(external_skill_lock(root), indent=2))
            return
        if args.skills_command == "rank":
            emit_progress("Ranking active external skill packs by trust, detection signals, and repo fit.")
            print(json.dumps(ranked_external_skills(root), indent=2))
            return
        if args.skills_command == "install":
            emit_progress("Installing the external skill source into .skilgen/external-skills so it can be managed through Skilgen.")
            print(
                json.dumps(
                    {
                        "installed_skill": install_external_skill(
                            project_root=root,
                            slug=args.slug,
                            git_url=args.git_url,
                            name=args.name,
                            force=args.force,
                            ref=args.ref,
                            active=args.activate,
                        )
                    },
                    indent=2,
                )
            )
            return
        if args.skills_command == "sync":
            if args.all:
                emit_progress("Syncing all installed external skill sources with their upstream repositories.")
                print(json.dumps(sync_all_external_skills(project_root=root), indent=2))
            else:
                emit_progress(f"Syncing the external skill source '{args.slug}' with its upstream repository.")
                print(json.dumps({"synced_skill": sync_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
        if args.skills_command == "remove":
            emit_progress(f"Removing the external skill source '{args.slug}' from the local Skilgen registry.")
            print(json.dumps({"removed_skill": remove_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
        if args.skills_command == "activate":
            emit_progress(f"Activating the external skill source '{args.slug}' for agent loading.")
            print(json.dumps({"activated_skill": activate_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
        if args.skills_command == "deactivate":
            emit_progress(f"Deactivating the external skill source '{args.slug}' for agent loading.")
            print(json.dumps({"deactivated_skill": deactivate_external_skill(project_root=root, slug=args.slug)}, indent=2))
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
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting feature synthesis with the {current_runtime_mode(root)} runtime. Skilgen is reading the project context to identify the capabilities that matter."
        )
        emit_progress("Reading the codebase and optional requirements to identify product capabilities.")
        requirements = Path(args.requirements).resolve() if args.requirements else None
        features = extract_features(requirements, root)
        emit_progress("Grouping detected backend, frontend, and planning signals into a reusable feature inventory.")
        print(json.dumps({"features": [feature.__dict__ for feature in features]}, indent=2))
        return
    if args.command == "plan":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting roadmap planning with the {current_runtime_mode(root)} runtime. Skilgen is turning project context into a staged implementation plan."
        )
        emit_progress("Reading project scope and available inputs for roadmap planning.")
        config = load_config(root)
        plan = build_roadmap_plan(
            config,
            parse_project_intent(root, Path(args.requirements).resolve() if args.requirements else None),
            root,
        )
        emit_progress("Synthesizing implementation phases and sequencing the next delivery steps.")
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
    if args.command == "doctor":
        payload = doctor_payload(Path(args.project_root).resolve())
        print(json.dumps(payload, indent=2))
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
                    Path(args.requirements).resolve() if args.requirements else None,
                    Path(args.project_root),
                    targets=targets,
                    domains=domains,
                ),
                indent=2,
            )
        )
        return

    if args.command == "watch":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting watch mode with the {current_runtime_mode(root)} runtime. Skilgen will explain each refresh as changes are detected."
        )
        runs = watch_delivery(
            Path(args.requirements).resolve() if args.requirements else None,
            root,
            targets=targets,
            domains=domains,
            interval_seconds=args.interval,
            cycles=args.cycles,
            once=args.once,
            progress_callback=emit_progress,
        )
        print(json.dumps({"runtime": current_runtime_mode(root), "runs": [[str(path) for path in generated] for generated in runs]}, indent=2))
        return

    root = Path(args.project_root).resolve()
    diagnostics = runtime_diagnostics(root)
    emit_progress(
        f"Starting delivery with the {current_runtime_mode(root)} runtime. This may take a bit while Skilgen builds project context and generates the final skill tree."
    )
    if diagnostics["runtime"] != "model_backed":
        emit_progress(f"Model-backed runtime is not ready: {diagnostics['reason']}")
    generated = run_delivery(
        Path(args.requirements).resolve() if args.requirements else None,
        root,
        targets=targets,
        domains=domains,
        dry_run=args.dry_run,
        progress_callback=emit_progress,
    )
    print(
        json.dumps(
            {
                "runtime": current_runtime_mode(root),
                "runtime_diagnostics": diagnostics,
                "generated_files": [str(path) for path in generated],
            },
            indent=2,
        )
    )


def console_main() -> None:
    main()


if __name__ == "__main__":
    console_main()
