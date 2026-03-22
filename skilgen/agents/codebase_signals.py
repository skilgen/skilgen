from __future__ import annotations

from pathlib import Path

from skilgen.core.models import CodebaseSignals


CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
UI_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
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
    ".skilgen",
}


def _iter_code_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        relative_parts = set(path.relative_to(project_root).parts)
        if relative_parts & IGNORED_PARTS:
            continue
        files.append(path)
    return sorted(files)


def _is_backend_route(relative_path: str, parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    route_markers = {"api", "routes", "route", "controllers", "controller", "handlers", "handler"}
    return bool(lowered_parts & route_markers) or relative_path.startswith("app/api/") or "router" in name.lower()


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
    service_markers = {"services", "service", "usecases", "usecase", "domain"}
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
    model_markers = {"models", "model", "schemas", "schema", "entities", "entity", "dto", "dtos"}
    lowered_name = name.lower()
    return bool(lowered_parts & model_markers) or lowered_name.endswith(("model.py", "schema.py", "entity.py"))


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
    }
    lowered_name = name.lower()
    return bool(lowered_parts & persistence_markers) or any(
        marker in lowered_name for marker in ("repository", "migration", "database", "db", "prisma")
    )


def _is_background_job(parts: tuple[str, ...], name: str) -> bool:
    lowered_parts = {part.lower() for part in parts}
    job_markers = {"jobs", "job", "workers", "worker", "queues", "queue", "tasks", "task", "cron"}
    lowered_name = name.lower()
    return bool(lowered_parts & job_markers) or any(
        marker in lowered_name for marker in ("job", "worker", "task", "queue", "cron")
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

    for path in _iter_code_files(root):
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        parts = tuple(relative_path.parts)
        name = path.name
        stem = path.stem

        if _is_test(relative, stem):
            tests.append(relative)
        if path.suffix.lower() in UI_EXTENSIONS and _is_frontend_route(relative, parts, name):
            frontend_routes.append(relative)
        if _is_backend_route(relative, parts, name):
            backend_routes.append(relative)
        if path.suffix.lower() in UI_EXTENSIONS and _is_component(parts, stem):
            components.append(relative)
        if _is_service(parts, name):
            services.append(relative)
        if _is_data_model(parts, stem, name):
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
    )
