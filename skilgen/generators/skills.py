from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import Callable

from skilgen.agents.architecture_planner import build_architecture_blueprint
from skilgen.agents.codebase_signals import analyze_codebase
from skilgen.agents.requirements_parser import parse_project_intent
from skilgen.agents.roadmap_planner import build_roadmap_plan
from skilgen.core.config import load_config
from skilgen.core.analytics import _compute_richness_score
from skilgen.core.dependency_risk import dependency_skill_signals
from skilgen.core.models import ArchitectureBlueprint, ArchitectureDomain, SkillMaterializationPlan
from skilgen.core.context import build_codebase_context
from skilgen.core.models import RequirementsContext, SkillSpec
from skilgen.deep_agents_core import run_deep_text


TODAY = date.today().isoformat()
ProgressCallback = Callable[[str], None]
CODE_EXAMPLE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
}

ANTI_PATTERN_TEMPLATES = {
    "backend": [
        "Don't bury business logic in route handlers — keep orchestration in services or use-case modules",
        "Don't change endpoint behaviour without success and failure-path tests",
        "Don't bypass existing persistence and validation contracts for one-off request handling",
    ],
    "api": [
        "Don't return raw exception messages to clients — always use structured error responses",
        "Don't skip input validation — validate at the API boundary, not only in the DB layer",
        "Don't hardcode environment-specific URLs or secrets in route handlers",
    ],
    "auth": [
        "Don't roll custom crypto or token generation — use established libraries",
        "Don't store raw passwords — always hash with bcrypt or argon2",
        "Don't trust client-supplied user IDs without verifying the session token",
    ],
    "database": [
        "Don't construct raw SQL strings with user input — always use parameterised queries",
        "Don't run migrations inside application startup — use a dedicated migration step",
        "Don't load entire tables into memory — always paginate or use streaming",
    ],
    "frontend": [
        "Don't fetch data inside render functions without caching — causes waterfalls",
        "Don't store sensitive data in localStorage — use httpOnly cookies",
        "Don't mutate props directly — always use state management patterns",
    ],
    "testing": [
        "Don't write tests that depend on execution order — each test must be independent",
        "Don't mock the system under test — only mock external dependencies",
        "Don't assert on implementation details — assert on observable behaviour",
    ],
}

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".rb": "ruby",
    ".java": "java",
    ".rs": "rust",
}


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _signal_bullets(items: list[str], fallback: str, limit: int = 5) -> list[str]:
    if not items:
        return [fallback]
    bullets = [f"Detected: `{item}`" for item in items[:limit]]
    if len(items) > limit:
        bullets.append(f"Detected {len(items) - limit} more matching files elsewhere in the repo.")
    return bullets


def _resolve_spec_path(project_root: Path, skill_dir: Path, raw: str) -> Path:
    normalized = raw.replace("{{project_root}}", str(project_root)).replace("{{skill_dir}}", str(skill_dir))
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (skill_dir / normalized).resolve()


def _candidate_source_paths(project_root: Path, spec: SkillSpec, limit: int = 8) -> list[Path]:
    skill_dir = project_root / "skills" / Path(spec.path).parent
    candidates: list[Path] = []
    for raw in spec.checks:
        path = _resolve_spec_path(project_root, skill_dir, raw)
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix.lower() in CODE_EXAMPLE_EXTENSIONS:
                    candidates.append(child)
                    if len(candidates) >= limit:
                        break
        if len(candidates) >= limit:
            break
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        try:
            relative = path.resolve().relative_to(project_root)
        except ValueError:
            continue
        if path in seen or "skills" in {part.lower() for part in relative.parts}:
            continue
        seen.add(path)
        unique.append(path)
    return unique[:limit]


def _interesting_code_window(lines: list[str], *, max_lines: int = 14) -> list[str]:
    start = 0
    patterns = (
        re.compile(r"^\s*(async\s+def|def|class)\s+\w+"),
        re.compile(r"^\s*export\s+(default\s+)?(async\s+)?function\s+\w+"),
        re.compile(r"^\s*(public|private|protected)?\s*(async\s+)?function\s+\w+"),
        re.compile(r"^\s*(const|let|var)\s+\w+\s*="),
    )
    for index, line in enumerate(lines):
        if any(pattern.search(line) for pattern in patterns):
            start = index
            break
    window = lines[start : start + max_lines]
    while window and not window[0].strip():
        window.pop(0)
    while window and not window[-1].strip():
        window.pop()
    return window


def _extract_code_examples(project_root: Path, spec: SkillSpec, *, limit: int = 2) -> list[tuple[str, str]]:
    examples: list[tuple[str, str]] = []
    for path in _candidate_source_paths(project_root, spec):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        window = _interesting_code_window(lines)
        if not window:
            continue
        relative = path.relative_to(project_root).as_posix()
        language = CODE_EXAMPLE_EXTENSIONS.get(path.suffix.lower(), "")
        snippet = "\n".join(window)
        examples.append((f"{relative} ({language})" if language else relative, snippet))
        if len(examples) >= limit:
            break
    return examples


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


def _architecture_domain_map(context: RequirementsContext, project_root: Path) -> dict[str, ArchitectureDomain]:
    blueprint = build_architecture_blueprint(project_root, context)
    domain_map: dict[str, ArchitectureDomain] = {}
    for domain in blueprint.domains:
        domain_map[domain.name] = domain
        if domain.recommended_skill_path:
            normalized = domain.recommended_skill_path.removeprefix("skills/").removesuffix("/SKILL.md")
            domain_map.setdefault(normalized, domain)
    return domain_map


def _materialization_plan_map(architecture: ArchitectureBlueprint) -> dict[str, SkillMaterializationPlan]:
    return {item.domain: item for item in architecture.materialization_plan}


def _dependency_ecosystems_for_spec(spec: SkillSpec) -> set[str]:
    """Map a skill domain to dependency ecosystems likely to affect that domain."""
    domain_text = f"{spec.domain} {spec.sub_domain}".lower()
    if "frontend" in domain_text or "component" in domain_text or "route" in domain_text:
        return {"npm"}
    if "backend" in domain_text or "api" in domain_text or "data" in domain_text or "service" in domain_text:
        return {"pip", "go", "cargo", "npm"}
    return {"pip", "npm", "go", "cargo"}


def _with_dependency_patterns(spec: SkillSpec, signals: list[str]) -> SkillSpec:
    """Append dependency risk bullets to a generated skill when manifests expose risks."""
    if not signals:
        return spec
    return SkillSpec(
        path=spec.path,
        name=spec.name,
        domain=spec.domain,
        sub_domain=spec.sub_domain,
        overview=spec.overview,
        checks=spec.checks,
        patterns=[*spec.patterns, ("Dependency signals", signals)],
        how_to=spec.how_to,
        references=spec.references,
        anti_patterns=spec.anti_patterns,
        code_examples=spec.code_examples,
        score=spec.score,
    )


def _anti_pattern_title(text: str) -> str:
    cleaned = text.replace("Don't ", "").replace("Do not ", "").strip(" .")
    return cleaned.split("—", 1)[0].strip().capitalize() or "Avoid brittle implementation"


def _invert_pattern(pattern: str) -> str | None:
    lower = pattern.lower()
    if "validate" in lower and ("api" in lower or "boundary" in lower):
        return "Don't validate only at the DB layer — errors surface too late and API clients receive inconsistent responses"
    if "authservice" in lower or ("shared" in lower and "auth" in lower):
        return "Don't implement custom auth logic inline — bypasses shared audit logging and permission checks"
    if "service" in lower and ("route" in lower or "handler" in lower):
        return "Don't bury business logic in route handlers — it becomes hard to test and reuse"
    if "test" in lower or "verify" in lower:
        return "Don't skip the local verification path — regressions survive until CI or production"
    if "prefer" in lower:
        return f"Don't ignore the preferred pattern — {pattern.strip()}"
    if "always" in lower:
        return f"Don't bypass this rule — {pattern.strip()}"
    if "use " in lower:
        return f"Don't invent a parallel approach — {pattern.strip()}"
    return None


def _anti_patterns_for_spec(spec: SkillSpec) -> list[str]:
    inverted: list[str] = []
    for _title, bullets in spec.patterns:
        for bullet in bullets:
            anti = _invert_pattern(bullet)
            if anti and anti not in inverted:
                inverted.append(anti)
            if len(inverted) >= 5:
                break
        if len(inverted) >= 5:
            break
    if len(inverted) >= 3:
        return inverted[:5]
    domain_text = f"{spec.domain} {spec.sub_domain} {spec.name}".lower()
    for key, values in ANTI_PATTERN_TEMPLATES.items():
        if key in domain_text:
            return values[:5]
    return [
        "Don't introduce a second pattern for the same workflow — duplicated conventions make agent edits unreliable",
        "Don't remove nearby verification steps — future agents need a fast way to prove behaviour still works",
        "Don't leave file references vague — agents waste time searching and may edit the wrong boundary",
    ]


def _extract_code_example(file_path: str | Path, max_lines: int = 20) -> str | None:
    try:
        with Path(file_path).open(encoding="utf-8") as handle:
            lines = handle.readlines()
        start = 0
        for index, line in enumerate(lines[:10]):
            stripped = line.strip()
            if stripped and not stripped.startswith(("#!", "/*", "*", "//", '"""', "'''")):
                start = index
                break
        snippet = "".join(lines[start : start + max_lines])
        return snippet.strip() or None
    except (OSError, UnicodeDecodeError):
        return None


def _language_for_path(path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "")


def _code_examples_for_spec(spec: SkillSpec, project_root: Path) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []
    candidates: list[Path] = []
    for raw in [*spec.checks, *spec.references]:
        clean = raw.strip().strip("`").removeprefix("./")
        if not clean or clean.endswith("SKILL.md") or clean.startswith("../"):
            continue
        path = (project_root / clean).resolve()
        if path.is_file() and path.suffix.lower() in LANGUAGE_BY_SUFFIX:
            candidates.append(path)
    for path in list(dict.fromkeys(candidates))[:2]:
        snippet = _extract_code_example(path)
        if not snippet:
            continue
        try:
            relative = path.relative_to(project_root).as_posix()
        except ValueError:
            relative = path.name
        examples.append(
            {
                "filename": relative,
                "description": "Representative implementation pattern from this domain",
                "language": _language_for_path(path),
                "snippet": snippet,
            }
        )
    return examples


def _dynamic_parent_specs(
    context: RequirementsContext,
    project_root: Path,
    architecture: ArchitectureBlueprint,
) -> list[SkillSpec]:
    codebase_context = build_codebase_context(project_root, context)
    architecture_domains = _architecture_domain_map(context, project_root)
    plan_map = _materialization_plan_map(architecture)
    parent_nodes = [node for node in codebase_context.domain_graph.nodes if node.parent_domain is None and node.skill_path]
    specs: list[SkillSpec] = []
    for node in parent_nodes:
        architecture = architecture_domains.get(node.name)
        plan = plan_map.get(node.name)
        references = []
        related_domains = list(node.related_domains)
        if plan is not None and plan.cross_links:
            related_domains.extend(
                Path(link).parts[1] if len(Path(link).parts) > 1 else Path(link).stem
                for link in plan.cross_links
                if link.startswith("skills/")
            )
        for related in related_domains:
            related_node = next((item for item in codebase_context.domain_graph.nodes if item.name == related and item.skill_path), None)
            if related_node is not None and related_node.skill_path != node.skill_path:
                references.append(_relative_skill_ref(node.skill_path, related_node.skill_path))
        for child_name in node.child_domains:
            child_node = next((item for item in codebase_context.domain_graph.nodes if item.name == child_name and item.skill_path), None)
            if child_node is not None:
                references.append(_relative_skill_ref(node.skill_path, child_node.skill_path))
        references = list(dict.fromkeys(references))
        overview = architecture.summary if architecture is not None else node.summary
        checks = (
            [f"{{{{project_root}}}}/{item}" for item in architecture.evidence_paths[:4]]
            if architecture is not None and architecture.evidence_paths
            else [f"{{{{project_root}}}}/{Path(item).parts[0]}/" if "/" in item else f"{{{{project_root}}}}/{item}" for item in node.key_files[:3]]
        ) or ["{{project_root}}/"]
        patterns = [
            ("Inferred domain patterns", node.key_patterns or ["Use the inferred project structure before introducing a new top-level convention."]),
            ("Dynamic topology", ["This parent skill was inferred from the current repo and may expand or contract as the codebase evolves."]),
        ]
        if architecture is not None and architecture.responsibilities:
            patterns.insert(0, ("Architecture responsibilities", architecture.responsibilities[:4]))
        if architecture is not None and architecture.evidence_paths:
            patterns.append(("Architecture evidence", [f"Evidence: `{item}`" for item in architecture.evidence_paths[:5]]))
        how_to = [
            "Start from the nearest evidence file in this inferred domain.",
            "Reuse the current structure before creating a new sibling domain or folder.",
            "Refresh this parent skill when the planner says the domain topology has changed.",
        ]
        if architecture is not None:
            how_to = [
                "Start from the architecture evidence paths before broadening the scope of the change.",
                "Use the listed responsibilities to keep changes inside the right domain boundary.",
                "Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.",
            ]
        if plan is not None:
            how_to.append(f"Honor the current materialization decision for this domain: `{plan.decision}`.")
        specs.append(
            SkillSpec(
                path=node.skill_path.removeprefix("skills/"),
                name=_slug_name(node.name),
                domain=node.name,
                sub_domain="platform",
                overview=overview,
                checks=checks,
                patterns=patterns,
                how_to=how_to,
                references=references,
            )
        )
    return specs


def _dynamic_child_specs(
    context: RequirementsContext,
    project_root: Path,
    architecture: ArchitectureBlueprint,
) -> list[SkillSpec]:
    codebase_context = build_codebase_context(project_root, context)
    nodes_by_name = {node.name: node for node in codebase_context.domain_graph.nodes}
    plan_map = _materialization_plan_map(architecture)
    specs: list[SkillSpec] = []
    for node in codebase_context.domain_graph.nodes:
        if node.parent_domain is None or not node.skill_path:
            continue
        parent_plan = plan_map.get(node.parent_domain)
        if parent_plan is not None and parent_plan.decision == "merge":
            continue
        parent_node = nodes_by_name.get(node.parent_domain)
        references: list[str] = []
        if parent_node is not None and parent_node.skill_path:
            references.append(_relative_skill_ref(node.skill_path, parent_node.skill_path))
        for related_name in node.related_domains:
            related_node = nodes_by_name.get(related_name)
            if related_node is not None and related_node.skill_path and related_node.skill_path != node.skill_path:
                references.append(_relative_skill_ref(node.skill_path, related_node.skill_path))
        checks = [f"{{{{project_root}}}}/{item}" for item in node.key_files[:4]] or ["{{project_root}}/"]
        patterns = [
            ("Inferred child domain patterns", node.key_patterns or ["Use the nearest existing implementation surface before creating a new sub-skill boundary."]),
        ]
        how_to = [
            "Start from the nearest evidence file in this child domain.",
            "Keep the change aligned with the parent domain contract before widening the boundary.",
            "Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.",
        ]
        specs.append(
            SkillSpec(
                path=node.skill_path.removeprefix("skills/"),
                name=_slug_name(node.name),
                domain=node.parent_domain or node.name,
                sub_domain=node.name,
                overview=node.summary,
                checks=checks,
                patterns=patterns,
                how_to=how_to,
                references=list(dict.fromkeys(references)),
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


def build_skill_specs(
    context: RequirementsContext,
    output_dir: Path,
    architecture: ArchitectureBlueprint | None = None,
) -> list[SkillSpec]:
    project_root = output_dir.parent
    architecture = architecture or build_architecture_blueprint(project_root, context)
    plan_map = _materialization_plan_map(architecture)
    merged_domains = {domain for domain, plan in plan_map.items() if plan.decision == "merge"}
    specs = _dynamic_parent_specs(context, project_root, architecture)
    specs.extend(_dynamic_child_specs(context, project_root, architecture))
    legacy_children = _legacy_child_specs(context, project_root)
    for spec in legacy_children:
        if spec.domain in merged_domains and spec.sub_domain != "platform":
            continue
        specs.append(spec)
    dependency_cache: dict[frozenset[str], list[str]] = {}
    specs_with_dependencies: list[SkillSpec] = []
    for spec in specs:
        ecosystems = frozenset(_dependency_ecosystems_for_spec(spec))
        if ecosystems not in dependency_cache:
            dependency_cache[ecosystems] = dependency_skill_signals(project_root, set(ecosystems))
        specs_with_dependencies.append(_with_dependency_patterns(spec, dependency_cache[ecosystems]))
    specs = specs_with_dependencies
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
    anti_patterns = _anti_patterns_for_spec(spec)
    code_examples = spec.code_examples
    pattern_sections = []
    for title, bullets in spec.patterns:
        block = [f"### {title}"]
        block.extend(f"- {item}" for item in bullets)
        pattern_sections.append("\n".join(block))
    example_sections = []
    for title, snippet in code_examples:
        language = ""
        match = re.search(r"\(([^)]+)\)$", title)
        if match:
            language = match.group(1)
        example_sections.extend(
            [
                f"### {title}",
                f"```{language}",
                snippet,
                "```",
                "",
            ]
        )

    body_sections = [
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
        "## Anti-patterns",
        *[f"- **{_anti_pattern_title(item)}**: {item}" for item in anti_patterns[:5]],
        "",
        "## How-To",
        *[f"{index}. {step}" for index, step in enumerate(spec.how_to, start=1)],
        "",
        *(["## Code Examples", "", *example_sections] if example_sections else []),
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
    score = spec.score or _compute_richness_score("\n".join(body_sections), spec)
    sections = [
        "---",
        f"name: {spec.name}",
        "version: 0.6.0",
        f"domain: {spec.domain}",
        f"sub_domain: {spec.sub_domain}",
        f"last_updated: {TODAY}",
        "triggered_by: requirements_pipeline",
        f"source_hash: {source_hash}",
        f"richness_score: {score.get('total', 0)}",
        "score:",
        f"  total: {score.get('total', 0)}",
        f"  groundedness: {score.get('groundedness', 0)}",
        f"  coverage: {score.get('coverage', 0)}",
        f"  freshness: {score.get('freshness', 0)}",
        f"  structure: {score.get('structure', 0)}",
        "references:",
        *[f"  - {item}" for item in spec.references],
        "status: active",
        "---",
        "",
        *body_sections,
    ]
    return "\n".join(sections)


def _should_render_natively(spec: SkillSpec) -> bool:
    if spec.path.count("/") >= 2:
        return True
    curated_top_level_domains = {"requirements", "backend", "frontend", "roadmap", "platform"}
    return spec.domain not in curated_top_level_domains


def render_skill(spec: SkillSpec, source_hash: str, project_root: Path | str = ".") -> str:
    root = Path(project_root).resolve()
    code_examples = spec.code_examples or _extract_code_examples(root, spec)
    spec = SkillSpec(
        path=spec.path,
        name=spec.name,
        domain=spec.domain,
        sub_domain=spec.sub_domain,
        overview=spec.overview,
        checks=spec.checks,
        patterns=spec.patterns,
        how_to=spec.how_to,
        references=spec.references,
        anti_patterns=_anti_patterns_for_spec(spec),
        code_examples=code_examples,
        score=spec.score,
    )
    if _should_render_natively(spec):
        return _render_skill_native(spec, source_hash)
    rendered = run_deep_text(
        "skill guidance synthesis",
        (
            "Write a markdown SKILL.md file with YAML frontmatter for Skilgen. "
            "Use the provided skill spec to generate higher-level reusable guidance while preserving references and "
            "traceability. Optimize for coding agents that need actionable, reusable execution guidance rather than "
            "generic prose. Preserve the intent of the domain, keep the path references stable, and make the How-To "
            "section operational enough that an agent can decide what to inspect, change, and validate next. "
            "Always include Anti-patterns, preserve the score frontmatter field, and include Code Examples only when real snippets are present.\n\n"
            f"Skill spec JSON:\n{spec}\nSource hash: {source_hash}"
        ),
        lambda: _render_skill_native(spec, source_hash),
        project_root=root,
    )
    if "## Anti-patterns" not in rendered or "score:" not in rendered:
        return _render_skill_native(spec, source_hash)
    return rendered


def _frontmatter_value(path: Path, field: str) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    in_frontmatter = False
    saw_fence = False
    prefix = f"{field}:"
    for line in lines[:40]:
        stripped = line.strip()
        if stripped.startswith("```") and not in_frontmatter and not saw_fence:
            saw_fence = True
            continue
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if in_frontmatter and stripped.startswith(prefix):
            return stripped[len(prefix):].strip().strip("'\"")
    return None


def _looks_generated_skill(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    markers = (
        "triggered_by: requirements_pipeline",
        "Generated from requirements source hash",
        "Generated by Skilgen",
        "This parent skill was inferred from the current repo",
        "```markdown\n---",
    )
    return any(marker in text for marker in markers)


def _prune_stale_generated_paths(
    output_dir: Path,
    planned_relative_paths: set[str],
    selected_domains: set[str],
    *,
    active_domains: set[str] | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    managed_prefixes = {
        Path(relative).parts[0]
        for relative in planned_relative_paths
        if relative not in {"MANIFEST.md", "GRAPH.md"} and Path(relative).parts
    }
    removed: list[Path] = []
    for pattern in ("SKILL.md", "SUMMARY.md"):
        for path in output_dir.rglob(pattern):
            relative = path.relative_to(output_dir).as_posix()
            if relative in planned_relative_paths:
                continue
            if not selected_domains:
                path.unlink()
                removed.append(path)
                continue
            prefix = Path(relative).parts[0] if Path(relative).parts else ""
            declared_domain = _frontmatter_value(path, "domain")
            triggered_by = _frontmatter_value(path, "triggered_by")
            generated_by_skilgen = triggered_by == "requirements_pipeline" or _looks_generated_skill(path)
            if prefix in managed_prefixes or (declared_domain in selected_domains if declared_domain else False):
                path.unlink()
                removed.append(path)
                continue
            if (
                generated_by_skilgen
                and active_domains
                and declared_domain
                and declared_domain not in active_domains
            ):
                path.unlink()
                removed.append(path)
    if removed:
        _emit_progress(progress_callback, f"Removed {len(removed)} stale generated skill files so the skill tree reflects the current repo shape.")
    return removed


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
        lines.append(f"| `{spec.path}` | `0.6.0` | `{spec.domain}` | `{TODAY}` | `requirements_pipeline` | `{source_hash}` |")
    lines.append("")
    return "\n".join(lines)


def render_graph(specs: list[SkillSpec], architecture: ArchitectureBlueprint | None = None) -> str:
    lines = [
        "# Skill Graph",
        "",
        "This file summarizes the generated skill tree and cross references.",
        "",
    ]
    if architecture is not None:
        skill_paths = {spec.path for spec in specs}
        normalized_skill_paths = {f"skills/{spec.path}" for spec in specs}
        lines.extend(
            [
                "## Architecture Blueprint",
                f"- Headline: {architecture.headline}",
                f"- Summary: {architecture.system_summary}",
            ]
        )
        if architecture.hotspots:
            lines.append("- Hotspots:")
            lines.extend(f"  - {item}" for item in architecture.hotspots[:5])
        if architecture.materialization_plan:
            lines.extend(["", "## Materialization Decisions"])
            for item in architecture.materialization_plan:
                lines.append(f"### {item.domain}")
                lines.append(f"- decision: `{item.decision}`")
                lines.append(f"- parent: `{item.parent_skill_path}`")
                if item.child_skill_paths:
                    lines.append("- child skills:")
                    for child in item.child_skill_paths[:8]:
                        marker = "materialized" if child in normalized_skill_paths or child.removeprefix("skills/") in skill_paths else "planned"
                        lines.append(f"  - `{child}` ({marker})")
                if item.cross_links:
                    lines.append("- cross-links:")
                    for link in item.cross_links[:8]:
                        lines.append(f"  - `{link}`")
                lines.append(f"- rationale: {item.rationale}")
        lines.append("")
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
    architecture = build_architecture_blueprint(output_dir.parent, context)
    specs = _select_specs(build_skill_specs(context, output_dir, architecture), selected)
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


def write_skills(
    context: RequirementsContext,
    output_dir: Path,
    selected_domains: set[str] | None = None,
    *,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    selected = selected_domains or set()
    _emit_progress(progress_callback, "Preparing the skill architecture so parent and child skill boundaries stay grounded in repo evidence.")
    signals = analyze_codebase(output_dir.parent)
    architecture = build_architecture_blueprint(output_dir.parent, context)
    specs = _select_specs(build_skill_specs(context, output_dir, architecture), selected)
    codebase_context = build_codebase_context(output_dir.parent, context)
    architecture_domains = {domain.name: domain for domain in architecture.domains}
    planned_relative_paths = {spec.path for spec in specs}
    planned_relative_paths.update({"MANIFEST.md", "GRAPH.md"})
    for node in codebase_context.domain_graph.nodes:
        if node.parent_domain is not None or not node.skill_path:
            continue
        if selected and node.name not in selected:
            continue
        summary_relative = (Path(node.skill_path.removeprefix("skills/")).parent / "SUMMARY.md").as_posix()
        planned_relative_paths.add(summary_relative)
    if "frontend" in {node.name for node in codebase_context.domain_graph.nodes if node.parent_domain is None} and (
        not selected or "frontend" in selected
    ):
        planned_relative_paths.add("frontend/components/SUMMARY.md")
    if "backend" in {node.name for node in codebase_context.domain_graph.nodes if node.parent_domain is None} and signals.services and (
        not selected or "backend" in selected
    ):
        planned_relative_paths.add("backend/services/SUMMARY.md")
    active_domains = {node.name for node in codebase_context.domain_graph.nodes}
    _prune_stale_generated_paths(
        output_dir,
        planned_relative_paths,
        selected,
        active_domains=active_domains,
        progress_callback=progress_callback,
    )
    written: list[Path] = []
    _emit_progress(progress_callback, f"Writing {len(specs)} skill files into the repo-local skill tree.")
    for spec in specs:
        target = output_dir / spec.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_skill(spec, context.source_hash, output_dir.parent), encoding="utf-8")
        written.append(target)

    _emit_progress(progress_callback, "Writing skills/MANIFEST.md and skills/GRAPH.md so agents can traverse the generated skill tree.")
    manifest = output_dir / "MANIFEST.md"
    manifest.write_text(render_manifest(specs, context.source_hash), encoding="utf-8")
    written.append(manifest)

    graph = output_dir / "GRAPH.md"
    graph.write_text(render_graph(specs, architecture), encoding="utf-8")
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
    _emit_progress(progress_callback, "Writing top-level domain summaries so each skill family explains its evidence and responsibilities.")
    for node in codebase_context.domain_graph.nodes:
        if node.parent_domain is not None or not node.skill_path:
            continue
        if selected and node.name not in selected:
            continue
        summary_path = output_dir / Path(node.skill_path.removeprefix("skills/")).parent / "SUMMARY.md"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        architecture_domain = architecture_domains.get(node.name)
        sections = summary_map.get(node.name, [("Key Files", node.key_files)])
        if architecture_domain is not None:
            sections = [
                ("Architecture responsibilities", architecture_domain.responsibilities),
                ("Evidence paths", [f"`{item}`" for item in architecture_domain.evidence_paths]),
                *sections,
            ]
        summary_path.write_text(
            render_domain_summary(f"{node.name.replace('-', ' ').title()} Summary", sections),
            encoding="utf-8",
        )
        written.append(summary_path)

    if "frontend" in {node.name for node in codebase_context.domain_graph.nodes if node.parent_domain is None} and (
        not selected or "frontend" in selected
    ):
        _emit_progress(progress_callback, "Writing frontend component summaries for reusable interface patterns.")
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
        _emit_progress(progress_callback, "Writing backend service summaries for deeper operational and implementation guidance.")
        service_summary = output_dir / "backend" / "services" / "SUMMARY.md"
        service_summary.parent.mkdir(parents=True, exist_ok=True)
        service_summary.write_text(
            render_domain_summary("Backend Services Summary", [("Detected Service Files", signals.services)]),
            encoding="utf-8",
        )
        written.append(service_summary)

    return written
