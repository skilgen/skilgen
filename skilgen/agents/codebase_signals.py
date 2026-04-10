from __future__ import annotations

import ast
import re
from pathlib import Path

from skilgen.core.models import CodebaseSignals


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".cbl",
    ".cob",
    ".cpy",
    ".java",
    ".go",
    ".rs",
}
UI_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
COBOL_EXTENSIONS = {".cbl", ".cob"}
COPYBOOK_EXTENSIONS = {".cpy"}
LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".vue": "vue",
    ".svelte": "svelte",
    ".cbl": "cobol",
    ".cob": "cobol",
    ".cpy": "copybook",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
}
IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea",
    ".pytest_cache",
}


def _relative_parts(path: Path, project_root: Path) -> set[str]:
    return {part.lower() for part in path.relative_to(project_root).parts}


def _iter_code_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        if _relative_parts(path, project_root) & IGNORED_PARTS:
            continue
        files.append(path)
    return sorted(files)


def _is_backend_route(relative_path: str, parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    route_markers = {"api", "routes", "route", "controllers", "controller", "handlers", "handler", "cics", "transactions", "transaction"}
    lowered_name = name.lower()
    return (
        bool(lowered_parts & route_markers)
        or relative_path.startswith("app/api/")
        or "router" in lowered_name
        or lowered_name.startswith(("txn", "trn"))
    )


def _is_frontend_route(relative_path: str, parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    ui_route_markers = {"pages", "page", "routes", "route", "screens", "screen"}
    return (
        bool(lowered_parts & ui_route_markers)
        or relative_path.startswith("app/")
        or name.lower() in {"page.tsx", "page.jsx", "page.js", "page.ts"}
    )


def _is_component(parts: tuple[str, ...], stem: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    return "components" in lowered_parts or (stem[:1].isupper() and len(stem) > 1)


def _is_service(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    service_markers = {"services", "service", "usecases", "usecase", "domain", "programs", "program", "business"}
    return bool(lowered_parts & service_markers) or "service" in name.lower()


def _is_test(relative_path: str, stem: str) -> bool:
    lowered = relative_path.lower()
    return (
        "/tests/" in lowered
        or lowered.startswith("tests/")
        or stem.endswith(".test")
        or stem.endswith(".spec")
        or lowered.endswith("_test.py")
    )


def _is_data_model(parts: tuple[str, ...], stem: str, name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    model_markers = {"models", "model", "schemas", "schema", "entities", "entity", "dto", "dtos", "copybook", "copybooks", "record", "records"}
    lowered_name = name.lower()
    return bool(lowered_parts & model_markers) or lowered_name.endswith(("model.py", "schema.py", "entity.py", ".cpy"))


def _is_persistence_layer(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    persistence_markers = {
        "db",
        "database",
        "persistence",
        "repository",
        "repositories",
        "migrations",
        "orm",
        "prisma",
        "vsam",
        "db2",
        "sql",
        "copybooks",
    }
    lowered_name = name.lower()
    return bool(lowered_parts & persistence_markers) or any(
        marker in lowered_name for marker in ("repository", "migration", "database", "db", "prisma", "vsam", "db2", "sql")
    )


def _is_background_job(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    job_markers = {"jobs", "job", "workers", "worker", "queues", "queue", "tasks", "task", "cron", "batch", "jcl"}
    lowered_name = name.lower()
    return bool(lowered_parts & job_markers) or any(
        marker in lowered_name for marker in ("job", "worker", "task", "queue", "cron", "batch", "jcl")
    )


def _is_auth_file(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    auth_markers = {"auth", "authentication", "authorization", "permissions", "security", "session"}
    lowered_name = name.lower()
    return bool(lowered_parts & auth_markers) or any(
        marker in lowered_name for marker in ("auth", "permission", "security", "session")
    )


def _is_state_file(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    state_markers = {"state", "store", "stores", "redux", "zustand", "context", "contexts"}
    lowered_name = name.lower()
    return bool(lowered_parts & state_markers) or any(
        marker in lowered_name for marker in ("store", "state", "context", "reducer")
    )


def _is_design_system_file(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    design_markers = {"design-system", "design_system", "theme", "themes", "tokens", "storybook", "ui"}
    lowered_name = name.lower()
    return bool(lowered_parts & design_markers) or any(
        marker in lowered_name for marker in ("theme", "token", "storybook", "design", "ui-kit")
    )


def _is_copybook(path: Path, parts: tuple[str, ...]) -> bool:
    lowered_parts = {part.lower() for part in parts}
    return path.suffix.lower() in COPYBOOK_EXTENSIONS or bool(lowered_parts & {"copybook", "copybooks", "copy"})


def _is_legacy_program(path: Path, parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    lowered_name = name.lower()
    return path.suffix.lower() in COBOL_EXTENSIONS or bool(
        lowered_parts & {"cobol", "cics", "batch", "program", "programs", "transactions", "bms"}
    ) or any(marker in lowered_name for marker in ("txn", "cics", "batch", "program"))


def _language_for_path(path: Path) -> str:
    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower(), path.suffix.lower().lstrip(".") or "text")


def _snippet_lines(text: str, *, limit: int = 12) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith(("*", "//", "/*", "#", "--")) and len(lines) > 2:
            continue
        lines.append(stripped[:180])
        if len(lines) >= limit:
            break
    return lines


def _python_structure(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return []
    lines: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            lines.append(f"class {node.name}")
        elif isinstance(node, ast.FunctionDef):
            lines.append(f"function {node.name}")
        elif isinstance(node, ast.AsyncFunctionDef):
            lines.append(f"async function {node.name}")
        elif isinstance(node, ast.Import):
            names = ", ".join(alias.name for alias in node.names[:4])
            lines.append(f"imports {names}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or "."
            names = ", ".join(alias.name for alias in node.names[:4])
            lines.append(f"from {module} import {names}")
        if len(lines) >= 10:
            break
    return lines


def _regex_structure(text: str, patterns: list[tuple[str, str]], *, limit: int = 10) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for label, pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            value = match.group(1).strip()
            if not value or value in seen:
                continue
            seen.add(value)
            lines.append(f"{label} {value}")
            if len(lines) >= limit:
                return lines
    return lines


def _language_structure(path: Path, text: str) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return _python_structure(path)
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}:
        return _regex_structure(
            text,
            [
                ("function", r"(?:export\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("class", r"class\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("component", r"(?:const|let|var)\s+([A-Z][A-Za-z0-9_]*)\s*=\s*\("),
                ("route", r"(?:app|router)\.(?:get|post|put|delete|patch)\(\s*[\"'`]([^\"'`]+)"),
            ],
        )
    if suffix == ".java":
        return _regex_structure(
            text,
            [
                ("class", r"class\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("interface", r"interface\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("method", r"(?:public|private|protected)\s+(?:static\s+)?[A-Za-z0-9_<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
            ],
        )
    if suffix == ".go":
        return _regex_structure(
            text,
            [
                ("package", r"package\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("type", r"type\s+([A-Za-z_][A-Za-z0-9_]*)\s+struct"),
                ("function", r"func\s+(?:\([^)]+\)\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\("),
            ],
        )
    if suffix == ".rs":
        return _regex_structure(
            text,
            [
                ("struct", r"struct\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("enum", r"enum\s+([A-Za-z_][A-Za-z0-9_]*)"),
                ("function", r"fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
                ("trait", r"trait\s+([A-Za-z_][A-Za-z0-9_]*)"),
            ],
        )
    if suffix in COBOL_EXTENSIONS:
        return _regex_structure(
            text,
            [
                ("program", r"PROGRAM-ID\.\s+([A-Za-z0-9_-]+)"),
                ("division", r"^\s*([A-Z-]+\s+DIVISION)\."),
                ("section", r"^\s*([A-Z0-9-]+\s+SECTION)\."),
                ("copy", r"^\s*COPY\s+([A-Z0-9-]+)"),
            ],
        )
    if suffix in COPYBOOK_EXTENSIONS:
        return _regex_structure(text, [("record", r"^\s*\d+\s+([A-Z0-9-]+)\.")])
    return []


def collect_code_evidence(project_root: Path, *, limit: int = 12) -> list[dict[str, object]]:
    root = project_root.resolve()
    signals = analyze_codebase(root)
    prioritized_paths = [
        *signals.backend_routes,
        *signals.services,
        *signals.data_models,
        *signals.persistence_layers,
        *signals.auth_files,
        *signals.background_jobs,
        *signals.copybooks,
        *signals.legacy_programs,
        *signals.frontend_routes,
        *signals.components,
    ]
    seen: set[str] = set()
    evidence_paths: list[Path] = []
    for relative in prioritized_paths:
        if relative in seen:
            continue
        candidate = root / relative
        if candidate.exists() and candidate.is_file():
            evidence_paths.append(candidate)
            seen.add(relative)
        if len(evidence_paths) >= limit:
            break
    if len(evidence_paths) < limit:
        for path in _iter_code_files(root):
            relative = path.relative_to(root).as_posix()
            if relative in seen:
                continue
            evidence_paths.append(path)
            seen.add(relative)
            if len(evidence_paths) >= limit:
                break

    evidence: list[dict[str, object]] = []
    for path in evidence_paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        snippet = _snippet_lines(text)
        if not snippet:
            continue
        relative = path.relative_to(root).as_posix()
        tags = []
        for name, bucket in [
            ("backend_routes", signals.backend_routes),
            ("frontend_routes", signals.frontend_routes),
            ("components", signals.components),
            ("services", signals.services),
            ("tests", signals.tests),
            ("data_models", signals.data_models),
            ("persistence_layers", signals.persistence_layers),
            ("background_jobs", signals.background_jobs),
            ("auth_files", signals.auth_files),
            ("state_files", signals.state_files),
            ("design_system_files", signals.design_system_files),
            ("legacy_programs", signals.legacy_programs),
            ("copybooks", signals.copybooks),
        ]:
            if relative in bucket:
                tags.append(name)
        evidence.append(
            {
                "path": relative,
                "language": _language_for_path(path),
                "tags": tags,
                "snippet": snippet,
            }
        )
    return evidence


def collect_structural_evidence(project_root: Path, *, limit: int = 16) -> list[dict[str, object]]:
    root = project_root.resolve()
    evidence: list[dict[str, object]] = []
    for path in _iter_code_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        structure = _language_structure(path, text)
        if not structure:
            continue
        relative = path.relative_to(root).as_posix()
        evidence.append(
            {
                "path": relative,
                "language": _language_for_path(path),
                "kind": "structure",
                "tags": ["structural-evidence"],
                "snippet": structure[:10],
            }
        )
        if len(evidence) >= limit:
            break
    return evidence


def analyze_codebase(project_root: Path) -> CodebaseSignals:
    root = project_root.resolve()
    backend_routes: list[str] = []
    frontend_routes: list[str] = []
    components: list[str] = []
    services: list[str] = []
    tests: list[str] = []
    data_models: list[str] = []
    persistence_layers: list[str] = []
    background_jobs: list[str] = []
    auth_files: list[str] = []
    state_files: list[str] = []
    design_system_files: list[str] = []
    legacy_programs: list[str] = []
    copybooks: list[str] = []
    language_inventory: dict[str, int] = {}

    for path in _iter_code_files(root):
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        parts = tuple(relative_path.parts)
        name = path.name
        stem = path.stem

        language = _language_for_path(path)
        language_inventory[language] = language_inventory.get(language, 0) + 1

        if _is_test(relative, stem):
            tests.append(relative)
        if path.suffix.lower() in UI_EXTENSIONS and _is_frontend_route(relative, parts, name):
            frontend_routes.append(relative)
        if _is_backend_route(relative, parts, name):
            backend_routes.append(relative)
        if path.suffix.lower() in UI_EXTENSIONS and _is_component(parts, stem):
            components.append(relative)
        if _is_service(parts, name) or _is_legacy_program(path, parts, name):
            services.append(relative)
        if _is_data_model(parts, stem, name) or _is_copybook(path, parts):
            data_models.append(relative)
        if _is_persistence_layer(parts, name):
            persistence_layers.append(relative)
        if _is_background_job(parts, name):
            background_jobs.append(relative)
        if _is_auth_file(parts, name):
            auth_files.append(relative)
        if path.suffix.lower() in UI_EXTENSIONS and _is_state_file(parts, name):
            state_files.append(relative)
        if path.suffix.lower() in UI_EXTENSIONS and _is_design_system_file(parts, name):
            design_system_files.append(relative)
        if _is_legacy_program(path, parts, name):
            legacy_programs.append(relative)
        if _is_copybook(path, parts):
            copybooks.append(relative)

    return CodebaseSignals(
        backend_routes=sorted(set(backend_routes)),
        frontend_routes=sorted(set(frontend_routes)),
        components=sorted(set(components)),
        services=sorted(set(services)),
        tests=sorted(set(tests)),
        data_models=sorted(set(data_models)),
        persistence_layers=sorted(set(persistence_layers)),
        background_jobs=sorted(set(background_jobs)),
        auth_files=sorted(set(auth_files)),
        state_files=sorted(set(state_files)),
        design_system_files=sorted(set(design_system_files)),
        legacy_programs=sorted(set(legacy_programs)),
        copybooks=sorted(set(copybooks)),
        language_inventory=dict(sorted(language_inventory.items())),
    )
