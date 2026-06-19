from __future__ import annotations

import json
import hashlib
from pathlib import Path

from skilgen.agents.codebase_signals import is_ignored_path_parts, is_internal_skillayer_monorepo
from skilgen.core.document_ingestion import extract_document_text
from skilgen.core.models import ProjectIntent, RequirementsContext


def extract_text(path: Path) -> str:
    return extract_document_text(path)


def normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def detect_domains(lines: list[str]) -> dict[str, bool]:
    text = "\n".join(lines).lower()
    return {
        "requirements": True,
        "backend": any(
            word in text for word in ["backend", "api endpoint", "fastapi", "django", "express", "service", "endpoint"]
        ),
        "frontend": any(
            word in text for word in ["frontend", "ui route", "next.js", "react", "component", "route"]
        ),
    }


def summarize_requirements(lines: list[str], limit: int = 12) -> list[str]:
    interesting: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(
            keyword in lower
            for keyword in [
                "product vision",
                "requirements",
                "phase",
                "endpoint",
                "feature",
                "skill",
                "frontend",
                "backend",
                "agent",
                "manifest",
            ]
        ):
            interesting.append(line)
        if len(interesting) == limit:
            break
    return interesting


def extract_project_intent(lines: list[str]) -> ProjectIntent:
    features: list[str] = []
    domain_concepts: list[str] = []
    entities: list[str] = []
    endpoints: list[str] = []
    ui_flows: list[str] = []

    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in ["feature", "phase", "skill generation", "auto-update", "versioning"]):
            features.append(line)
        if any(keyword in lower for keyword in ["domain", "architecture", "frontend", "backend", "agent", "skilltree"]):
            domain_concepts.append(line)
        if any(keyword in lower for keyword in ["entity", "service", "component", "skill", "codebasecontext", "changeevent"]):
            entities.append(line)
        if any(keyword in lower for keyword in ["endpoint", "api", "route", "controller"]):
            endpoints.append(line)
        if any(keyword in lower for keyword in ["flow", "dashboard", "ui route", "component", "quick start"]):
            ui_flows.append(line)

    return ProjectIntent(
        features=features[:12],
        domain_concepts=domain_concepts[:12],
        entities=entities[:12],
        endpoints=endpoints[:12],
        ui_flows=ui_flows[:12],
    )


def load_requirements(path: Path) -> RequirementsContext:
    text = extract_text(path)
    lines = normalize_lines(text)
    return RequirementsContext(
        requirements_path=path.resolve(),
        raw_text=text,
        lines=lines,
        domains=detect_domains(lines),
        source_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        summary=summarize_requirements(lines),
    )


def synthesize_requirements_context(project_root: Path) -> RequirementsContext:
    root = project_root.resolve()
    internal_monorepo = is_internal_skillayer_monorepo(root)
    file_tree = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and ".git/" not in path.as_posix()
        and not path.relative_to(root).as_posix().startswith(("skills/", ".skilgen/"))
        and not is_ignored_path_parts(path.relative_to(root).parts, internal_monorepo=internal_monorepo)
        and path.name
        not in {
            "AGENTS.md",
            "ANALYSIS.md",
            "ARCHITECTURE.md",
            "FEATURES.md",
            "REPORT.md",
            "TRACEABILITY.md",
            "skilgen-dashboard.html",
            "skilgen.yml",
        }
    )
    backend_detected = any(
        marker in path.lower()
        for path in file_tree
        for marker in ["api/", "server/", "services/", "route", "controller", "handler"]
    )
    frontend_detected = any(
        marker in path.lower()
        for path in file_tree
        for marker in ["src/", "app/", "frontend/", "components/", "pages/", ".tsx", ".jsx", ".vue", ".svelte"]
    )
    summary = ["Codebase-only mode: no requirements file supplied."]
    if backend_detected:
        summary.append("Detected backend-oriented structure from routes, services, or server files.")
    if frontend_detected:
        summary.append("Detected frontend-oriented structure from routes, pages, or component files.")
    if file_tree:
        summary.append(f"Scanned {len(file_tree)} files from the project root.")
        summary.extend(f"Observed: {path}" for path in file_tree[:6])
    raw_text = "\n".join(summary)
    return RequirementsContext(
        requirements_path=root / "CODEBASE_ONLY",
        raw_text=raw_text,
        lines=summary,
        domains={
            "requirements": False,
            "backend": backend_detected,
            "frontend": frontend_detected,
        },
        source_hash=hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
        summary=summary[:12],
    )


def _remembered_requirements_path(project_root: Path) -> Path | None:
    root = project_root.resolve()
    run_memory_path = root / ".skilgen" / "memory" / "current_run.json"
    if run_memory_path.exists():
        try:
            payload = json.loads(run_memory_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        remembered = payload.get("requirements_path")
        if isinstance(remembered, str) and remembered.strip():
            candidate = Path(remembered).resolve()
            if candidate.exists():
                return candidate

    autoupdate_path = root / ".skilgen" / "state" / "autoupdate-requirements.txt"
    if autoupdate_path.exists():
        remembered = autoupdate_path.read_text(encoding="utf-8").strip()
        if remembered:
            candidate = Path(remembered).resolve()
            if candidate.exists():
                return candidate

    return None


def load_project_context(project_root: Path, requirements_path: Path | None = None) -> RequirementsContext:
    if requirements_path is not None:
        return load_requirements(requirements_path.resolve())
    remembered = _remembered_requirements_path(project_root)
    if remembered is not None:
        return load_requirements(remembered)
    return synthesize_requirements_context(project_root.resolve())
