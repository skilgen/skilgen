from __future__ import annotations

from pathlib import Path

from skilgen.agents.codebase_signals import analyze_codebase
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


def build_domain_graph_native(project_root: Path, requirements: RequirementsContext) -> DomainGraph:
    root = project_root.resolve()
    signals = analyze_codebase(root)
    requirements_path = requirements.requirements_path if requirements.requirements_path.exists() else None
    intent = parse_project_intent_native(root, requirements_path)

    backend_children = ["backend-api", "backend-testing"]
    if signals.backend_routes:
        backend_children.append("backend-routes")
    if signals.services:
        backend_children.append("backend-services")
    if signals.data_models or signals.persistence_layers:
        backend_children.append("backend-data")
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
        [signals.backend_routes, signals.services, signals.data_models, signals.persistence_layers, signals.auth_files]
    )
    if requirements.domains.get("backend") or backend_detected:
        nodes.append(
            _node(
                "backend",
                summary="Server-side delivery domain covering route handlers, services, persistence, and verification of backend changes.",
                confidence=0.88,
                key_files=_top_file(
                    [*signals.backend_routes, *signals.services, *signals.data_models, *signals.auth_files],
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
    if requirements.domains.get("frontend") or frontend_detected:
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

    if signals.design_system_files and not (signals.frontend_routes or signals.components):
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

    if signals.auth_files and not (signals.backend_routes or signals.services):
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

    if signals.background_jobs and not (signals.backend_routes or signals.services):
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

    if (signals.data_models or signals.persistence_layers) and not (signals.backend_routes or signals.services):
        nodes.append(
            _node(
                "data-platform",
                summary="Standalone data platform domain inferred from data models, schemas, or persistence layers without a stronger application-service boundary.",
                confidence=0.8,
                key_files=_top_file([*signals.data_models, *signals.persistence_layers], ["models/", "db/"]),
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
            "Service and use-case guidance for existing orchestration and business logic modules.",
            _top_file(signals.services, ["services/"]),
            ["service boundaries", "orchestration separation", "reusable business logic"],
            "skills/backend/services/SKILL.md",
        ),
        (
            "backend-data",
            "Data models, repositories, and persistence guidance inferred from backend storage layers.",
            _top_file([*signals.data_models, *signals.persistence_layers], ["models/", "db/"]),
            ["data contracts", "repository boundaries", "schema-to-domain alignment"],
            "skills/backend/data/SKILL.md",
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
        if name in backend_children:
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
        if name in frontend_children:
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
