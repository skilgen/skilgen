from __future__ import annotations

import json
from pathlib import Path
import re
try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from skilgen.agents.relationship_mapper import build_import_graph
from skilgen.agents.workspace_graph import build_workspace_graph
from skilgen.core.models import DependencyRiskEdge, DependencyRiskGraph, DependencyRiskNode


_DEPRECATED_PACKAGES = {
    "request": "superseded by requests",
    "left-pad": "historically deprecated package",
    "tslint": "deprecated in favor of eslint",
    "node-sass": "deprecated in favor of sass",
}
_CONFIG_DIRS = {".git", ".skilgen", "skills", "node_modules", "__pycache__", ".venv", "venv"}
_UNPINNED_PATTERNS = (
    re.compile(r"^[A-Za-z0-9_.-]+$"),
    re.compile(r"^\^"),
    re.compile(r"^~"),
    re.compile(r"^\*"),
    re.compile(r"^>=?"),
)


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: set[tuple[str, ...]] = set()
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            if node in stack:
                start = stack.index(node)
                cycle = tuple(stack[start:] + [node])
                cycles.add(cycle)
            return
        visiting.add(node)
        stack.append(node)
        for target in graph.get(node, []):
            if target in graph:
                visit(target)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    normalized: list[list[str]] = []
    for cycle in sorted(cycles):
        if len(cycle) > 1:
            normalized.append(list(cycle))
    return normalized


def _external_dependency_signals(name: str, version: str | None) -> list[str]:
    signals: list[str] = []
    if name in _DEPRECATED_PACKAGES:
        signals.append(f"deprecated:{_DEPRECATED_PACKAGES[name]}")
    if version:
        cleaned = version.strip()
        if any(pattern.search(cleaned) for pattern in _UNPINNED_PATTERNS):
            signals.append("version:loosely-pinned")
        if any(marker in cleaned.lower() for marker in ("alpha", "beta", "rc")):
            signals.append("version:prerelease")
    else:
        signals.append("version:missing")
    return signals


def _load_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _package_json_deps(path: Path) -> list[tuple[str, str | None]]:
    payload = _load_json(path)
    dependencies: list[tuple[str, str | None]] = []
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        entries = payload.get(section, {})
        if isinstance(entries, dict):
            for name, version in entries.items():
                dependencies.append((str(name), str(version) if version is not None else None))
    return dependencies


def _requirements_deps(path: Path) -> list[tuple[str, str | None]]:
    dependencies: list[tuple[str, str | None]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return dependencies
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "--")):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*([<>=!~].+)?$", line)
        if match:
            dependencies.append((match.group(1), match.group(2).strip() if match.group(2) else None))
    return dependencies


def _pyproject_deps(path: Path) -> list[tuple[str, str | None]]:
    if tomllib is None:
        return []
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, tomllib.TOMLDecodeError):
        return []
    dependencies: list[tuple[str, str | None]] = []
    project = payload.get("project", {})
    if isinstance(project, dict):
        for entry in project.get("dependencies", []):
            if isinstance(entry, str):
                match = re.match(r"^([A-Za-z0-9_.-]+)\s*(.*)$", entry.strip())
                if match:
                    version = match.group(2).strip() or None
                    dependencies.append((match.group(1), version))
    poetry = payload.get("tool", {}).get("poetry", {}) if isinstance(payload.get("tool"), dict) else {}
    if isinstance(poetry, dict):
        poetry_deps = poetry.get("dependencies", {})
        if isinstance(poetry_deps, dict):
            for name, version in poetry_deps.items():
                if name == "python":
                    continue
                dependencies.append((str(name), str(version) if not isinstance(version, dict) else str(version.get("version"))))
    return dependencies


def _cargo_deps(path: Path) -> list[tuple[str, str | None]]:
    if tomllib is None:
        return []
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, tomllib.TOMLDecodeError):
        return []
    entries = payload.get("dependencies", {})
    if not isinstance(entries, dict):
        return []
    dependencies: list[tuple[str, str | None]] = []
    for name, version in entries.items():
        if isinstance(version, dict):
            dependencies.append((str(name), str(version.get("version")) if version.get("version") is not None else None))
        else:
            dependencies.append((str(name), str(version) if version is not None else None))
    return dependencies


def _go_mod_deps(path: Path) -> list[tuple[str, str | None]]:
    dependencies: list[tuple[str, str | None]] = []
    current_block = False
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line.startswith("require ("):
            current_block = True
            continue
        if current_block and line == ")":
            current_block = False
            continue
        if current_block and line:
            parts = line.split()
            if len(parts) >= 2:
                dependencies.append((parts[0], parts[1]))
        elif line.startswith("require "):
            parts = line.split()
            if len(parts) >= 3:
                dependencies.append((parts[1], parts[2]))
    return dependencies


def _manifest_dependencies(project_root: Path) -> tuple[dict[str, list[str]], list[DependencyRiskNode], list[DependencyRiskEdge]]:
    manifest_map: dict[str, list[str]] = {}
    nodes: list[DependencyRiskNode] = []
    edges: list[DependencyRiskEdge] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root).as_posix()
        if set(Path(relative).parts) & _CONFIG_DIRS:
            continue
        dependencies: list[tuple[str, str | None]] = []
        if path.name == "package.json":
            dependencies = _package_json_deps(path)
        elif path.name == "requirements.txt":
            dependencies = _requirements_deps(path)
        elif path.name == "pyproject.toml":
            dependencies = _pyproject_deps(path)
        elif path.name == "Cargo.toml":
            dependencies = _cargo_deps(path)
        elif path.name == "go.mod":
            dependencies = _go_mod_deps(path)
        if not dependencies:
            continue
        manifest_map[relative] = [name for name, _ in dependencies]
        source_id = f"manifest:{relative}"
        manifest_signals = []
        if len(dependencies) > 20:
            manifest_signals.append("fanout:large-manifest")
        nodes.append(
            DependencyRiskNode(
                id=source_id,
                kind="manifest",
                risk_score=min(1.0, round(len(manifest_signals) * 0.25, 2)),
                signals=manifest_signals,
                dependencies=[name for name, _ in dependencies],
            )
        )
        for name, version in dependencies:
            dependency_id = f"package:{name}"
            signals = _external_dependency_signals(name, version)
            edges.append(
                DependencyRiskEdge(
                    source=source_id,
                    target=dependency_id,
                    kind="external-package",
                    risk_signals=signals,
                )
            )
            nodes.append(
                DependencyRiskNode(
                    id=dependency_id,
                    kind="external-package",
                    risk_score=min(1.0, round(0.2 * len(signals), 2)),
                    signals=signals,
                    dependencies=[],
                )
            )
    deduped_nodes: dict[str, DependencyRiskNode] = {}
    for node in nodes:
        existing = deduped_nodes.get(node.id)
        if existing is None or node.risk_score > existing.risk_score:
            deduped_nodes[node.id] = node
    return manifest_map, list(deduped_nodes.values()), edges


def build_dependency_risk_graph(project_root: Path) -> DependencyRiskGraph:
    root = project_root.resolve()
    import_graph = build_import_graph(root)
    workspace_graph = build_workspace_graph(root)
    nodes: dict[str, DependencyRiskNode] = {}
    edges: list[DependencyRiskEdge] = []

    file_graph = {path: [target for target in targets if target in import_graph] for path, targets in import_graph.items()}
    file_cycles = _find_cycles(file_graph)
    fanout_sorted = sorted(import_graph.items(), key=lambda item: (-len(item[1]), item[0]))
    for path, targets in import_graph.items():
        signals: list[str] = []
        if len(targets) >= 8:
            signals.append("fanout:high")
        if any(path in cycle for cycle in file_cycles):
            signals.append("cycle:internal")
        nodes[path] = DependencyRiskNode(
            id=path,
            kind="source-file",
            risk_score=min(1.0, round(0.15 * len(signals), 2)),
            signals=signals,
            dependencies=targets[:16],
        )
        for target in targets[:24]:
            if "/" in target and "." in Path(target).name:
                edges.append(
                    DependencyRiskEdge(
                        source=path,
                        target=target,
                        kind="repo-import",
                        risk_signals=["cycle:internal"] if any(path in cycle and target in cycle for cycle in file_cycles) else [],
                    )
                )

    workspace_edges: dict[str, list[str]] = {}
    package_names = {package.id: package.root_path for package in workspace_graph.packages}
    for package in workspace_graph.packages:
        workspace_edges[package.id] = []
        nodes[f"workspace:{package.id}"] = DependencyRiskNode(
            id=f"workspace:{package.id}",
            kind="workspace-package",
            risk_score=0.0,
            signals=[],
            dependencies=[],
        )
    for edge in workspace_graph.dependencies:
        workspace_edges.setdefault(edge.source, []).append(edge.target)
        edges.append(
            DependencyRiskEdge(
                source=f"workspace:{edge.source}",
                target=f"workspace:{edge.target}",
                kind="workspace-package",
                risk_signals=[],
            )
        )
    package_cycles = _find_cycles(workspace_edges)
    for package_id, dependencies in workspace_edges.items():
        node_id = f"workspace:{package_id}"
        signals: list[str] = []
        if len(dependencies) >= 4:
            signals.append("fanout:workspace-high")
        if any(package_id in cycle for cycle in package_cycles):
            signals.append("cycle:workspace")
        nodes[node_id] = DependencyRiskNode(
            id=node_id,
            kind="workspace-package",
            risk_score=min(1.0, round(0.25 * len(signals), 2)),
            signals=signals,
            dependencies=[package_names.get(dep, dep) for dep in dependencies[:12]],
        )

    _manifest_map, manifest_nodes, manifest_edges = _manifest_dependencies(root)
    for node in manifest_nodes:
        existing = nodes.get(node.id)
        if existing is None or node.risk_score > existing.risk_score:
            nodes[node.id] = node
    edges.extend(manifest_edges)

    cycles = file_cycles[:12] + [[package_names.get(item, item) for item in cycle] for cycle in package_cycles[:12]]
    recommendations: list[str] = []
    if cycles:
        recommendations.append("Break internal dependency cycles before materializing fine-grained skills around those files or packages.")
    if any("fanout:high" in node.signals for node in nodes.values()):
        hotspots = [node.id for node in nodes.values() if "fanout:high" in node.signals][:5]
        recommendations.append(f"High fan-out dependency hotspots surfaced in: {', '.join(hotspots)}.")
    deprecated = [node.id for node in nodes.values() if any(signal.startswith("deprecated:") for signal in node.signals)]
    if deprecated:
        recommendations.append(f"Deprecated external packages were detected: {', '.join(deprecated[:6])}.")
    loosely_pinned = [edge.target for edge in edges if "version:loosely-pinned" in edge.risk_signals]
    if loosely_pinned:
        recommendations.append(f"Loosely pinned external dependencies increase drift risk: {', '.join(sorted(dict.fromkeys(loosely_pinned))[:6])}.")

    ordered_nodes = sorted(nodes.values(), key=lambda node: (-node.risk_score, node.id))
    ordered_edges = sorted(edges, key=lambda edge: (edge.source, edge.target, edge.kind))
    return DependencyRiskGraph(
        nodes=ordered_nodes,
        edges=ordered_edges,
        cycles=cycles,
        recommendations=recommendations,
    )
