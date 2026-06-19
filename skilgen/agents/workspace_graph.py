from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency is declared in pyproject
    yaml = None

from skilgen.core.models import WorkspaceDependency, WorkspaceGraph, WorkspacePackage


_IGNORED_DIRS = {
    ".git",
    ".skilgen",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "__pycache__",
    "vendor",
}
_WORKSPACE_PRIORITY = ("nx", "turbo", "pnpm", "bazel")


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _package_id(root_path: str) -> str:
    return root_path.replace("/", "-").replace("_", "-").strip("-") or "root"


def _safe_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_yaml(path: Path) -> dict[str, object]:
    text = _safe_text(path)
    if not text:
        return {}
    if yaml is not None:
        try:
            payload = yaml.safe_load(text)
        except yaml.YAMLError:
            payload = None
        if isinstance(payload, dict):
            return payload
    payload: dict[str, object] = {}
    current_key: str | None = None
    current_items: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and not line.startswith("- "):
            if current_key is not None:
                payload[current_key] = list(current_items)
            current_key = line[:-1].strip()
            current_items = []
            continue
        if line.startswith("- ") and current_key is not None:
            current_items.append(line[2:].strip().strip("'\""))
    if current_key is not None:
        payload[current_key] = list(current_items)
    return payload


def _safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _visible_directory(path: Path) -> bool:
    return path.is_dir() and not any(part in _IGNORED_DIRS or part.startswith(".") for part in path.parts)


def _package_roots_from_patterns(project_root: Path, patterns: list[str]) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            continue
        normalized = pattern.strip().rstrip("/")
        candidates = list(project_root.glob(normalized))
        if not candidates and not normalized.endswith("/**"):
            candidates = list(project_root.glob(f"{normalized}/**"))
        for candidate in sorted(candidates):
            if not _visible_directory(candidate):
                continue
            if not (candidate / "package.json").exists() and not (candidate / "project.json").exists():
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            roots.append(candidate)
    return roots


def _manifest_name(directory: Path, project_root: Path, project_payload: dict[str, object]) -> str:
    package_json = directory / "package.json"
    if package_json.exists():
        payload = _safe_json(package_json)
        name = str(payload.get("name", "")).strip()
        if name:
            return name
    name = str(project_payload.get("name", "")).strip()
    if name:
        return name
    return _relative(project_root, directory)


def _package_type(directory: Path, project_payload: dict[str, object]) -> str | None:
    project_type = str(project_payload.get("projectType", "")).strip().lower()
    if project_type:
        return project_type
    root_name = directory.name.lower()
    if root_name in {"app", "apps", "web", "site"} or "app" in directory.parts:
        return "app"
    if "service" in root_name or "services" in directory.parts:
        return "service"
    if root_name in {"lib", "libs", "packages"} or "libs" in directory.parts or "packages" in directory.parts:
        return "library"
    return None


def _package_manifest_paths(directory: Path, project_root: Path) -> list[str]:
    manifests = []
    for file_name in ("package.json", "project.json", "pyproject.toml", "BUILD", "BUILD.bazel"):
        path = directory / file_name
        if path.exists():
            manifests.append(_relative(project_root, path))
    return manifests


def _package_config_evidence(directory: Path, project_root: Path, extra: list[str] | None = None) -> list[str]:
    evidence = list(_package_manifest_paths(directory, project_root))
    if extra:
        evidence.extend(extra)
    return list(dict.fromkeys(item for item in evidence if item))


def _package_from_directory(
    project_root: Path,
    directory: Path,
    *,
    extra_evidence: list[str] | None = None,
) -> WorkspacePackage:
    project_payload = _safe_json(directory / "project.json")
    root_path = _relative(project_root, directory)
    return WorkspacePackage(
        id=_package_id(root_path),
        name=_manifest_name(directory, project_root, project_payload),
        root_path=root_path,
        package_type=_package_type(directory, project_payload),
        manifest_paths=_package_manifest_paths(directory, project_root),
        config_evidence=_package_config_evidence(directory, project_root, extra_evidence),
    )


def _internal_dependency_names(package_json: dict[str, object]) -> set[str]:
    names: set[str] = set()
    for field in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        payload = package_json.get(field, {})
        if isinstance(payload, dict):
            names.update(str(name).strip() for name in payload if str(name).strip())
    return names


def _entrypoints(packages: list[WorkspacePackage]) -> list[str]:
    entrypoints: list[str] = []
    for package in packages:
        package_type = (package.package_type or "").lower()
        if package_type in {"app", "application", "service"}:
            entrypoints.append(package.id)
            continue
        root_path = package.root_path.lower()
        if root_path.startswith(("apps/", "services/", "cmd/")):
            entrypoints.append(package.id)
    return list(dict.fromkeys(entrypoints))


def _package_edges_from_manifests(project_root: Path, packages: list[WorkspacePackage]) -> list[WorkspaceDependency]:
    name_to_id = {package.name: package.id for package in packages}
    root_to_id = {package.root_path: package.id for package in packages}
    edges: list[WorkspaceDependency] = []
    seen: set[tuple[str, str]] = set()
    for package in packages:
        package_json = _safe_json(project_root / package.root_path / "package.json")
        for dependency_name in sorted(_internal_dependency_names(package_json)):
            target = name_to_id.get(dependency_name)
            if target is None or target == package.id or (package.id, target) in seen:
                continue
            seen.add((package.id, target))
            edges.append(
                WorkspaceDependency(
                    source=package.id,
                    target=target,
                    evidence=[f"{package.root_path}/package.json:{dependency_name}"],
                )
            )
        project_json = _safe_json(project_root / package.root_path / "project.json")
        implicit = project_json.get("implicitDependencies", [])
        if isinstance(implicit, list):
            for dependency_name in sorted(str(item).strip() for item in implicit if str(item).strip()):
                target = name_to_id.get(dependency_name) or root_to_id.get(dependency_name)
                if target is None or target == package.id or (package.id, target) in seen:
                    continue
                seen.add((package.id, target))
                edges.append(
                    WorkspaceDependency(
                        source=package.id,
                        target=target,
                        evidence=[f"{package.root_path}/project.json:{dependency_name}"],
                    )
                )
    return edges


def _pnpm_workspace_graph(project_root: Path) -> WorkspaceGraph | None:
    config_path = project_root / "pnpm-workspace.yaml"
    if not config_path.exists():
        return None
    payload = _safe_yaml(config_path)
    patterns = payload.get("packages", [])
    if not isinstance(patterns, list):
        patterns = []
    package_dirs = _package_roots_from_patterns(project_root, [str(item) for item in patterns])
    packages = [_package_from_directory(project_root, directory, extra_evidence=[_relative(project_root, config_path)]) for directory in package_dirs]
    return WorkspaceGraph(
        tool="pnpm",
        packages=packages,
        dependencies=_package_edges_from_manifests(project_root, packages),
        entrypoints=_entrypoints(packages),
        confidence=0.93 if packages else 0.45,
        detection_evidence=[_relative(project_root, config_path)],
    )


def _root_workspace_patterns(project_root: Path) -> list[str]:
    package_json = _safe_json(project_root / "package.json")
    workspaces = package_json.get("workspaces", [])
    if isinstance(workspaces, list):
        return [str(item) for item in workspaces if str(item).strip()]
    if isinstance(workspaces, dict):
        packages = workspaces.get("packages", [])
        if isinstance(packages, list):
            return [str(item) for item in packages if str(item).strip()]
    pnpm_graph = _pnpm_workspace_graph(project_root)
    if pnpm_graph is not None and pnpm_graph.packages:
        return [package.root_path for package in pnpm_graph.packages]
    return ["apps/*", "packages/*"]


def _nx_workspace_graph(project_root: Path) -> WorkspaceGraph | None:
    config_path = project_root / "nx.json"
    if not config_path.exists():
        return None
    payload = _safe_json(config_path)
    layout = payload.get("workspaceLayout", {})
    apps_dir = "apps"
    libs_dir = "libs"
    if isinstance(layout, dict):
        apps_dir = str(layout.get("appsDir", apps_dir)).strip() or apps_dir
        libs_dir = str(layout.get("libsDir", libs_dir)).strip() or libs_dir
    package_dirs: dict[Path, list[str]] = {}
    for config in sorted(project_root.rglob("project.json")):
        if any(part in _IGNORED_DIRS for part in config.parts):
            continue
        package_dirs[config.parent] = [_relative(project_root, config), _relative(project_root, config_path)]
    if not package_dirs:
        patterns = [f"{apps_dir}/*", f"{libs_dir}/*", *_root_workspace_patterns(project_root)]
        for directory in _package_roots_from_patterns(project_root, patterns):
            package_dirs.setdefault(directory, [_relative(project_root, config_path)])
    packages = [_package_from_directory(project_root, directory, extra_evidence=evidence) for directory, evidence in sorted(package_dirs.items())]
    return WorkspaceGraph(
        tool="nx",
        packages=packages,
        dependencies=_package_edges_from_manifests(project_root, packages),
        entrypoints=_entrypoints(packages),
        confidence=0.96 if packages else 0.5,
        detection_evidence=[_relative(project_root, config_path)],
    )


def _turbo_workspace_graph(project_root: Path) -> WorkspaceGraph | None:
    config_path = project_root / "turbo.json"
    if not config_path.exists():
        return None
    patterns = _root_workspace_patterns(project_root)
    package_dirs = _package_roots_from_patterns(project_root, patterns)
    packages = [_package_from_directory(project_root, directory, extra_evidence=[_relative(project_root, config_path)]) for directory in package_dirs]
    return WorkspaceGraph(
        tool="turbo",
        packages=packages,
        dependencies=_package_edges_from_manifests(project_root, packages),
        entrypoints=_entrypoints(packages),
        confidence=0.92 if packages else 0.45,
        detection_evidence=[_relative(project_root, config_path)],
    )


def _bazel_package_dirs(project_root: Path) -> list[Path]:
    directories: list[Path] = []
    seen: set[Path] = set()
    for name in ("BUILD", "BUILD.bazel"):
        for build_file in sorted(project_root.rglob(name)):
            if any(part in _IGNORED_DIRS for part in build_file.parts):
                continue
            directory = build_file.parent
            if directory in seen:
                continue
            seen.add(directory)
            directories.append(directory)
    return directories


def _bazel_label_to_id(label: str, root_to_id: dict[str, str]) -> str | None:
    match = re.search(r"//([^:\"]+)", label)
    if not match:
        return None
    return root_to_id.get(match.group(1))


def _bazel_workspace_graph(project_root: Path) -> WorkspaceGraph | None:
    evidence_files = [name for name in ("WORKSPACE", "WORKSPACE.bazel", "MODULE.bazel") if (project_root / name).exists()]
    if not evidence_files:
        return None
    package_dirs = _bazel_package_dirs(project_root)
    packages = [_package_from_directory(project_root, directory, extra_evidence=evidence_files) for directory in package_dirs]
    root_to_id = {package.root_path: package.id for package in packages}
    edges: list[WorkspaceDependency] = []
    seen: set[tuple[str, str]] = set()
    for package in packages:
        directory = project_root / package.root_path
        for file_name in ("BUILD", "BUILD.bazel"):
            build_file = directory / file_name
            if not build_file.exists():
                continue
            text = _safe_text(build_file)
            for label in sorted(set(re.findall(r"//[^\"\s,\]]+", text))):
                target = _bazel_label_to_id(label, root_to_id)
                if target is None or target == package.id or (package.id, target) in seen:
                    continue
                seen.add((package.id, target))
                edges.append(
                    WorkspaceDependency(
                        source=package.id,
                        target=target,
                        evidence=[f"{package.root_path}/{file_name}:{label}"],
                    )
                )
    return WorkspaceGraph(
        tool="bazel",
        packages=packages,
        dependencies=edges,
        entrypoints=_entrypoints(packages),
        confidence=0.9 if packages else 0.4,
        detection_evidence=evidence_files,
    )


def _python_libs_fallback(project_root: Path) -> WorkspaceGraph:
    libs_root = project_root / "libs"
    if not libs_root.exists():
        return WorkspaceGraph(tool=None, packages=[], dependencies=[], entrypoints=[], confidence=0.0, detection_evidence=[])
    packages: list[WorkspacePackage] = []
    for directory in sorted(path for path in libs_root.iterdir() if path.is_dir()):
        has_python = any((candidate / "__init__.py").exists() for candidate in [directory, *[path for path in directory.iterdir() if path.is_dir()]])
        if not has_python:
            continue
        packages.append(
            WorkspacePackage(
                id=_package_id(_relative(project_root, directory)),
                name=directory.name.replace("_", "-"),
                root_path=_relative(project_root, directory),
                package_type="library",
                manifest_paths=[],
                config_evidence=["libs/"],
            )
        )
    confidence = 0.58 if len(packages) >= 2 else 0.0
    return WorkspaceGraph(
        tool=None,
        packages=packages if len(packages) >= 2 else [],
        dependencies=[],
        entrypoints=[],
        confidence=confidence,
        detection_evidence=["libs/"] if len(packages) >= 2 else [],
    )


def build_workspace_graph(project_root: Path) -> WorkspaceGraph:
    root = project_root.resolve()
    graphs = {
        "nx": _nx_workspace_graph(root),
        "turbo": _turbo_workspace_graph(root),
        "pnpm": _pnpm_workspace_graph(root),
        "bazel": _bazel_workspace_graph(root),
    }
    for tool in _WORKSPACE_PRIORITY:
        graph = graphs.get(tool)
        if graph is None:
            continue
        if graph.packages:
            return graph
        if graph.detection_evidence:
            return graph
    return _python_libs_fallback(root)
