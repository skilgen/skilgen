from __future__ import annotations

import hashlib
import html
import re
import zipfile
from pathlib import Path

from skilgen.core.models import ProjectIntent, RequirementsContext


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<[^>]+>", "", xml)
        return html.unescape(xml)
    return path.read_text(encoding="utf-8")


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
    file_tree = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and ".git/" not in path.as_posix()
        and not path.relative_to(root).as_posix().startswith(("skills/", ".skilgen/"))
        and path.name not in {"AGENTS.md", "ANALYSIS.md", "FEATURES.md", "REPORT.md", "TRACEABILITY.md"}
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


def load_project_context(project_root: Path, requirements_path: Path | None = None) -> RequirementsContext:
    if requirements_path is not None:
        return load_requirements(requirements_path.resolve())
    return synthesize_requirements_context(project_root.resolve())
