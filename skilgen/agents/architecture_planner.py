from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from skilgen.agents.domain_graph_planner import build_domain_graph
from skilgen.agents.evidence_graph import build_evidence_graph
from skilgen.deep_agents_core import run_deep_json
from skilgen.core.models import (
    ArchitectureBlueprint,
    ArchitectureDomain,
    DomainGraph,
    DomainGraphNode,
    EvidenceGraph,
    RequirementsContext,
    SkillMaterializationPlan,
)


def _native_architecture(project_root: Path, domain_graph: DomainGraph, evidence_graph: EvidenceGraph) -> ArchitectureBlueprint:
    nodes_by_name: dict[str, DomainGraphNode] = {node.name: node for node in domain_graph.nodes}
    top_level = [node for node in domain_graph.nodes if node.parent_domain is None]
    domains: list[ArchitectureDomain] = []
    for node in top_level:
        child_names = node.child_domains[:4]
        responsibilities = [node.summary]
        if child_names:
            responsibilities.append(f"Coordinates subdomains: {', '.join(child_names)}.")
        if node.key_patterns:
            responsibilities.extend(node.key_patterns[:2])
        evidence_paths = list(dict.fromkeys(node.key_files[:5]))
        domains.append(
            ArchitectureDomain(
                name=node.name,
                summary=node.summary,
                confidence=node.confidence,
                responsibilities=responsibilities[:4],
                evidence_paths=evidence_paths,
                related_domains=node.related_domains,
                recommended_skill_path=node.skill_path,
            )
        )

    hotspots: list[str] = []
    low_confidence = sorted((node for node in domain_graph.nodes if node.confidence < 0.7), key=lambda item: item.confidence)
    for node in low_confidence[:4]:
        hotspots.append(f"{node.name} has low confidence ({node.confidence:.2f}) and may need stronger evidence or clearer skill boundaries.")
    if evidence_graph.dominant_languages:
        hotspots.append(f"Dominant languages: {', '.join(evidence_graph.dominant_languages)}.")
    if not evidence_graph.items:
        hotspots.append("No rich evidence items were extracted; architecture confidence will be limited.")

    recommendations = [
        "Use architecture domains as the parents for the skill tree, and keep sub-skills close to strong evidence files.",
        "Regenerate skills when dominant domain evidence or domain boundaries change materially.",
        *evidence_graph.recommendations[:2],
    ]
    materialization_plan: list[SkillMaterializationPlan] = []
    for node in top_level:
        child_skill_paths = [
            child.skill_path
            for child in domain_graph.nodes
            if child.parent_domain == node.name and child.skill_path
        ]
        cross_links = [
            nodes_by_name[related].skill_path
            for related in node.related_domains
            if related in nodes_by_name and nodes_by_name[related].skill_path
        ]
        if len(child_skill_paths) >= 2:
            decision = "split"
            rationale = "Multiple concrete child domains exist, so a parent skill plus child skills will be easier for agents to navigate."
        elif node.confidence < 0.65 and len(node.key_files) <= 1:
            decision = "merge"
            rationale = "The domain has weak evidence and low confidence, so it should likely merge into a related higher-confidence domain."
        else:
            decision = "keep"
            rationale = "The domain has enough direct evidence to remain a first-class skill boundary."
        materialization_plan.append(
            SkillMaterializationPlan(
                domain=node.name,
                parent_skill_path=node.skill_path,
                child_skill_paths=[path for path in child_skill_paths if path][:6],
                cross_links=[path for path in cross_links if path][:6],
                decision=decision,
                rationale=rationale,
            )
        )
    headline = "Evidence-backed architecture blueprint for the codebase"
    system_summary = (
        f"Skilgen identified {len(domains)} top-level architecture domains from {len(evidence_graph.items)} evidence items "
        f"and {len(domain_graph.nodes)} domain graph nodes. "
        f"Parser backends in use: {', '.join(sorted({payload.get('backend', 'unknown') for payload in evidence_graph.parser_summary.values()})) or 'none'}. "
        f"Source comprehension currently tracks {len(evidence_graph.symbol_graph)} symbol-bearing files, "
        f"{len(evidence_graph.call_graph)} call-bearing files, and {len(evidence_graph.test_mapping)} mapped tests."
    )
    return ArchitectureBlueprint(
        headline=headline,
        system_summary=system_summary,
        domains=domains,
        hotspots=hotspots[:5],
        recommendations=recommendations[:5],
        materialization_plan=materialization_plan,
    )


def build_architecture_blueprint(project_root: Path, requirements: RequirementsContext) -> ArchitectureBlueprint:
    root = project_root.resolve()
    evidence_graph = build_evidence_graph(root, requirements)
    domain_graph = build_domain_graph(root, requirements)
    native = _native_architecture(root, domain_graph, evidence_graph)
    payload = run_deep_json(
        "architecture synthesis",
        (
            "Build an evidence-backed architecture blueprint for Skilgen. Return JSON with keys "
            "headline, system_summary, domains, hotspots, recommendations, materialization_plan. Each domain must contain: "
            "name, summary, confidence, responsibilities, evidence_paths, related_domains, recommended_skill_path. "
            "Each materialization plan item must contain: domain, parent_skill_path, child_skill_paths, cross_links, decision, rationale. "
            "Use the evidence graph and domain graph to define the best architecture boundaries for skills. "
            "Prefer domain names and responsibilities that would help a coding agent understand the system quickly.\n\n"
            f"Project root: {root}\n"
            f"Requirements summary: {requirements.summary}\n"
            f"Evidence graph JSON: {asdict(evidence_graph)}\n"
            f"Domain graph JSON: {asdict(domain_graph)}\n"
            f"Native architecture JSON: {asdict(native)}\n"
        ),
        lambda: {
            "headline": native.headline,
            "system_summary": native.system_summary,
            "domains": [domain.__dict__ for domain in native.domains],
            "hotspots": native.hotspots,
            "recommendations": native.recommendations,
            "materialization_plan": [item.__dict__ for item in native.materialization_plan],
        },
        project_root=root,
    )
    domains = [
        ArchitectureDomain(
            name=str(item.get("name", "domain")),
            summary=str(item.get("summary", "")),
            confidence=float(item.get("confidence", 0.5)),
            responsibilities=[str(entry) for entry in item.get("responsibilities", [])],
            evidence_paths=[str(entry) for entry in item.get("evidence_paths", [])],
            related_domains=[str(entry) for entry in item.get("related_domains", [])],
            recommended_skill_path=str(item.get("recommended_skill_path")) if item.get("recommended_skill_path") else None,
        )
        for item in payload.get("domains", [])
    ]
    if not domains:
        domains = native.domains
    materialization_plan = [
        SkillMaterializationPlan(
            domain=str(item.get("domain", "domain")),
            parent_skill_path=str(item.get("parent_skill_path")) if item.get("parent_skill_path") else None,
            child_skill_paths=[str(entry) for entry in item.get("child_skill_paths", [])],
            cross_links=[str(entry) for entry in item.get("cross_links", [])],
            decision=str(item.get("decision", "keep")),
            rationale=str(item.get("rationale", "")),
        )
        for item in payload.get("materialization_plan", [])
    ] or native.materialization_plan
    return ArchitectureBlueprint(
        headline=str(payload.get("headline", native.headline)),
        system_summary=str(payload.get("system_summary", native.system_summary)),
        domains=domains,
        hotspots=[str(item) for item in payload.get("hotspots", [])] or native.hotspots,
        recommendations=[str(item) for item in payload.get("recommendations", [])] or native.recommendations,
        materialization_plan=materialization_plan,
    )
