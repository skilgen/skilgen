from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from skilgen.agents.domain_graph_planner import build_domain_graph
from skilgen.agents.evidence_graph import build_evidence_graph
from skilgen.core.config import load_config
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


def _redact_snippet_lines(lines: list[str], *, limit: int) -> list[str]:
    redacted: list[str] = []
    for line in lines[:limit]:
        updated = line
        updated = updated.replace("api_key", "[redacted]")
        updated = updated.replace("apikey", "[redacted]")
        updated = updated.replace("password", "[redacted]")
        updated = updated.replace("secret", "[redacted]")
        updated = updated.replace("token", "[redacted]")
        redacted.append(updated[:180])
    return redacted


def _evidence_graph_payload(project_root: Path, evidence_graph: EvidenceGraph) -> dict[str, object]:
    config = load_config(project_root)
    mode = (config.model_redaction_mode or "balanced").strip().lower()
    if mode == "off":
        return asdict(evidence_graph)

    items: list[dict[str, object]] = []
    for item in evidence_graph.items:
        payload = {
            "path": item.path,
            "kind": item.kind,
            "language": item.language,
            "tags": item.tags,
            "related_imports": item.related_imports[:8],
        }
        if mode == "strict":
            payload["snippet"] = []
        elif item.kind == "config":
            payload["snippet"] = []
        else:
            payload["snippet"] = _redact_snippet_lines(item.snippet, limit=4)
        items.append(payload)

    parser_summary = {
        path: {
            "language": payload.get("language"),
            "backend": payload.get("backend"),
            "symbol_count": payload.get("symbol_count"),
            "call_count": payload.get("call_count"),
            "import_count": payload.get("import_count"),
        }
        for path, payload in evidence_graph.parser_summary.items()
    }
    sanitized = {
        "language_inventory": evidence_graph.language_inventory,
        "dominant_languages": evidence_graph.dominant_languages,
        "import_graph": evidence_graph.import_graph,
        "items": items,
        "recommendations": evidence_graph.recommendations,
        "parser_summary": parser_summary,
        "symbol_graph": evidence_graph.symbol_graph,
        "call_graph": evidence_graph.call_graph,
        "config_runtime_graph": evidence_graph.config_runtime_graph,
        "test_mapping": evidence_graph.test_mapping,
        "workspace_graph": asdict(evidence_graph.workspace_graph),
        "symbol_relationships": [asdict(item) for item in evidence_graph.symbol_relationships],
        "runtime_signals": asdict(evidence_graph.runtime_signals),
        "dependency_risk_graph": asdict(evidence_graph.dependency_risk_graph),
        "redaction_mode": mode,
    }
    return sanitized


def _sanitize_architecture_payload(
    project_root: Path,
    domain_graph: DomainGraph,
    native: ArchitectureBlueprint,
    payload: dict[str, object],
) -> ArchitectureBlueprint:
    top_level_nodes = {node.name: node for node in domain_graph.nodes if node.parent_domain is None}
    all_nodes = {node.name: node for node in domain_graph.nodes}
    native_domains = {domain.name: domain for domain in native.domains}
    native_materialization = {item.domain: item for item in native.materialization_plan}

    raw_domains = {
        str(item.get("name", "")).strip(): item
        for item in payload.get("domains", [])
        if isinstance(item, dict) and str(item.get("name", "")).strip() in native_domains
    }
    domains: list[ArchitectureDomain] = []
    for name, native_domain in native_domains.items():
        node = top_level_nodes.get(name)
        raw = raw_domains.get(name, {})
        responsibilities = [str(entry).strip() for entry in raw.get("responsibilities", []) if str(entry).strip()]
        evidence_paths = [
            str(entry).strip()
            for entry in raw.get("evidence_paths", [])
            if str(entry).strip() and (project_root / str(entry).strip()).exists()
        ]
        related_domains = [
            str(entry).strip()
            for entry in raw.get("related_domains", [])
            if str(entry).strip() in all_nodes
        ]
        recommended_skill_path = str(raw.get("recommended_skill_path")).strip() if raw.get("recommended_skill_path") else None
        expected_skill_path = node.skill_path if node is not None else native_domain.recommended_skill_path
        domains.append(
            ArchitectureDomain(
                name=name,
                summary=str(raw.get("summary", native_domain.summary)).strip() or native_domain.summary,
                confidence=float(raw.get("confidence", native_domain.confidence)),
                responsibilities=responsibilities or native_domain.responsibilities,
                evidence_paths=evidence_paths or native_domain.evidence_paths,
                related_domains=related_domains or native_domain.related_domains,
                recommended_skill_path=expected_skill_path if recommended_skill_path != expected_skill_path else recommended_skill_path,
            )
        )

    raw_materialization = {
        str(item.get("domain", "")).strip(): item
        for item in payload.get("materialization_plan", [])
        if isinstance(item, dict) and str(item.get("domain", "")).strip() in native_materialization
    }
    materialization_plan: list[SkillMaterializationPlan] = []
    for domain, native_item in native_materialization.items():
        raw = raw_materialization.get(domain, {})
        valid_children = set(native_item.child_skill_paths)
        valid_cross_links = set(native_item.cross_links)
        child_skill_paths = [
            str(entry).strip()
            for entry in raw.get("child_skill_paths", [])
            if str(entry).strip() in valid_children
        ]
        cross_links = [
            str(entry).strip()
            for entry in raw.get("cross_links", [])
            if str(entry).strip() in valid_cross_links
        ]
        decision = str(raw.get("decision", native_item.decision)).strip().lower()
        if decision not in {"keep", "split", "merge"}:
            decision = native_item.decision
        materialization_plan.append(
            SkillMaterializationPlan(
                domain=domain,
                parent_skill_path=native_item.parent_skill_path,
                child_skill_paths=child_skill_paths or native_item.child_skill_paths,
                cross_links=cross_links or native_item.cross_links,
                decision=decision,
                rationale=str(raw.get("rationale", native_item.rationale)).strip() or native_item.rationale,
            )
        )

    headline = str(payload.get("headline", native.headline)).strip() or native.headline
    system_summary = str(payload.get("system_summary", native.system_summary)).strip() or native.system_summary
    hotspots = [str(item).strip() for item in payload.get("hotspots", []) if str(item).strip()] or native.hotspots
    recommendations = [str(item).strip() for item in payload.get("recommendations", []) if str(item).strip()] or native.recommendations
    return ArchitectureBlueprint(
        headline=headline,
        system_summary=system_summary,
        domains=domains or native.domains,
        hotspots=hotspots,
        recommendations=recommendations,
        materialization_plan=materialization_plan or native.materialization_plan,
    )


def _native_architecture(project_root: Path, domain_graph: DomainGraph, evidence_graph: EvidenceGraph) -> ArchitectureBlueprint:
    nodes_by_name: dict[str, DomainGraphNode] = {node.name: node for node in domain_graph.nodes}
    top_level = [node for node in domain_graph.nodes if node.parent_domain is None]
    domains: list[ArchitectureDomain] = []
    for node in top_level:
        child_names = node.child_domains[:4]
        child_nodes = [item for item in domain_graph.nodes if item.parent_domain == node.name]
        responsibilities = [node.summary]
        if child_names:
            responsibilities.append(f"Coordinates subdomains: {', '.join(child_names)}.")
        if node.key_patterns:
            responsibilities.extend(node.key_patterns[:2])
        evidence_pool = list(node.key_files)
        for child in child_nodes:
            evidence_pool.extend(child.key_files[:2])
        evidence_paths = list(dict.fromkeys(path for path in evidence_pool if path))[:6]
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
        child_nodes = [item for item in domain_graph.nodes if item.parent_domain == node.name]
        child_skill_paths = [
            child.skill_path
            for child in child_nodes
            if child.skill_path
        ]
        evidence_paths = list(dict.fromkeys(node.key_files + [path for child in child_nodes for path in child.key_files]))[:6]
        cross_links = [
            nodes_by_name[related].skill_path
            for related in node.related_domains
            if related in nodes_by_name and nodes_by_name[related].skill_path
        ]
        child_labels = ", ".join(child.name for child in child_nodes[:3]) or "no child domains"
        related_labels = ", ".join(node.related_domains[:3]) or "adjacent domains"
        if len(child_skill_paths) >= 2:
            decision = "split"
            rationale = (
                f"Split because {len(child_skill_paths)} concrete child skill surfaces emerged from {len(evidence_paths)} grounded evidence paths. "
                f"The parent skill can hold shared context while child skills isolate the distinct capability seams around {child_labels}."
            )
        elif node.confidence < 0.65 and len(node.key_files) <= 1:
            decision = "merge"
            rationale = (
                f"Merge because confidence is only {node.confidence:.2f} and the domain has just {len(evidence_paths)} strong evidence paths. "
                f"The nuance is currently weaker than adjacent boundaries around {related_labels}."
            )
        else:
            decision = "keep"
            rationale = (
                f"Keep as a first-class boundary because confidence is {node.confidence:.2f}, "
                f"{len(evidence_paths)} evidence paths cluster around one coherent responsibility set, "
                f"and the boundary is clearer as a single skill than as shallower splits."
            )
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
        f"{len(evidence_graph.call_graph)} call-bearing files, {len(evidence_graph.test_mapping)} mapped tests, "
        f"and {len(evidence_graph.workspace_graph.packages)} workspace packages."
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
            f"Evidence graph JSON: {_evidence_graph_payload(root, evidence_graph)}\n"
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
    return _sanitize_architecture_payload(root, domain_graph, native, payload)
