from __future__ import annotations

from pathlib import Path

from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence
from skilgen.agents.relationship_mapper import build_import_graph
from skilgen.core.models import EvidenceGraph, EvidenceItem, RequirementsContext


_DOC_NAMES = {"README.md", "AGENTS.md", "FEATURES.md", "REPORT.md", "TRACEABILITY.md"}
_CONFIG_NAMES = {
    "pyproject.toml",
    "package.json",
    "skilgen.yml",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
}


def _text_preview(text: str, *, limit: int = 8) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        lines.append(stripped[:180])
        if len(lines) >= limit:
            break
    return lines


def _collect_document_items(project_root: Path, *, limit: int = 6) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root).as_posix()
        if ".git/" in relative or relative.startswith(("skills/", ".skilgen/")):
            continue
        if path.name not in _DOC_NAMES:
            continue
        try:
            snippet = _text_preview(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if not snippet:
            continue
        items.append(EvidenceItem(path=relative, kind="documentation", language=None, tags=["docs"], snippet=snippet))
        if len(items) >= limit:
            break
    return items


def _collect_config_items(project_root: Path, *, limit: int = 6) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root).as_posix()
        if ".git/" in relative or relative.startswith(("skills/", ".skilgen/")):
            continue
        if path.name not in _CONFIG_NAMES:
            continue
        try:
            snippet = _text_preview(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if not snippet:
            continue
        items.append(EvidenceItem(path=relative, kind="config", language=None, tags=["config"], snippet=snippet))
        if len(items) >= limit:
            break
    return items


def build_evidence_graph(project_root: Path, requirements: RequirementsContext) -> EvidenceGraph:
    root = project_root.resolve()
    signals = analyze_codebase(root)
    import_graph = build_import_graph(root)
    source_items = [
        EvidenceItem(
            path=str(item["path"]),
            kind="source",
            language=str(item["language"]) if item.get("language") is not None else None,
            tags=[str(tag) for tag in item.get("tags", [])],
            snippet=[str(line) for line in item.get("snippet", [])],
            related_imports=import_graph.get(str(item["path"]), []),
        )
        for item in collect_code_evidence(root)
    ]
    doc_items = _collect_document_items(root)
    config_items = _collect_config_items(root)
    requirements_item = EvidenceItem(
        path=requirements.requirements_path.name,
        kind="requirements",
        language=None,
        tags=["requirements"],
        snippet=requirements.summary[:8],
    )
    items = [requirements_item, *source_items, *doc_items, *config_items]
    dominant_languages = [name for name, _count in sorted(signals.language_inventory.items(), key=lambda item: (-item[1], item[0]))[:3]]
    recommendations = [
        "Use high-signal source evidence to define domain boundaries before generating skills.",
        "Prefer domains that are supported by both code evidence and requirements intent.",
    ]
    if signals.copybooks:
        recommendations.append("Preserve copybook-backed data contracts as first-class skill evidence for legacy domains.")
    if signals.language_inventory:
        recommendations.append(f"Optimize skill synthesis around the dominant languages: {', '.join(dominant_languages)}.")
    return EvidenceGraph(
        language_inventory=signals.language_inventory,
        dominant_languages=dominant_languages,
        import_graph=import_graph,
        items=items,
        recommendations=recommendations,
    )
