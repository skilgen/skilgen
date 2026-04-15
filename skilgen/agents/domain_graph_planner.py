from __future__ import annotations

from pathlib import Path

from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence
from skilgen.agents.requirements_parser import parse_project_intent_native
from skilgen.deep_agents_core import run_deep_json
from skilgen.core.models import CodebaseSignals, DomainGraph, DomainGraphNode, RequirementsContext


def _node(
    name: str,
    *,
    summary: str,
    confidence: float,
    key_files: list[str],
    key_patterns: list[str],
    parent_domain: str | None = None,
    child_domains: list[str] | None = None,
    related_domains: list[str] | None = None,
    skill_path: str | None = None,
) -> DomainGraphNode:
    return DomainGraphNode(
        name=name,
        summary=summary,
        confidence=confidence,
        key_files=key_files,
        key_patterns=key_patterns,
        parent_domain=parent_domain,
        child_domains=child_domains or [],
        related_domains=related_domains or [],
        skill_path=skill_path,
    )


def _top_file(paths: list[str], fallback: list[str], limit: int = 4) -> list[str]:
    if paths:
        return paths[:limit]
    return fallback


def _python_package_root(project_root: Path) -> Path | None:
    candidates = [
        path
        for path in sorted(project_root.iterdir())
        if path.is_dir()
        and (path / "__init__.py").exists()
        and path.name not in {"tests", "docs", "scripts", "skills"}
    ]
    return candidates[0] if candidates else None


def _relative_py_files(project_root: Path, directory: Path, *, top_level_only: bool = False, limit: int = 6) -> list[str]:
    if not directory.exists():
        return []
    pattern = "*.py" if top_level_only else "**/*.py"
    files = [
        path.relative_to(project_root).as_posix()
        for path in sorted(directory.glob(pattern))
        if path.is_file()
    ]
    return files[:limit]


def _relative_code_files(project_root: Path, directory: Path, *, limit: int = 24) -> list[str]:
    if not directory.exists():
        return []
    files = [
        path.relative_to(project_root).as_posix()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".rs"}
    ]
    return files[:limit]


def _python_monorepo_libraries(project_root: Path) -> list[tuple[str, Path, Path | None]]:
    libs_root = project_root / "libs"
    if not libs_root.exists():
        return []
    libraries: list[tuple[str, Path, Path | None]] = []
    for lib_dir in sorted(path for path in libs_root.iterdir() if path.is_dir()):
        package_candidates = [
            path
            for path in sorted(lib_dir.rglob("*"))
            if path.is_dir()
            and (path / "__init__.py").exists()
            and ".git" not in path.parts
            and "tests" not in {part.lower() for part in path.relative_to(lib_dir).parts}
        ]
        package_root = min(package_candidates, key=lambda path: len(path.parts)) if package_candidates else None
        libraries.append((lib_dir.name.replace("_", "-"), lib_dir, package_root))
    return libraries


def _top_level_app_surfaces(project_root: Path) -> list[tuple[str, Path, list[str]]]:
    surfaces: list[tuple[str, Path, list[str]]] = []
    ignored = {
        "skills",
        "docs",
        "node_modules",
        "dist",
        "build",
        "coverage",
        "vendor",
        "__pycache__",
    }
    for directory in sorted(path for path in project_root.iterdir() if path.is_dir() and not path.name.startswith(".")):
        if directory.name in ignored:
            continue
        files = _relative_code_files(project_root, directory, limit=48)
        if len(files) < 3 and directory.name not in {"config", "e2e"}:
            continue
        surfaces.append((directory.name.replace("_", "-"), directory, files))
    return surfaces


def _confidence_value(raw: object) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).strip().lower()
    mapping = {
        "very_high": 0.95,
        "very high": 0.95,
        "high": 0.85,
        "medium": 0.65,
        "low": 0.4,
        "very_low": 0.2,
        "very low": 0.2,
    }
    if text in mapping:
        return mapping[text]
    try:
        return float(text)
    except ValueError:
        return 0.5


def _package_module_slug(path: str) -> str:
    stem = Path(path).stem
    if stem == "__main__":
        return "cli"
    if stem == "__init__":
        return "core"
    return stem.replace("_", "-")


def _package_module_summary(package_name: str, path: str) -> str:
    slug = _package_module_slug(path)
    labels = {
        "analyze": "Graph analysis and insight guidance for metrics, surprising connections, and code understanding queries.",
        "benchmark": "Benchmarking guidance for measuring context reduction, performance, and token efficiency.",
        "build": "Graph construction guidance for assembling extracted artifacts into connected graph structures.",
        "cache": "Cache guidance for skipping unchanged files and preserving extraction performance.",
        "cluster": "Clustering guidance for community detection, cohesion scoring, and graph partitioning.",
        "detect": "Detection guidance for file discovery, corpus classification, and repository health checks.",
        "export": "Export guidance for turning graph data into HTML, JSON, SVG, GraphML, or other delivery surfaces.",
        "extract": "Extraction guidance for parsing files, symbols, and relationships from repository inputs.",
        "hooks": "Hook and automation guidance for install-time or git-integrated Graphify workflows.",
        "ingest": "Ingestion guidance for bringing code, docs, and repo signals into the graph pipeline.",
        "manifest": "Manifest guidance for graph metadata, packaging, and generated surface coordination.",
        "report": "Reporting guidance for narrative summaries and consumable graph insights.",
        "security": "Security guidance for URL validation, path safety, and defensive runtime boundaries.",
        "serve": "Serving guidance for local dashboard or API-style delivery of graph outputs.",
        "transcribe": "Transcription guidance for converting external artifacts into repo-usable graph inputs.",
        "validate": "Validation guidance for integrity checks, graph sanity checks, and delivery guardrails.",
        "watch": "Watch-mode guidance for incremental rebuilds, file watching, and refresh loops.",
        "wiki": "Knowledge-surface guidance for wiki or docs-oriented graph publishing.",
        "cli": "CLI guidance for command-line entrypoints and operator workflows exposed through the package.",
        "core": f"Core {package_name} package guidance for shared entrypoints and package-level contracts.",
    }
    return labels.get(slug, f"{package_name} module guidance for `{Path(path).name}` and its closely related implementation seams.")


def _library_summary(library_name: str, relative_root: str) -> str:
    labels = {
        "core": "Shared LangChain core abstractions for runnables, prompts, messages, tools, outputs, and execution plumbing.",
        "langchain": "Primary LangChain library guidance for chains, agents, retrieval, memory, and higher-level orchestration.",
        "langchain-v1": "Versioned LangChain v1 package guidance for the modern public API surface and migration-friendly entrypoints.",
        "text-splitters": "Text splitting guidance for chunking, token-aware segmentation, and document preparation flows.",
        "model-profiles": "Model profile guidance for provider capability metadata, compatibility, and runtime selection surfaces.",
        "standard-tests": "Shared testing guidance for package-level conformance, integration baselines, and reusable validation fixtures.",
        "partners": "Partner integration guidance for provider-specific packages shipped within the LangChain monorepo.",
    }
    return labels.get(library_name, f"Monorepo library guidance for `{relative_root}` and its package-specific implementation boundaries.")


def _subpackage_summary(library_name: str, subpackage_name: str) -> str:
    return f"{library_name.replace('-', ' ').title()} guidance for the `{subpackage_name}` subpackage and its closely related implementation seams."


def _app_surface_summary(surface_name: str, relative_root: str) -> str:
    labels = {
        "api": "Backend application guidance for API routes, services, persistence, auth, and runtime orchestration under the repo's `api/` surface.",
        "client": "Frontend application guidance for the user-facing client, routes, UI composition, and client-side runtime behavior.",
        "packages": "Shared package guidance for reusable internal packages that support the app runtime and product surfaces.",
        "config": "Configuration guidance for runtime configuration, feature flags, translation setup, and environment-driven behavior.",
        "e2e": "End-to-end testing guidance for browser workflows, setup, and cross-surface regression coverage.",
        "helm": "Deployment guidance for Helm charts, release packaging, and cluster-facing operational configuration.",
        "utils": "Utility guidance for shared scripts, support code, and operational helpers that sit outside the main app surfaces.",
        "src": "Source-surface guidance for repo-level source files that do not live under a more specific package boundary.",
    }
    return labels.get(surface_name, f"Repo-native app guidance for the `{relative_root}` surface and its closely related implementation seams.")


def _app_child_summary(parent_name: str, child_name: str) -> str:
    return f"{parent_name.replace('-', ' ').title()} guidance for the `{child_name}` surface and its closely related implementation seams."


def build_domain_graph_native(project_root: Path, requirements: RequirementsContext) -> DomainGraph:
    root = project_root.resolve()
    signals = analyze_codebase(root)
    requirements_path = requirements.requirements_path if requirements.requirements_path.exists() else None
    intent = parse_project_intent_native(root, requirements_path)
    package_root = _python_package_root(root)
    package_runtime_files = _relative_py_files(root, package_root, top_level_only=True, limit=100) if package_root is not None else []
    package_focused_repo = bool(
        package_root is not None
        and len(package_runtime_files) >= 4
        and not signals.backend_routes
        and not signals.services
        and not signals.frontend_routes
        and not signals.components
        and not signals.data_models
        and not signals.persistence_layers
        and not signals.background_jobs
        and not signals.legacy_programs
        and not signals.copybooks
    )
    monorepo_libraries = _python_monorepo_libraries(root)
    monorepo_focused_repo = bool(
        not package_focused_repo
        and len(monorepo_libraries) >= 2
        and (root / "libs").exists()
    )
    app_surfaces = _top_level_app_surfaces(root)
    app_native_repo = bool(
        not package_focused_repo
        and not monorepo_focused_repo
        and len(app_surfaces) >= 3
        and {name for name, _, _ in app_surfaces} & {"api", "client", "packages"}
    )

    backend_children = ["backend-api", "backend-testing"]
    if signals.backend_routes:
        backend_children.append("backend-routes")
    if signals.services or signals.legacy_programs:
        backend_children.append("backend-services")
    if signals.data_models or signals.persistence_layers:
        backend_children.append("backend-data")
    if signals.copybooks:
        backend_children.append("backend-copybooks")
    if signals.auth_files:
        backend_children.append("backend-auth")
    if signals.background_jobs:
        backend_children.append("backend-jobs")

    frontend_children = ["frontend-components"]
    if signals.frontend_routes:
        frontend_children.append("frontend-routes")
    if signals.state_files:
        frontend_children.append("frontend-state")
    if signals.design_system_files:
        frontend_children.append("frontend-design-system")

    nodes: list[DomainGraphNode] = []
    if requirements.domains.get("requirements") or requirements.requirements_path.exists():
        nodes.append(
            _node(
                "requirements",
                summary="Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.",
                confidence=0.99,
                key_files=_top_file([requirements.requirements_path.name], ["docs/"], limit=1),
                key_patterns=["requirements-first planning", "skill scaffolding", "agent operating guidance"],
                child_domains=[],
                related_domains=[name for name in ["backend", "frontend", "roadmap"] if name],
                skill_path="skills/requirements/SKILL.md",
            )
        )

    backend_detected = any(
        [
            signals.backend_routes,
            signals.services,
            signals.data_models,
            signals.persistence_layers,
            signals.auth_files,
            signals.legacy_programs,
            signals.copybooks,
        ]
    )
    if not package_focused_repo and not monorepo_focused_repo and not app_native_repo and (requirements.domains.get("backend") or backend_detected):
        nodes.append(
            _node(
                "backend",
                summary="Server-side delivery domain covering route handlers, services, persistence, and verification of backend changes.",
                confidence=0.88,
                key_files=_top_file(
                    [
                        *signals.backend_routes,
                        *signals.services,
                        *signals.data_models,
                        *signals.auth_files,
                        *signals.legacy_programs,
                        *signals.copybooks,
                    ],
                    ["api/", "services/"],
                ),
                key_patterns=["endpoint quality gate", "service boundaries", "transport-to-domain separation"],
                child_domains=backend_children,
                related_domains=["requirements", "roadmap", "frontend"],
                skill_path="skills/backend/SKILL.md",
            )
        )

    frontend_detected = any(
        [signals.frontend_routes, signals.components, signals.state_files, signals.design_system_files]
    )
    if not package_focused_repo and not monorepo_focused_repo and not app_native_repo and (requirements.domains.get("frontend") or frontend_detected):
        nodes.append(
            _node(
                "frontend",
                summary="User-facing delivery domain covering route composition, reusable UI, state, and design-system concerns.",
                confidence=0.88,
                key_files=_top_file(
                    [*signals.frontend_routes, *signals.components, *signals.state_files, *signals.design_system_files],
                    ["src/", "app/"],
                ),
                key_patterns=["route-driven UI structure", "shared components", "stateful UX flows"],
                child_domains=frontend_children,
                related_domains=["requirements", "roadmap", "backend"],
                skill_path="skills/frontend/SKILL.md",
            )
        )

    platform_areas: list[tuple[str, str, list[str], list[str], str]] = []
    if package_root is not None:
        runtime_files = _relative_py_files(root, package_root, top_level_only=True)
        agents_files = _relative_py_files(root, package_root / "agents")
        cli_files = _relative_py_files(root, package_root / "cli")
        core_files = _relative_py_files(root, package_root / "core")
        generator_files = _relative_py_files(root, package_root / "generators")
        script_files = _relative_py_files(root, root / "scripts")
        if runtime_files:
            if (root / "setup.py").exists():
                runtime_files = [*runtime_files[:5], "setup.py"]
            platform_areas.append(
                (
                    "platform-runtime",
                    "Runtime orchestration guidance for package-level entrypoints, delivery orchestration, and repo-wide integration surfaces.",
                    runtime_files,
                    ["runtime orchestration", "repo-wide coordination", "package entrypoints"],
                    "skills/platform/runtime/SKILL.md",
                )
            )
        if agents_files:
            platform_areas.append(
                (
                    "platform-agents",
                    "Planner and inference guidance for domain graphing, architecture synthesis, and decision intelligence.",
                    agents_files,
                    ["domain inference", "architecture synthesis", "agent planning logic"],
                    "skills/platform/agents/SKILL.md",
                )
            )
        if cli_files:
            platform_areas.append(
                (
                    "platform-cli",
                    "Operator-facing CLI guidance for command surfaces, progress reporting, and repo-local execution flows.",
                    cli_files,
                    ["command surfaces", "operator UX", "progress orchestration"],
                    "skills/platform/cli/SKILL.md",
                )
            )
        if core_files:
            platform_areas.append(
                (
                    "platform-core",
                    "Shared core guidance for scoring, freshness, diffing, context loading, and validation primitives.",
                    core_files,
                    ["shared models", "freshness and scoring", "validation primitives"],
                    "skills/platform/core/SKILL.md",
                )
            )
        if generator_files:
            platform_areas.append(
                (
                    "platform-generators",
                    "Artifact materialization guidance for docs, skills, dashboards, and output rendering flows.",
                    generator_files,
                    ["artifact rendering", "materialization flow", "repo-local outputs"],
                    "skills/platform/generators/SKILL.md",
                )
            )
        if script_files:
            platform_areas.append(
                (
                    "platform-scripts",
                    "Maintenance automation guidance for release helpers and repo scripts that support the generation pipeline.",
                    script_files,
                    ["maintenance automation", "release helpers", "pipeline scripts"],
                    "skills/platform/scripts/SKILL.md",
                )
            )

    if len(platform_areas) >= 2:
        platform_children = [name for name, *_ in platform_areas]
        platform_key_files: list[str] = []
        for _, _, files, _, _ in platform_areas:
            platform_key_files.extend(files[:2])
        platform_parent_files = list(dict.fromkeys(platform_key_files))[:8]
        if not platform_parent_files:
            platform_parent_files = [f"{package_root.name}/"] if package_root is not None else ["scripts/"]
        nodes.append(
            _node(
                "platform",
                summary="Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.",
                confidence=0.9,
                key_files=platform_parent_files,
                key_patterns=["tooling platform", "generation engine", "repo-local operating surface"],
                child_domains=platform_children,
                related_domains=["requirements", "backend", "roadmap", "frontend"],
                skill_path="skills/platform/SKILL.md",
            )
        )
        for name, summary, key_files, key_patterns, skill_path in platform_areas:
            nodes.append(
                _node(
                    name,
                    summary=summary,
                    confidence=0.84,
                    key_files=key_files,
                    key_patterns=key_patterns,
                    parent_domain="platform",
                    related_domains=["requirements", "roadmap", "backend"],
                    skill_path=skill_path,
                )
            )

    if package_focused_repo and package_root is not None:
        package_name = package_root.name.replace("_", "-")
        package_parent = f"{package_name}-core"
        module_paths = [path for path in package_runtime_files if not path.endswith("__init__.py")]
        worked_paths = _relative_code_files(root, root / "worked", limit=12)
        child_domains: list[str] = []
        nodes.append(
            _node(
                package_parent,
                summary=f"Primary {package_root.name} package domain covering the repo's core runtime modules, operator flows, and graph-processing seams.",
                confidence=0.93,
                key_files=package_runtime_files[:16],
                key_patterns=["package-level runtime", "module-oriented tooling", "repo-native graph workflows"],
                child_domains=child_domains,
                related_domains=["roadmap", "requirements", "testing"] if requirements.requirements_path.exists() else ["roadmap", "testing"],
                skill_path=f"skills/{package_parent}/SKILL.md",
            )
        )
        for relative in module_paths[:16]:
            slug = _package_module_slug(relative)
            child_name = f"{package_name}-{slug}"
            child_domains.append(child_name)
            nodes.append(
                _node(
                    child_name,
                    summary=_package_module_summary(package_root.name, relative),
                    confidence=0.84,
                    key_files=[relative],
                    key_patterns=[f"{package_root.name} module: {Path(relative).name}", "Stay close to the module boundary before widening scope."],
                    parent_domain=package_parent,
                    related_domains=["roadmap"],
                    skill_path=f"skills/{package_root.name}/{slug}/SKILL.md",
                )
            )
        if signals.tests:
            child_name = f"{package_name}-testing"
            child_domains.append(child_name)
            nodes.append(
                _node(
                    child_name,
                    summary=f"Testing guidance for {package_root.name}, including repo-local verification, regression checks, and module-level confidence work.",
                    confidence=0.82,
                    key_files=signals.tests[:8],
                    key_patterns=["module verification", "regression coverage", "repo-native test discipline"],
                    parent_domain=package_parent,
                    related_domains=["roadmap"],
                    skill_path=f"skills/{package_root.name}/testing/SKILL.md",
                )
            )
        if worked_paths:
            child_name = f"{package_name}-examples"
            child_domains.append(child_name)
            nodes.append(
                _node(
                    child_name,
                    summary=f"Example and worked-corpus guidance for {package_root.name}, including sample inputs, fixtures, and demonstration flows.",
                    confidence=0.78,
                    key_files=worked_paths[:8],
                    key_patterns=["worked examples", "sample corpus", "fixture-backed exploration"],
                    parent_domain=package_parent,
                    related_domains=["roadmap"],
                    skill_path=f"skills/{package_root.name}/examples/SKILL.md",
                )
            )

    if monorepo_focused_repo:
        for library_name, lib_dir, package_dir in monorepo_libraries:
            relative_root = lib_dir.relative_to(root).as_posix()
            key_files = _relative_code_files(root, package_dir or lib_dir, limit=24)
            if not key_files:
                continue
            child_domains: list[str] = []
            parent_domain = library_name
            nodes.append(
                _node(
                    parent_domain,
                    summary=_library_summary(library_name, relative_root),
                    confidence=0.88,
                    key_files=key_files,
                    key_patterns=["library package surface", "monorepo implementation seam", "repo-native module guidance"],
                    child_domains=child_domains,
                    related_domains=["roadmap"],
                    skill_path=f"skills/{library_name}/SKILL.md",
                )
            )
            if package_dir is None:
                continue
            child_items: list[tuple[str, list[str], str]] = []
            for py_file in sorted(package_dir.glob("*.py"))[:8]:
                if py_file.name == "__init__.py":
                    continue
                slug = py_file.stem.replace("_", "-")
                child_items.append((slug, [py_file.relative_to(root).as_posix()], py_file.name))
            for subdir in sorted(path for path in package_dir.iterdir() if path.is_dir() and (path / "__init__.py").exists())[:8]:
                slug = subdir.name.replace("_", "-")
                child_files = _relative_code_files(root, subdir, limit=8)
                if child_files:
                    child_items.append((slug, child_files, subdir.name))
            seen_child_slugs: set[str] = set()
            for slug, child_files, label in child_items:
                if slug in seen_child_slugs:
                    continue
                seen_child_slugs.add(slug)
                child_name = f"{library_name}-{slug}"
                child_domains.append(child_name)
                nodes.append(
                    _node(
                        child_name,
                        summary=_subpackage_summary(library_name, label),
                        confidence=0.8,
                        key_files=child_files,
                        key_patterns=[f"{library_name} subpackage: {label}", "Stay close to the inferred library seam before widening scope."],
                        parent_domain=parent_domain,
                        related_domains=["roadmap"],
                        skill_path=f"skills/{library_name}/{slug}/SKILL.md",
                    )
                )

    if app_native_repo:
        for surface_name, surface_dir, key_files in app_surfaces:
            child_domains: list[str] = []
            nodes.append(
                _node(
                    surface_name,
                    summary=_app_surface_summary(surface_name, surface_dir.relative_to(root).as_posix()),
                    confidence=0.87,
                    key_files=key_files[:24],
                    key_patterns=["repo-native app surface", "top-level implementation boundary", "folder-driven capability map"],
                    child_domains=child_domains,
                    related_domains=["roadmap"],
                    skill_path=f"skills/{surface_name}/SKILL.md",
                )
            )
            child_entries: list[tuple[str, list[str], str]] = []
            for child_dir in sorted(path for path in surface_dir.iterdir() if path.is_dir() and not path.name.startswith(".")):
                child_files = _relative_code_files(root, child_dir, limit=12)
                if len(child_files) < 3:
                    continue
                child_entries.append((child_dir.name.replace("_", "-"), child_files, child_dir.name))
            seen_child_names: set[str] = set()
            for child_slug, child_files, child_label in child_entries[:8]:
                if child_slug in seen_child_names:
                    continue
                seen_child_names.add(child_slug)
                child_name = f"{surface_name}-{child_slug}"
                child_domains.append(child_name)
                nodes.append(
                    _node(
                        child_name,
                        summary=_app_child_summary(surface_name, child_label),
                        confidence=0.79,
                        key_files=child_files,
                        key_patterns=[f"{surface_name} surface: {child_label}", "Stay close to the repo-native folder seam before widening scope."],
                        parent_domain=surface_name,
                        related_domains=["roadmap"],
                        skill_path=f"skills/{surface_name}/{child_slug}/SKILL.md",
                    )
                )

    nodes.append(
        _node(
            "roadmap",
            summary="Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.",
            confidence=0.84,
            key_files=["skills/roadmap/SKILL.md", "REPORT.md"],
            key_patterns=["phase-based delivery", "sequenced implementation planning", "traceable next steps"],
            child_domains=["roadmap-phase-0", "roadmap-phase-1", "roadmap-phase-2", "roadmap-phase-3"],
            related_domains=["requirements", "backend", "frontend"],
            skill_path="skills/roadmap/SKILL.md",
        )
    )

    if signals.design_system_files and not package_focused_repo and not monorepo_focused_repo and not app_native_repo and not (signals.frontend_routes or signals.components):
        nodes.append(
            _node(
                "design-system",
                summary="Standalone visual system domain inferred from themes, tokens, or shared UI primitives without a broader frontend app structure.",
                confidence=0.83,
                key_files=_top_file(signals.design_system_files, ["src/theme/"]),
                key_patterns=["design tokens", "theme primitives", "shared visual language"],
                related_domains=["roadmap", "requirements"],
                skill_path="skills/design-system/SKILL.md",
            )
        )

    if signals.auth_files and not package_focused_repo and not monorepo_focused_repo and not app_native_repo and not (signals.backend_routes or signals.services):
        nodes.append(
            _node(
                "security",
                summary="Standalone security domain inferred from authentication, authorization, or session management files.",
                confidence=0.83,
                key_files=_top_file(signals.auth_files, ["auth/"]),
                key_patterns=["authentication", "authorization", "session discipline"],
                related_domains=["roadmap", "requirements"],
                skill_path="skills/security/SKILL.md",
            )
        )

    if signals.background_jobs and not package_focused_repo and not monorepo_focused_repo and not app_native_repo and not (signals.backend_routes or signals.services or signals.legacy_programs):
        nodes.append(
            _node(
                "operations",
                summary="Standalone operations domain inferred from workers, tasks, queues, or background jobs.",
                confidence=0.8,
                key_files=_top_file(signals.background_jobs, ["jobs/"]),
                key_patterns=["async execution", "scheduled work", "worker reliability"],
                related_domains=["roadmap", "requirements"],
                skill_path="skills/operations/SKILL.md",
            )
        )

    if not package_focused_repo and not monorepo_focused_repo and not app_native_repo and (signals.data_models or signals.persistence_layers or signals.copybooks) and not (
        signals.backend_routes or signals.services or signals.legacy_programs
    ):
        nodes.append(
            _node(
                "data-platform",
                summary="Standalone data platform domain inferred from data models, schemas, or persistence layers without a stronger application-service boundary.",
                confidence=0.8,
                key_files=_top_file([*signals.data_models, *signals.persistence_layers, *signals.copybooks], ["models/", "db/"]),
                key_patterns=["schema discipline", "repository boundaries", "data contracts"],
                related_domains=["roadmap", "requirements"],
                skill_path="skills/data-platform/SKILL.md",
            )
        )

    for name, summary, key_files, key_patterns, skill_path in [
        (
            "backend-api",
            "API contract and handler guidance for backend routes and request/response boundaries.",
            _top_file(signals.backend_routes, ["api/"]),
            ["request/response contracts", "thin handlers", "endpoint coverage"],
            "skills/backend/api/SKILL.md",
        ),
        (
            "backend-testing",
            "Verification guidance for endpoints and core flows touched by backend delivery.",
            _top_file(signals.tests, ["tests/"]),
            ["happy path coverage", "failure path coverage", "endpoint-first verification"],
            "skills/backend/testing/SKILL.md",
        ),
        (
            "backend-routes",
            "Route and controller guidance derived from existing backend route files.",
            _top_file(signals.backend_routes, ["api/routes/"]),
            ["route extension", "edge validation", "thin transport layer"],
            "skills/backend/routes/SKILL.md",
        ),
        (
            "backend-services",
            "Service and use-case guidance for existing orchestration, business logic modules, and legacy programs.",
            _top_file([*signals.services, *signals.legacy_programs], ["services/", "cobol/"]),
            ["service boundaries", "orchestration separation", "reusable business logic", "legacy program boundaries"],
            "skills/backend/services/SKILL.md",
        ),
        (
            "backend-data",
            "Data models, repositories, and persistence guidance inferred from backend storage layers.",
            _top_file([*signals.data_models, *signals.persistence_layers, *signals.copybooks], ["models/", "db/"]),
            ["data contracts", "repository boundaries", "schema-to-domain alignment"],
            "skills/backend/data/SKILL.md",
        ),
        (
            "backend-copybooks",
            "Copybook and record-layout guidance inferred from COBOL copybooks and shared record definitions.",
            _top_file(signals.copybooks, ["copybooks/"]),
            ["copybook contracts", "record layouts", "shared data definitions"],
            "skills/backend/copybooks/SKILL.md",
        ),
        (
            "backend-auth",
            "Auth and permission guidance inferred from backend security and authorization files.",
            _top_file(signals.auth_files, ["auth/"]),
            ["auth safety", "permission checks", "explicit unauthorized-path testing"],
            "skills/backend/auth/SKILL.md",
        ),
        (
            "backend-jobs",
            "Background worker and async execution guidance inferred from queue, worker, or task files.",
            _top_file(signals.background_jobs, ["jobs/"]),
            ["async execution safety", "idempotency", "retry-aware design"],
            "skills/backend/jobs/SKILL.md",
        ),
    ]:
        if not package_focused_repo and not monorepo_focused_repo and not app_native_repo and name in backend_children:
            nodes.append(
                _node(
                    name,
                    summary=summary,
                    confidence=0.8,
                    key_files=key_files,
                    key_patterns=key_patterns,
                    parent_domain="backend",
                    related_domains=["requirements", "roadmap"],
                    skill_path=skill_path,
                )
            )

    for name, summary, key_files, key_patterns, skill_path in [
        (
            "frontend-components",
            "Reusable component and UI composition guidance inferred from existing frontend component files.",
            _top_file(signals.components, ["src/components/"]),
            ["shared component composition", "route-to-component reuse", "UI modularity"],
            "skills/frontend/components/SKILL.md",
        ),
        (
            "frontend-routes",
            "Frontend route and page guidance inferred from the current route or page structure.",
            _top_file(signals.frontend_routes, ["src/routes/"]),
            ["route-driven UI", "page composition", "screen-level reuse"],
            "skills/frontend/routes/SKILL.md",
        ),
        (
            "frontend-state",
            "State-management guidance inferred from detected stores, contexts, or reducer-style files.",
            _top_file(signals.state_files, ["src/state/"]),
            ["state boundaries", "shared state discipline", "predictable updates"],
            "skills/frontend/state/SKILL.md",
        ),
        (
            "frontend-design-system",
            "Design-system guidance inferred from themes, tokens, or reusable UI primitives.",
            _top_file(signals.design_system_files, ["src/theme/"]),
            ["shared visual primitives", "token-driven styling", "UI consistency"],
            "skills/frontend/design-system/SKILL.md",
        ),
    ]:
        if not package_focused_repo and not monorepo_focused_repo and not app_native_repo and name in frontend_children:
            nodes.append(
                _node(
                    name,
                    summary=summary,
                    confidence=0.8,
                    key_files=key_files,
                    key_patterns=key_patterns,
                    parent_domain="frontend",
                    related_domains=["requirements", "roadmap"],
                    skill_path=skill_path,
                )
            )

    for phase in ["phase-0", "phase-1", "phase-2", "phase-3"]:
        nodes.append(
            _node(
                f"roadmap-{phase}",
                summary=f"Roadmap phase node for {phase} planning and sequencing guidance.",
                confidence=0.72,
                key_files=["skills/roadmap/SKILL.md"],
                key_patterns=["phase sequencing", "delivery planning"],
                parent_domain="roadmap",
                related_domains=["requirements"],
                skill_path=f"skills/roadmap/{phase}/SKILL.md",
            )
        )

    recommendations = [
        "Use the inferred domain graph to decide which parent and child skills need regeneration.",
        "Refresh AGENTS.md whenever parent skill entry points or core domain relationships change.",
    ]
    if signals.tests:
        recommendations.append("Keep endpoint and flow validation coupled to the inferred domains when code changes.")
    if intent.features:
        recommendations.append("Re-run planning when new requirements materially change the inferred domain topology.")
    return DomainGraph(nodes=nodes, recommendations=recommendations)


def build_domain_graph(project_root: Path, requirements: RequirementsContext) -> DomainGraph:
    root = project_root.resolve()
    native_graph = build_domain_graph_native(root, requirements)
    requirements_path = requirements.requirements_path if requirements.requirements_path.exists() else None
    signals = analyze_codebase(root)
    code_evidence = collect_code_evidence(root)
    structural_evidence = collect_structural_evidence(root)
    intent = parse_project_intent_native(root, requirements_path)
    payload = run_deep_json(
        "dynamic domain graph planning",
        (
            "Infer the domain graph for Skilgen from repository evidence and requirements. Return JSON with keys "
            "nodes and recommendations. Each node must contain: name, summary, confidence, key_files, key_patterns, "
            "parent_domain, child_domains, related_domains, skill_path. Treat this as dynamic skill-topology planning, "
            "not a fixed taxonomy exercise. Use the code evidence to decide which parent domains, subdomains, and "
            "skill paths should exist. You may preserve common families like backend or frontend when they clearly "
            "exist, but introduce more precise domain families when the repo structure deserves them. Prefer stable, "
            "implementation-relevant names, realistic parent-child relationships, and skill_path values under skills/ "
            "that a coding agent could actually use to navigate the repository.\n\n"
            f"Project root: {root}\n"
            f"Requirements summary: {requirements.summary}\n"
            f"Requirements domains: {requirements.domains}\n"
            f"Intent JSON: {intent.__dict__}\n"
            f"Signals JSON: {signals.__dict__}\n"
            f"Code evidence JSON: {code_evidence}\n"
            f"Structural evidence JSON: {structural_evidence}\n"
            f"Native graph JSON: { {'nodes': [node.__dict__ for node in native_graph.nodes], 'recommendations': native_graph.recommendations} }\n"
        ),
        lambda: {
            "nodes": [node.__dict__ for node in native_graph.nodes],
            "recommendations": native_graph.recommendations,
        },
        project_root=root,
    )
    nodes = [
        DomainGraphNode(
            name=str(node.get("name", "domain")),
            summary=str(node.get("summary", "")),
            confidence=_confidence_value(node.get("confidence", 0.5)),
            key_files=[str(item) for item in node.get("key_files", [])],
            key_patterns=[str(item) for item in node.get("key_patterns", [])],
            parent_domain=str(node.get("parent_domain")) if node.get("parent_domain") is not None else None,
            child_domains=[str(item) for item in node.get("child_domains", [])],
            related_domains=[str(item) for item in node.get("related_domains", [])],
            skill_path=str(node.get("skill_path")) if node.get("skill_path") else None,
        )
        for node in payload.get("nodes", [])
    ]
    if not nodes:
        nodes = native_graph.nodes
    recommendations = [str(item) for item in payload.get("recommendations", [])] or native_graph.recommendations
    return DomainGraph(nodes=nodes, recommendations=recommendations)
