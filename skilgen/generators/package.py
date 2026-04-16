from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
import json
import re
import sys
from pathlib import Path
from typing import Callable

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


ProgressCallback = Callable[[str], None]


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _trend_label(entry: dict[str, object], index: int, total: int) -> str:
    timestamp = str(entry.get("timestamp", "")).strip()
    if timestamp:
        try:
            normalized = timestamp.replace("Z", "+00:00")
            moment = datetime.fromisoformat(normalized)
            return moment.strftime("%b %d %H:%M:%S")
        except ValueError:
            pass
    if index == total - 1:
        return "Current"
    return f"Run {index + 1}"


def _trend_signature(entry: dict[str, object]) -> tuple[float, float, str, tuple[tuple[str, float], ...]]:
    raw_domain_scores = entry.get("domain_scores", {})
    if not isinstance(raw_domain_scores, dict):
        raw_domain_scores = {}
    domain_scores = tuple(
        sorted((str(key), round(float(value), 2)) for key, value in raw_domain_scores.items())
    )
    return (
        round(float(entry.get("score", 0.0)), 2),
        round(float(entry.get("raw_score", entry.get("score", 0.0))), 2),
        str(entry.get("rating", "")),
        domain_scores,
    )


def _meaningful_trend_points(
    score_history: list[dict[str, object]],
    current_score: dict[str, object],
    *,
    limit: int = 8,
) -> list[dict[str, object]]:
    snapshots = [dict(item) for item in score_history]
    current_snapshot = {
        "timestamp": "",
        "source": "current",
        "score": current_score.get("score", 0.0),
        "raw_score": current_score.get("raw_score", current_score.get("score", 0.0)),
        "rating": current_score.get("rating", ""),
        "domain_scores": {
            str(item.get("domain", "")): float(item.get("score", 0.0))
            for item in current_score.get("domains", [])
        },
    }
    if not snapshots or _trend_signature(snapshots[-1]) != _trend_signature(current_snapshot):
        snapshots.append(current_snapshot)

    if not snapshots:
        return [current_snapshot]

    compressed: list[dict[str, object]] = []
    for snapshot in snapshots:
        if not compressed or _trend_signature(compressed[-1]) != _trend_signature(snapshot):
            compressed.append(snapshot)

    if len(compressed) == 1 and len(snapshots) > 1:
        return [snapshots[0], snapshots[-1]][-limit:]
    return compressed[-limit:]


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


def _graph_domain_name(value: str) -> str:
    mapping = {
        "requirements": "Planning",
        "backend": "Services",
        "frontend": "Experience",
        "roadmap": "Delivery",
    }
    return mapping.get(value, _display_domain_name(value))


def _display_skill_name(path_or_name: str) -> str:
    cleaned = path_or_name.strip("/").split("/")[-2] if "/SKILL.md" in path_or_name and "/" in path_or_name else path_or_name
    return _display_domain_name(cleaned)


def _compact_label(value: str, *, max_length: int = 28) -> str:
    cleaned = value.strip()
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 1].rstrip() + "…"


def _count_phrase(count: int, singular: str, plural: str | None = None) -> str:
    plural_form = plural or f"{singular}s"
    return f"{count} {singular if count == 1 else plural_form}"


def _graph_skill_name(path_or_name: str) -> str:
    if "/SKILL.md" in path_or_name:
        parts = Path(path_or_name).parts
        if len(parts) >= 4:
            group = parts[-3].replace("-", " ").replace("_", " ").title()
            parent = parts[-2].replace("-", " ").replace("_", " ").title()
            if parent.lower() in {"backend", "frontend", "requirements", "roadmap"}:
                return _graph_domain_name(parent.lower())
            if group.lower() == parent.lower():
                return parent
            return parent
        if len(parts) >= 3:
            parent = parts[-2].replace("-", " ").replace("_", " ").title()
            return _graph_domain_name(parent.lower())
    return _graph_domain_name(path_or_name)


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
        "<svg class='skilgen-mark' viewBox='0 0 1200 640' fill='none' xmlns='http://www.w3.org/2000/svg' aria-label='Skilgen logo'>"
        "<defs><filter id='skilgenGlow' x='-15%' y='-15%' width='130%' height='130%'><feDropShadow dx='0' dy='12' stdDeviation='10' flood-color='rgba(0,0,0,0.42)'/></filter></defs>"
        "<g stroke-linejoin='round' stroke-linecap='round' stroke-width='16' filter='url(#skilgenGlow)'>"
        "<path d='M260 122 350 170v98l-90 48-90-48v-98l90-48Z' stroke='#F2D679'/>"
        "<path d='M510 122 600 170v98l-90 48-90-48v-98l90-48Z' stroke='#F3F4F8'/>"
        "<path d='M760 122 850 170v98l-90 48-90-48v-98l90-48Z' stroke='#F3F4F8'/>"
        "<path d='M1010 122 1100 170v98l-90 48-90-48v-98l90-48Z' stroke='#F2D679'/>"
        "<path d='M385 332 475 380v98l-90 48-90-48v-98l90-48Z' stroke='#F3F4F8'/>"
        "<path d='M635 332 725 380v98l-90 48-90-48v-98l90-48Z' stroke='#F3F4F8'/>"
        "<path d='M885 332 975 380v98l-90 48-90-48v-98l90-48Z' stroke='#F3F4F8'/>"
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
        item_id = f"item::{path}"
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
    ordered_sources = sorted(bundle.import_graph.items(), key=lambda item: (-len(item[1]), item[0]))
    for source, targets in ordered_sources:
        if edge_count >= 48:
            break
        nodes.setdefault(
            source,
            {
                "id": source,
                "label": source.split("/")[-1],
                "group": "source",
                "value": 14,
                "title": source,
                "detail_title": source.split("/")[-1],
                "detail_body": f"{source} is a connected source node in the dependency graph. Skilgen uses these relationships to reason about coupling, fan-out, and likely blast radius.",
                "detail_meta": ["Dependency role: source", f"Path: {source}"],
            },
        )
        prioritized_targets = sorted(
            targets,
            key=lambda item: (0 if "/" in item or item.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs", ".cbl", ".cob", ".cpy")) else 1, item),
        )
        for target in prioritized_targets[:5]:
            nodes.setdefault(
                target,
                {
                    "id": target,
                    "label": target.split("/")[-1],
                    "group": "target",
                    "value": 12,
                    "title": target,
                    "detail_title": target.split("/")[-1],
                    "detail_body": f"{target} is pulled into the live dependency map because it is imported or referenced by other implementation files.",
                    "detail_meta": ["Dependency role: target", f"Path: {target}"],
                },
            )
            edges.append({"from": source, "to": target})
            edge_count += 1
            if edge_count >= 48:
                break
    if not nodes:
        nodes["empty"] = {
            "id": "empty",
            "label": "No dependencies",
            "group": "repo",
            "value": 18,
            "title": "No import dependencies detected yet",
            "detail_title": "No dependencies",
            "detail_body": "Skilgen did not detect enough import or module-link evidence to draw a dependency network yet.",
            "detail_meta": ["This usually happens in very small repos or non-import-heavy codebases."],
        }
    return {"nodes": list(nodes.values()), "edges": edges}


def render_dependency_sankey_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    nodes: list[dict[str, object]] = [
        {
            "id": "dependencies",
            "name": "Dependencies",
            "layer": 0,
            "detail": "Skilgen is tracing import pressure from source files into repo modules, the Python standard library, and external packages.",
            "detail_meta": [
                "This flow surfaces which files create the most dependency pull before an agent starts editing.",
            ],
        }
    ]
    node_ids = {"dependencies"}
    links: list[dict[str, object]] = []
    internal_prefixes = {
        prefix
        for source in bundle.import_graph
        for prefix in [source.split("/", 1)[0].split(".", 1)[0]]
        if prefix
    }
    internal_prefixes.update(part for part in [project_root.name, project_root.name.replace("-", "_")] if part)
    stdlib_modules = set(getattr(sys, "stdlib_module_names", ()))
    inbound_counts: dict[str, int] = {}
    for targets in bundle.import_graph.values():
        for target in targets:
            inbound_counts[target] = inbound_counts.get(target, 0) + 1

    def ensure_node(node_id: str, name: str, layer: int) -> None:
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "name": name, "layer": layer, "detail": name, "detail_meta": []})

    def classify_target(target: str) -> tuple[str, str, str, list[str]]:
        normalized = target.strip()
        primary = normalized.split("/", 1)[0].split(".", 1)[0]
        if normalized.startswith("tests/") or normalized.startswith("tests.") or primary == "tests":
            return (
                "bucket::tests",
                "test boundary",
                "Test-only imports that shape verification pressure and blast radius during changes.",
                ["Bucket: test boundary", "Use this to see which dependencies are mostly test scaffolding or validation paths."],
            )
        if "/" in normalized or primary in internal_prefixes:
            return (
                "bucket::internal",
                "repo modules",
                "Repo-local modules and files that create direct coupling inside the codebase.",
                ["Bucket: repo modules", "These edges reveal where edits can ripple across internal implementation seams."],
            )
        if primary in stdlib_modules:
            return (
                "bucket::stdlib",
                "python stdlib",
                "Standard-library imports that shape runtime behavior without adding third-party package risk.",
                ["Bucket: python stdlib", "Useful for spotting utility-heavy files versus package-heavy files."],
            )
        return (
            "bucket::external",
            "external packages",
            "Third-party package imports that create supply, upgrade, or environment surface area.",
            ["Bucket: external packages", "Use this to spot files that rely on vendor libraries or ecosystem glue."],
        )

    edge_budget = 0
    ordered_sources = sorted(bundle.import_graph.items(), key=lambda item: (-len(item[1]), item[0]))
    for source, targets in ordered_sources[:12]:
        selected_targets = sorted(
            set(targets),
            key=lambda item: (
                0 if item.split("/", 1)[0].split(".", 1)[0] in internal_prefixes or "/" in item else 1,
                item,
            ),
        )[:4]
        if not selected_targets:
            continue
        source_id = f"source::{source}"
        ensure_node(source_id, source.split("/")[-1], 1)
        for node in nodes:
            if node["id"] == source_id:
                node["detail"] = f"{source} is a dependency source hotspot. Skilgen tracked {_count_phrase(len(targets), 'import edge')} leaving this file."
                node["detail_meta"] = [
                    f"Source path: {source}",
                    f"Tracked outgoing edges: {len(targets)}",
                ]
        links.append({"source": "dependencies", "target": source_id, "value": max(1, min(3, len(selected_targets)))})
        for target in selected_targets:
            bucket_id, bucket_name, bucket_detail, bucket_meta = classify_target(target)
            ensure_node(bucket_id, bucket_name, 2)
            for node in nodes:
                if node["id"] == bucket_id:
                    node["detail"] = bucket_detail
                    node["detail_meta"] = bucket_meta
            target_id = f"target::{target}"
            target_label = target.split("/")[-1] if "/" in target else target.split(".")[-1]
            ensure_node(target_id, target_label, 3)
            for node in nodes:
                if node["id"] == target_id:
                    node["detail"] = f"{target} is a concrete dependency endpoint in the current codebase slice."
                    node["detail_meta"] = [
                        f"Target: {target}",
                        f"Imported by {_count_phrase(inbound_counts.get(target, 0), 'tracked source file')}",
                        f"Bucket: {bucket_name}",
                    ]
            links.append({"source": source_id, "target": bucket_id, "value": 1})
            links.append({"source": bucket_id, "target": target_id, "value": 1})
            edge_budget += 1
            if edge_budget >= 40:
                break
        if edge_budget >= 40:
            break

    if len(nodes) == 1:
        ensure_node("bucket::empty", "no dependencies", 2)
        links.append({"source": "dependencies", "target": "bucket::empty", "value": 1})
        for node in nodes:
            if node["id"] == "bucket::empty":
                node["detail"] = "Skilgen did not detect enough import relationships to build a dependency flow yet."
                node["detail_meta"] = ["This usually happens in very small repos or repos without import-heavy code." ]
    return {"nodes": nodes, "links": links}


def render_architecture_sunburst_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    architecture = bundle.architecture
    plans = {item.domain: item for item in architecture.materialization_plan}
    root: dict[str, object] = {
        "name": "Architecture",
        "summary": "Skilgen architecture view built from file-level evidence, parser output, and materialization planning.",
        "detail_meta": [
            "Rooted in parser-backed evidence, symbols, tests, docs, and config/runtime signals.",
            "Click a domain to inspect why Skilgen separated that capability boundary.",
        ],
        "children": [],
    }
    for domain in architecture.domains:
        plan = plans.get(domain["name"] if isinstance(domain, dict) else domain.name)
        domain_name = domain["name"] if isinstance(domain, dict) else domain.name
        domain_label = _graph_domain_name(domain_name)
        domain_summary = domain["summary"] if isinstance(domain, dict) else domain.summary
        responsibilities = domain["responsibilities"] if isinstance(domain, dict) else domain.responsibilities
        evidence_paths = domain["evidence_paths"] if isinstance(domain, dict) else domain.evidence_paths
        node = {
            "name": domain_label,
            "summary": domain_summary,
            "value": max(3, len(evidence_paths) + min(2, len(responsibilities))),
            "detail_meta": [
                f"Evidence paths: {len(evidence_paths)}",
                f"Responsibilities: {len(responsibilities)}",
                f"Recommended skill path: {(domain['recommended_skill_path'] if isinstance(domain, dict) else domain.recommended_skill_path) or 'not set'}",
            ],
            "children": [],
        }
        for child in (plan.child_skill_paths if plan is not None else [])[:6]:
            node["children"].append(
                    {
                        "name": _graph_skill_name(child),
                        "summary": f"Generated skill path: {child}",
                        "value": 1,
                        "detail_meta": [
                            f"Skill path: {child}",
                            f"Decision: {plan.decision if plan is not None else 'derived from evidence'}",
                        ],
                    }
                )
        if not node["children"]:
            for path in evidence_paths[:4]:
                node["children"].append(
                    {
                        "name": path.split("/")[-1],
                        "summary": f"Evidence path: {path}",
                        "value": 1,
                        "detail_meta": [f"Path: {path}", "This evidence stayed attached to the parent capability instead of becoming a new skill node."],
                    }
                )
        root["children"].append(node)
    return root


def render_evidence_sankey_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    evidence_graph = bundle.evidence_graph
    nodes: list[dict[str, object]] = [{"id": "repo", "name": "Repository", "layer": 0, "detail": "Skilgen is traversing the whole repository and grounding evidence into a connected flow."}]
    node_ids = {"repo"}
    links: list[dict[str, object]] = []

    def ensure_node(node_id: str, name: str, layer: int) -> None:
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "name": name, "layer": layer, "detail": name, "detail_meta": []})

    for language in evidence_graph.dominant_languages[:5]:
        language_id = f"lang::{language}"
        ensure_node(language_id, language, 1)
        for node in nodes:
            if node["id"] == language_id:
                node["detail"] = f"Dominant language signal. Skilgen found concrete repository evidence in {language} and used it to anchor domain reasoning."
                node["detail_meta"] = ["File-by-file evidence is grouped under language before deeper domain synthesis happens."]
        links.append({"source": "repo", "target": language_id, "value": 2})

    grouped_items: dict[str, dict[str, object]] = {}
    for item in evidence_graph.items[:16]:
        entry = grouped_items.setdefault(
            item.path,
            {
                "path": item.path,
                "language": item.language,
                "snippet": list(item.snippet[:2]),
                "kinds": [],
            },
        )
        if item.kind not in entry["kinds"]:
            entry["kinds"].append(item.kind)
        if not entry["language"] and item.language:
            entry["language"] = item.language
        if not entry["snippet"] and item.snippet:
            entry["snippet"] = list(item.snippet[:2])

    for entry in list(grouped_items.values())[:16]:
        path = str(entry["path"])
        language = str(entry["language"] or "")
        kinds = [str(kind) for kind in entry["kinds"]]
        item_id = f"item::{path}"
        file_label = "Codebase Snapshot" if path == "CODEBASE_ONLY" else path.split("/")[-1]
        ensure_node(item_id, file_label, 3)
        for node in nodes:
            if node["id"] == item_id:
                node["detail"] = (
                    "Codebase-only analysis input. Skilgen used the current repository state as the planning baseline because no standalone requirements file was supplied."
                    if path == "CODEBASE_ONLY"
                    else f"{path} — {' '.join(entry['snippet']).strip() or 'No snippet captured.'}"
                )
                node["detail_meta"] = [
                    f"Path: {path}",
                    f"Language: {language or 'unknown'}",
                    f"Kinds: {', '.join(kinds) or 'unknown'}",
                ]
        if language:
            language_id = f"lang::{language}"
            ensure_node(language_id, language, 1)
        else:
            language_id = "repo"
        for kind in kinds:
            kind_id = f"kind::{kind}"
            ensure_node(kind_id, kind.replace("_", " "), 2)
            for node in nodes:
                if node["id"] == kind_id:
                    node["detail"] = f"Evidence kind: {kind.replace('_', ' ')}. This bucket groups repo signals before Skilgen hands them to architecture synthesis."
                    node["detail_meta"] = [f"Bucket: {kind.replace('_', ' ')}", "Used to separate code, config, docs, tests, and runtime clues."]
            links.append({"source": language_id, "target": kind_id, "value": 1})
            links.append({"source": kind_id, "target": item_id, "value": 1})
    return {"nodes": nodes, "links": links}


def render_skill_sankey_data(context: RequirementsContext, project_root: Path, bundle: ProjectAnalysisBundle | None = None) -> dict[str, object]:
    bundle = bundle or _analysis_bundle(context, project_root)
    architecture = bundle.architecture
    nodes: list[dict[str, object]] = [{"id": "root", "name": "Skill System", "layer": 0, "detail": "Skilgen’s living skill map combines generated domains, deeper nuances, and imported ecosystem capability.", "detail_meta": ["Generated skills, merged nuance, and external skill packs all live in one connected layer."]}]
    node_ids = {"root"}
    links: list[dict[str, object]] = []

    def ensure_node(node_id: str, name: str, layer: int) -> None:
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "name": name, "layer": layer, "detail": name, "detail_meta": []})

    for item in architecture.materialization_plan[:18]:
        domain_id = f"domain::{item.domain}"
        ensure_node(domain_id, _graph_domain_name(item.domain), 1)
        links.append({"source": "root", "target": domain_id, "value": max(1, len(item.child_skill_paths) or 1)})
        parent_path = item.parent_skill_path or item.domain
        parent_id = f"parent::{parent_path}"
        ensure_node(parent_id, f"Parent · {_graph_skill_name(parent_path)}", 2)
        links.append({"source": domain_id, "target": parent_id, "value": max(1, len(item.child_skill_paths) or 1)})
        for node in nodes:
            if node["id"] == domain_id:
                node["detail"] = f"{_display_domain_name(item.domain)} is a materialized architecture family. Decision: {item.decision}. Rationale: {item.rationale}"
                node["detail_meta"] = [f"Decision: {item.decision.upper()}", f"Parent skill: {parent_path}"]
            if node["id"] == parent_id:
                node["detail"] = f"Parent skill path: {parent_path}. This skill stays close to the dominant evidence and coordinates the subskills under { _display_domain_name(item.domain)}."
                node["detail_meta"] = ["Parent skills organize the domain before child skills or retained nuance are loaded by an agent."]
        if item.child_skill_paths:
            for child in item.child_skill_paths[:5]:
                child_id = f"child::{child}"
                ensure_node(child_id, f"Skill · {_graph_skill_name(child)}", 3)
                links.append({"source": parent_id, "target": child_id, "value": 1})
                for node in nodes:
                    if node["id"] == child_id:
                        node["detail"] = f"Generated child skill: {child}. Skilgen split this out because the repo showed a repeatable nuance that would be easy for an agent to miss if it stayed buried in the parent skill."
                        node["detail_meta"] = [
                            f"Child skill path: {child}",
                            f"Parent domain: {_display_domain_name(item.domain)}",
                            "Created only where the evidence was strong enough to justify a dedicated reusable guide.",
                        ]
        else:
            leaf_id = f"leaf::{parent_path}"
            ensure_node(leaf_id, f"Nuance · {_graph_skill_name(parent_path)}", 3)
            links.append({"source": parent_id, "target": leaf_id, "value": 1})
            for node in nodes:
                if node["id"] == leaf_id:
                    node["detail"] = f"Deep nuance retained inside the parent skill. Skilgen decided not to split {parent_path} because the evidence is stronger as concentrated guidance. {item.rationale}"
                    node["detail_meta"] = [f"Retained in: {parent_path}", "Kept merged to avoid shallow or redundant sub-skills."]
    ecosystem_id = "ecosystem::external"
    external_skills = active_external_skills(project_root)[:6]
    if external_skills:
        ensure_node(ecosystem_id, "Ecosystem Packs", 1)
        links.append({"source": "root", "target": ecosystem_id, "value": max(1, len(external_skills))})
        for node in nodes:
            if node["id"] == ecosystem_id:
                node["detail"] = "External skill packs that Skilgen activated because the repository signaled they add real capability on top of the repo-native tree."
                node["detail_meta"] = ["These packs are shown separately so repo-generated skills do not get visually buried by imported ecosystems."]
    for external in external_skills:
        slug = str(external.get("slug", "external-skill"))
        external_id = f"external::{slug}"
        ensure_node(external_id, f"Pack · {slug}", 3)
        links.append({"source": ecosystem_id, "target": external_id, "value": 1})
        for node in nodes:
            if node["id"] == external_id:
                node["detail"] = f"External skill pack already installed because the repo signaled it was useful: {slug}."
                node["detail_meta"] = [
                    "Installed from repo signals",
                    str(external.get("summary") or "Adds ecosystem knowledge beside the repo-native skills."),
                ]
    return {"nodes": nodes, "links": links}


def render_analytics_radial_data(project_root: Path, analytics: dict[str, object]) -> list[dict[str, object]]:
    usage = analytics.get("skill_usage", [])
    if not usage:
        return []
    max_load = max(int(item.get("effective_loads", item.get("loads", 0))) for item in usage) or 1
    max_richness = max(int(item.get("richness", 0)) for item in usage) or 1
    title_counts: dict[str, int] = {}
    for item in usage:
        raw_title = str(item.get("title", item.get("skill", "Unknown skill")))
        title_counts[raw_title] = title_counts.get(raw_title, 0) + 1
    radial_rows: list[dict[str, object]] = []
    for item in usage:
        metrics = item.get("metrics", {}) if isinstance(item.get("metrics"), dict) else {}
        loads = int(item.get("effective_loads", item.get("loads", 0)))
        richness = int(item.get("richness", 0))
        depth = int(item.get("depth", 1))
        raw_title = str(item.get("title", item.get("skill", "Unknown skill")))
        title = raw_title
        if title_counts.get(raw_title, 0) > 1:
            family = str(item.get("family", "other")).replace("-", " ").replace("_", " ").title()
            title = f"{family} {raw_title}"
        title = _compact_label(title, max_length=22)
        summary = str(item.get("summary", ""))
        family = str(item.get("family", "other"))
        skill = str(item.get("skill", title))
        radial_rows.append(
            {
                "skill": skill,
                "title": title,
                "family": family,
                "kind": str(item.get("kind", "repo")),
                "summary": summary,
                "loads": loads,
                "recorded_loads": int(item.get("loads", 0)),
                "usage_label": str(item.get("usage_label", "Usage")),
                "load_score": round((loads / max_load) * 100, 2) if max_load else 0.0,
                "depth_score": min(100, depth * 22),
                "richness_score": round((richness / max_richness) * 100, 2) if max_richness else 0.0,
                "depth": depth,
                "richness": richness,
                "headings": int(metrics.get("headings", 0)),
                "bullets": int(metrics.get("bullets", 0)),
                "references": int(metrics.get("references", 0)),
                "words": int(metrics.get("words", 0)),
            }
        )
    return radial_rows


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
    score_compare = dashboard_payload.get("score_compare", {})
    repo_name = project_root.name
    score_value = float(score["score"])
    score_percent = max(0.0, min(100.0, score_value))
    score_label = escape(str(score["rating"]).replace("-", " ").title())
    stale_skill_paths = [str(path) for path in diff["stale_skill_paths"]]
    stale_count = len(stale_skill_paths)
    changed_count = int(diff["changed_file_count"])
    parser_backends = sorted({str(payload.get("backend", "unknown")) for payload in evidence_graph["parser_summary"].values()})
    generated_outputs = [
        {"name": "AGENTS.md", "exists": status["agents_exists"], "counts_ready": status["agents_exists"], "note": "project-root artifact"},
        {"name": "ANALYSIS.md", "exists": status["analysis_exists"], "counts_ready": status["analysis_exists"], "note": "project-root artifact"},
        {"name": "ARCHITECTURE.md", "exists": status["architecture_exists"], "counts_ready": status["architecture_exists"], "note": "project-root artifact"},
        {"name": "FEATURES.md", "exists": status["features_exists"], "counts_ready": status["features_exists"], "note": "project-root artifact"},
        {"name": "REPORT.md", "exists": status["report_exists"], "counts_ready": status["report_exists"], "note": "project-root artifact"},
        {"name": "TRACEABILITY.md", "exists": status["traceability_exists"], "counts_ready": status["traceability_exists"], "note": "project-root artifact"},
        {"name": "skills/MANIFEST.md", "exists": status["manifest_exists"], "counts_ready": status["manifest_exists"], "note": "project-root artifact"},
        {"name": "skills/GRAPH.md", "exists": status["graph_exists"], "counts_ready": status["graph_exists"], "note": "project-root artifact"},
        {
            "name": "skilgen-dashboard.html",
            "exists": True,
            "counts_ready": status.get("dashboard_exists", False),
            "note": "preview rendering this surface" if not status.get("dashboard_exists", False) else "project-root artifact",
        },
    ]
    evidence_count = len(evidence_graph["items"])
    dependency_edges = sum(len(targets) for targets in bundle.import_graph.values())
    call_edges = sum(len(targets) for targets in bundle.evidence_graph.call_graph.values())
    config_edges = sum(len(targets) for targets in bundle.evidence_graph.config_runtime_graph.values())
    test_links = sum(len(targets) for targets in bundle.evidence_graph.test_mapping.values())
    mapped_test_files = len(bundle.evidence_graph.test_mapping)
    total_symbol_files = len(bundle.evidence_graph.symbol_graph)
    dependency_network = render_dependency_network_data(context, project_root, bundle)
    architecture_sunburst = render_architecture_sunburst_data(context, project_root, bundle)
    evidence_sankey = render_evidence_sankey_data(context, project_root, bundle)
    dependency_sankey = render_dependency_sankey_data(context, project_root, bundle)
    skill_sankey = render_skill_sankey_data(context, project_root, bundle)
    analytics_radial = render_analytics_radial_data(project_root, analytics)
    external_skill_labels = [item.get("slug", "unknown") for item in external_skills["installed"][:6]]
    brand_mark = _skilgen_logo_svg()
    usage_mode = str(analytics.get("usage_mode", "live"))
    baseline_scorecard = score_compare.get("baseline", {})
    baseline_value = float(baseline_scorecard.get("score", 0.0))
    baseline_label = escape(str(baseline_scorecard.get("rating", "baseline")).replace("-", " ").title())
    score_delta_value = float(score_compare.get("delta", score_value - baseline_value))
    subscore_delta = score_compare.get("subscore_delta", {})
    planned_child_skill_paths = sorted(
        {
            str(path)
            for item in architecture.get("materialization_plan", [])
            for path in item.get("child_skill_paths", [])
            if str(path).strip()
        }
    )
    on_disk_skill_files = [str(path) for path in status.get("skill_files", [])]
    on_disk_child_skill_files = [path for path in on_disk_skill_files if path.count("/") > 2]
    total_skills = max(len(score.get("skills", [])), len(on_disk_skill_files))
    top_level_domains = len(architecture["domains"])
    child_skill_count = max(len(planned_child_skill_paths), max(0, total_skills - top_level_domains))
    on_disk_child_skill_count = len(on_disk_child_skill_files)
    outputs_ready = sum(1 for item in generated_outputs if item["counts_ready"])
    output_total = len(generated_outputs)
    stale_domain_count = sum(1 for item in diff["impacted_domain_details"] if item["stale"])
    stale_surface_label = "pending skill surfaces" if not on_disk_skill_files else "stale skill surfaces"
    stale_badge = f"{stale_count} {stale_surface_label}"
    parser_labels = [backend for backend in parser_backends if backend != "empty"]
    parser_note = ", ".join(parser_labels[:3]) if parser_labels else "no concrete parser backend detected"
    trend_points = _meaningful_trend_points(score_history, score, limit=8)
    trend_scores = [float(item.get("score", score_value)) for item in trend_points]
    trend_is_flat = len({round(item, 2) for item in trend_scores}) <= 1
    trend_labels: list[str] = []
    seen_trend_labels: dict[str, int] = {}
    for index, item in enumerate(trend_points):
        base_label = _trend_label(item, index, len(trend_points))
        duplicate_count = seen_trend_labels.get(base_label, 0)
        seen_trend_labels[base_label] = duplicate_count + 1
        trend_labels.append(base_label if duplicate_count == 0 else f"{base_label} · {duplicate_count + 1}")
    visible_trend_points = trend_points
    if len(trend_points) <= 1:
        trend_markup = f"<div class='spark-empty'>First run — baseline at {int(round(score_value))}. Trend unlocks after a few distinct runs.</div>"
        trend_ticks_markup = ""
    else:
        trend_markup = "\n".join(
            f"<div class='spark-point' style='height:{max(18, min(100, float(item.get('score', 0))))}%'><span>{int(round(float(item.get('score', 0))))}</span></div>"
            for item in visible_trend_points
        ) or "<div class='spark-empty'>Score history will appear after a few runs.</div>"
        trend_ticks_markup = "\n".join(
            f"<span>{escape(label)}</span>"
            for label in trend_labels
        )
    if len(trend_points) <= 1:
        trend_summary = "This is the current baseline. Trend history will become more useful after a few distinct runs."
    elif trend_is_flat:
        trend_summary = f"Score has stayed at {int(round(score_value))} across the last {len(trend_points)} snapshots. Skilgen will surface a stronger trend once the score meaningfully changes."
    else:
        delta_from_previous = float(score_trend["delta_from_previous"])
        trend_summary = (
            "Improving compared with the previous snapshot."
            if delta_from_previous > 0
            else "Falling compared with the previous snapshot."
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
    changed_files_empty = (
        "No repo drift detected yet. Skilgen has planned surfaces, but no materialized freshness baseline exists in the project root."
        if not diff["changed_files"] and not on_disk_skill_files and stale_count
        else "No source changes detected since the last generation baseline."
    )
    changed_files_markup = "\n".join(
        f"<li><span class='change-type {escape(item['change_type'])}'>{escape(item['change_type'])}</span><strong>{escape(item['path'])}</strong></li>"
        for item in diff["changed_files"][:8]
    ) or f"<li class='muted'>{escape(changed_files_empty)}</li>"
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
    stale_skills_markup = "\n".join(
        f"<li><div><strong>{escape(Path(path).parts[-2] if len(Path(path).parts) > 2 else path)}</strong><span>{escape(path)}</span></div>{pill('pending' if not on_disk_skill_files else 'stale', 'warning')}</li>"
        for path in stale_skill_paths[:12]
    ) or "<li class='muted'>No pending or stale skill surfaces right now.</li>"
    outputs_markup = "\n".join(
        (
            "<li>"
            f"<div><strong>{escape(item['name'])}</strong><span>{escape(item['note'])}</span></div>"
            f"{pill('ready' if item['exists'] else 'missing', 'good' if item['exists'] else 'warning')}"
            "</li>"
        )
        for item in generated_outputs
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
    recommended_connector_markup = "\n".join(
        (
            "<li>"
            f"{escape(item.get('slug', 'unknown'))}"
            f"{pill('recommended', 'good')}"
            f"{pill('official' if item.get('official_source_verified') else 'community', 'good' if item.get('official_source_verified') else 'warning')}"
            "</li>"
        )
        for item in mcp_connectors.get("recommended", {}).get("connectors", [])[:6]
    ) or "<li class='muted'>No recommended connector profiles right now.</li>"
    analytics_markup = "\n".join(
        f"<li><div><strong>{escape(str(item['title']))}</strong><span>{escape(str(item['skill']))}</span></div><span>{int(item.get('effective_loads', item['loads']))} {escape('loads' if usage_mode == 'live' else 'attention')}</span></li>"
        for item in analytics.get("skill_usage", [])[:8]
    ) or "<li class='muted'>Usage analytics will populate as agents load skills.</li>"
    hot_skill = analytics.get("skill_usage", [{}])[0] if analytics.get("skill_usage") else {}
    domain_cards_parts: list[str] = []
    plan_by_domain = {str(item["domain"]): item for item in architecture.get("materialization_plan", [])}
    for domain in architecture["domains"][:6]:
        confidence_label = f"{float(domain['confidence']):.2f}"
        domain_label = _display_domain_name(str(domain["name"]))
        related_domains = ", ".join(_display_domain_name(str(item)) for item in domain["related_domains"][:3]) or "No related domains surfaced"
        plan = plan_by_domain.get(str(domain["name"]))
        domain_responsibilities = [
            item for item in domain["responsibilities"][:4]
            if str(item).strip().lower() != str(domain["summary"]).strip().lower()
        ]
        if not domain_responsibilities:
            domain_responsibilities = domain["responsibilities"][:4]
        nuance_bits = [
            (
                "1 grounded evidence path backs this boundary."
                if len(domain["evidence_paths"]) == 1
                else f"{len(domain['evidence_paths'])} grounded evidence paths back this boundary."
            ),
            (
                "1 responsibility stayed coherent enough to keep this capability readable for an agent."
                if len(domain["responsibilities"]) == 1
                else f"{len(domain['responsibilities'])} responsibilities stayed coherent enough to keep this capability readable for an agent."
            ),
        ]
        if plan is not None:
            nuance_bits.append(str(plan["rationale"]))
            if plan.get("cross_links"):
                nuance_bits.append(f"Cross-domain pressure is strongest with {', '.join(_display_skill_name(link) for link in plan['cross_links'][:3])}.")
        elif domain["related_domains"]:
            nuance_bits.append(f"Cross-domain pressure is strongest with {related_domains}.")
        domain_cards_parts.append(
            "<article class='domain-card'>"
            f"<div class='domain-head'><h3>{escape(domain_label)}</h3>{pill(confidence_label, 'good')}</div>"
            f"<p>{escape(domain['summary'])}</p>"
            f"<div class='micro-label'>Responsibilities</div><ul>{list_items(domain_responsibilities, empty='No responsibilities captured')}</ul>"
            f"<div class='micro-label'>Evidence</div><ul>{list_items(domain['evidence_paths'][:3], empty='No evidence paths captured')}</ul>"
            f"<div class='micro-label'>Nuance</div><p class='nuance-copy'>{escape(' '.join(nuance_bits))}</p>"
            "</article>"
        )
    domain_cards = "\n".join(domain_cards_parts)
    architecture_palette = ["#EFD37A", "#67D5FF", "#8FD9A8", "#FF8F70", "#C99BFF", "#FF6B9A", "#6EE7D2", "#7C8EFF"]
    architecture_legend = "\n".join(
        f"<li><strong><span class='legend-dot' style='background:{architecture_palette[index % len(architecture_palette)]}'></span>{escape(_display_domain_name(str(domain['name'])))}</strong><span>{escape(domain['recommended_skill_path'] or 'domain')}</span></li>"
        for index, domain in enumerate(architecture["domains"][:8])
    ) or "<li class='muted'>No architecture domains yet.</li>"
    score_compare_markup = "\n".join(
        (
            "<li>"
            f"<span>{escape(name.title())}</span>"
            f"{pill(f'{delta:+.0f}', 'good' if delta > 0 else 'default')}"
            "</li>"
        )
        for name, delta in subscore_delta.items()
    ) or "<li class='muted'>Score deltas will appear once comparison data is available.</li>"
    unmapped_files = [str(path) for path in score["subscores"]["coverage"].get("unmapped_files", [])[:5]]
    readiness_signal = (
        "Preview only — materialize outputs into the project root before agents can load a grounded skill system."
        if outputs_ready == 0 and not on_disk_skill_files
        else "Agents can load repo-local skills now, but some operating artifacts are still incomplete."
        if outputs_ready < output_total
        else "Agents can load the current repo-local outputs now."
    )
    compare_headline = (
        "Skilgen has inferred a repo-specific materialization plan, but groundedness and structure are still at zero because the child skills and operating artifacts have not been written into the project root yet."
        if not on_disk_skill_files
        else "Skilgen converts repo analysis into a maintained skill system with grounded references, explicit startup guidance, and freshness tracking that agents can actually use."
    )
    action_items = [
        f"Run `skilgen deliver --project-root .` to materialize {child_skill_count} planned child skills and the repo-local operating artifacts.",
    ]
    if unmapped_files:
        action_items.append(f"Review the {len(unmapped_files)} unmapped implementation files to raise coverage and groundedness: {', '.join(unmapped_files)}.")
    if stale_count:
        action_items.append(
            "This run is showing pending skill surfaces rather than drifted ones because no on-disk materialized baseline exists yet."
            if not on_disk_skill_files
            else f"Refresh the {stale_count} stale skill surfaces after source changes land."
        )
    action_markup = "".join(f"<li>{escape(item)}</li>" for item in action_items[:3])
    process_cards_markup = "\n".join(
        [
            (
                "<article class='process-card'>"
                "<div class='micro-label'>1. Read The Repo</div>"
                f"<strong>{total_symbol_files} parser-backed files</strong>"
                f"<p class='nuance-copy'>Skilgen starts from {evidence_count} evidence items, {dependency_edges} dependency edges, {call_edges} call edges, and {_count_phrase(test_links, 'test-to-code link')} across {mapped_test_files} mapped test files so the skill system is grounded in the actual repo rather than a template.</p>"
                "</article>"
            ),
            (
                "<article class='process-card'>"
                "<div class='micro-label'>2. Materialize Skills</div>"
                f"<strong>{top_level_domains} top-level domains, {child_skill_count} planned child skills</strong>"
                f"<p class='nuance-copy'>Those repo seams have been planned into reusable parent and child skills, but only {on_disk_child_skill_count} child skill files and {outputs_ready}/{output_total} operating artifacts currently exist on disk.</p>"
                "</article>"
            ),
            (
                "<article class='process-card'>"
                "<div class='micro-label'>3. Help Agents Work Better</div>"
                f"<strong>{score_delta_value:+.2f} score lift</strong>"
                f"<p class='nuance-copy'>Right now the visible lift is mostly freshness because groundedness and structure have not fired yet. Materializing the planned skill tree is the next step that turns this from a status page into a working agent surface.</p>"
                "</article>"
            ),
        ]
    )
    plan_rows = "\n".join(
        (
            "<tr>"
            f"<td>{escape(_display_domain_name(str(item['domain'])))}</td>"
            f"<td>{pill(str(item['decision']).upper(), 'warning' if item['decision'] == 'split' else 'default')}</td>"
            f"<td>{escape(item['parent_skill_path'] or '-')}</td>"
            f"<td>{escape(', '.join(item['child_skill_paths'][:4]) or '-')}</td>"
            f"<td>{escape(item['rationale'])}"
            f"<div class='rationale-note'>Grounded in {_count_phrase(len(item['child_skill_paths']) or 1, 'concrete skill surface')}, {_count_phrase(len(item.get('cross_links', [])), 'cross-link')}, and the evidence attached to {escape(_display_domain_name(str(item['domain'])))} rather than a template split.</div></td>"
            "</tr>"
        )
        for item in architecture["materialization_plan"][:8]
    ) or "<tr><td colspan='5' class='muted'>No materialization plan entries yet.</td></tr>"

    network_payload_json = json.dumps({"dependencies": dependency_network})
    sunburst_payload_json = json.dumps(architecture_sunburst)
    sankey_payload_json = json.dumps({"evidence": evidence_sankey, "dependencies": dependency_sankey, "skills": skill_sankey})
    radial_payload_json = json.dumps({"analytics": analytics_radial})
    score_signal = (
        "Needs work"
        if score_value < 60
        else "Fair quality"
        if score_value < 75
        else "Strong quality"
        if score_value < 90
        else "Excellent quality"
    )
    dashboard_styles = """
:root{--background:#131313;--background-soft:#0e0e0e;--surface:#1c1b1b;--surface-2:#201f1f;--surface-3:#2a2a2a;--surface-4:#353534;--line:rgba(151,144,127,.18);--line-strong:rgba(239,211,122,.26);--text:#e5e2e1;--muted:#a7a095;--primary:#efd37a;--primary-soft:#fff0cb;--secondary:#d5c69c;--tertiary:#b4d9ff;--good:#8fd9a8;--warning:#ffb86b;--danger:#ff8f70;--shadow:0 24px 80px rgba(0,0,0,.34)}
*{box-sizing:border-box}html,body{min-height:100%}html{scroll-behavior:smooth}body{margin:0;font-family:'Manrope',ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:radial-gradient(circle at top left, rgba(239,211,122,.12), transparent 26%),linear-gradient(180deg,#131313,#0e0e0e 52%,#131313 100%);color:var(--text)}
body::before{content:'';position:fixed;inset:0;pointer-events:none;opacity:.16;background-image:radial-gradient(rgba(76,70,56,.9) .65px, transparent .65px);background-size:34px 34px}
a{color:inherit;text-decoration:none}
.topbar{position:fixed;top:0;left:0;right:0;z-index:40;height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;background:rgba(19,19,19,.78);backdrop-filter:blur(22px);border-bottom:1px solid rgba(151,144,127,.12)}
.topbar-brand{display:flex;align-items:center;gap:18px}.topbar-brand strong,.topbar-nav a,.rail-title,.section-title,.panel h2,.hero-copy h1,.metric-value,.stat-value,.compare-score-value,.score-ring-content strong,.graph-aside h3,.graph-detail h4,.ops-tile strong,.chapter-title,.footer-mark,.score-block-title,.table-kicker,.list-kicker{font-family:'Space Grotesk','Manrope',sans-serif}
.topbar-brand strong{font-size:1.08rem;letter-spacing:.18em;text-transform:uppercase;color:var(--primary)}
.topbar-brand span{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.topbar-nav{display:flex;gap:18px;flex-wrap:wrap}.topbar-nav a{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;padding:10px 14px;border:1px solid transparent;border-radius:999px;color:#8d8779;transition:.18s ease}.topbar-nav a:hover,.topbar-nav a.active{color:var(--primary);border-color:rgba(239,211,122,.22);background:rgba(239,211,122,.08)}
.topbar-actions{display:flex;align-items:center;gap:12px}.topbar-icon,.corner-badge{display:inline-flex;align-items:center;justify-content:center;border:1px solid rgba(151,144,127,.18);background:rgba(28,27,27,.72);color:#cec6b3;border-radius:999px}
.topbar-icon{width:38px;height:38px;font-size:.75rem;letter-spacing:.08em;text-transform:uppercase}
.corner-badge{padding:0 14px;height:38px;font-size:.76rem;letter-spacing:.14em;text-transform:uppercase}
.rail{position:fixed;top:72px;left:0;bottom:0;width:284px;padding:26px 18px 24px;background:rgba(19,19,19,.96);border-right:1px solid rgba(151,144,127,.12);display:grid;align-content:start;gap:18px;overflow:auto}
.rail-card,.panel,.hero-panel,.mini-panel,.metric-card,.stat-card,.compare-card,.process-card,.ops-tile{border:1px solid var(--line);background:linear-gradient(180deg,rgba(42,42,42,.66),rgba(28,27,27,.9));box-shadow:var(--shadow)}
.rail-card{padding:18px;border-radius:0}.rail-title{font-size:.78rem;letter-spacing:.18em;text-transform:uppercase;color:var(--primary)}.rail-subtitle,.repo-chip,.footer-note,.section-copy,.metric-subtitle,.stat-note,.nuance-copy,.rationale-note,.graph-aside p,.graph-detail p,.subscore-value,.graph-legend li span,.trend-summary,.hero-context,.compare-score-label,.list li span,.quality-list li p{color:var(--muted)}
.rail-subtitle{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase}.rail-nav{display:grid;gap:8px}.rail-nav a{display:flex;align-items:center;gap:10px;padding:14px 16px;font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;color:#8d8779;border:1px solid transparent;background:transparent;transition:.18s ease}.rail-nav a.active,.rail-nav a:hover{color:var(--primary);background:rgba(32,31,31,.96);border-color:rgba(239,211,122,.14)}
.rail-legend,.quality-list,.compare-list,.graph-legend,.list,.mini-panel ul{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.rail-legend li,.graph-legend li,.list li,.mini-panel li,.quality-list li{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.legend-dot{display:inline-block;width:10px;height:10px;border-radius:999px;margin-right:8px;flex:0 0 auto}
.legend-row{display:flex;align-items:center;gap:10px;color:#d9d3ca;font-size:.9rem}
.metric-pile{display:grid;gap:10px}.metric-chip{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border:1px solid rgba(151,144,127,.16);background:rgba(14,14,14,.56)}.metric-chip strong{font-size:1rem;color:var(--text)}.metric-chip span{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.page{max-width:1500px;margin:0 auto;padding:104px 28px 64px 320px;display:grid;gap:28px}
.chapter{display:grid;gap:18px;scroll-margin-top:104px}.chapter-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;flex-wrap:wrap}.chapter-kicker,.eyebrow,.metric-eyebrow,.micro-label,.table-kicker,.list-kicker{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--primary)}
.chapter-title{margin:0;font-size:clamp(2.5rem,5vw,4.6rem);line-height:.92;letter-spacing:-.08em}
.chapter-copy{max-width:72ch;color:#cec6b3;line-height:1.68}
.chapter-brand{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap}.chapter-brand .skilgen-mark{width:220px;max-width:min(36vw,220px)}
.hero-grid,.score-rail,.compare-grid,.process-grid,.analytics-board,.dashboard-columns,.systems-grid,.domain-grid,.ops-grid,.score-board,.graph-frame{display:grid;gap:18px}
.hero-grid{grid-template-columns:minmax(0,1.1fr) minmax(360px,.9fr)}
.hero-panel,.panel{padding:28px;border-radius:0;overflow:hidden;position:relative}
.hero-panel::before,.panel::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,rgba(239,211,122,.35),transparent)}
.hero-left{display:grid;gap:22px}
.brand-wrap{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap}.brand-lockup{display:grid;gap:8px}.skilgen-mark{width:320px;max-width:100%;height:auto;display:block;filter:drop-shadow(0 20px 46px rgba(0,0,0,.42))}
.repo-chip,.pill{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid rgba(151,144,127,.18);border-radius:999px;background:rgba(19,19,19,.5);font-size:.76rem;letter-spacing:.1em;text-transform:uppercase}
.pill.good{color:var(--good);border-color:rgba(143,217,168,.24);background:rgba(143,217,168,.08)}.pill.warning{color:var(--warning);border-color:rgba(255,184,107,.22);background:rgba(255,184,107,.08)}.pill.default{color:var(--text)}
.hero-copy{display:grid;gap:14px;max-width:66ch}.hero-note{margin:0;font-size:1.05rem;color:var(--primary-soft)}.hero-context{margin:0}
.hero-actions{display:flex;flex-wrap:wrap;gap:12px}.hero-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.metric-card,.stat-card,.compare-card,.process-card,.mini-panel,.ops-tile{padding:18px;border-radius:0}
.metric-value,.stat-value,.compare-score-value{font-size:2rem;font-weight:700;letter-spacing:-.05em}.metric-subtitle,.stat-note{line-height:1.5}
.score-top{display:grid;gap:16px;justify-items:center;text-align:center}.score-ring{--score:0;width:min(232px,100%);aspect-ratio:1;border-radius:50%;padding:18px;background:conic-gradient(var(--primary) calc(var(--score)*1%), rgba(151,144,127,.18) 0);display:grid;place-items:center;box-shadow:inset 0 0 0 1px rgba(151,144,127,.18)}
.score-ring-content{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;gap:6px;background:radial-gradient(circle at center, rgba(53,53,52,.96), rgba(14,14,14,.98));text-align:center;padding:22px}.score-ring-content strong{font-size:3rem;letter-spacing:-.09em}.score-ring-content small{font-size:1rem;color:var(--muted);margin-left:4px}.score-ring-note{line-height:1.5;color:#cec6b3}
.score-rail{grid-template-columns:repeat(2,minmax(0,1fr))}.stat-card{background:linear-gradient(180deg,rgba(32,31,31,.96),rgba(19,19,19,.94))}
.panel h2{margin:0;font-size:1.8rem;letter-spacing:-.05em}.section-title{font-size:1rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.section-copy{margin-top:10px;max-width:76ch;line-height:1.65}
.analytics-board{grid-template-columns:minmax(0,1.18fr) minmax(320px,.82fr);align-items:stretch}
.analytics-side{display:grid;gap:16px}.analytics-side .mini-panel li div{display:grid;gap:3px}.analytics-side .mini-panel li span{font-size:.82rem}
.compare-grid{grid-template-columns:repeat(3,minmax(0,1fr));margin-top:18px}.compare-card{display:grid;gap:12px}.compare-score{display:flex;align-items:flex-end;gap:14px;flex-wrap:wrap}
.compare-list li{padding:10px 0;border-bottom:1px solid rgba(151,144,127,.16)}.compare-list li:last-child{border-bottom:0}
.process-grid{grid-template-columns:repeat(3,minmax(0,1fr));margin-top:18px}.process-card strong{display:block;font-size:1.12rem;margin-bottom:8px}
.score-board{grid-template-columns:minmax(0,1fr) minmax(340px,.86fr);margin-top:18px}.subscore-stack{display:grid;gap:14px}.subscore-row{display:grid;grid-template-columns:160px minmax(0,1fr) auto;align-items:center;gap:12px}.subscore-label{text-transform:capitalize}.subscore-bar{height:10px;background:rgba(151,144,127,.18);overflow:hidden}.subscore-bar span{display:block;height:100%;background:linear-gradient(90deg,var(--primary),var(--primary-soft))}
.quality-list li{padding:14px 16px;background:rgba(14,14,14,.34);border:1px solid rgba(151,144,127,.16)}.quality-list li strong{display:block}.quality-list li span{display:inline-flex;margin-top:8px;color:var(--primary)}
.trend-panel{display:grid;gap:16px}.trend-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-end;flex-wrap:wrap}.sparkline{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));align-items:end;gap:8px;min-height:160px}.spark-point{display:grid;align-items:end;min-height:28px;padding-bottom:34px;background:linear-gradient(180deg,rgba(239,211,122,.18),rgba(239,211,122,.92));position:relative}.spark-point span{position:absolute;bottom:10px;left:0;right:0;text-align:center;font-size:.82rem;font-weight:700;color:#131313}.spark-empty{grid-column:1/-1;display:grid;place-items:center;min-height:120px;border:1px dashed rgba(151,144,127,.22);color:var(--muted);padding:18px;text-align:center}.trend-ticks{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:8px;color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.12em}.trend-ticks span{text-align:center}.trend-summary{line-height:1.6}
.graph-shell{position:relative;overflow:hidden;background:linear-gradient(180deg,rgba(14,14,14,.92),rgba(19,19,19,.98))}.graph-shell::before{content:'';position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(rgba(76,70,56,.45) .7px, transparent .7px);background-size:34px 34px;opacity:.22}
.graph-toolbar{display:flex;justify-content:space-between;gap:14px;align-items:center;flex-wrap:wrap;margin-top:18px;margin-bottom:18px;position:relative;z-index:1}
.graph-tabs,.ops-tabs,.surface-tabs,.legend,.hero-actions{display:flex;flex-wrap:wrap;gap:10px}.graph-tab,.ops-tab,.surface-tab{border:1px solid rgba(151,144,127,.18);background:rgba(28,27,27,.92);color:var(--text);padding:11px 15px;border-radius:999px;cursor:pointer;font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:.75rem}
.graph-tab.active,.ops-tab.active,.surface-tab.active{background:rgba(239,211,122,.12);border-color:rgba(239,211,122,.32);color:var(--primary)}
.graph-frame{grid-template-columns:minmax(0,1.18fr) minmax(320px,.82fr);position:relative;z-index:1}.graph-panel{display:none;height:100%}.graph-panel.active{display:block;height:100%}
.graph-stage{height:620px;border:1px solid rgba(239,211,122,.2);background:linear-gradient(180deg,#0f1115,#090a0d);padding:16px;overflow:hidden}.graph-aside{padding:22px;border:1px solid rgba(151,144,127,.18);background:linear-gradient(180deg,rgba(32,31,31,.96),rgba(19,19,19,.96));display:grid;align-content:start;gap:16px;min-width:0}.graph-copy{display:none;gap:16px}.graph-copy.active{display:grid}.graph-aside h3{margin:0;font-size:1.24rem}.graph-aside ul{margin:0;padding-left:18px;color:#ded8d0}
.graph-detail{padding:16px;border:1px solid rgba(239,211,122,.16);background:rgba(14,14,14,.42);display:grid;gap:10px}.graph-detail h4{margin:0;font-size:1rem}.graph-detail-meta{display:grid;gap:8px;list-style:none;padding:0;margin:0;max-height:240px;overflow:auto}.graph-detail-meta li{padding:10px 12px;background:rgba(32,31,31,.84);border:1px solid rgba(151,144,127,.16);color:#ded8d0;overflow-wrap:anywhere}
.sunburst-canvas,.sankey-canvas,.network-canvas,.radial-canvas{width:100%;height:100%;min-height:540px;position:relative;overflow:hidden;background:radial-gradient(circle at top, rgba(239,211,122,.08), transparent 38%), rgba(255,255,255,.02)}.network-canvas{min-height:540px;height:540px}.network-canvas,.network-canvas .vis-network,.network-canvas canvas{background:transparent!important}.network-canvas canvas{width:100%!important;height:100%!important;display:block}.graph-stage svg{width:100%;height:100%;display:block}
.graph-legend{max-height:320px;overflow:auto}.graph-legend li{padding:10px 12px;border:1px solid rgba(151,144,127,.16);background:rgba(14,14,14,.34);min-width:0}.graph-legend li strong,.graph-legend li span{overflow-wrap:anywhere;word-break:break-word}
.canvas-fallback{display:grid;place-items:center;min-height:280px;padding:24px;border:1px dashed rgba(151,144,127,.22);color:var(--muted);text-align:center;line-height:1.6}.network-mobile-note{display:none}
.dashboard-columns{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.list{margin:18px 0 0}.list li{padding:12px 14px;border:1px solid rgba(151,144,127,.16);background:rgba(14,14,14,.34)}.list li div{display:grid;gap:4px}.change-type{text-transform:uppercase;font-size:.72rem;letter-spacing:.12em;padding:4px 8px;border-radius:999px;border:1px solid rgba(151,144,127,.18)}.change-type.added{color:var(--good)}.change-type.modified{color:var(--warning)}.change-type.deleted{color:var(--danger)}.muted{color:var(--muted)!important}
.domain-grid{grid-template-columns:repeat(2,minmax(0,1fr));margin-top:18px}.domain-card{padding:20px;border:1px solid rgba(151,144,127,.16);background:linear-gradient(180deg,rgba(32,31,31,.96),rgba(19,19,19,.94))}.domain-head{display:flex;justify-content:space-between;align-items:center;gap:12px}.domain-card h3{margin:0;font-size:1.02rem}.domain-card p{color:#d8d2ca}.domain-card ul{padding-left:18px;color:var(--muted)}
table{width:100%;border-collapse:collapse;border-spacing:0;margin-top:18px}th,td{padding:14px 12px;border-bottom:1px solid rgba(151,144,127,.16);text-align:left;vertical-align:top}th{color:var(--muted);font-size:.76rem;text-transform:uppercase;letter-spacing:.16em}
.systems-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.mini-panel ul{margin:12px 0 0}.mini-panel li span{overflow-wrap:anywhere;word-break:break-word}
.ops-board{display:grid;gap:18px;margin-top:18px}.ops-copy,.surface-copy{display:none}.ops-copy.active,.surface-copy.active{display:block}.ops-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.radial-legend{display:grid;gap:10px}.footer-note{font-size:.92rem}.tooltip{position:absolute;pointer-events:none;background:rgba(14,14,14,.98);border:1px solid rgba(239,211,122,.28);padding:12px 14px;color:#f6f7fb;font-size:.86rem;line-height:1.45;box-shadow:0 18px 40px rgba(0,0,0,.28);opacity:0;transform:translate(-50%,-100%);transition:opacity .16s ease;max-width:280px}.tooltip strong{display:block;color:var(--primary);margin-bottom:6px}
.score-callout{display:grid;gap:14px}.score-copy{padding:18px;border:1px solid rgba(151,144,127,.16);background:rgba(14,14,14,.34)}.score-copy strong{display:block;font-size:1.04rem;margin-bottom:6px;color:var(--primary-soft)}
.health-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:18px}.health-tile{padding:16px;border:1px solid rgba(151,144,127,.16);background:rgba(14,14,14,.34)}.health-tile span{display:block;font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}.health-tile strong{display:block;font-size:1.38rem;margin-top:8px;font-family:'Space Grotesk','Manrope',sans-serif}
.footer-bar{display:flex;justify-content:space-between;gap:18px;align-items:center;flex-wrap:wrap;padding:22px 28px;border:1px solid rgba(151,144,127,.16);background:linear-gradient(180deg,rgba(32,31,31,.96),rgba(19,19,19,.94))}.footer-mark{font-size:.9rem;letter-spacing:.16em;text-transform:uppercase;color:var(--primary)}
@media (max-width:1180px){.rail{display:none}.page{padding-left:28px}.hero-grid,.analytics-board,.score-board,.dashboard-columns,.graph-frame,.compare-grid,.process-grid{grid-template-columns:1fr}.hero-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.systems-grid,.domain-grid,.ops-grid,.health-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:760px){.topbar{padding:12px 16px;min-height:72px;height:auto;flex-wrap:wrap;gap:10px}.topbar-nav{width:100%;overflow:auto;padding-bottom:4px}.page{padding:112px 16px 48px}.hero-panel,.panel{padding:20px}.hero-copy h1,.chapter-title{font-size:clamp(2.1rem,14vw,3.4rem)}.hero-metrics,.score-rail,.systems-grid,.domain-grid,.ops-grid,.health-grid{grid-template-columns:1fr}.graph-stage{height:auto;min-height:280px}.sunburst-canvas,.sankey-canvas,.radial-canvas{min-height:320px}.network-canvas{display:none}.network-mobile-note{display:grid}.graph-aside{gap:12px}.subscore-row{grid-template-columns:1fr}.subscore-value{text-align:left}.dashboard-columns{grid-template-columns:1fr}}
""".strip()

    dashboard_script = f"""
window.__SKILGEN_NETWORKS__ = {network_payload_json};
window.__SKILGEN_SUNBURST__ = {sunburst_payload_json};
window.__SKILGEN_SANKEY__ = {sankey_payload_json};
window.__SKILGEN_RADIAL__ = {radial_payload_json};
const tabs=[...document.querySelectorAll('.graph-tab')];
const panels=[...document.querySelectorAll('.graph-stage .graph-panel')];
const copies=[...document.querySelectorAll('.graph-aside .graph-copy')];
const opsTabs=[...document.querySelectorAll('.ops-tab')];
const opsCopies=[...document.querySelectorAll('.ops-copy')];
const surfaceTabs=[...document.querySelectorAll('.surface-tab')];
const surfaceCopies=[...document.querySelectorAll('.surface-copy')];
const tooltip=document.createElement('div');
tooltip.className='tooltip';
document.body.appendChild(tooltip);
const renderFallback=(container,title,message)=>{{
  if(!container) return;
  container.dataset.loaded='1';
  container.innerHTML=`<div class="canvas-fallback"><div><strong>${{title}}</strong><br>${{message}}</div></div>`;
}};
const showTooltip=(event,title,body='')=>{{
  const escapeHtml=(value)=>String(value)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/\"/g,'&quot;')
    .replace(/'/g,'&#39;');
  tooltip.innerHTML=`<strong>${{escapeHtml(title)}}</strong>${{escapeHtml(body).replace(/\\n/g,'<br>')}}`;
  const viewportWidth=window.innerWidth||document.documentElement.clientWidth||1280;
  const viewportHeight=window.innerHeight||document.documentElement.clientHeight||720;
  const tooltipWidth=Math.max(220, tooltip.offsetWidth || 280);
  const tooltipHeight=Math.max(64, tooltip.offsetHeight || 96);
  const preferredTop=event.pageY-16;
  const clampedX=Math.min(Math.max(tooltipWidth/2+8,event.pageX),viewportWidth-(tooltipWidth/2)-8);
  const placeBelow=(preferredTop-tooltipHeight) < 8;
  const clampedY=placeBelow ? Math.min(viewportHeight-tooltipHeight-8, event.pageY+18) : Math.min(Math.max(tooltipHeight+8, preferredTop),viewportHeight-8);
  tooltip.style.left=`${{clampedX}}px`;
  tooltip.style.top=`${{clampedY}}px`;
  tooltip.style.transform=placeBelow ? 'translate(-50%, 0)' : 'translate(-50%, -100%)';
  tooltip.style.opacity='1';
}};
const hideTooltip=()=>{{ tooltip.style.opacity='0'; tooltip.style.transform='translate(-50%, -100%)'; }};
const activateSet=(buttons,panels,target,buttonKey,panelKey)=>{{
  buttons.forEach((button)=>{{
    const active=button.dataset[buttonKey]===target;
    button.classList.toggle('active',active);
    if(button.getAttribute('role')==='tab') button.setAttribute('aria-selected', active ? 'true' : 'false');
  }});
  panels.forEach((panel)=>{{
    const active=panel.dataset[panelKey]===target;
    panel.classList.toggle('active',active);
    if(panel.getAttribute('role')==='tabpanel') panel.setAttribute('aria-hidden', active ? 'false' : 'true');
  }});
}};
const detailDefaults={{
  architecture:{{
    title:'Architecture Sunburst',
    body:'Skilgen starts from parser-backed evidence, then lets the architecture view reveal how responsibilities split across the repo. Click an arc to inspect that specific capability boundary.',
    meta:[
      'Color separates architecture families so the high-level shape is easy to scan.',
      'Clicking a domain replaces this summary with node-specific detail.',
    ],
  }},
  evidence:{{
    title:'Evidence Flow',
    body:'Skilgen walks file by file and groups the repo into languages, evidence kinds, and concrete artifacts. Click any node to inspect the exact nuance that was extracted.',
    meta:[
      'Evidence is grounded in real files, snippets, configs, docs, and tests.',
      'This is the proof layer beneath every generated skill.',
    ],
  }},
  dependencies:{{
    title:'Dependency Flow',
    body:'Skilgen groups high-fanout source files into dependency buckets, then fans back out into the exact modules they pull in. This makes coupling and blast radius easier to read than a force-directed graph.',
    meta:[
      'Left: source files creating dependency pressure.',
      'Middle: dependency buckets such as repo modules, stdlib, tests, or external packages.',
      'Right: concrete modules or files the source depends on.',
    ],
  }},
  skills:{{
    title:'Skill Flow',
    body:'Skilgen does not stop at high-level domains. It goes file by file, then decides where nuance deserves its own child skill, where it should stay merged, and where external packs strengthen the repo-native tree.',
    meta:[
      'Click a skill node to inspect why that skill exists.',
      'External packs show which ecosystem skills are already active in the map.',
    ],
  }},
  analytics:{{
    title:'Usage Analytics',
    body:'Skilgen shows every tracked skill as its own radial bar, layering real usage, structural depth, and content richness together so the most meaningful skills stand out immediately.',
    meta:[
      'Gold measures usage intensity.',
      'Blue measures structural depth in the skill tree.',
      'Green measures content richness inside the skill.',
    ],
  }},
}};
const setDetail=(target,title,body,meta=[])=>{{
  const titleSlot=document.querySelector(`[data-copy-title="${{target}}"]`);
  if(titleSlot) titleSlot.textContent=title;
  const bodySlot=document.querySelector(`[data-copy-body="${{target}}"]`);
  if(bodySlot) bodySlot.textContent=body;
  const box=document.querySelector(`[data-detail="${{target}}"]`);
  if(!box) return;
  const safeMeta=(meta||[]).slice(0,4);
  box.innerHTML=`<h4>${{title}}</h4><p>${{body}}</p><ul class="graph-detail-meta">${{safeMeta.map((item)=>`<li>${{item}}</li>`).join('')}}</ul>`;
}};
Object.entries(detailDefaults).forEach(([key,value])=>setDetail(key,value.title,value.body,value.meta));
const networkOptions={{
  autoResize:true,
  physics:{{stabilization:true,barnesHut:{{gravitationalConstant:-3200,centralGravity:0.18,springLength:132,springConstant:0.03}}}},
  interaction:{{hover:true,navigationButtons:true,keyboard:true}},
  nodes:{{shape:'dot',borderWidth:2,font:{{color:'#F6F7FB',face:'Inter'}},color:{{border:'#EFD37A',background:'#11161E',highlight:{{border:'#F8DF8E',background:'#1B2430'}}}}}},
  edges:{{color:{{color:'rgba(255,255,255,0.26)',highlight:'#EFD37A'}},smooth:true,width:1.2}},
  groups:{{repo:{{size:38,color:{{border:'#F8DF8E',background:'#1B1A12'}}}},source:{{size:15,color:{{border:'#7DD8FF',background:'#131D29'}}}},target:{{size:13,color:{{border:'#8FD9A8',background:'#101A17'}}}},language:{{size:18,color:{{border:'#F6F7FB',background:'#171A21'}}}},reference:{{size:11,color:{{border:'#C99BFF',background:'#151125'}}}}}},
}};
const renderedNetworks=new Map();
const renderNetwork=(target, canvas)=>{{
  if(window.innerWidth <= 760 && target === 'dependencies') {{
    renderFallback(canvas, 'Dependency network hidden on small screens', 'Open this dashboard on a wider screen to inspect the interactive network, or use the detail panel to understand hotspot guidance.');
    return;
  }}
  if(!window.vis) {{
    renderFallback(canvas, 'Dependency network unavailable', 'The network library did not load, so Skilgen cannot render the interactive dependency map in this browser session.');
    return;
  }}
  const graph=window.__SKILGEN_NETWORKS__[target];
  if(!graph || !graph.nodes || !graph.nodes.length) {{
    renderFallback(canvas, 'Dependency network unavailable', 'Skilgen did not find enough dependency nodes to render the interactive map for this snapshot.');
    return;
  }}
  if(renderedNetworks.has(target)){{
    const existing=renderedNetworks.get(target);
    existing.setData({{nodes:new vis.DataSet(graph.nodes),edges:new vis.DataSet(graph.edges)}});
    existing.setSize('100%','100%');
    existing.redraw();
    existing.fit({{animation:false}});
    return;
  }}
  canvas.innerHTML='';
  canvas.style.background='transparent';
  const data={{nodes:new vis.DataSet(graph.nodes),edges:new vis.DataSet(graph.edges)}};
  const network=new vis.Network(canvas,data,networkOptions);
  renderedNetworks.set(target,network);
  const clearNetworkBackground=()=>{{
    canvas.style.background='transparent';
    canvas.querySelectorAll('canvas,.vis-network').forEach((node)=>{{ node.style.background='transparent'; }});
  }};
  clearNetworkBackground();
  network.once('stabilized',()=>{{ network.setSize('100%','100%'); network.redraw(); clearNetworkBackground(); network.fit({{animation:false}}); network.setOptions({{physics:false}}); }});
  network.on('hoverNode',(params)=>{{
    const node=graph.nodes.find((entry)=>entry.id===params.node);
    if(node) showTooltip(params.event.event,node.label,node.title||'');
  }});
  network.on('blurNode',hideTooltip);
  network.on('click',(params)=>{{
    if(!params.nodes.length) return;
    const node=graph.nodes.find((entry)=>entry.id===params.nodes[0]);
    if(!node) return;
    const prefix = target === 'dependencies' ? 'Dependency' : target === 'evidence' ? 'Evidence' : target === 'skills' ? 'Skill' : 'Graph';
    setDetail(
      target,
      `${{prefix}} · ${{node.detail_title || node.label}}`,
      node.detail_body || node.title || node.label,
      node.detail_meta || []
    );
  }});
  setTimeout(()=>{{ network.setSize('100%','100%'); network.redraw(); clearNetworkBackground(); network.fit({{animation:false}}); }},120);
}};
const renderSunburst=(container)=>{{
  if(container.dataset.loaded) return;
  if(!window.d3) {{
    renderFallback(container, 'Architecture visualization unavailable', 'D3 did not load, so the sunburst could not render. The detail panel still explains the architecture split.');
    return;
  }}
  container.dataset.loaded='1';
  const width=container.clientWidth||860;
  const height=container.clientHeight||560;
  const radius=Math.min(width,height)/2-18;
  const root=d3.hierarchy(window.__SKILGEN_SUNBURST__).sum((d)=>d.value||1).sort((a,b)=>b.value-a.value);
  d3.partition().size([2*Math.PI, root.height+1])(root);
  root.each((d)=>d.current=d);
  const color=d3.scaleOrdinal()
    .domain(root.descendants().map((d)=>d.data.name))
    .range(['#F4D76A','#46C9FF','#7AF0AE','#FF8D5C','#C685FF','#FF5CA8','#3FE0C6','#6F8CFF']);
  const svg=d3.select(container).append('svg').attr('viewBox',`${{-width/2}} ${{-height/2}} ${{width}} ${{height}}`).attr('role','img').attr('aria-label','Architecture sunburst showing top-level domains, child skills, and evidence-backed capability boundaries.').style('font','12px Inter');
  const ringScale=radius/(root.height+1);
  const arc=d3.arc()
    .startAngle((d)=>d.x0)
    .endAngle((d)=>d.x1)
    .padAngle((d)=>Math.min((d.x1-d.x0)/2,0.01))
    .padRadius(radius*1.4)
    .innerRadius((d)=>Math.max(0,d.y0*ringScale))
    .outerRadius((d)=>Math.max(d.y0*ringScale,d.y1*ringScale-2));
  const arcVisible=(d)=>d.y1<=3&&d.y0>=1&&d.x1>d.x0;
  const labelVisible=(d)=>arcVisible(d)&&((d.x1-d.x0)*(d.y1-d.y0))>0.1;
  const labelTransform=(d)=>{{
    const x=(d.x0+d.x1)/2*180/Math.PI;
    const y=(d.y0+d.y1)/2*ringScale;
    return `rotate(${{x-90}}) translate(${{y}},0) rotate(${{x<180?0:180}})`;
  }};
  const center=svg.append('g').attr('pointer-events','none');
  const label=center.append('text').attr('text-anchor','middle').attr('fill','#F6F7FB').style('font-size','18px').style('font-weight','700').text(root.data.name);
  center.append('text').attr('text-anchor','middle').attr('fill','#98A1B2').attr('dy','1.8em').text('click to zoom');
  const applyDetail=(node)=>{{
    const title=node.depth ? `Architecture · ${{node.data.name}}` : 'Architecture Sunburst';
    setDetail('architecture', title, node.data.summary || node.data.name, node.data.detail_meta || []);
  }};
  const path=svg.append('g').selectAll('path')
    .data(root.descendants().slice(1))
    .join('path')
    .attr('fill',(d)=>{{ let current=d; while(current.depth>1) current=current.parent; return color(current.data.name); }})
    .attr('fill-opacity',(d)=>d.children?1:0.92)
    .attr('stroke','#050608')
    .attr('stroke-width',1.5)
    .attr('d',(d)=>arc(d.current))
    .style('cursor','pointer')
    .on('click',(_,p)=>clicked(p))
    .on('mousemove',(event,d)=>showTooltip(event,d.data.name,d.data.summary||d.data.name))
    .on('mouseleave',hideTooltip);
  const text=svg.append('g')
    .attr('pointer-events','none')
    .attr('text-anchor','middle')
    .style('user-select','none')
    .selectAll('text')
    .data(root.descendants().slice(1))
    .join('text')
    .attr('dy','0.35em')
    .attr('fill','#F6F7FB')
    .style('font-size','11px')
    .attr('fill-opacity',(d)=>+labelVisible(d.current))
    .attr('transform',(d)=>labelTransform(d.current))
    .text((d)=>d.data.name);
  const parent=svg.append('circle').datum(root).attr('r',radius/(root.height+1)).attr('fill','transparent').attr('pointer-events','all').on('click',(_,p)=>clicked(p));
  function clicked(p){{
    applyDetail(p);
    parent.datum(p.parent||root);
    root.each((d)=>d.target={{
      x0:Math.max(0,Math.min(1,(d.x0-p.x0)/(p.x1-p.x0)))*2*Math.PI,
      x1:Math.max(0,Math.min(1,(d.x1-p.x0)/(p.x1-p.x0)))*2*Math.PI,
      y0:Math.max(0,d.y0-p.depth),
      y1:Math.max(0,d.y1-p.depth)
    }});
    const t=svg.transition().duration(750);
    path.transition(t)
      .tween('data',(d)=>{{ const i=d3.interpolate(d.current,d.target); return (tick)=>d.current=i(tick); }})
      .filter(function(d){{ return +this.getAttribute('fill-opacity')||arcVisible(d.target); }})
      .attr('fill-opacity',(d)=>arcVisible(d.target)?(d.children?0.96:0.86):0)
      .attrTween('d',(d)=>()=>arc(d.current));
    text.filter(function(d){{ return +this.getAttribute('fill-opacity')||labelVisible(d.target); }})
      .transition(t)
      .attr('fill-opacity',(d)=>+labelVisible(d.target))
      .attrTween('transform',(d)=>()=>labelTransform(d.current));
    label.text(p.data.name);
  }}
  applyDetail(root);
}};
const renderedSankeys=new Map();
const renderSankey=(target, container)=>{{
  if(!window.d3||!window.d3.sankey) {{
    const fallbackTitle = (target === 'skills' ? 'Skill flow' : target === 'dependencies' ? 'Dependency flow' : 'Evidence flow') + ' unavailable';
    renderFallback(container, fallbackTitle, 'The Sankey libraries did not load, so this graph could not render. The detail panel still contains the explanatory copy.');
    return;
  }}
  if(renderedSankeys.has(target) && container.dataset.loaded==='1') return;
  container.dataset.loaded='1';
  container.innerHTML='';
  const width=container.clientWidth||860;
  const height=container.clientHeight||560;
  const raw=window.__SKILGEN_SANKEY__[target];
  const graph={{nodes:raw.nodes.map((d)=>({{...d}})),links:raw.links.map((d)=>({{...d}}))}};
  const svg=d3.select(container).append('svg').attr('viewBox',`0 0 ${{width}} ${{height}}`).attr('role','img').attr('aria-label', target==='skills' ? 'Skill flow sankey showing domains, parent skills, child skills, and ecosystem packs.' : target==='dependencies' ? 'Dependency flow sankey showing source files, dependency buckets, and concrete imported modules.' : 'Evidence sankey showing languages, evidence kinds, and grounded repository artifacts.');
  const sankey=d3.sankey().nodeId((d)=>d.id).nodeWidth(18).nodePadding(20).extent([[16,18],[width-16,height-18]]);
  const {{nodes,links}}=sankey(graph);
  const linkColor = target==='skills' ? 'rgba(103,213,255,0.34)' : target==='dependencies' ? 'rgba(143,217,168,0.42)' : 'rgba(239,211,122,0.42)';
  svg.append('g').selectAll('path').data(links).join('path')
    .attr('d',d3.sankeyLinkHorizontal())
    .attr('stroke',linkColor)
    .attr('stroke-width',(d)=>Math.max(1,d.width))
    .attr('fill','none')
    .attr('stroke-opacity',0.82)
    .on('mousemove',(event,d)=>showTooltip(event,`${{d.source.name}} → ${{d.target.name}}`,`Value ${{d.value}}`))
    .on('mouseleave',hideTooltip);
  const node=svg.append('g').selectAll('g').data(nodes).join('g');
  node.append('rect')
    .attr('x',(d)=>d.x0)
    .attr('y',(d)=>d.y0)
    .attr('height',(d)=>Math.max(1,d.y1-d.y0))
    .attr('width',(d)=>d.x1-d.x0)
    .attr('rx',7)
    .attr('fill',(d)=>d.layer===1 ? (target==='skills' ? '#67D5FF' : target==='dependencies' ? '#EFD37A' : '#EFD37A') : d.layer===2 ? (target==='skills' ? '#8FD9A8' : target==='dependencies' ? '#67D5FF' : '#B9C2D4') : target==='dependencies' ? '#8FD9A8' : '#11161E')
    .attr('stroke','#F6F7FB')
    .attr('stroke-opacity',0.32)
    .style('cursor','pointer')
    .on('mousemove',(event,d)=>showTooltip(event,d.name,`Layer ${{d.layer}}`))
    .on('mouseleave',hideTooltip)
    .on('click',(_,d)=>{{
      if(detailDefaults[target]) {{
        const prefix = target === 'skills' ? 'Skill' : target === 'dependencies' ? 'Dependency' : 'Evidence';
        setDetail(target, `${{prefix}} · ${{d.name}}`, d.detail || d.name, d.detail_meta || []);
      }}
    }});
  node.append('text')
    .attr('x',(d)=>d.x0<width/2?d.x1+8:d.x0-8)
    .attr('y',(d)=>(d.y1+d.y0)/2)
    .attr('dy','0.35em')
    .attr('text-anchor',(d)=>d.x0<width/2?'start':'end')
    .attr('fill','#F6F7FB')
    .style('font','12px Inter')
    .text((d)=>d.name);
  renderedSankeys.set(target,true);
  if(detailDefaults[target]) setDetail(target, detailDefaults[target].title, detailDefaults[target].body, detailDefaults[target].meta);
}};
const renderAnalyticsRadial=(container)=>{{
  if(container.dataset.loaded==='1') return;
  if(!window.d3) {{
    renderFallback(container, 'Usage analytics unavailable', 'D3 did not load, so the radial analytics view could not render. The ranking cards still summarize the most important skills.');
    return;
  }}
  container.dataset.loaded='1';
  const data=(window.__SKILGEN_RADIAL__ && window.__SKILGEN_RADIAL__.analytics) || [];
  container.innerHTML='';
  const width=container.clientWidth||860;
  const height=container.clientHeight||560;
  const innerRadius=88;
  const outerRadius=Math.min(width,height)/2-30;
  const svg=d3.select(container).append('svg').attr('viewBox',`${{-width/2}} ${{-height/2}} ${{width}} ${{height}}`).attr('role','img').attr('aria-label','Radial analytics chart showing per-skill usage, depth, and content richness.');
  if(!data.length){{
    svg.append('text').attr('fill','#98A1B2').attr('text-anchor','middle').text('No skill usage recorded yet');
    return;
  }}
  const keys=['load_score','depth_score','richness_score'];
  const colors={{
    load_score:'#EFD37A',
    depth_score:'#67D5FF',
    richness_score:'#8FD9A8',
  }};
  const x=d3.scaleBand().domain(data.map((d)=>d.title)).range([0,2*Math.PI]).align(0);
  const maxValue=d3.max(data,(d)=>d.load_score+d.depth_score+d.richness_score)||100;
  const y=d3.scaleLinear().domain([0,maxValue]).range([innerRadius,outerRadius]);
  const stack=d3.stack().keys(keys);
  const stacked=stack(data);
  const arc=d3.arc()
    .innerRadius((d)=>y(d[0]))
    .outerRadius((d)=>y(d[1]))
    .startAngle((d)=>x(d.data.title))
    .endAngle((d)=>x(d.data.title)+x.bandwidth())
    .padAngle(0.018)
    .padRadius(innerRadius);
  const layers=svg.append('g').selectAll('g').data(stacked).join('g').attr('fill',(d)=>colors[d.key]);
  layers.selectAll('path').data((d)=>d.map((entry)=>Object.assign(entry,{{key:d.key}}))).join('path')
    .attr('d',arc)
    .attr('stroke','#050608')
    .attr('stroke-width',1.2)
    .style('cursor','pointer')
    .on('mousemove',(event,d)=>showTooltip(event,d.data.title,`${{d.key.replace('_score','').replace('_',' ')}} · ${{Math.round(d.data[d.key])}}`))
    .on('mouseleave',hideTooltip)
    .on('click',(_,d)=>setDetail('analytics', `Usage · ${{d.data.title}}`, d.data.summary, [
      `${{d.data.usage_label}}: ${{d.data.loads}}`,
      `Recorded loads: ${{d.data.recorded_loads}}`,
      `Depth score: ${{Math.round(d.data.depth_score)}}`,
      `Richness score: ${{Math.round(d.data.richness_score)}}`,
      `Headings: ${{d.data.headings}}, bullets: ${{d.data.bullets}}, references: ${{d.data.references}}`,
    ]));
  svg.append('g').selectAll('text').data(data).join('text')
    .attr('text-anchor',(d)=>((x(d.title)+x.bandwidth()/2+Math.PI/2)%(2*Math.PI))<Math.PI?'start':'end')
    .attr('transform',(d)=>{{
      const angle=(x(d.title)+x.bandwidth()/2)-Math.PI/2;
      const radius=outerRadius+10;
      const rotation=angle*180/Math.PI;
      const flip=rotation>90&&rotation<270?180:0;
      return `rotate(${{rotation}}) translate(${{radius}},0) rotate(${{flip}})`;
    }})
    .attr('fill','#F6F7FB')
    .style('font','10px Inter')
    .text((d)=>d.title);
  const legend=svg.append('g').attr('transform',`translate(${{-outerRadius + 28}},${{-outerRadius + 28}})`);
  [
    ['Usage','#EFD37A'],
    ['Depth','#67D5FF'],
    ['Content','#8FD9A8'],
  ].forEach(([label,color],index)=>{{
    const row=legend.append('g').attr('transform',`translate(0,${{index*18}})`);
    row.append('circle').attr('r',5).attr('cx',0).attr('cy',0).attr('fill',color);
    row.append('text').attr('x',12).attr('y',4).attr('fill','#98A1B2').style('font','11px Inter').text(label);
  }});
  const usageMode = data[0] ? data[0].usage_label : 'Usage';
  const hasLiveUsage = data.some((entry)=>Number(entry.recorded_loads || 0) > 0);
  svg.append('text').attr('text-anchor','middle').attr('fill','#F6F7FB').style('font','700 15px Inter').text(hasLiveUsage ? 'Live Usage' : 'Modeled Usage');
  svg.append('text').attr('text-anchor','middle').attr('dy','1.6em').attr('fill','#98A1B2').style('font','11px Inter').text(hasLiveUsage ? 'depth + content' : 'content signal only');
  if(data[0]){{
    setDetail('analytics', `Usage · ${{data[0].title}}`, data[0].summary, [
      `${{data[0].usage_label}}: ${{data[0].loads}}`,
      `Recorded loads: ${{data[0].recorded_loads}}`,
      `Depth score: ${{Math.round(data[0].depth_score)}}`,
      `Richness score: ${{Math.round(data[0].richness_score)}}`,
      `Headings: ${{data[0].headings}}, bullets: ${{data[0].bullets}}, references: ${{data[0].references}}`,
    ]);
  }}
}};
const setPanel=(target)=>{{
  activateSet(tabs,panels,target,'target','panel');
  activateSet(tabs,copies,target,'target','copy');
  window.requestAnimationFrame(()=>{{
    const panel=document.querySelector(`.graph-panel[data-panel="${{target}}"]`);
    const networkCanvas=panel?.querySelector('.network-canvas');
    if(networkCanvas){{ renderNetwork(target,networkCanvas); return; }}
    const sunburstCanvas=panel?.querySelector('.sunburst-canvas');
    if(sunburstCanvas){{ renderSunburst(sunburstCanvas); return; }}
    const sankeyCanvas=panel?.querySelector('.sankey-canvas');
    if(sankeyCanvas){{ renderSankey(target,sankeyCanvas); }}
  }});
}};
tabs.forEach((tab,index)=>{{
  tab.addEventListener('click',()=>setPanel(tab.dataset.target));
  tab.addEventListener('keydown',(event)=>{{
    if(event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    event.preventDefault();
    const offset = event.key === 'ArrowRight' ? 1 : -1;
    const nextIndex = (index + offset + tabs.length) % tabs.length;
    tabs[nextIndex].focus();
    setPanel(tabs[nextIndex].dataset.target);
  }});
}});
opsTabs.forEach((tab)=>tab.addEventListener('click',()=>activateSet(opsTabs,opsCopies,tab.dataset.target,'target','copy')));
surfaceTabs.forEach((tab)=>tab.addEventListener('click',()=>activateSet(surfaceTabs,surfaceCopies,tab.dataset.target,'target','copy')));
const analyticsCanvas=document.querySelector('[data-radial="analytics"]');
if(analyticsCanvas) renderAnalyticsRadial(analyticsCanvas);
const dependencyNetworkCanvas=document.querySelector('[data-network="dependencies"]');
if(dependencyNetworkCanvas) renderNetwork('dependencies', dependencyNetworkCanvas);
const chapterLinks=[...document.querySelectorAll('.topbar-nav a[href^="#"], .rail-nav a[href^="#"]')];
chapterLinks.forEach((link)=>link.addEventListener('click',(event)=>{{
  const targetId=link.getAttribute('href');
  if(!targetId || targetId === '#') return;
  const target=document.querySelector(targetId);
  if(!target) return;
  event.preventDefault();
  const offset=96;
  const top=target.getBoundingClientRect().top + window.scrollY - offset;
  window.scrollTo({{top:Math.max(0, top), behavior:'smooth'}});
  chapterLinks.forEach((item)=>item.classList.toggle('active', item === link));
  if(window.history && window.history.replaceState) window.history.replaceState(null,'',targetId);
}}));
setPanel('architecture');
if(opsTabs.length) activateSet(opsTabs,opsCopies,'worker','target','copy');
if(surfaceTabs.length) activateSet(surfaceTabs,surfaceCopies,'external','target','copy');
window.addEventListener('resize',()=>{{
  const activePanel=document.querySelector('.graph-panel.active');
  const activeTarget=activePanel ? activePanel.dataset.panel : 'architecture';
  if(activeTarget) setPanel(activeTarget);
}});
""".strip()

    return f"""
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Skilgen Dashboard · {escape(repo_name)}</title>
<link rel='preconnect' href='https://fonts.googleapis.com'>
<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
<link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap' rel='stylesheet'>
<script src='https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js' integrity='sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i' crossorigin='anonymous'></script>
<script src='https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js' integrity='sha384-SM54CE5h+qdDI046d2Y5ym7wq1kq4uxcQ1cqGq5/+5jrE5tPLeDJSq711Q8sIska' crossorigin='anonymous'></script>
<script src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js' integrity='sha384-m/pqkSdIs50f1nWlv062s9HmCAygFne+xY7uot2M8ZVijdcC+c/n97dFCfAZnKwO' crossorigin='anonymous'></script>
<style>{dashboard_styles}</style>
</head>
<body>
<header class='topbar'>
  <div class='topbar-brand'>
    <strong>Skilgen</strong>
    <span>Agent Intelligence Surface</span>
  </div>
  <nav class='topbar-nav'>
    <a class='active' href='#pulse'>The Pulse</a>
    <a href='#weaver'>The Weaver</a>
    <a href='#nexus'>The Nexus</a>
    <a href='#foundry'>The Foundry</a>
  </nav>
  <div class='topbar-actions'>
    <div class='topbar-icon'>hub</div>
    <div class='topbar-icon'>ops</div>
    <div class='corner-badge'>&copy; Skilgen</div>
  </div>
</header>
<aside class='rail'>
  <section class='rail-card'>
    <div class='rail-title'>Skilgen OS</div>
    <div class='rail-subtitle'>Repository · {escape(_compact_label(repo_name, max_length=28))}</div>
  </section>
  <nav class='rail-nav'>
    <a class='active' href='#pulse'>The Pulse</a>
    <a href='#weaver'>The Weaver</a>
    <a href='#nexus'>The Nexus</a>
    <a href='#foundry'>The Foundry</a>
  </nav>
  <section class='rail-card'>
    <div class='rail-title'>Legend</div>
    <ul class='rail-legend'>
      <li><div class='legend-row'><span class='legend-dot' style='background:{architecture_palette[0]}'></span>Active domains</div><strong>{top_level_domains}</strong></li>
      <li><div class='legend-row'><span class='legend-dot' style='background:{architecture_palette[1]}'></span>Evidence items</div><strong>{evidence_count}</strong></li>
      <li><div class='legend-row'><span class='legend-dot' style='background:{architecture_palette[2]}'></span>Dependency edges</div><strong>{dependency_edges}</strong></li>
    </ul>
  </section>
  <section class='rail-card'>
    <div class='rail-title'>Live State</div>
    <div class='metric-pile'>
      <div class='metric-chip'><span>Score</span><strong>{int(round(score_value))}</strong></div>
      <div class='metric-chip'><span>Freshness</span><strong>{int(round(float(diff['freshness_score'])))}/{int(diff['freshness_max'])}</strong></div>
      <div class='metric-chip'><span>Outputs</span><strong>{outputs_ready}</strong></div>
      <div class='metric-chip'><span>Stale</span><strong>{stale_count}</strong></div>
    </div>
  </section>
</aside>
<main class='page'>
  <section id='pulse' class='chapter'>
    <div class='chapter-head'>
      <div class='chapter-brand'>
        <div>
          <div class='chapter-kicker'>The Pulse</div>
          <h1 class='chapter-title'>Skilgen Operating System</h1>
        </div>
        {brand_mark}
      </div>
      <div class='legend'>
        {pill(f"{stale_count} stale skills" if stale_count else "All skills current", "warning" if stale_count else "good")}
        {pill(f"Auto-update {'on' if auto_update.get('enabled') else 'off'}", "good" if auto_update.get("enabled") else "warning")}
        {pill("File-state freshness" if str(diff['git']['event_type']) == 'not_git_repo' else f"Git-aware {str(diff['git']['event_type']).replace('_', ' ')}")}
      </div>
    </div>
    <section class='hero-grid'>
      <section class='hero-panel hero-left'>
        <div class='brand-wrap'>
          <div class='repo-chip' title='{escape(repo_name)}'>Repository · {escape(_compact_label(repo_name, max_length=30))}</div>
        </div>
        <div class='hero-metrics'>
          {metric("Active Domains", str(top_level_domains), "Top-level architecture seams now materialized into the skill tree.")}
          {metric("Evidence", str(evidence_count), "Files, snippets, config, docs, and tests feeding the graph.")}
          {metric("Dependency Edges", str(dependency_edges), "Import pressure surfaced from the active repository graph.")}
        </div>
      </section>
      <aside class='hero-panel hero-right'>
        <div class='score-top'>
          <div class='eyebrow'>Quality + freshness in one surface</div>
          <div class='score-ring' style='--score:{score_percent};'><div class='score-ring-content'><strong>{int(round(score_value))}<small>/100</small></strong><span>{score_label}</span></div></div>
          <div class='score-ring-note'>{escape(score_signal)} · {int(round(score_value))} out of 100</div>
        </div>
        <div class='score-rail'>
          <article class='stat-card'><div class='stat-label'>Freshness</div><div class='stat-value'>{int(round(float(diff['freshness_score'])))}/{int(diff['freshness_max'])}</div><div class='stat-note'>{escape(str(diff['reason']).replace('_', ' '))}</div></article>
          <article class='stat-card'><div class='stat-label'>Parsers</div><div class='stat-value'>{len(parser_backends) or 1}</div><div class='stat-note'>{escape(', '.join(parser_backends[:3]) or 'unknown')}</div></article>
          <article class='stat-card'><div class='stat-label'>Calls</div><div class='stat-value'>{call_edges}</div><div class='stat-note'>Observed call relationships from parsed source evidence.</div></article>
          <article class='stat-card'><div class='stat-label'>Tests</div><div class='stat-value'>{test_links}</div><div class='stat-note'>Tests mapped back to concrete implementation files.</div></article>
        </div>
      </aside>
    </section>
    <section class='panel'>
      <h2>Usage Analytics</h2>
      <div class='section-copy'>Skilgen tracks every skill separately, then layers in tree depth, content richness, and live runtime traces so you can see where agent attention actually lands.</div>
      <div class='analytics-board'>
        <div class='graph-stage'>
          <div class='radial-canvas' data-radial='analytics'></div>
        </div>
        <div class='analytics-side'>
          <div class='legend'>
            {pill(_count_phrase(int(analytics.get("live_event_count", 0)), "live usage event"), "good" if int(analytics.get("live_event_count", 0)) else "default")}
            {pill(f"{len(analytics.get('skill_usage', []))} mapped skills")}
            {pill("Modeled attention" if usage_mode != "live" else "Live traces", "warning" if usage_mode != "live" else "good")}
            {pill(f"{int(analytics.get('planner_event_count', 0))} planner warmups ignored")}
          </div>
          <div class='mini-panel'>
            <div class='micro-label'>{'Skill Attention Ranking' if usage_mode != 'live' else 'Most Active Skills'}</div>
            <ul>{analytics_markup}</ul>
          </div>
          <div class='mini-panel'>
            <div class='micro-label'>Selected Skill</div>
            <p class='nuance-copy'><strong>{escape(str(hot_skill.get('title', 'No real skill usage yet')))}</strong><br>{escape(str(hot_skill.get('summary', 'Skilgen will surface the hottest genuinely-used skill here once agent usage events exist.')))}</p>
            <p class='nuance-copy'>{escape('Modeled attention' if usage_mode != 'live' else 'Live usage')}: {int(hot_skill.get('effective_loads', hot_skill.get('loads', 0)))} · Recorded loads: {int(hot_skill.get('loads', 0))} · Depth: {int(hot_skill.get('depth', 0))} · Richness: {int(hot_skill.get('richness', 0))}</p>
            <div class='graph-detail' data-detail='analytics'>
              <h4>Usage Analytics</h4>
              <p>Skilgen surfaces the currently most meaningful skill here. Click a radial segment to inspect its summary, usage, and content shape.</p>
              <ul class='graph-detail-meta'>
                <li>Usage is live when real skill loads exist.</li>
                <li>Otherwise Skilgen falls back to modeled attention so the surface still teaches something useful.</li>
              </ul>
            </div>
          </div>
          <div class='trend-panel mini-panel'>
            <div class='trend-head'>
              <div>
                <div class='micro-label'>Score Trend</div>
                <div class='section-copy'>This sparkline reflects the most meaningful recent snapshots rather than noisy identical reruns.</div>
              </div>
              <div class='legend'>
                {"<strong>Stable</strong>" if trend_is_flat else ""}
                {pill(f"Delta {score_trend['delta_from_previous']:+.2f}", "good" if float(score_trend["delta_from_previous"]) >= 0 else "warning")}
              </div>
            </div>
            <div class='sparkline'>{trend_markup}</div>
            <div class='trend-ticks'>{trend_ticks_markup}</div>
            <div class='trend-summary'>{escape(trend_summary)}</div>
          </div>
        </div>
      </div>
    </section>
    <section class='panel'>
      <h2>Before vs After</h2>
      <div class='section-copy'>This makes the lift explicit: how the repo looked before Skilgen materialized any skills, what Skilgen created, and why that changes agent usefulness.</div>
      <div class='compare-grid'>
        <article class='compare-card'>
          <div class='micro-label'>Before Skilgen</div>
          <div class='compare-score'><div class='compare-score-value'>{int(round(baseline_value))}</div><div class='compare-score-label'>{baseline_label}</div></div>
          <p class='nuance-copy'>{escape(str(baseline_scorecard.get('explanation', 'The repo is readable as code, but no reusable skill system exists yet.')))}</p>
          <ul class='compare-list'>
            <li><span>Coverage from repo shape</span><strong>{int(round(float(baseline_scorecard.get('subscores', {}).get('coverage', {}).get('score', 0))))} / 25</strong></li>
            <li><span>Grounded reusable skills</span><strong>0 / 25</strong></li>
            <li><span>Freshness contract</span><strong>0 / 25</strong></li>
            <li><span>Agent operating artifacts</span><strong>0 / 25</strong></li>
          </ul>
        </article>
        <article class='compare-card'>
          <div class='micro-label'>With Skilgen</div>
          <div class='compare-score'><div class='compare-score-value'>{int(round(score_value))}</div><div class='compare-score-label'>{score_label}</div>{pill(f'{score_delta_value:+.2f}', 'good' if score_delta_value > 0 else 'default')}</div>
          <p class='nuance-copy'>Skilgen converts repo analysis into a maintained skill system with grounded references, explicit startup guidance, and freshness tracking that agents can actually use.</p>
          <ul class='compare-list'>{score_compare_markup}</ul>
        </article>
        <article class='compare-card'>
          <div class='micro-label'>What Was Created</div>
          <div class='compare-score'><div class='compare-score-value'>{total_skills}</div><div class='compare-score-label'>Total Skills</div></div>
          <p class='nuance-copy'>{top_level_domains} top-level domains turned into {child_skill_count} child skills and {outputs_ready} repo-local operating artifacts, so the output is navigable instead of just descriptive.</p>
          <ul class='compare-list'>
            <li><span>Top-level domains</span><strong>{top_level_domains}</strong></li>
            <li><span>Child skills</span><strong>{child_skill_count}</strong></li>
            <li><span>Ready outputs</span><strong>{outputs_ready}</strong></li>
            <li><span>Skills currently stale</span><strong>{stale_count}</strong></li>
          </ul>
        </article>
      </div>
      <div class='process-grid'>{process_cards_markup}</div>
    </section>
  </section>
  <section id='weaver' class='chapter'>
    <div class='chapter-head'>
      <div>
        <div class='chapter-kicker'>The Weaver</div>
        <h2 class='chapter-title'>Graph Studio</h2>
        <p class='chapter-copy'>Graph Studio keeps the same features and plots, but presents them as a darker operating canvas. Architecture Sunburst, Evidence Flow, dependency flow, skill flow, and a dedicated Dependency Network all stay available.</p>
      </div>
      <div class='legend'>
        {pill(f"{len(architecture['domains'])} active domains", "good")}
        {pill(f"{evidence_count} evidence items")}
        {pill(f"{dependency_edges} dependency edges")}
      </div>
    </div>
    <section class='panel graph-shell'>
      <div class='graph-toolbar'>
        <div class='section-title'>Graph Studio</div>
        <div class='graph-tabs'>
          <button class='graph-tab active' data-target='architecture' role='tab' aria-selected='true'>Architecture</button>
          <button class='graph-tab' data-target='evidence' role='tab' aria-selected='false'>Evidence</button>
          <button class='graph-tab' data-target='dependencies' role='tab' aria-selected='false'>Dependencies</button>
          <button class='graph-tab' data-target='skills' role='tab' aria-selected='false'>Skills</button>
        </div>
      </div>
      <div class='graph-frame'>
        <div class='graph-stage'>
          <div class='graph-panel active' data-panel='architecture' role='tabpanel' aria-hidden='false'><div class='sunburst-canvas' data-sunburst='architecture'></div></div>
          <div class='graph-panel' data-panel='evidence' role='tabpanel' aria-hidden='true'><div class='sankey-canvas' data-sankey='evidence'></div></div>
          <div class='graph-panel' data-panel='dependencies' role='tabpanel' aria-hidden='true'><div class='sankey-canvas' data-sankey='dependencies'></div></div>
          <div class='graph-panel' data-panel='skills' role='tabpanel' aria-hidden='true'><div class='sankey-canvas' data-sankey='skills'></div></div>
        </div>
        <aside class='graph-aside'>
          <div class='graph-copy active' data-copy='architecture'>
            <h3 data-copy-title='architecture'>Architecture Sunburst</h3>
            <p data-copy-body='architecture'>{escape(architecture['system_summary'])}</p>
            <ul>
              <li>{escape(_count_phrase(len(architecture['domains']), 'top-level domain'))} are visible in the current architecture slice.</li>
              <li>{escape(_count_phrase(len(architecture['materialization_plan']), 'materialization decision'))} shape how parent and child skills are split.</li>
              <li>Click any arc to inspect the exact capability boundary, evidence count, and recommended skill path.</li>
            </ul>
            <div class='micro-label'>Visible Domain Legend</div>
            <ul class='graph-legend'>{architecture_legend}</ul>
            <div class='graph-detail' data-detail='architecture'>
              <h4>Architecture Sunburst</h4>
              <p>Skilgen starts from parser-backed evidence, then lets the architecture view reveal how responsibilities split across the repo. Click an arc to inspect that specific capability boundary.</p>
              <ul class='graph-detail-meta'>
                <li>Color separates architecture families so the high-level shape is easy to scan.</li>
                <li>Clicking a domain replaces this summary with node-specific detail.</li>
              </ul>
            </div>
          </div>
          <div class='graph-copy' data-copy='evidence'>
            <h3 data-copy-title='evidence'>Evidence Flow</h3>
            <p data-copy-body='evidence'>Follow how languages and evidence kinds feed concrete files. This is the visible proof behind the architecture Skilgen is synthesizing.</p>
            <ul>
              <li>Left: dominant languages or repo root.</li>
              <li>Middle: evidence kinds.</li>
              <li>Right: files or source artifacts.</li>
            </ul>
            <div class='graph-detail' data-detail='evidence'>
              <h4>Evidence Flow</h4>
              <p>Skilgen walks file by file and groups the repo into languages, evidence kinds, and concrete artifacts. Click any node to inspect the exact nuance that was extracted.</p>
              <ul class='graph-detail-meta'>
                <li>Evidence is grounded in real files, snippets, configs, docs, and tests.</li>
                <li>This is the proof layer beneath every generated skill.</li>
              </ul>
            </div>
          </div>
          <div class='graph-copy' data-copy='dependencies'>
            <h3 data-copy-title='dependencies'>Dependency Flow</h3>
            <p data-copy-body='dependencies'>Follow how high-fanout source files pull on repo modules, stdlib, test boundaries, and external packages. This makes dependency risk readable in the same visual language as Evidence.</p>
            <ul>
              <li>Left: source files creating dependency pressure.</li>
              <li>Middle: dependency buckets.</li>
              <li>Right: exact imported modules or files.</li>
            </ul>
            <div class='graph-detail' data-detail='dependencies'>
              <h4>Dependency Flow</h4>
              <p>Skilgen turns import relationships into a dependency flow so you can see what will feel expensive, central, or risky before an agent starts editing.</p>
              <ul class='graph-detail-meta'>
                <li>Click any node to inspect the source hotspot, bucket meaning, or concrete dependency endpoint.</li>
                <li>This uses the same reading pattern as Evidence so the dashboard stays visually consistent.</li>
              </ul>
            </div>
          </div>
          <div class='graph-copy' data-copy='skills'>
            <h3 data-copy-title='skills'>Skill Flow</h3>
            <p data-copy-body='skills'>See how domains become parent skills, generated child skills, and external packs that Skilgen has already pulled in because the repo signaled they matter.</p>
            <ul>
              <li>Left: domain families.</li>
              <li>Middle: parent skills.</li>
              <li>Right: generated child skills and external skill packs.</li>
            </ul>
            <div class='micro-label'>External skills in play</div>
            <ul class='graph-legend'>{("".join(f"<li><strong>{escape(item)}</strong><span>installed from repo signals</span></li>" for item in external_skill_labels) or "<li class='muted'>No external skills installed yet.</li>")}</ul>
            <p class='nuance-copy'>Skilgen folds external skill packs into the same surface so agents can see generated skill boundaries and imported ecosystem capability together.</p>
            <div class='graph-detail' data-detail='skills'>
              <h4>Skill Flow</h4>
              <p>Skilgen does not stop at high-level domains. It goes file by file, then decides where nuance deserves its own child skill, where it should stay merged, and where external packs strengthen the repo-native tree.</p>
              <ul class='graph-detail-meta'>
                <li>Click a skill node to inspect why that skill exists.</li>
                <li>External packs show which ecosystem skills are already active in the map.</li>
              </ul>
            </div>
          </div>
        </aside>
      </div>
      <div class='health-grid'>
        <div class='health-tile'><span>Dependency Network</span><strong>{dependency_edges}</strong><div class='nuance-copy'>Interactive dependency map lives below the flow view so network hotspots still remain available.</div></div>
        <div class='health-tile'><span>Parser-backed Files</span><strong>{total_symbol_files}</strong><div class='nuance-copy'>The living map is grounded in parser-backed evidence rather than only filenames.</div></div>
        <div class='health-tile'><span>Architecture Plan</span><strong>{len(architecture['materialization_plan'])}</strong><div class='nuance-copy'>Split and keep decisions stay tied to evidence and cross-domain pressure.</div></div>
      </div>
      <div class='dashboard-columns'>
        <div class='mini-panel'>
          <div class='micro-label'>Dependency Network</div>
          <div class='network-canvas' data-network='dependencies' aria-label='Interactive dependency network showing repo-local import relationships.'></div>
          <div class='network-mobile-note canvas-fallback'>Dependency network hidden on small screens. Open on a wider screen to inspect the interactive map.</div>
        </div>
        <div class='mini-panel'>
          <div class='micro-label'>Architecture Legend</div>
          <ul class='graph-legend'>{architecture_legend}</ul>
        </div>
      </div>
    </section>
  </section>
  <section id='nexus' class='chapter'>
    <div class='chapter-head'>
      <div>
        <div class='chapter-kicker'>The Nexus</div>
        <h2 class='chapter-title'>Insight Layer</h2>
        <p class='chapter-copy'>Quality gates, freshness, and architecture decisions sit together here so the repo’s score and operating shape can be interpreted without guessing.</p>
      </div>
    </div>
    <section class='panel'>
      <h2>Skilgen Score</h2>
      <div class='section-copy'>Groundedness, coverage, freshness, and structure are grouped here as one quality bar instead of separate floating metrics.</div>
      <div class='score-board'>
        <div>
          <div class='subscore-stack'>{subscores_markup}</div>
          <ul class='quality-list'>{quality_gates_markup}</ul>
          {("<p class='nuance-copy'><strong>Coverage action:</strong> No mapped tests were found yet, so coverage is being dragged down. Add test files or map existing tests into the repo surface, then rerun `skilgen deliver` to raise grounded coverage.</p>" if test_links == 0 else "")}
          {(f"<p class='nuance-copy'><strong>Unmapped files:</strong> {escape(', '.join(score['subscores']['coverage'].get('unmapped_files', [])[:5]))}</p>" if score["subscores"]["coverage"].get("unmapped_files") else "")}
        </div>
        <div class='score-callout'>
          <div class='score-copy'>
            <strong>{escape(score_signal)}</strong>
            <div class='nuance-copy'>This score is not saying Skilgen failed to generate skills. It is reporting how grounded, covered, fresh, and structurally usable the current repo-to-skill surface is right now.</div>
          </div>
          <div class='score-copy'>
            <strong>What the number means</strong>
            <div class='nuance-copy'>A lower score usually means the repo still has missing evidence, weak test mapping, stale generated outputs, or sparse skill structure. It is an improvement target, not a public confession that the product is broken.</div>
          </div>
          <div class='legend'>
            {pill(f"Regressions {len(score_trend['regressions'])}", "warning" if score_trend["regressions"] else "good")}
            {pill(f"{config_edges} config/runtime edges")}
            {pill(f"{call_edges} call edges")}
          </div>
        </div>
      </div>
    </section>
    <section class='panel'>
      <h2>Diff + Freshness</h2>
      <div class='section-copy'>See exactly what changed, which domains are stale, and what remains safe to reuse.</div>
      <div class='dashboard-columns'>
        <div><div class='micro-label'>Changed Files</div><ul class='list'>{changed_files_markup}</ul></div>
        <div><div class='micro-label'>Impacted Domains</div><ul class='list'>{impacted_markup}</ul></div>
      </div>
      <div class='legend'>
        {pill(f"Current domains: {', '.join(diff['current_domains'][:4]) or 'none'}")}
        {pill("No git metadata; freshness is file-state based" if str(diff['git']['event_type']) == 'not_git_repo' else f"Git event {str(diff['git']['event_type']).replace('_', ' ')}")}
        {pill(f"Freshness {int(round(float(diff['freshness_score'])))} / {int(diff['freshness_max'])}", "good" if float(diff["freshness_score"]) >= 20 else "warning")}
      </div>
    </section>
    <section class='panel'>
      <h2>Architecture Materialization</h2>
      <div class='section-copy'>Skilgen uses the architecture plan to decide where skills should split, merge, or stay consolidated.</div>
      <table><thead><tr><th>Domain</th><th>Decision</th><th>Parent Skill</th><th>Child Skills</th><th>Rationale</th></tr></thead><tbody>{plan_rows}</tbody></table>
      <div class='domain-grid'>{domain_cards}</div>
    </section>
  </section>
  <section id='foundry' class='chapter'>
    <div class='chapter-head'>
      <div>
        <div class='chapter-kicker'>The Foundry</div>
        <h2 class='chapter-title'>Operations</h2>
        <p class='chapter-copy'>Worker execution, outputs, capability packs, and startup guidance all stay on the same operating page so the dashboard is not just decorative.</p>
      </div>
    </div>
    <section class='panel'>
      <h2>Auto-Update + Agent Readiness</h2>
      <div class='section-copy'>A live operations board for the worker, the last repo event, the start order, and the repo-local outputs currently ready to load.</div>
      <div class='ops-board'>
        <div class='ops-tabs'>
          <button class='ops-tab active' data-target='worker' role='tab' aria-selected='true'>Worker</button>
          <button class='ops-tab' data-target='event' role='tab' aria-selected='false'>Last Event</button>
          <button class='ops-tab' data-target='order' role='tab' aria-selected='false'>Start Order</button>
          <button class='ops-tab' data-target='outputs' role='tab' aria-selected='false'>Outputs</button>
        </div>
        <div class='ops-copy active' data-copy='worker' role='tabpanel' aria-hidden='false'>
          <div class='ops-grid'><div class='ops-tile'><strong>Worker state</strong><span>{escape('Running in background' if auto_update.get('running') else 'Idle until the next change')}</span></div><div class='ops-tile'><strong>Refresh policy</strong><span>{escape(str(auto_update.get('enabled') and 'Automatic refresh is enabled' or 'Manual refresh only'))}</span></div><div class='ops-tile'><strong>Current freshness</strong><span>{int(round(float(diff['freshness_score'])))}/{int(diff['freshness_max'])}</span></div><div class='ops-tile'><strong>Readiness signal</strong><span>{escape('Agents can load the current repo-local outputs now')}</span></div></div>
        </div>
        <div class='ops-copy' data-copy='event' role='tabpanel' aria-hidden='true'>
          <div class='ops-grid'><div class='ops-tile'><strong>Last git-aware event</strong><span>{escape(str(auto_update.get('last_event') or diff['git'].get('event_type') or 'none').replace('_', ' '))}</span></div><div class='ops-tile'><strong>Reason</strong><span>{escape(str(diff['reason']).replace('_', ' '))}</span></div><div class='ops-tile'><strong>Changed files</strong><span>{changed_count}</span></div><div class='ops-tile'><strong>Stale skills</strong><span>{stale_count}</span></div></div>
        </div>
        <div class='ops-copy' data-copy='order' role='tabpanel' aria-hidden='true'>
          <div class='ops-grid'><div class='ops-tile'><strong>Decision focus</strong><span>{escape(', '.join(_display_domain_name(item) for item in decision.get('prioritized_domains', [])[:4]) or 'No prioritized domains yet')}</span></div><div class='ops-tile'><strong>Memory load</strong><span>{escape(', '.join(decision.get('memory_to_load', [])[:3]) or 'No memory recommended')}</span></div><div class='ops-tile'><strong>Prioritized skills</strong><span>{escape(', '.join(_display_skill_name(item) for item in decision.get('prioritized_skill_paths', [])[:3]) or 'No prioritized skills yet')}</span></div><div class='ops-tile'><strong>Nuance</strong><span>{escape('Skilgen is sequencing agent context from evidence, score, diff, architecture, and live repo state instead of a static startup order.')}</span></div></div>
        </div>
        <div class='ops-copy' data-copy='outputs' role='tabpanel' aria-hidden='true'>
          <div class='micro-label'>Generated Outputs</div>
          <ul class='list'>{outputs_markup}</ul>
          <div class='micro-label'>Prioritized Skills</div>
          <ul class='list'>{list_items(decision.get('prioritized_skill_paths', [])[:6], empty='No prioritized skills yet')}</ul>
        </div>
      </div>
    </section>
    <section class='panel'>
      <h2>Capability Layer</h2>
      <div class='section-copy'>External skills, enterprise packs, and MCP connectors share the same operating surface.</div>
      <div class='surface-tabs'>
        <button class='surface-tab active' data-target='external' role='tab' aria-selected='true'>External Skills</button>
        <button class='surface-tab' data-target='enterprise' role='tab' aria-selected='false'>Enterprise Skills</button>
        <button class='surface-tab' data-target='connectors' role='tab' aria-selected='false'>MCP Connectors</button>
      </div>
      <div class='surface-copy active' data-copy='external' role='tabpanel' aria-hidden='false'><div class='mini-panel'><div class='micro-label'>External skills present</div><ul>{external_markup}</ul><p class='nuance-copy'>These packs were installed because the repository signaled they were relevant, so the skill system includes ecosystem knowledge as well as repo-native guidance.</p></div></div>
      <div class='surface-copy' data-copy='enterprise' role='tabpanel' aria-hidden='true'><div class='mini-panel'><div class='micro-label'>Enterprise skills present</div><ul>{enterprise_markup}</ul><p class='nuance-copy'>Enterprise packs let the repo-local skill map inherit organization-specific standards, playbooks, and internal conventions.</p></div></div>
      <div class='surface-copy' data-copy='connectors' role='tabpanel' aria-hidden='true'><div class='mini-panel'><div class='micro-label'>Connected profiles</div><ul>{connector_markup}</ul><div class='micro-label'>Recommended profiles</div><ul>{recommended_connector_markup}</ul><p class='nuance-copy'>These are capability profiles available to bind into an agent runtime. Recommended profiles are not shown as live authenticated sessions unless the runtime has actually connected them.</p></div></div>
    </section>
    <section class='panel'>
      <h2>Process Surface</h2>
      <div class='section-copy'>This is the operating loop beneath the visuals: read the repo, materialize skills, and give agents a better startup surface.</div>
      <div class='process-grid'>{process_cards_markup}</div>
    </section>
  </section>
  <footer class='footer-bar'>
    <div class='footer-mark'>Generated by Skilgen</div>
    <div class='footer-note'>Generated by Skilgen from live repository evidence, architecture synthesis, score history, diff state, analytics, and enterprise capability context.</div>
  </footer>
</main>
<script>{dashboard_script}</script>
</body>
</html>
""".strip()


def ensure_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return path
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
            "## Skill Telemetry Hook",
            "- When you actually open a repo skill file to use it during implementation, record that load with Skilgen analytics.",
            "- Built-in hook command:",
            "  - `python -m skilgen.cli.main analytics --project-root . --record-skill skills/backend/SKILL.md --context codex_live --agent codex`",
            "- Record the most specific child skill you actually used, not just the parent skill Skilgen recommended.",
            "- Use `codex_live`, `claude_code_live`, or another explicit runtime context so live metrics stay separate from planner warmups.",
            "- Optional session metadata:",
            "  - `python -m skilgen.cli.main analytics --project-root . --record-skill skills/backend/api/SKILL.md --context codex_live --agent codex --session-id task-123 --task \"implement billing retry\"`",
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


def write_project_docs(
    context: RequirementsContext,
    project_root: Path,
    *,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    written = []
    _emit_progress(progress_callback, "Assembling the evidence bundle that powers AGENTS.md, reports, and the dashboard.")
    bundle = _analysis_bundle(context, project_root)
    _emit_progress(progress_callback, "Rendering AGENTS.md with repo contract, startup guidance, and operating rules.")
    agents = render_agents_contract(context, project_root)
    _emit_progress(progress_callback, "Rendering ANALYSIS.md with the raw framework, evidence, and graph payloads.")
    analysis = render_analysis_report(context, project_root, bundle)
    _emit_progress(progress_callback, "Rendering ARCHITECTURE.md with domain boundaries, parser signals, and materialization decisions.")
    architecture = render_architecture_report(context, project_root, bundle)
    _emit_progress(progress_callback, "Rendering FEATURES.md so agents can see the current feature inventory.")
    features = render_feature_inventory(context)
    _emit_progress(progress_callback, "Rendering REPORT.md with human-readable summary, hotspots, and starting points.")
    report = render_project_report(context, project_root, bundle)
    _emit_progress(progress_callback, "Rendering TRACEABILITY.md so every generated artifact has evidence behind it.")
    traceability = render_traceability_report(context, project_root, bundle)
    _emit_progress(progress_callback, "Writing AGENTS.md, ANALYSIS.md, ARCHITECTURE.md, FEATURES.md, REPORT.md, and TRACEABILITY.md to disk.")
    written.append(ensure_file(project_root / "AGENTS.md", agents))
    written.append(ensure_file(project_root / "ANALYSIS.md", analysis))
    written.append(ensure_file(project_root / "ARCHITECTURE.md", architecture))
    written.append(ensure_file(project_root / "FEATURES.md", features))
    written.append(ensure_file(project_root / "REPORT.md", report))
    written.append(ensure_file(project_root / "TRACEABILITY.md", traceability))
    config_path = project_root / "skilgen.yml"
    if not config_path.exists():
        written.append(ensure_file(config_path, render_default_config()))
    return written


def write_dashboard_doc(
    context: RequirementsContext,
    project_root: Path,
    *,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    from skilgen.deep_agents_runtime import native_dashboard_payload_with_progress

    _emit_progress(progress_callback, "Building skilgen-dashboard.html from the fully materialized repo state.")
    dashboard_html = str(
        native_dashboard_payload_with_progress(
            project_root,
            context.requirements_path if context.requirements_path.exists() else None,
            progress_callback=progress_callback,
        )["html"]
    )
    _emit_progress(progress_callback, "Writing the final skilgen-dashboard.html snapshot to disk.")
    return ensure_file(project_root / "skilgen-dashboard.html", dashboard_html)
