from __future__ import annotations

from pathlib import Path

from skilgen.agents.domain_graph_planner import _top_level_app_surfaces, build_domain_graph, detect_repo_archetype
from skilgen.agents.framework_fingerprint import fingerprint_project
from skilgen.agents.codebase_signals import analyze_codebase, is_ignored_path_parts, is_internal_skillayer_monorepo
from skilgen.agents.workspace_graph import build_workspace_graph
from skilgen.core.models import (
    CodebaseContext,
    DomainGraph,
    DomainGraphNode,
    DomainRecord,
    RequirementsContext,
    SkillTreeNode,
)


def _build_file_tree(project_root: Path) -> list[str]:
    internal_monorepo = is_internal_skillayer_monorepo(project_root)
    return sorted(
        path.relative_to(project_root).as_posix()
        for path in project_root.rglob("*")
        if path.is_file()
        and ".git/" not in path.as_posix()
        and not path.relative_to(project_root).as_posix().startswith(".skilgen/")
        and not is_ignored_path_parts(path.relative_to(project_root).parts, internal_monorepo=internal_monorepo)
    )


def _domain_records(domain_graph: DomainGraph) -> list[DomainRecord]:
    records: list[DomainRecord] = []
    for node in domain_graph.nodes:
        records.append(
            DomainRecord(
                name=node.name,
                confidence=node.confidence,
                key_files=node.key_files,
                key_patterns=node.key_patterns,
                sub_domains=node.child_domains,
            )
        )
    return records


def _skill_tree(domain_graph: DomainGraph) -> list[SkillTreeNode]:
    nodes_by_name: dict[str, DomainGraphNode] = {node.name: node for node in domain_graph.nodes}
    tree: list[SkillTreeNode] = []
    for node in domain_graph.nodes:
        if not node.skill_path:
            continue
        parent_skill = None
        if node.parent_domain:
            parent = nodes_by_name.get(node.parent_domain)
            if parent is not None:
                parent_skill = parent.skill_path
        child_skills = [
            child.skill_path
            for child_name in node.child_domains
            if (child := nodes_by_name.get(child_name)) is not None and child.skill_path is not None
        ]
        cross_references = [
            related.skill_path
            for related_name in node.related_domains
            if (related := nodes_by_name.get(related_name)) is not None and related.skill_path is not None
        ]
        tree.append(
            SkillTreeNode(
                path=node.skill_path,
                domain=node.name,
                parent_skill=parent_skill,
                child_skills=child_skills,
                cross_references=cross_references,
            )
        )
    return tree


def _dependency_map(domain_graph: DomainGraph) -> dict[str, list[str]]:
    dependency_map: dict[str, list[str]] = {}
    for node in domain_graph.nodes:
        deps = list(dict.fromkeys([*node.child_domains, *node.related_domains]))
        if deps:
            dependency_map[node.name] = deps
    return dependency_map


def build_codebase_context(project_root: Path, requirements: RequirementsContext) -> CodebaseContext:
    root = project_root.resolve()
    signals = analyze_codebase(root)
    workspace_graph = build_workspace_graph(root)
    package_root = None
    if is_internal_skillayer_monorepo(root) and (root / "skilgen" / "__init__.py").exists():
        package_root = root / "skilgen"
    else:
        for candidate in sorted(root.iterdir()):
            if candidate.is_dir() and (candidate / "__init__.py").exists() and candidate.name not in {"tests", "docs", "scripts", "skills"}:
                package_root = candidate
                break
    package_top_level_files = sorted(
        path.relative_to(root).as_posix()
        for path in package_root.glob("*.py")
        if package_root is not None and path.is_file()
    ) if package_root is not None else []
    app_surfaces = _top_level_app_surfaces(root)
    repo_archetype = detect_repo_archetype(
        root,
        signals,
        package_root=package_root,
        package_top_level_files=package_top_level_files,
        workspace_graph=workspace_graph,
        app_surfaces=app_surfaces,
    )
    domain_graph = build_domain_graph(root, requirements)
    return CodebaseContext(
        project_root=root,
        file_tree=_build_file_tree(root),
        domain_graph=domain_graph,
        detected_domains=_domain_records(domain_graph),
        dependency_map=_dependency_map(domain_graph),
        framework_fingerprint=fingerprint_project(root),
        skill_tree=_skill_tree(domain_graph),
        workspace_graph=workspace_graph,
        repo_archetype=repo_archetype,
    )
