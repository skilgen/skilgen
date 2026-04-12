from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
import re
from pathlib import Path

from skilgen.agents import analyze_codebase, build_agent_decision, build_architecture_blueprint, build_evidence_graph, build_import_graph, fingerprint_project
from skilgen.agents.feature_extractor import extract_features
from skilgen.agents.requirements_parser import parse_project_intent
from skilgen.deep_agents_core import run_deep_text
from skilgen.core.config import render_default_config
from skilgen.core.context import build_codebase_context
from skilgen.enterprise_skills import active_enterprise_skills, active_mcp_connectors, recommend_mcp_connectors
from skilgen.external_skills import active_external_skills, detect_external_skill_sources, external_skill_policy, installed_external_skills, ranked_external_skills
from skilgen.core.models import RequirementsContext


@dataclass(frozen=True)
class ProjectAnalysisBundle:
    fingerprint: object
    signals: object
    import_graph: dict[str, list[str]]
    codebase_context: object
    evidence_graph: object
    architecture: object


def _node_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_")
    return cleaned.lower() or "node"


def _display_domain_name(value: str) -> str:
    mapping = {
        "requirements": "Planning Intelligence",
        "backend": "Service Architecture",
        "frontend": "Experience System",
        "roadmap": "Delivery Phases",
    }
    return mapping.get(value, value.replace("-", " ").replace("_", " ").title())


def _display_skill_name(path_or_name: str) -> str:
    cleaned = path_or_name.strip("/").split("/")[-2] if "/SKILL.md" in path_or_name and "/" in path_or_name else path_or_name
    return _display_domain_name(cleaned)


def _analysis_bundle(context: RequirementsContext, project_root: Path) -> ProjectAnalysisBundle:
    return ProjectAnalysisBundle(
        fingerprint=fingerprint_project(project_root),
        signals=analyze_codebase(project_root),
        import_graph=build_import_graph(project_root),
        codebase_context=build_codebase_context(project_root, context),
        evidence_graph=build_evidence_graph(project_root, context),
        architecture=build_architecture_blueprint(project_root, context),
    )


def render_architecture_graph_mermaid(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    architecture = bundle.architecture
    lines = ["graph TD"]
    for domain in architecture.domains:
        domain_id = _node_id(domain.name)
        lines.append(f'  {domain_id}["{domain.name}"]')
        for related in domain.related_domains[:4]:
            related_id = _node_id(related)
            lines.append(f'  {domain_id} --> {related_id}["{related}"]')
        for evidence_path in domain.evidence_paths[:3]:
            evidence_id = _node_id(f"{domain.name}_{evidence_path}")
            lines.append(f'  {domain_id} -. evidence .-> {evidence_id}["{evidence_path}"]')
    for plan in architecture.materialization_plan[:10]:
        domain_id = _node_id(plan.domain)
        parent_id = _node_id(plan.parent_skill_path)
        lines.append(f'  {domain_id} --> {parent_id}["{plan.parent_skill_path}"]')
        for child in plan.child_skill_paths[:5]:
            child_id = _node_id(child)
            lines.append(f'  {parent_id} --> {child_id}["{child}"]')
        for link in plan.cross_links[:4]:
            link_id = _node_id(link)
            lines.append(f'  {parent_id} -. cross-link .-> {link_id}["{link}"]')
    for path, symbols in list(evidence_graph.symbol_graph.items())[:6]:
        file_id = _node_id(path)
        lines.append(f'  {file_id}["{path}"]')
        for symbol in symbols[:2]:
            symbol_id = _node_id(f"{path}_{symbol}")
            lines.append(f'  {file_id} --> {symbol_id}["{symbol}"]')
    return "\n".join(lines)


def render_architecture_graph_json(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    architecture = bundle.architecture
    return {
        "headline": architecture.headline,
        "system_summary": architecture.system_summary,
        "domains": [domain.__dict__ for domain in architecture.domains],
        "materialization_plan": [item.__dict__ for item in architecture.materialization_plan],
        "parser_summary": evidence_graph.parser_summary,
        "symbol_graph": evidence_graph.symbol_graph,
        "call_graph": evidence_graph.call_graph,
        "config_runtime_graph": evidence_graph.config_runtime_graph,
        "test_mapping": evidence_graph.test_mapping,
    }


def render_architecture_graph_html(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    mermaid = render_architecture_graph_mermaid(context, project_root, bundle)
    architecture = bundle.architecture
    parser_backends = sorted({str(payload.get("backend", "unknown")) for payload in bundle.evidence_graph.parser_summary.values()})
    cards = []
    for domain in architecture.domains[:8]:
        cards.append(
            "\n".join(
                [
                    '<div class="domain-card">',
                    f"<h3>{domain.name}</h3>",
                    f"<p>{domain.summary}</p>",
                    f"<p><strong>Confidence:</strong> {domain.confidence:.2f}</p>",
                    "</div>",
                ]
            )
        )
    plan_rows = []
    for item in architecture.materialization_plan[:10]:
        plan_rows.append(
            "<tr>"
            f"<td>{item.domain}</td>"
            f"<td>{item.decision}</td>"
            f"<td>{item.parent_skill_path}</td>"
            f"<td>{', '.join(item.child_skill_paths[:4]) or '-'}</td>"
            "</tr>"
        )
    return "\n".join(
        [
            "<!doctype html>",
            "<html><head><meta charset='utf-8'><title>Skilgen Architecture Graph</title>",
            "<script type='module'>import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'; mermaid.initialize({ startOnLoad: true, theme: 'neutral' });</script>",
            "<style>body{font-family:ui-sans-serif,system-ui,sans-serif;margin:2rem;line-height:1.5;color:#1f2937;} .domain-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1.5rem 0;} .domain-card{border:1px solid #d1d5db;border-radius:12px;padding:1rem;background:#f9fafb;} .mermaid{margin:2rem 0;} .pill{display:inline-block;border-radius:999px;padding:0.2rem 0.6rem;background:#e5eefc;margin-right:0.5rem;margin-bottom:0.5rem;} table{border-collapse:collapse;width:100%;margin-top:1.5rem;} th,td{border:1px solid #d1d5db;padding:0.75rem;text-align:left;vertical-align:top;} th{background:#f3f4f6;}</style>",
            "</head><body>",
            f"<h1>{architecture.headline}</h1>",
            f"<p>{architecture.system_summary}</p>",
            "<h2>Parser Backends</h2>",
            *(f"<span class='pill'>{backend}</span>" for backend in parser_backends),
            "<div class='domain-grid'>",
            *cards,
            "</div>",
            f"<pre class='mermaid'>{mermaid}</pre>",
            "<h2>Skill Materialization Plan</h2>",
            "<table><thead><tr><th>Domain</th><th>Decision</th><th>Parent Skill</th><th>Child Skills</th></tr></thead><tbody>",
            *plan_rows,
            "</tbody></table>",
            "</body></html>",
        ]
    )


def render_evidence_graph_mermaid(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    lines = ["graph LR", '  repo["Repository Evidence"]']
    for language in evidence_graph.dominant_languages[:5]:
        language_id = _node_id(f"language_{language}")
        lines.append(f'  repo --> {language_id}["{language}"]')
    for item in evidence_graph.items[:10]:
        item_id = _node_id(f"evidence_{item.path}")
        kind_id = _node_id(f"kind_{item.kind}")
        lines.append(f'  repo --> {item_id}["{item.path}"]')
        lines.append(f'  {item_id} --> {kind_id}["{item.kind}"]')
        for tag in item.tags[:3]:
            tag_id = _node_id(f"{item.path}_{tag}")
            lines.append(f'  {item_id} -.-> {tag_id}["{tag}"]')
    return "\n".join(lines)


def render_dependency_graph_mermaid(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    import_graph = bundle.import_graph
    lines = ["graph LR"]
    edge_count = 0
    for source, targets in import_graph.items():
        source_id = _node_id(source)
        lines.append(f'  {source_id}["{source}"]')
        for target in targets[:4]:
            target_id = _node_id(target)
            lines.append(f'  {source_id} --> {target_id}["{target}"]')
            edge_count += 1
            if edge_count >= 24:
                return "\n".join(lines)
    if edge_count == 0:
        lines.append('  idle["No import dependencies detected yet"]')
    return "\n".join(lines)


def render_skill_graph_mermaid(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    architecture = bundle.architecture
    lines = ["graph TD", '  root["Skilgen Skill System"]']
    for plan in architecture.materialization_plan[:12]:
        parent = plan.parent_skill_path or plan.domain
        parent_id = _node_id(parent)
        lines.append(f'  root --> {parent_id}["{parent}"]')
        for child in plan.child_skill_paths[:5]:
            child_id = _node_id(child)
            lines.append(f'  {parent_id} --> {child_id}["{child}"]')
        for link in plan.cross_links[:3]:
            link_id = _node_id(link)
            lines.append(f'  {parent_id} -.-> {link_id}["{link}"]')
    return "\n".join(lines)


def _skilgen_logo_svg() -> str:
    return (
        "<svg class='skilgen-mark' viewBox='0 0 760 360' fill='none' xmlns='http://www.w3.org/2000/svg' aria-label='Skilgen logo'>"
        "<defs><filter id='skilgenGlow' x='-20%' y='-20%' width='140%' height='140%'><feDropShadow dx='0' dy='10' stdDeviation='10' flood-color='rgba(0,0,0,0.38)'/></filter></defs>"
        "<g stroke-linejoin='round' stroke-linecap='round' stroke-width='14' filter='url(#skilgenGlow)'>"
        "<path d='M86 18 146 52v68l-60 34-60-34V52l60-34Z' stroke='#F2D679'/>"
        "<path d='M254 18 314 52v68l-60 34-60-34V52l60-34Z' stroke='#F3F4F8'/>"
        "<path d='M422 18 482 52v68l-60 34-60-34V52l60-34Z' stroke='#F3F4F8'/>"
        "<path d='M590 18 650 52v68l-60 34-60-34V52l60-34Z' stroke='#F2D679'/>"
        "<path d='M170 156 230 190v68l-60 34-60-34v-68l60-34Z' stroke='#F3F4F8'/>"
        "<path d='M338 156 398 190v68l-60 34-60-34v-68l60-34Z' stroke='#F3F4F8'/>"
        "<path d='M506 156 566 190v68l-60 34-60-34v-68l60-34Z' stroke='#F3F4F8'/>"
        "</g>"
        "</svg>"
    )


def render_evidence_network_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    nodes: list[dict[str, object]] = [
        {"id": "repo", "label": project_root.name, "group": "repo", "value": 38, "title": "Repository root"},
    ]
    edges: list[dict[str, object]] = []
    for language in evidence_graph.dominant_languages[:6]:
        language_id = f"lang::{language}"
        nodes.append({"id": language_id, "label": language, "group": "language", "value": 20, "title": f"Dominant language: {language}"})
        edges.append({"from": "repo", "to": language_id})
    for item in evidence_graph.items[:18]:
        item_id = f"item::{item.path}"
        snippet = " ".join(item.snippet[:2]).strip() or "No snippet captured"
        title = f"{item.kind}: {item.path}\n{snippet}"
        nodes.append({"id": item_id, "label": item.path.split("/")[-1], "group": item.kind, "value": 14, "title": title})
        edges.append({"from": "repo", "to": item_id})
        if item.language:
            language_id = f"lang::{item.language}"
            if not any(node["id"] == language_id for node in nodes):
                nodes.append({"id": language_id, "label": item.language, "group": "language", "value": 18, "title": f"Language: {item.language}"})
            edges.append({"from": language_id, "to": item_id})
        for related in item.related_imports[:2]:
            related_id = f"ref::{related}"
            if not any(node["id"] == related_id for node in nodes):
                nodes.append({"id": related_id, "label": related.split("/")[-1], "group": "reference", "value": 10, "title": related})
            edges.append({"from": item_id, "to": related_id})
    return {"nodes": nodes, "edges": edges}


def render_dependency_network_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    nodes: dict[str, dict[str, object]] = {}
    edges: list[dict[str, object]] = []
    edge_count = 0
    for source, targets in bundle.import_graph.items():
        if edge_count >= 48:
            break
        nodes.setdefault(
            source,
            {"id": source, "label": source.split("/")[-1], "group": "source", "value": 14, "title": source},
        )
        for target in targets[:5]:
            nodes.setdefault(
                target,
                {"id": target, "label": target.split("/")[-1], "group": "target", "value": 12, "title": target},
            )
            edges.append({"from": source, "to": target})
            edge_count += 1
            if edge_count >= 48:
                break
    if not nodes:
        nodes["empty"] = {"id": "empty", "label": "No dependencies", "group": "repo", "value": 18, "title": "No import dependencies detected yet"}
    return {"nodes": list(nodes.values()), "edges": edges}


def render_architecture_sunburst_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    architecture = bundle.architecture
    plans = {item.domain: item for item in architecture.materialization_plan}
    root: dict[str, object] = {
        "name": project_root.name,
        "children": [],
    }
    for domain in architecture.domains:
        plan = plans.get(domain["name"] if isinstance(domain, dict) else domain.name)
        domain_name = domain["name"] if isinstance(domain, dict) else domain.name
        domain_label = _display_domain_name(domain_name)
        domain_summary = domain["summary"] if isinstance(domain, dict) else domain.summary
        responsibilities = domain["responsibilities"] if isinstance(domain, dict) else domain.responsibilities
        evidence_paths = domain["evidence_paths"] if isinstance(domain, dict) else domain.evidence_paths
        node = {
            "name": domain_label,
            "summary": domain_summary,
            "value": max(1, len(evidence_paths) + len(responsibilities)),
            "children": [],
        }
        for child in (plan.child_skill_paths if plan is not None else [])[:6]:
            node["children"].append(
                {
                    "name": _display_skill_name(child),
                    "summary": child,
                    "value": max(1, len(child)),
                }
            )
        if not node["children"]:
            for path in evidence_paths[:4]:
                node["children"].append(
                    {
                        "name": path.split("/")[-1],
                        "summary": path,
                        "value": 1,
                    }
                )
        root["children"].append(node)
    return root


def render_evidence_sankey_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    nodes: list[dict[str, object]] = [{"id": "repo", "name": project_root.name, "layer": 0}]
    node_ids = {"repo"}
    links: list[dict[str, object]] = []

    def ensure_node(node_id: str, name: str, layer: int) -> None:
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "name": name, "layer": layer})

    for language in evidence_graph.dominant_languages[:5]:
        language_id = f"lang::{language}"
        ensure_node(language_id, language, 1)
        links.append({"source": "repo", "target": language_id, "value": 2})

    for item in evidence_graph.items[:16]:
        item_id = f"item::{item.path}"
        kind_id = f"kind::{item.kind}"
        file_label = item.path.split("/")[-1]
        ensure_node(kind_id, item.kind.replace("_", " "), 2)
        ensure_node(item_id, file_label, 3)
        if item.language:
            language_id = f"lang::{item.language}"
            ensure_node(language_id, item.language, 1)
            links.append({"source": language_id, "target": kind_id, "value": 1})
        else:
            links.append({"source": "repo", "target": kind_id, "value": 1})
        links.append({"source": kind_id, "target": item_id, "value": 1})
    return {"nodes": nodes, "links": links}


def render_skill_sankey_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    architecture = bundle.architecture
    nodes: list[dict[str, object]] = [{"id": "root", "name": project_root.name, "layer": 0}]
    node_ids = {"root"}
    links: list[dict[str, object]] = []

    def ensure_node(node_id: str, name: str, layer: int) -> None:
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "name": name, "layer": layer})

    for item in architecture.materialization_plan[:18]:
        domain_id = f"domain::{item.domain}"
        ensure_node(domain_id, _display_domain_name(item.domain), 1)
        links.append({"source": "root", "target": domain_id, "value": max(1, len(item.child_skill_paths) or 1)})
        parent_path = item.parent_skill_path or item.domain
        parent_id = f"parent::{parent_path}"
        ensure_node(parent_id, _display_skill_name(parent_path), 2)
        links.append({"source": domain_id, "target": parent_id, "value": max(1, len(item.child_skill_paths) or 1)})
        if item.child_skill_paths:
            for child in item.child_skill_paths[:5]:
                child_id = f"child::{child}"
                ensure_node(child_id, _display_skill_name(child), 3)
                links.append({"source": parent_id, "target": child_id, "value": 1})
        else:
            leaf_id = f"leaf::{parent_path}"
            ensure_node(leaf_id, "core guidance", 3)
            links.append({"source": parent_id, "target": leaf_id, "value": 1})
    return {"nodes": nodes, "links": links}


def render_analytics_sankey_data(project_root: Path, analytics: dict[str, object]) -> dict[str, object]:
    nodes: list[dict[str, object]] = [{"id": "loads", "name": "Skill Loads", "layer": 0}]
    node_ids = {"loads"}
    links: list[dict[str, object]] = []

    def ensure_node(node_id: str, name: str, layer: int) -> None:
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "name": name, "layer": layer})

    top_skills = analytics.get("top_skills", [])
    if not top_skills:
        ensure_node("none", "No usage yet", 1)
        links.append({"source": "loads", "target": "none", "value": 1})
        return {"nodes": nodes, "links": links}

    for item in top_skills[:10]:
        skill = str(item.get("skill", "unknown"))
        loads = int(item.get("loads", 0))
        parts = Path(skill).parts
        domain = parts[1] if len(parts) > 2 else "other"
        domain_id = f"domain::{domain}"
        skill_id = f"skill::{skill}"
        bucket = "hot" if loads >= 5 else "active" if loads >= 2 else "low"
        bucket_id = f"bucket::{bucket}"
        ensure_node(domain_id, domain, 1)
        ensure_node(skill_id, Path(skill).parent.name or skill, 2)
        ensure_node(bucket_id, bucket.title(), 3)
        links.append({"source": "loads", "target": domain_id, "value": max(1, loads)})
        links.append({"source": domain_id, "target": skill_id, "value": max(1, loads)})
        links.append({"source": skill_id, "target": bucket_id, "value": max(1, loads)})
    return {"nodes": nodes, "links": links}


def render_dashboard_html(
    context: RequirementsContext,
    project_root: Path,
    dashboard_payload: dict[str, object],
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    score = dashboard_payload["score"]
    diff = dashboard_payload["diff"]
    auto_update = dashboard_payload["auto_update"]
    analytics = dashboard_payload["analytics"]
    status = dashboard_payload["status"]
    decision = dashboard_payload["agent_decision"]
    score_history = dashboard_payload["score_history"]
    score_trend = dashboard_payload["score_trend"]
    external_skills = dashboard_payload["external_skills"]
    enterprise_skills = dashboard_payload["enterprise_skills"]
    mcp_connectors = dashboard_payload["mcp_connectors"]
    architecture = dashboard_payload["architecture"]
    evidence_graph = dashboard_payload["evidence_graph"]
    repo_name = project_root.name
    score_value = float(score["score"])
    score_percent = max(0.0, min(100.0, score_value))
    score_label = escape(str(score["rating"]).replace("-", " ").title())
    stale_count = len(diff["stale_skill_paths"])
    changed_count = int(diff["changed_file_count"])
    parser_backends = sorted({str(payload.get("backend", "unknown")) for payload in evidence_graph["parser_summary"].values()})
    generated_outputs = [
        ("AGENTS.md", status["agents_exists"]),
        ("ANALYSIS.md", status["analysis_exists"]),
        ("ARCHITECTURE.md", status["architecture_exists"]),
        ("FEATURES.md", status["features_exists"]),
        ("REPORT.md", status["report_exists"]),
        ("TRACEABILITY.md", status["traceability_exists"]),
        ("skills/MANIFEST.md", status["manifest_exists"]),
        ("skills/GRAPH.md", status["graph_exists"]),
        ("skilgen-dashboard.html", status.get("dashboard_exists", False)),
    ]
    evidence_count = len(evidence_graph["items"])
    dependency_edges = sum(len(targets) for targets in bundle.import_graph.values())
    call_edges = sum(len(targets) for targets in bundle.evidence_graph.call_graph.values())
    config_edges = sum(len(targets) for targets in bundle.evidence_graph.config_runtime_graph.values())
    test_links = sum(len(targets) for targets in bundle.evidence_graph.test_mapping.values())
    total_symbol_files = len(bundle.evidence_graph.symbol_graph)
    architecture_mermaid = render_architecture_graph_mermaid(context, project_root, bundle)
    skill_mermaid = render_skill_graph_mermaid(context, project_root, bundle)
    dependency_network = render_dependency_network_data(context, project_root, bundle)
    architecture_sunburst = render_architecture_sunburst_data(context, project_root, bundle)
    evidence_sankey = render_evidence_sankey_data(context, project_root, bundle)
    skill_sankey = render_skill_sankey_data(context, project_root, bundle)
    analytics_sankey = render_analytics_sankey_data(project_root, analytics)
    external_skill_labels = [item.get("slug", "unknown") for item in external_skills["installed"][:6]]
    brand_mark = _skilgen_logo_svg()
    trend_points = score_history[-8:]
    if not trend_points:
        trend_points = [
            {"score": score_value, "source": "baseline"},
            {"score": score_value, "source": "current"},
        ]
    elif len(trend_points) == 1:
        trend_points = [trend_points[0], {"score": score_value, "source": "current"}]
    trend_markup = "\n".join(
        f"<div class='spark-point' style='height:{max(18, min(100, float(item.get('score', 0))))}%'><span>{int(round(float(item.get('score', 0))))}</span></div>"
        for item in trend_points
    ) or "<div class='spark-empty'>Score history will appear after a few runs.</div>"
    trend_ticks_markup = "\n".join(
        f"<span>{escape(str(item.get('source', 'current')).replace('_', ' '))}</span>"
        for item in trend_points
    )

    def pill(label: str, tone: str = "default") -> str:
        return f"<span class='pill {tone}'>{escape(label)}</span>"

    def metric(title: str, value: str, subtitle: str) -> str:
        return (
            "<article class='metric-card'>"
            f"<div class='metric-eyebrow'>{escape(title)}</div>"
            f"<div class='metric-value'>{escape(value)}</div>"
            f"<div class='metric-subtitle'>{escape(subtitle)}</div>"
            "</article>"
        )

    def list_items(items: list[str], *, empty: str = "None yet") -> str:
        if not items:
            return f"<li class='muted'>{escape(empty)}</li>"
        return "\n".join(f"<li>{escape(item)}</li>" for item in items)

    subscores_markup = "\n".join(
        (
            "<div class='subscore-row'>"
            f"<div class='subscore-label'>{escape(name.title())}</div>"
            f"<div class='subscore-bar'><span style='width:{max(4.0, min(100.0, (float(payload['score']) / float(payload['max_score'])) * 100))}%'></span></div>"
            f"<div class='subscore-value'>{int(round(float(payload['score'])))} / {int(payload['max_score'])}</div>"
            "</div>"
        )
        for name, payload in score["subscores"].items()
    )
    quality_gates_markup = "\n".join(
        "<li><strong>{name}</strong><span>cap {cap}</span><p>{reason}</p></li>".format(
            name=escape(str(gate["name"]).replace("_", " ").title()),
            cap=escape(str(gate["cap"])),
            reason=escape(str(gate["reason"])),
        )
        for gate in score.get("quality_gates", [])
    ) or "<li class='muted'>No active quality gates are lowering the score right now.</li>"
    changed_files_markup = "\n".join(
        f"<li><span class='change-type {escape(item['change_type'])}'>{escape(item['change_type'])}</span><strong>{escape(item['path'])}</strong></li>"
        for item in diff["changed_files"][:8]
    ) or "<li class='muted'>No source changes detected since the last generation baseline.</li>"
    impacted_markup = "\n".join(
        (
            "<li>"
            f"<div><strong>{escape(item['domain'])}</strong><span>{escape(item['skill_path'] or '-')}</span></div>"
            f"{pill('STALE' if item['stale'] else 'CURRENT', 'warning' if item['stale'] else 'good')}"
            "</li>"
        )
        for item in diff["impacted_domain_details"][:8]
        if item["domain"] in diff["impacted_domains"]
    ) or "<li class='muted'>All materialized domains are current.</li>"
    outputs_markup = "\n".join(
        (
            "<li>"
            f"<span>{escape(name)}</span>"
            f"{pill('ready' if exists else 'missing', 'good' if exists else 'warning')}"
            "</li>"
        )
        for name, exists in generated_outputs
    )
    external_markup = "\n".join(
        f"<li>{escape(item.get('slug', 'unknown'))}{pill('active' if item.get('active') else 'installed', 'good' if item.get('active') else 'default')}</li>"
        for item in external_skills["installed"][:6]
    ) or "<li class='muted'>No external skills installed yet.</li>"
    enterprise_markup = "\n".join(
        f"<li>{escape(item.get('slug', 'unknown'))}{pill(str(item.get('kind', 'enterprise')), 'default')}</li>"
        for item in enterprise_skills["active"][:6]
    ) or "<li class='muted'>No enterprise skills active yet.</li>"
    connector_markup = "\n".join(
        (
            "<li>"
            f"{escape(item.get('slug', 'unknown'))}"
            f"{pill('official' if item.get('official_source_verified') else 'community', 'good' if item.get('official_source_verified') else 'warning')}"
            f"{pill('oauth' if item.get('oauth_ready') else 'custom auth', 'default')}"
            "</li>"
        )
        for item in mcp_connectors["active"][:6]
    ) or "<li class='muted'>No MCP connectors active yet.</li>"
    analytics_markup = "\n".join(
        f"<li><strong>{escape(item['skill'])}</strong><span>{int(item['loads'])} loads</span></li>"
        for item in analytics["top_skills"][:6]
    ) or "<li class='muted'>Usage analytics will populate as agents load skills.</li>"
    domain_cards_parts: list[str] = []
    for domain in architecture["domains"][:6]:
        confidence_label = f"{float(domain['confidence']):.2f}"
        domain_label = _display_domain_name(str(domain["name"]))
        related_domains = ", ".join(_display_domain_name(str(item)) for item in domain["related_domains"][:3]) or "No related domains surfaced"
        domain_cards_parts.append(
            "<article class='domain-card'>"
            f"<div class='domain-head'><h3>{escape(domain_label)}</h3>{pill(confidence_label, 'good')}</div>"
            f"<p>{escape(domain['summary'])}</p>"
            f"<div class='micro-label'>Responsibilities</div><ul>{list_items(domain['responsibilities'][:4], empty='No responsibilities captured')}</ul>"
            f"<div class='micro-label'>Evidence</div><ul>{list_items(domain['evidence_paths'][:3], empty='No evidence paths captured')}</ul>"
            f"<div class='micro-label'>Nuance</div><p class='nuance-copy'>{escape(related_domains)}</p>"
            "</article>"
        )
    domain_cards = "\n".join(domain_cards_parts)
    architecture_legend = "\n".join(
        f"<li><strong>{escape(_display_domain_name(str(domain['name'])))}</strong><span>{escape(domain['recommended_skill_path'] or 'domain')}</span></li>"
        for domain in architecture["domains"][:8]
    ) or "<li class='muted'>No architecture domains yet.</li>"
    plan_rows = "\n".join(
        (
            "<tr>"
            f"<td>{escape(_display_domain_name(str(item['domain'])))}</td>"
            f"<td>{pill(str(item['decision']).upper(), 'warning' if item['decision'] == 'split' else 'default')}</td>"
            f"<td>{escape(item['parent_skill_path'] or '-')}</td>"
            f"<td>{escape(', '.join(item['child_skill_paths'][:4]) or '-')}</td>"
            f"<td>{escape(item['rationale'])}"
            f"<div class='rationale-note'>Grounded in parser evidence, symbol surfaces, import relationships, and cross-domain context for {escape(_display_domain_name(str(item['domain'])))}.</div></td>"
            "</tr>"
        )
        for item in architecture["materialization_plan"][:8]
    ) or "<tr><td colspan='5' class='muted'>No materialization plan entries yet.</td></tr>"

    graph_payload_json = json.dumps({"architecture": architecture_mermaid})
    network_payload_json = json.dumps({"dependencies": dependency_network})
    sunburst_payload_json = json.dumps(architecture_sunburst)
    sankey_payload_json = json.dumps({"evidence": evidence_sankey, "skills": skill_sankey, "analytics": analytics_sankey})
    dashboard_styles = """
:root{--bg:#050608;--bg-soft:#090b0f;--panel:#10141b;--panel-strong:#0d1117;--line:rgba(255,255,255,.08);--line-strong:rgba(239,211,122,.18);--text:#f6f7fb;--muted:#98a1b2;--gold:#efd37a;--gold-strong:#f8df8e;--white:#f3f4f8;--good:#8fd9a8;--warning:#ffb86b;--danger:#ff7a7a;--shadow:0 28px 90px rgba(0,0,0,.42);}
*{box-sizing:border-box}html,body{min-height:100%}body{margin:0;font-family:'Sora','Inter',ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:radial-gradient(circle at left top, rgba(239,211,122,.12), transparent 28%),radial-gradient(circle at right top, rgba(243,244,248,.07), transparent 22%),var(--bg);color:var(--text)}
body::before{content:'';position:fixed;inset:0;pointer-events:none;opacity:.18;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='156' viewBox='0 0 180 156'%3E%3Cg fill='none' stroke='%23efd37a' stroke-opacity='.17' stroke-width='2.6'%3E%3Cpath d='M45 3l39 19.5v39L45 81 6 61.5v-39z'/%3E%3Cpath d='M135 3l39 19.5v39L135 81 96 61.5v-39z'/%3E%3Cpath d='M90 75l39 19.5v39L90 153 51 133.5v-39z'/%3E%3C/g%3E%3C/svg%3E");background-size:250px 216px;background-position:center top}
a{color:inherit}.page{max-width:1500px;margin:0 auto;padding:24px 24px 64px}.hero-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(360px,.85fr);gap:24px;align-items:stretch}.panel,.hero-panel{background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.02));border:1px solid var(--line);border-radius:30px;box-shadow:var(--shadow);backdrop-filter:blur(14px)}
.hero-panel{padding:30px;position:relative;overflow:hidden}.hero-panel::after{content:'';position:absolute;right:-80px;bottom:-80px;width:260px;height:260px;background:radial-gradient(circle, rgba(239,211,122,.16), transparent 68%)}.hero-left{display:grid;gap:22px}.brand-wrap{display:flex;align-items:center;justify-content:space-between;gap:18px}.brand-lockup{display:grid;gap:10px}
.skilgen-mark{width:240px;max-width:100%;height:auto;display:block;filter:drop-shadow(0 20px 46px rgba(0,0,0,.42))}.skilgen-mark.compact{width:210px;margin:0 auto 8px}.eyebrow{color:var(--gold);text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:700}.repo-chip{display:inline-flex;align-items:center;padding:8px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.04);color:var(--muted);font-size:.88rem}
.hero-copy h1{margin:0;font-size:clamp(2.2rem,4vw,4.2rem);line-height:.94;max-width:12ch}.hero-note{margin:14px 0 0;max-width:54ch;color:#d8dde7;font-size:1.02rem;line-height:1.55;font-style:italic}.hero-context{margin:12px 0 0;max-width:64ch;color:var(--muted);font-size:1rem;line-height:1.55}.hero-actions{display:flex;gap:10px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);color:var(--text);font-size:.84rem}.pill.good{border-color:rgba(143,217,168,.3);color:var(--good)}.pill.warning{border-color:rgba(255,184,107,.32);color:var(--warning)}.hero-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.metric-card{padding:18px;border-radius:22px;border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.02))}
.metric-eyebrow{font-size:.72rem;text-transform:uppercase;letter-spacing:.16em;color:var(--gold)}.metric-value{font-size:2rem;font-weight:700;margin-top:10px}.metric-subtitle{margin-top:8px;color:var(--muted);font-size:.92rem;line-height:1.4}.hero-right{display:grid;gap:18px}.score-top{display:grid;gap:18px;justify-items:center}.score-ring{width:220px;height:220px;border-radius:50%;background:conic-gradient(var(--gold) 0% calc(var(--score) * 1%), rgba(255,255,255,.08) 0% 100%);display:grid;place-items:center;position:relative}
.score-ring::before{content:'';width:164px;height:164px;border-radius:50%;background:var(--bg-soft);border:1px solid rgba(255,255,255,.08)}.score-ring-content{position:absolute;text-align:center}.score-ring-content strong{display:block;font-size:3.2rem;line-height:1}.score-ring-content span{display:block;color:var(--muted);text-transform:uppercase;letter-spacing:.18em;font-size:.76rem;margin-top:8px}.score-rail{display:grid;grid-template-columns:1fr 1fr;gap:14px}.stat-card{padding:16px 18px;border-radius:22px;border:1px solid var(--line);background:rgba(255,255,255,.03)}.stat-label{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}.stat-value{font-size:1.8rem;font-weight:700;margin-top:10px}.stat-note{margin-top:6px;color:var(--muted);font-size:.9rem;line-height:1.35}
.layout{display:grid;gap:24px;margin-top:24px}.panel{padding:24px}.panel h2{margin:0;font-size:1.1rem}.section-copy{margin:8px 0 0;color:var(--muted);line-height:1.5}.score-board{display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr);gap:24px}.subscore-stack{display:grid;gap:12px;margin-top:20px}.subscore-row{display:grid;grid-template-columns:120px 1fr 70px;gap:12px;align-items:center}.subscore-label{font-size:.92rem;color:#e4e8ef}.subscore-bar{height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden}.subscore-bar span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--gold),#fff3be)}.subscore-value{text-align:right;color:var(--muted);font-size:.86rem}
.quality-gates{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:12px}.quality-gates li{padding:14px 16px;border-radius:18px;border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.03)}.quality-gates li p{margin:8px 0 0;color:var(--muted)}.quality-gates li span{float:right;color:var(--gold)}.trend-shell{display:grid;gap:16px}.sparkline{display:flex;align-items:flex-end;gap:10px;height:152px;padding:18px;border-radius:22px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}.spark-point{flex:1;border-radius:18px 18px 8px 8px;background:linear-gradient(180deg,var(--gold),rgba(239,211,122,.18));position:relative;min-height:18px}.spark-point span{position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%);font-size:.75rem;color:var(--muted)}.spark-empty{color:var(--muted)}.trend-ticks{display:flex;gap:10px;justify-content:space-between;color:var(--muted);font-size:.76rem;text-transform:uppercase;letter-spacing:.12em}
.legend{display:flex;flex-wrap:wrap;gap:10px}.graph-shell{display:grid;gap:18px}.graph-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;flex-wrap:wrap}.graph-tabs{display:flex;gap:10px;flex-wrap:wrap}.graph-tab{border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);color:var(--text);padding:10px 14px;border-radius:999px;cursor:pointer;font-weight:600}.graph-tab.active{background:rgba(239,211,122,.14);border-color:rgba(239,211,122,.35);color:var(--gold-strong)}.graph-frame{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(300px,.55fr);gap:18px;align-items:stretch}
.graph-panel{display:none;height:100%}.graph-panel.active{display:block;height:100%}.graph-stage{height:560px;border-radius:26px;border:1px solid var(--line-strong);background:linear-gradient(180deg,#0a0d13,#06080d);padding:16px;overflow:hidden}.graph-stage .mermaid{height:100%;overflow:auto}.graph-aside{padding:20px;border-radius:26px;border:1px solid rgba(255,255,255,.07);background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.02));display:grid;align-content:start;gap:16px}.graph-aside h3{margin:0;font-size:1rem}.graph-aside p{margin:0;color:var(--muted);line-height:1.5}.graph-aside ul{margin:0;padding-left:18px;color:#dce1ea}
.sunburst-canvas,.sankey-canvas,.network-canvas{width:100%;height:100%;min-height:500px;border-radius:20px;position:relative;overflow:hidden;background:radial-gradient(circle at top, rgba(239,211,122,.08), transparent 38%), rgba(255,255,255,.02)}.network-canvas canvas{width:100%!important;height:100%!important;display:block}.graph-stage svg{width:100%;height:100%;display:block}.graph-legend{list-style:none;padding:0;margin:0;display:grid;gap:10px}.graph-legend li{display:flex;justify-content:space-between;gap:12px;padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}.graph-legend li span{color:var(--muted);font-size:.88rem}
.dashboard-columns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px}.list{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:10px}.list li{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}.list li div{display:grid;gap:4px}.list li span{color:var(--muted)}.change-type{text-transform:uppercase;font-size:.74rem;letter-spacing:.12em;padding:4px 8px;border-radius:999px;border:1px solid rgba(255,255,255,.08);color:var(--text)}.change-type.added{color:var(--good)}.change-type.modified{color:var(--warning)}.change-type.deleted{color:var(--danger)}.muted{color:var(--muted)!important}.section-stack{display:grid;gap:24px}
.domain-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:18px}.domain-card{padding:20px;border-radius:22px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.02))}.domain-head{display:flex;justify-content:space-between;align-items:center;gap:12px}.domain-card h3{margin:0;font-size:1.02rem}.domain-card p{color:#d6dbe5}.micro-label{margin-top:14px;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}.domain-card ul{padding-left:18px;color:var(--muted)}table{width:100%;border-collapse:collapse;border-spacing:0;margin-top:18px}th,td{padding:14px 12px;border-bottom:1px solid rgba(255,255,255,.08);text-align:left;vertical-align:top}th{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.14em}
.systems-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.mini-panel{padding:18px;border-radius:22px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.03)}.mini-panel ul{list-style:none;padding:0;margin:12px 0 0;display:grid;gap:10px}.mini-panel li{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.ops-board{display:grid;gap:18px;margin-top:18px}.ops-tabs,.surface-tabs{display:flex;flex-wrap:wrap;gap:10px}.ops-tab,.surface-tab{border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);color:var(--text);padding:10px 14px;border-radius:999px;cursor:pointer;font-weight:600}.ops-tab.active,.surface-tab.active{background:rgba(239,211,122,.14);border-color:rgba(239,211,122,.35);color:var(--gold-strong)}.ops-copy,.surface-copy{display:none}.ops-copy.active,.surface-copy.active{display:block}.ops-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.ops-tile{padding:16px;border-radius:18px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.03)}.ops-tile strong{display:block;font-size:1rem;margin-bottom:6px}
.analytics-board{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr);gap:18px;align-items:stretch}.analytics-side{display:grid;gap:16px}.nuance-copy,.rationale-note{margin-top:8px;color:var(--muted);font-size:.92rem;line-height:1.5}.footer-note{margin-top:12px;color:var(--muted);font-size:.92rem}.tooltip{position:absolute;pointer-events:none;background:rgba(6,8,11,.98);border:1px solid rgba(239,211,122,.3);border-radius:14px;padding:12px 14px;color:#f6f7fb;font-size:.86rem;line-height:1.45;box-shadow:0 18px 40px rgba(0,0,0,.28);opacity:0;transform:translate(-50%,-100%);transition:opacity .16s ease;max-width:280px}.tooltip strong{display:block;color:var(--gold);margin-bottom:6px}
@media (max-width:1180px){.hero-grid,.score-board,.dashboard-columns,.graph-frame,.analytics-board{grid-template-columns:1fr}.hero-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.systems-grid,.domain-grid,.ops-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:760px){.page{padding:18px}.hero-panel,.panel{padding:20px}.hero-metrics,.score-rail,.systems-grid,.domain-grid,.ops-grid{grid-template-columns:1fr}.hero-copy h1{font-size:clamp(2.1rem,14vw,3.4rem)}.skilgen-mark{width:200px}.skilgen-mark.compact{width:180px}.graph-stage{height:420px}.sunburst-canvas,.sankey-canvas,.network-canvas{min-height:360px}.subscore-row{grid-template-columns:1fr}.subscore-value{text-align:left}}
""".strip()

    return "\n".join(
        [
            "<!doctype html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='utf-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1'>",
            f"<title>Skilgen Dashboard · {escape(repo_name)}</title>",
            "<script type='module'>import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'; window.__mermaid = mermaid; mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });</script>",
            "<script src='https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js'></script>",
            "<script src='https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js'></script>",
            "<script src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>",
            f"<style>{dashboard_styles}</style>",
            "</head>",
            "<body>",
            "<div class='page'>",
            "<section class='hero-grid'>",
            "<section class='hero-panel hero-left'>",
            "<div class='brand-wrap'>",
            "<div class='brand-lockup'>",
            "<div class='eyebrow'>Living skill intelligence, mapped in one page.</div>",
            brand_mark,
            "</div>",
            f"<div class='repo-chip'>Repository · {escape(repo_name)}</div>",
            "</div>",
            "<div class='hero-copy'>",
            "<h1>Skilgen Operating System</h1>",
            "<p class='hero-note'><em>All your skill intelligence — alive, connected, and visible on a single surface. Not a dashboard. A living map.</em></p>",
            f"<p class='hero-context'><strong>{escape(repo_name)}</strong> is translated into one operating surface for coding agents: architecture, evidence, dependencies, skill flows, score, freshness, analytics, auto-update, and capability context together.</p>",
            "</div>",
            "<div class='hero-actions'>",
            pill(f"Skilgen Score {int(round(score_value))}/100", "good" if score_value >= 75 else "warning"),
            pill(f"{stale_count} stale skills" if stale_count else "All skills current", "warning" if stale_count else "good"),
            pill(f"{changed_count} changed files" if changed_count else "No diff since baseline"),
            pill(f"Auto-update {'on' if auto_update.get('enabled') else 'off'}", "good" if auto_update.get("enabled") else "warning"),
            "</div>",
            "<div class='hero-metrics'>",
            metric("Evidence", str(evidence_count), "Files, snippets, config, docs, and tests feeding the graph."),
            metric("Dependencies", str(dependency_edges), "Import edges across the active repository graph."),
            metric("Calls", str(call_edges), "Observed call relationships from parsed source evidence."),
            metric("Tests", str(test_links), "Tests mapped back to implementation files."),
            "</div>",
            "</section>",
            "<aside class='hero-panel hero-right'>",
            "<div class='score-top'>",
            brand_mark.replace("class='skilgen-mark'", "class='skilgen-mark compact'"),
            f"<div class='score-ring' style='--score:{score_percent};'><div class='score-ring-content'><strong>{int(round(score_value))}</strong><span>{score_label}</span></div></div>",
            "</div>",
            "<div class='score-rail'>",
            f"<article class='stat-card'><div class='stat-label'>Freshness</div><div class='stat-value'>{int(round(float(diff['freshness_score'])))}/{int(diff['freshness_max'])}</div><div class='stat-note'>{escape(str(diff['reason']).replace('_', ' '))}</div></article>",
            f"<article class='stat-card'><div class='stat-label'>Domains</div><div class='stat-value'>{len(architecture['domains'])}</div><div class='stat-note'>Materialized architecture domains in play.</div></article>",
            f"<article class='stat-card'><div class='stat-label'>Parsers</div><div class='stat-value'>{len(parser_backends) or 1}</div><div class='stat-note'>{escape(', '.join(parser_backends[:3]) or 'unknown')}</div></article>",
            f"<article class='stat-card'><div class='stat-label'>Outputs</div><div class='stat-value'>{sum(1 for _, exists in generated_outputs if exists)}</div><div class='stat-note'>Repo-local artifacts ready for agents.</div></article>",
            "</div>",
            "</aside>",
            "</section>",
            "<section class='layout section-stack'>",
            "<section class='panel'>",
            "<h2>Usage Analytics</h2>",
            "<div class='section-copy'>Skilgen tracks where agent attention actually lands. This surface shows load flow through the skill tree before you ever dive into the graph studio.</div>",
            "<div class='analytics-board'>",
            "<div class='graph-stage'>",
            "<div class='sankey-canvas' data-sankey='analytics'></div>",
            "</div>",
            "<div class='analytics-side'>",
            "<div class='legend'>"
            + pill(
                f"{int(analytics.get('event_count', 0))} recorded events",
                "good" if int(analytics.get("event_count", 0)) else "default",
            )
            + pill(f"{len(analytics.get('top_skills', []))} tracked skills")
            + "</div>",
            "<div class='mini-panel'><div class='micro-label'>Most Loaded Skills</div>"
            + f"<ul>{analytics_markup}</ul></div>",
            "<div class='mini-panel'><div class='micro-label'>Least Used</div><ul>"
            + "\n".join(
                f"<li><strong>{escape(item['skill'])}</strong><span>{int(item['loads'])} loads</span></li>"
                for item in analytics.get("least_used", [])[:6]
            )
            + ("</ul></div>" if analytics.get("least_used") else "<li class='muted'>No underused skills yet.</li></ul></div>"),
            "<div class='mini-panel'><div class='micro-label'>Deep nuance</div>"
            f"<p class='nuance-copy'>Skilgen is not just summarizing the repo. It is grounding load analytics against {total_symbol_files} parsed files, {dependency_edges} dependency edges, {call_edges} call edges, and {test_links} test mappings so agent attention can be interpreted in context.</p></div>",
            "</div>",
            "</div>",
            "</section>",
            "<section class='panel graph-shell'>",
            "<div class='graph-head'>",
            "<div><h2>Graph Studio</h2><div class='section-copy'>Skilgen walks the repository file by file, extracts symbols, calls, configs, tests, docs, and capability clues, then turns those nuances into a living operating map.</div></div>",
            "<div class='graph-tabs'>",
            "<button class='graph-tab active' data-target='architecture'>Architecture</button>",
            "<button class='graph-tab' data-target='evidence'>Evidence</button>",
            "<button class='graph-tab' data-target='dependencies'>Dependencies</button>",
            "<button class='graph-tab' data-target='skills'>Skills</button>",
            "</div>",
            "</div>",
            "<div class='graph-frame'>",
            "<div class='graph-stage'>",
            "<div class='graph-panel active' data-panel='architecture'><div class='sunburst-canvas' data-sunburst='architecture'></div></div>",
            "<div class='graph-panel' data-panel='evidence'><div class='sankey-canvas' data-sankey='evidence'></div></div>",
            "<div class='graph-panel' data-panel='dependencies'><div class='network-canvas' data-network='dependencies'></div></div>",
            "<div class='graph-panel' data-panel='skills'><div class='sankey-canvas' data-sankey='skills'></div></div>",
            "</div>",
            "<aside class='graph-aside'>",
            "<div class='graph-copy active' data-copy='architecture'><h3>Architecture Sunburst</h3><p>Zoom through top-level domains, sub-skills, and evidence surfaces. Click deeper to focus a capability boundary and click the center to move back out.</p><ul><li>Outer rings represent planned or generated child skills.</li><li>Ring sizes scale with evidence and responsibilities.</li><li>Hover reveals domain summaries and skill context.</li></ul><div class='micro-label'>Visible Domain Legend</div><ul class='graph-legend'>"
            + architecture_legend
            + "</ul></div>",
            "<div class='graph-copy' data-copy='evidence'><h3>Evidence Flow</h3><p>Follow how languages and evidence kinds feed concrete files. This is the visible proof behind the architecture Skilgen is synthesizing.</p><ul><li>Left: dominant languages or repo root.</li><li>Middle: evidence kinds.</li><li>Right: files or source artifacts.</li></ul></div>",
            "<div class='graph-copy' data-copy='dependencies'><h3>Dependency Network</h3><p>Pan, zoom, and inspect the live import network. This makes coupling and high-fanout modules obvious before the agent ever starts coding.</p><ul><li>Use the built-in controls to zoom around.</li><li>Hover nodes to inspect exact paths.</li><li>Dense clusters often signal hot spots.</li></ul></div>",
            "<div class='graph-copy' data-copy='skills'><h3>Skill Flow</h3><p>See how domains become parent skills, generated child skills, and external packs that Skilgen has already pulled in because the repo signaled they matter.</p><ul><li>Left: domain families.</li><li>Middle: parent skills.</li><li>Right: generated child skills and external skill packs.</li></ul><div class='micro-label'>External skills in play</div><ul class='graph-legend'>"
            + (
                "".join(f"<li><strong>{escape(item)}</strong><span>installed from repo signals</span></li>" for item in external_skill_labels)
                or "<li class='muted'>No external skills installed yet.</li>"
            )
            + "</ul><p class='nuance-copy'>Skilgen folds external skill packs into the same surface so agents can see generated skill boundaries and imported ecosystem capability together.</p></div>",
            "<div class='legend'>",
            pill(f"{len(architecture['domains'])} active domains", "good"),
            pill(f"{evidence_count} evidence items"),
            pill(f"{dependency_edges} dependency edges"),
            "</div>",
            "</aside>",
            "</div>",
            "</section>",
            "<section class='panel'>",
            "<h2>Skilgen Score</h2>",
            "<div class='section-copy'>Groundedness, coverage, freshness, and structure are grouped here as one quality bar instead of separate floating metrics.</div>",
            "<div class='score-board'>",
            f"<div><div class='subscore-stack'>{subscores_markup}</div><ul class='quality-gates'>{quality_gates_markup}</ul></div>",
            "<div class='trend-shell'>",
            "<div class='micro-label'>Score Trend</div>",
            f"<div class='sparkline'>{trend_markup}</div>",
            f"<div class='trend-ticks'>{trend_ticks_markup}</div>",
            "<div class='legend'>",
            pill(f"Delta {score_trend['delta_from_previous']:+.2f}", "good" if float(score_trend["delta_from_previous"]) >= 0 else "warning"),
            pill(f"Regressions {len(score_trend['regressions'])}", "warning" if score_trend["regressions"] else "good"),
            pill(f"{config_edges} config/runtime edges"),
            "</div>",
            "</div>",
            "</div>",
            "</section>",
            "<section class='panel'>",
            "<h2>Diff + Freshness</h2>",
            "<div class='section-copy'>See exactly what changed, which domains are stale, and what remains safe to reuse.</div>",
            "<div class='dashboard-columns'>",
            f"<div><div class='micro-label'>Changed Files</div><ul class='list'>{changed_files_markup}</ul></div>",
            f"<div><div class='micro-label'>Impacted Domains</div><ul class='list'>{impacted_markup}</ul></div>",
            "</div>",
            "<div class='legend'>",
            pill(f"Current domains: {', '.join(diff['current_domains'][:4]) or 'none'}"),
            pill(f"Git event {str(diff['git']['event_type']).replace('_', ' ')}"),
            pill(f"Freshness {int(round(float(diff['freshness_score'])))} / {int(diff['freshness_max'])}", "good" if float(diff["freshness_score"]) >= 20 else "warning"),
            "</div>",
            "</section>",
            "<section class='panel'>",
            "<h2>Architecture Materialization</h2>",
            "<div class='section-copy'>Skilgen uses the architecture plan to decide where skills should split, merge, or stay consolidated.</div>",
            "<table><thead><tr><th>Domain</th><th>Decision</th><th>Parent Skill</th><th>Child Skills</th><th>Rationale</th></tr></thead><tbody>",
            plan_rows,
            "</tbody></table>",
            f"<div class='domain-grid'>{domain_cards}</div>",
            "</section>",
            "<section class='panel'>",
            "<h2>Auto-Update + Agent Readiness</h2>",
            "<div class='section-copy'>A live operations board for the worker, the last repo event, the start order, and the repo-local outputs currently ready to load.</div>",
            "<div class='ops-board'>",
            "<div class='ops-tabs'>",
            "<button class='ops-tab active' data-target='worker'>Worker</button>",
            "<button class='ops-tab' data-target='event'>Last Event</button>",
            "<button class='ops-tab' data-target='order'>Start Order</button>",
            "<button class='ops-tab' data-target='outputs'>Outputs</button>",
            "</div>",
            "<div class='ops-copy active' data-copy='worker'>"
            f"<div class='ops-grid'><div class='ops-tile'><strong>Worker state</strong><span>{escape('Running in background' if auto_update.get('running') else 'Idle until the next change')}</span></div><div class='ops-tile'><strong>Refresh policy</strong><span>{escape(str(auto_update.get('enabled') and 'Automatic refresh is enabled' or 'Manual refresh only'))}</span></div><div class='ops-tile'><strong>Current freshness</strong><span>{int(round(float(diff['freshness_score'])))}/{int(diff['freshness_max'])}</span></div><div class='ops-tile'><strong>Readiness signal</strong><span>{escape('Agents can load the current repo-local outputs now')}</span></div></div>"
            "</div>",
            "<div class='ops-copy' data-copy='event'>"
            f"<div class='ops-grid'><div class='ops-tile'><strong>Last git-aware event</strong><span>{escape(str(auto_update.get('last_event') or diff['git'].get('event_type') or 'none').replace('_', ' '))}</span></div><div class='ops-tile'><strong>Reason</strong><span>{escape(str(diff['reason']).replace('_', ' '))}</span></div><div class='ops-tile'><strong>Changed files</strong><span>{changed_count}</span></div><div class='ops-tile'><strong>Stale skills</strong><span>{stale_count}</span></div></div>"
            "</div>",
            "<div class='ops-copy' data-copy='order'>"
            f"<div class='ops-grid'><div class='ops-tile'><strong>Decision focus</strong><span>{escape(', '.join(decision.get('prioritized_domains', [])[:4]) or 'No prioritized domains yet')}</span></div><div class='ops-tile'><strong>Memory load</strong><span>{escape(', '.join(decision.get('memory_to_load', [])[:3]) or 'No memory recommended')}</span></div><div class='ops-tile'><strong>Prioritized skills</strong><span>{escape(', '.join(decision.get('prioritized_skill_paths', [])[:3]) or 'No prioritized skills yet')}</span></div><div class='ops-tile'><strong>Nuance</strong><span>{escape('Skilgen is sequencing agent context from evidence, score, diff, and architecture state instead of a static startup order.')}</span></div></div>"
            "</div>",
            "<div class='ops-copy' data-copy='outputs'>"
            f"<div class='micro-label'>Generated Outputs</div><ul class='list'>{outputs_markup}</ul><div class='micro-label'>Prioritized Skills</div><ul class='list'>{list_items(decision.get('prioritized_skill_paths', [])[:6], empty='No prioritized skills yet')}</ul>"
            "</div>",
            "</div>",
            "</section>",
            "<section class='panel'>",
            "<h2>Capability Layer</h2>",
            "<div class='section-copy'>External skills, enterprise packs, and MCP connectors share the same operating surface.</div>",
            "<div class='surface-tabs'>",
            "<button class='surface-tab active' data-target='external'>External Skills</button>",
            "<button class='surface-tab' data-target='enterprise'>Enterprise Skills</button>",
            "<button class='surface-tab' data-target='connectors'>MCP Connectors</button>",
            "</div>",
            "<div class='surface-copy active' data-copy='external'><div class='mini-panel'><div class='micro-label'>External skills present</div><ul>"
            + external_markup
            + "</ul><p class='nuance-copy'>These packs were installed because the repository signaled they were relevant, so the skill system includes ecosystem knowledge as well as repo-native guidance.</p></div></div>",
            "<div class='surface-copy' data-copy='enterprise'><div class='mini-panel'><div class='micro-label'>Enterprise skills present</div><ul>"
            + enterprise_markup
            + "</ul><p class='nuance-copy'>Enterprise packs let the repo-local skill map inherit organization-specific standards, playbooks, and internal conventions.</p></div></div>",
            "<div class='surface-copy' data-copy='connectors'><div class='mini-panel'><div class='micro-label'>Capability connectors</div><ul>"
            + connector_markup
            + "</ul><p class='nuance-copy'>Connectors make the skill map operational by binding domains to approved enterprise capabilities instead of leaving them as static prose.</p></div></div>",
            "</section>",
            "<p class='footer-note'>Generated by Skilgen from live repository evidence, architecture synthesis, score history, diff state, analytics, and enterprise capability context.</p>",
            "</section>",
            "</div>",
            f"<script>window.__SKILGEN_GRAPHS__ = {graph_payload_json}; window.__SKILGEN_NETWORKS__ = {network_payload_json}; window.__SKILGEN_SUNBURST__ = {sunburst_payload_json}; window.__SKILGEN_SANKEY__ = {sankey_payload_json}; const tabs=[...document.querySelectorAll('.graph-tab')]; const panels=[...document.querySelectorAll('.graph-stage .graph-panel')]; const copies=[...document.querySelectorAll('.graph-aside .graph-copy')]; const opsTabs=[...document.querySelectorAll('.ops-tab')]; const opsCopies=[...document.querySelectorAll('.ops-copy')]; const surfaceTabs=[...document.querySelectorAll('.surface-tab')]; const surfaceCopies=[...document.querySelectorAll('.surface-copy')]; const tooltip=document.createElement('div'); tooltip.className='tooltip'; document.body.appendChild(tooltip); const showTooltip=(event,title,body='')=>{{ tooltip.innerHTML=`<strong>${{title}}</strong>${{body}}`; tooltip.style.left=`${{event.pageX}}px`; tooltip.style.top=`${{event.pageY-16}}px`; tooltip.style.opacity='1'; }}; const hideTooltip=()=>{{ tooltip.style.opacity='0'; }}; const activateSet=(buttons,panels,target,buttonKey,panelKey)=>{{ buttons.forEach((button)=>button.classList.toggle('active',button.dataset[buttonKey]===target)); panels.forEach((panel)=>panel.classList.toggle('active',panel.dataset[panelKey]===target)); }}; const networkOptions={{autoResize:true,physics:{{stabilization:true,barnesHut:{{gravitationalConstant:-3200,centralGravity:0.18,springLength:132,springConstant:0.03}}}},interaction:{{hover:true,navigationButtons:true,keyboard:true}},nodes:{{shape:'dot',borderWidth:2,font:{{color:'#F6F7FB',face:'Inter'}},color:{{border:'#EFD37A',background:'#11161E',highlight:{{border:'#F8DF8E',background:'#1B2430'}}}}}},edges:{{color:{{color:'rgba(255,255,255,0.26)',highlight:'#EFD37A'}},smooth:true,width:1.2}},groups:{{repo:{{size:38,color:{{border:'#F8DF8E',background:'#1B1A12'}}}},source:{{size:15,color:{{border:'#F6F7FB',background:'#171A21'}}}},target:{{size:13,color:{{border:'#B7C0D0',background:'#11161E'}}}}}}}}; const renderedNetworks=new Map(); const renderNetwork=(target, canvas)=>{{ if(!window.vis) return; const graph=window.__SKILGEN_NETWORKS__[target]; if(renderedNetworks.has(target)){{ const existing=renderedNetworks.get(target); existing.setData({{nodes:new vis.DataSet(graph.nodes),edges:new vis.DataSet(graph.edges)}}); existing.redraw(); existing.fit({{animation:true}}); return; }} const data={{nodes:new vis.DataSet(graph.nodes),edges:new vis.DataSet(graph.edges)}}; const network=new vis.Network(canvas,data,networkOptions); renderedNetworks.set(target,network); network.once('stabilized',()=>network.fit({{animation:true}})); network.on('hoverNode',(params)=>{{ const node=graph.nodes.find((entry)=>entry.id===params.node); if(node) showTooltip(params.event.event,node.label,node.title||''); }}); network.on('blurNode',hideTooltip); setTimeout(()=>{{ network.redraw(); network.fit({{animation:true}}); }},80); }}; const renderSunburst=(container)=>{{ if(container.dataset.loaded||!window.d3) return; container.dataset.loaded='1'; const width=container.clientWidth||860; const height=container.clientHeight||520; const radius=Math.min(width,height)/2-18; const root=d3.hierarchy(window.__SKILGEN_SUNBURST__).sum((d)=>d.value||1).sort((a,b)=>b.value-a.value); d3.partition().size([2*Math.PI, root.height+1])(root); root.each((d)=>d.current=d); const color=d3.scaleOrdinal().domain(root.descendants().map((d)=>d.data.name)).range(['#EFD37A','#F8DF8E','#F6F7FB','#B9C2D4','#8FD9A8','#FFB86B','#6DA5FF','#C191FF']); const svg=d3.select(container).append('svg').attr('viewBox',`${{-width/2}} ${{-height/2}} ${{width}} ${{height}}`).style('font','12px Inter'); const ringScale=radius/(root.height+1); const arc=d3.arc().startAngle((d)=>d.x0).endAngle((d)=>d.x1).padAngle((d)=>Math.min((d.x1-d.x0)/2,0.008)).padRadius(radius*1.4).innerRadius((d)=>Math.max(0,d.y0*ringScale)).outerRadius((d)=>Math.max(d.y0*ringScale,d.y1*ringScale-2)); const arcVisible=(d)=>d.y1<=3&&d.y0>=1&&d.x1>d.x0; const labelVisible=(d)=>arcVisible(d)&&((d.x1-d.x0)*(d.y1-d.y0))>0.16; const labelTransform=(d)=>{{ const x=(d.x0+d.x1)/2*180/Math.PI; const y=(d.y0+d.y1)/2*ringScale; return `rotate(${{x-90}}) translate(${{y}},0) rotate(${{x<180?0:180}})`; }}; const center=svg.append('g').attr('pointer-events','none'); const label=center.append('text').attr('text-anchor','middle').attr('fill','#F6F7FB').style('font-size','18px').style('font-weight','700').text(root.data.name); center.append('text').attr('text-anchor','middle').attr('fill','#98A1B2').attr('dy','1.8em').text('click to zoom'); const path=svg.append('g').selectAll('path').data(root.descendants().slice(1)).join('path').attr('fill',(d)=>{{ let current=d; while(current.depth>1) current=current.parent; return color(current.data.name); }}).attr('fill-opacity',(d)=>d.children?0.92:0.74).attr('d',(d)=>arc(d.current)).style('cursor','pointer').on('click',(_,p)=>clicked(p)).on('mousemove',(event,d)=>showTooltip(event,d.data.name,d.data.summary||d.data.name)).on('mouseleave',hideTooltip); const text=svg.append('g').attr('pointer-events','none').attr('text-anchor','middle').style('user-select','none').selectAll('text').data(root.descendants().slice(1)).join('text').attr('dy','0.35em').attr('fill','#F6F7FB').attr('fill-opacity',(d)=>+labelVisible(d.current)).attr('transform',(d)=>labelTransform(d.current)).text((d)=>d.data.name); const parent=svg.append('circle').datum(root).attr('r',radius/(root.height+1)).attr('fill','transparent').attr('pointer-events','all').on('click',(_,p)=>clicked(p)); function clicked(p){{ parent.datum(p.parent||root); root.each((d)=>d.target={{ x0:Math.max(0,Math.min(1,(d.x0-p.x0)/(p.x1-p.x0)))*2*Math.PI, x1:Math.max(0,Math.min(1,(d.x1-p.x0)/(p.x1-p.x0)))*2*Math.PI, y0:Math.max(0,d.y0-p.depth), y1:Math.max(0,d.y1-p.depth) }}); const t=svg.transition().duration(750); path.transition(t).tween('data',(d)=>{{ const i=d3.interpolate(d.current,d.target); return (tick)=>d.current=i(tick); }}).filter(function(d){{ return +this.getAttribute('fill-opacity')||arcVisible(d.target); }}).attr('fill-opacity',(d)=>arcVisible(d.target)?(d.children?0.92:0.74):0).attrTween('d',(d)=>()=>arc(d.current)); text.filter(function(d){{ return +this.getAttribute('fill-opacity')||labelVisible(d.target); }}).transition(t).attr('fill-opacity',(d)=>+labelVisible(d.target)).attrTween('transform',(d)=>()=>labelTransform(d.current)); label.text(p.data.name); }} }}; const renderedSankeys=new Map(); const renderSankey=(target, container)=>{{ if(!window.d3||!window.d3.sankey||renderedSankeys.has(target)&&container.dataset.loaded==='1') return; container.dataset.loaded='1'; container.innerHTML=''; const width=container.clientWidth||860; const height=container.clientHeight||520; const raw=window.__SKILGEN_SANKEY__[target]; const graph={{nodes:raw.nodes.map((d)=>({{...d}})),links:raw.links.map((d)=>({{...d}}))}}; const svg=d3.select(container).append('svg').attr('viewBox',`0 0 ${{width}} ${{height}}`); const sankey=d3.sankey().nodeId((d)=>d.id).nodeWidth(18).nodePadding(20).extent([[16,18],[width-16,height-18]]); const {{nodes,links}}=sankey(graph); svg.append('g').selectAll('path').data(links).join('path').attr('d',d3.sankeyLinkHorizontal()).attr('stroke',target==='analytics'?'rgba(143,217,168,0.44)':'rgba(239,211,122,0.42)').attr('stroke-width',(d)=>Math.max(1,d.width)).attr('fill','none').attr('stroke-opacity',0.82).on('mousemove',(event,d)=>showTooltip(event,`${{d.source.name}} → ${{d.target.name}}`,`Value ${{d.value}}`)).on('mouseleave',hideTooltip); const node=svg.append('g').selectAll('g').data(nodes).join('g'); node.append('rect').attr('x',(d)=>d.x0).attr('y',(d)=>d.y0).attr('height',(d)=>Math.max(1,d.y1-d.y0)).attr('width',(d)=>d.x1-d.x0).attr('rx',7).attr('fill',(d)=>d.layer===1?'#EFD37A':d.layer===2?'#B9C2D4':d.layer===3&&target==='analytics'?'#8FD9A8':'#11161E').attr('stroke','#F6F7FB').attr('stroke-opacity',0.32).on('mousemove',(event,d)=>showTooltip(event,d.name,`Layer ${{d.layer}}`)).on('mouseleave',hideTooltip); node.append('text').attr('x',(d)=>d.x0<width/2?d.x1+8:d.x0-8).attr('y',(d)=>(d.y1+d.y0)/2).attr('dy','0.35em').attr('text-anchor',(d)=>d.x0<width/2?'start':'end').attr('fill','#F6F7FB').style('font','12px Inter').text((d)=>d.name); renderedSankeys.set(target,true); }}; const setPanel=async(target)=>{{ activateSet(tabs,panels,target,'target','panel'); activateSet(tabs,copies,target,'target','copy'); const panel=document.querySelector(`.graph-panel[data-panel=\"${{target}}\"]`); const networkCanvas=panel?.querySelector('.network-canvas'); if(networkCanvas){{ renderNetwork(target,networkCanvas); return; }} const sunburstCanvas=panel?.querySelector('.sunburst-canvas'); if(sunburstCanvas){{ renderSunburst(sunburstCanvas); return; }} const sankeyCanvas=panel?.querySelector('.sankey-canvas'); if(sankeyCanvas){{ renderSankey(target,sankeyCanvas); }} }}; tabs.forEach((tab)=>tab.addEventListener('click',()=>setPanel(tab.dataset.target))); opsTabs.forEach((tab)=>tab.addEventListener('click',()=>activateSet(opsTabs,opsCopies,tab.dataset.target,'target','copy'))); surfaceTabs.forEach((tab)=>tab.addEventListener('click',()=>activateSet(surfaceTabs,surfaceCopies,tab.dataset.target,'target','copy'))); const analyticsCanvas=document.querySelector('[data-sankey=\"analytics\"]'); if(analyticsCanvas) renderSankey('analytics', analyticsCanvas); setPanel('architecture'); if(opsTabs.length) activateSet(opsTabs,opsCopies,'worker','target','copy'); if(surfaceTabs.length) activateSet(surfaceTabs,surfaceCopies,'external','target','copy');</script>",
            "</body>",
            "</html>",
        ]
    )


def ensure_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def project_doc_paths(project_root: Path) -> list[Path]:
    return [
        project_root / "AGENTS.md",
        project_root / "ANALYSIS.md",
        project_root / "ARCHITECTURE.md",
        project_root / "FEATURES.md",
        project_root / "REPORT.md",
        project_root / "TRACEABILITY.md",
        project_root / "skilgen-dashboard.html",
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


def render_analysis_report(
    context: RequirementsContext,
    project_root: Path,
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    fingerprint = bundle.fingerprint
    signals = bundle.signals
    import_graph = bundle.import_graph
    codebase_context = bundle.codebase_context
    evidence_graph = bundle.evidence_graph
    architecture = bundle.architecture
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
        "evidence_graph": evidence_graph.__dict__ | {"items": [item.__dict__ for item in evidence_graph.items]},
        "architecture": architecture.__dict__
        | {
            "domains": [domain.__dict__ for domain in architecture.domains],
            "materialization_plan": [item.__dict__ for item in architecture.materialization_plan],
        },
    }
    return "\n".join(["# Analysis", "", "```json", json.dumps(payload, indent=2), "```", ""])


def render_architecture_report(
    context: RequirementsContext,
    project_root: Path,
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    architecture = bundle.architecture
    dominant_languages = [f"- `{language}`" for language in evidence_graph.dominant_languages] or ["- none"]
    source_summary = [
        f"- Symbol graph files: `{len(evidence_graph.symbol_graph)}`",
        f"- Call graph files: `{len(evidence_graph.call_graph)}`",
        f"- Config/runtime files: `{len(evidence_graph.config_runtime_graph)}`",
        f"- Tests mapped to code: `{len(evidence_graph.test_mapping)}`",
    ]
    backend_counts: dict[str, int] = {}
    for payload in evidence_graph.parser_summary.values():
        backend = str(payload.get("backend", "unknown"))
        backend_counts[backend] = backend_counts.get(backend, 0) + 1
    parser_lines = [f"- `{backend}`: `{count}` files" for backend, count in sorted(backend_counts.items())] or ["- none"]
    lines = [
        "# Architecture",
        "",
        f"## {architecture.headline}",
        "",
        architecture.system_summary,
        "",
        "## Visual Overview",
        "```mermaid",
        render_architecture_graph_mermaid(context, project_root, bundle),
        "```",
        "",
        "## Dominant Languages",
        *dominant_languages,
        "",
        "## Source Comprehension",
        *source_summary,
        "",
        "## Parser Backends",
        *parser_lines,
        "",
        "### Example Symbol Surfaces",
    ]
    if evidence_graph.symbol_graph:
        for path, symbols in list(evidence_graph.symbol_graph.items())[:8]:
            lines.append(f"- `{path}`: {', '.join(f'`{symbol}`' for symbol in symbols[:4])}")
    else:
        lines.append("- No symbol graph entries were extracted.")
    lines.extend(
        [
            "",
            "### Example Config And Runtime Signals",
        ]
    )
    if evidence_graph.config_runtime_graph:
        for path, entries in list(evidence_graph.config_runtime_graph.items())[:8]:
            lines.append(f"- `{path}`: {', '.join(f'`{entry}`' for entry in entries[:5])}")
    else:
        lines.append("- No config/runtime graph entries were extracted.")
    lines.extend(
        [
            "",
            "### Example Test Mapping",
        ]
    )
    if evidence_graph.test_mapping:
        for path, targets in list(evidence_graph.test_mapping.items())[:8]:
            lines.append(f"- `{path}` -> {', '.join(f'`{target}`' for target in targets[:4])}")
    else:
        lines.append("- No test-to-code mappings were extracted.")
    lines.extend(
        [
            "",
            "## Skill Materialization Plan",
        ]
    )
    if architecture.materialization_plan:
        for item in architecture.materialization_plan[:10]:
            lines.append(f"### {item.domain}")
            lines.append(f"- Decision: `{item.decision}`")
            lines.append(f"- Parent skill: `{item.parent_skill_path}`")
            if item.child_skill_paths:
                lines.append("- Child skills:")
                lines.extend(f"  - `{path}`" for path in item.child_skill_paths[:8])
            if item.cross_links:
                lines.append("- Cross-links:")
                lines.extend(f"  - `{path}`" for path in item.cross_links[:8])
            lines.append(f"- Rationale: {item.rationale}")
            lines.append("")
    else:
        lines.extend(["- No materialization plan was inferred.", ""])
    lines.extend(
        [
            "## Architecture Domains",
        ]
    )
    
    for domain in architecture.domains:
        lines.append(f"### {domain.name}")
        lines.append(f"- Confidence: `{domain.confidence:.2f}`")
        lines.append(f"- Summary: {domain.summary}")
        if domain.responsibilities:
            lines.append("- Responsibilities:")
            lines.extend(f"  - {item}" for item in domain.responsibilities[:5])
        if domain.evidence_paths:
            lines.append("- Evidence paths:")
            lines.extend(f"  - `{item}`" for item in domain.evidence_paths[:6])
        if domain.related_domains:
            lines.append(f"- Related domains: {', '.join(f'`{item}`' for item in domain.related_domains)}")
        if domain.recommended_skill_path:
            lines.append(f"- Recommended skill path: `{domain.recommended_skill_path}`")
        lines.append("")
    lines.extend(["## Evidence Graph Recommendations"])
    lines.extend(f"- {item}" for item in evidence_graph.recommendations[:8])
    lines.append("")
    if architecture.hotspots:
        lines.append("## Hotspots")
        lines.extend(f"- {item}" for item in architecture.hotspots[:8])
        lines.append("")
    return "\n".join(lines)


def _render_traceability_report_native(
    context: RequirementsContext,
    project_root: Path,
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    intent = parse_project_intent(project_root, requirements_path)
    bundle = bundle or _analysis_bundle(context, project_root)
    signals = bundle.signals
    codebase_context = bundle.codebase_context
    architecture = bundle.architecture
    installed_skill_packs = installed_external_skills(project_root)
    ranked_skill_packs = ranked_external_skills(project_root).get("skills", [])
    enterprise_skill_packs = active_enterprise_skills(project_root)
    active_connectors = active_mcp_connectors(project_root)
    recommended_connectors = recommend_mcp_connectors(project_root).get("connectors", [])
    policy = external_skill_policy(project_root)
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

    lines.extend(["## Architecture Traceability", ""])
    for domain in architecture.domains[:10]:
        lines.append(f"### {domain.name}")
        lines.append(f"- Summary: {domain.summary}")
        lines.append(f"- Evidence paths: {', '.join(f'`{item}`' for item in domain.evidence_paths) if domain.evidence_paths else 'none'}")
        lines.append(f"- Recommended skill path: `{domain.recommended_skill_path or 'none'}`")
        lines.append("")

    lines.extend(
        [
            "## Generated Outputs",
            "- `ANALYSIS.md` for full machine-readable project analysis",
            "- `ARCHITECTURE.md` for evidence-backed domain architecture",
            "- `FEATURES.md` for detected and planned feature inventory",
            "- `REPORT.md` for human-readable summary",
            "- `skills/MANIFEST.md` and `skills/GRAPH.md` for skill discovery",
            "- `skills/<domain>/SKILL.md` for domain-specific execution guidance",
            "",
        ]
    )
    lines.extend(["## External Skill Traceability"])
    lines.append(f"- Policy mode: `{policy['policy_mode']}`")
    if installed_skill_packs:
        for entry in installed_skill_packs[:8]:
            provenance = entry.get("provenance", {}) if isinstance(entry.get("provenance"), dict) else {}
            license_payload = entry.get("license", {}) if isinstance(entry.get("license"), dict) else {}
            lines.append(
                f"- Installed `{entry.get('slug', 'unknown')}` from `{provenance.get('repository_url', entry.get('repository_url', 'unknown'))}`"
            )
            lines.append(f"  Trust: `{entry.get('trust_level', 'unknown')}` score `{entry.get('trust_score', 0)}`")
            lines.append(f"  License: `{license_payload.get('summary', 'unknown')}`")
            if provenance.get("imported_from"):
                lines.append(f"  Imported from directory source: `{provenance['imported_from']}`")
    else:
        lines.append("- No external skill packs were installed for this run.")
    if ranked_skill_packs:
        lines.append("")
        lines.append("### Preferred External Packs")
        for entry in ranked_skill_packs[:5]:
            lines.append(f"- `{entry['slug']}`: {entry.get('priority_reason', 'Ranked by trust and repo fit.')}")
    lines.append("")
    lines.append("## Enterprise Skill Traceability")
    if enterprise_skill_packs:
        for entry in enterprise_skill_packs[:8]:
            lines.append(f"- Enterprise skill `{entry.get('slug', 'unknown')}` from `{entry.get('install_path', 'unknown')}`")
            lines.append(f"  Kind: `{entry.get('kind', 'enterprise')}`")
            if entry.get("readme"):
                lines.append(f"  Summary: {entry['readme'].get('summary', 'No summary available.')}")
    else:
        lines.append("- No active enterprise skills were installed for this run.")
    lines.append("")
    lines.append("## MCP Connector Traceability")
    if active_connectors:
        for entry in active_connectors[:8]:
            lines.append(f"- Active connector `{entry.get('slug', 'unknown')}` ({entry.get('system', 'unknown')}): {entry.get('description', '')}")
            lines.append(
                f"  Source status: `{entry.get('source_status', 'unknown')}`; auth: `{entry.get('auth_scheme', 'unknown')}`; "
                f"official source verified: `{entry.get('official_source_verified', False)}`"
            )
            authorization = entry.get("authorization", {})
            if authorization:
                lines.append(f"  Authorization status: `{authorization.get('status', 'unknown')}`")
            if entry.get("official_source_url"):
                lines.append(f"  Official source: `{entry['official_source_url']}`")
            elif entry.get("recommended_source_url"):
                lines.append(f"  Recommended source: `{entry['recommended_source_url']}`")
    else:
        lines.append("- No MCP connectors are currently active.")
    if recommended_connectors:
        lines.append("")
        lines.append("### Recommended MCP Connectors")
        for entry in recommended_connectors[:6]:
            lines.append(
                f"- `{entry['slug']}` (`{entry.get('source_status', 'unknown')}`, oauth `{entry.get('oauth_supported', False)}`): "
                f"{'; '.join(entry.get('reasons', []))}"
            )
    lines.append("")
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


def render_traceability_report(
    context: RequirementsContext,
    project_root: Path,
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    intent = parse_project_intent(project_root, requirements_path)
    bundle = bundle or _analysis_bundle(context, project_root)
    signals = bundle.signals
    codebase_context = bundle.codebase_context
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
        lambda: _render_traceability_report_native(context, project_root, bundle),
        project_root=project_root,
    )


def _render_project_report_native(
    context: RequirementsContext,
    project_root: Path,
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    signals = bundle.signals
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    features = extract_features(requirements_path, project_root)
    codebase_context = bundle.codebase_context
    architecture = bundle.architecture
    ranked_skill_packs = ranked_external_skills(project_root).get("skills", [])
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
        f"- Architecture domains: {len(architecture.domains)}",
        "",
        "## Generated Outputs",
        "- ANALYSIS.md",
        "- ARCHITECTURE.md",
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
    if architecture.domains:
        lines.extend(["", "## Architecture Highlights"])
        for domain in architecture.domains[:5]:
            lines.append(f"- `{domain.name}`: {domain.summary}")
    lines.extend(
        [
            "",
            "## External Skill Packs",
            f"- Installed packs: {len(installed_external_skills(project_root))}",
            f"- Active packs: {len(active_external_skills(project_root))}",
        ]
    )
    if ranked_skill_packs:
        lines.append("- Preferred packs to load first:")
        for entry in ranked_skill_packs[:5]:
            lock_metadata = entry.get("lock_metadata", {})
            if not isinstance(lock_metadata, dict):
                lock_metadata = {}
            license_payload = lock_metadata.get("license", {})
            if not isinstance(license_payload, dict):
                license_payload = {}
            lines.append(
                f"  - `{entry['slug']}` (score {entry.get('priority_score', 0)}, trust `{entry.get('trust_level', 'unknown')}`, license `{license_payload.get('summary', 'unknown')}`)"
            )
    else:
        lines.append("- No active external skill packs have been ranked yet.")
    imported_packs = [
        entry
        for entry in installed_external_skills(project_root)
        if isinstance(entry.get("provenance"), dict) and entry["provenance"].get("imported_from")
    ]
    lines.extend(["", "## External Skill Provenance"])
    if installed_external_skills(project_root):
        for entry in installed_external_skills(project_root)[:8]:
            provenance = entry.get("provenance", {}) if isinstance(entry.get("provenance"), dict) else {}
            lines.append(
                f"- `{entry.get('slug', 'unknown')}` from `{provenance.get('repository_url', entry.get('repository_url', 'unknown'))}` at `{provenance.get('resolved_revision', entry.get('resolved_revision', 'unknown'))}`"
            )
            if provenance.get("imported_from"):
                lines.append(f"  Imported from: `{provenance['imported_from']}`")
    else:
        lines.append("- No external skill packs have been installed yet.")
    if imported_packs:
        lines.append("")
        lines.append("### Imported Directory Candidates")
        for entry in imported_packs[:8]:
            provenance = entry.get("provenance", {}) if isinstance(entry.get("provenance"), dict) else {}
            lines.append(f"- `{entry.get('slug', 'unknown')}` imported from `{provenance.get('imported_from', 'unknown')}`")
    lines.append("")
    return "\n".join(lines)


def render_project_report(
    context: RequirementsContext,
    project_root: Path,
    bundle: ProjectAnalysisBundle | None = None,
) -> str:
    bundle = bundle or _analysis_bundle(context, project_root)
    signals = bundle.signals
    requirements_path = context.requirements_path if context.requirements_path.exists() else None
    features = extract_features(requirements_path, project_root)
    codebase_context = bundle.codebase_context
    return run_deep_text(
        "project report synthesis",
        (
            "Write a concise markdown project report for Skilgen with sections Summary, Generated Outputs, and Recommended Starting Points.\n\n"
            f"Signals JSON:\n{json.dumps(signals.__dict__, indent=2)}\n\n"
            f"Features count: {len(features)}\n"
            f"Detected domains JSON:\n{json.dumps([record.__dict__ for record in codebase_context.detected_domains], indent=2)}"
        ),
        lambda: _render_project_report_native(context, project_root, bundle),
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
    ranked_skill_packs = ranked_external_skills(project_root).get("skills", [])
    enterprise_skill_packs = active_enterprise_skills(project_root)
    active_connectors = active_mcp_connectors(project_root)
    recommended_connectors = recommend_mcp_connectors(project_root).get("connectors", [])
    policy = external_skill_policy(project_root)
    external_skill_lines = [
        f"- `{entry['slug']}` ({entry.get('ecosystem', 'unknown')}, trust `{entry.get('trust_level', 'unknown')}`): installed at `{entry.get('install_path', '')}`"
        for entry in installed_skill_packs
    ] or ["- No external skill packs have been installed yet."]
    active_external_lines = [
        f"- `{entry['slug']}` ({entry.get('lock_metadata', {}).get('normalized', {}).get('adapter', 'raw')}, trust score {entry.get('lock_metadata', {}).get('trust_score', entry.get('trust_score', 0))}): load from `{entry.get('install_path', '')}`"
        for entry in active_skill_packs
    ] or ["- No external skill packs are currently active."]
    ranked_external_lines = [
        f"- `{entry['slug']}` (score {entry.get('priority_score', 0)}): {entry.get('priority_reason', 'Ranked by trust and repo fit.')}"
        for entry in ranked_skill_packs
    ] or ["- No active external skill packs have been ranked yet."]
    recommended_external_lines = [
        f"- `{entry['slug']}`: {'; '.join(entry.get('reasons', []))}"
        for entry in detect_external_skill_sources(project_root).get("manual_recommendations", [])
    ] or ["- No additional external skill recommendations were inferred."]
    enterprise_skill_lines = [
        f"- `{entry['slug']}` ({entry.get('kind', 'enterprise')}): installed at `{entry.get('install_path', '')}`"
        for entry in enterprise_skill_packs
    ] or ["- No enterprise skill packs are currently active."]
    connector_lines = [
        (
            f"- `{entry['slug']}` ({entry.get('system', 'unknown')}, "
            f"source `{entry.get('source_status', 'unknown')}`, auth `{entry.get('auth_scheme', 'unknown')}`): "
            f"{entry.get('description', '')}"
        )
        for entry in active_connectors
    ] or ["- No MCP connectors are currently active."]
    recommended_connector_lines = [
        (
            f"- `{entry['slug']}` (source `{entry.get('source_status', 'unknown')}`, "
            f"oauth `{entry.get('oauth_supported', False)}`): {'; '.join(entry.get('reasons', []))}"
        )
        for entry in recommended_connectors
    ] or ["- No MCP connectors were recommended."]
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
            "## External Skill Policy",
            f"- Policy mode: `{policy['policy_mode']}`",
            f"- Auto install enabled: `{policy['auto_install_enabled']}`",
            f"- Auto activate enabled: `{policy['auto_activate_enabled']}`",
            "",
            "## Preferred External Skill Packs",
            *ranked_external_lines,
            "",
            "## Enterprise Skill Packs",
            *enterprise_skill_lines,
            "",
            "## MCP Connectors",
            *connector_lines,
            "",
            "## Recommended MCP Connectors",
            *recommended_connector_lines,
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
    bundle = _analysis_bundle(context, project_root)
    agents = render_agents_contract(context, project_root)
    analysis = render_analysis_report(context, project_root, bundle)
    architecture = render_architecture_report(context, project_root, bundle)
    features = render_feature_inventory(context)
    report = render_project_report(context, project_root, bundle)
    traceability = render_traceability_report(context, project_root, bundle)
    from skilgen.deep_agents_runtime import native_dashboard_payload

    dashboard_html = str(native_dashboard_payload(project_root, context.requirements_path if context.requirements_path.exists() else None)["html"])
    written.append(ensure_file(project_root / "AGENTS.md", agents))
    written.append(ensure_file(project_root / "ANALYSIS.md", analysis))
    written.append(ensure_file(project_root / "ARCHITECTURE.md", architecture))
    written.append(ensure_file(project_root / "FEATURES.md", features))
    written.append(ensure_file(project_root / "REPORT.md", report))
    written.append(ensure_file(project_root / "TRACEABILITY.md", traceability))
    written.append(ensure_file(project_root / "skilgen-dashboard.html", dashboard_html))
    config_path = project_root / "skilgen.yml"
    if not config_path.exists():
        written.append(ensure_file(config_path, render_default_config()))
    return written
