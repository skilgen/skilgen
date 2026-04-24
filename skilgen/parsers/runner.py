"""Execute non-code source parsers with config-aware detection and explicit path support."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from skilgen.core.models import SourceConfigValue
from skilgen.parsers.auto_detect import detect_source_paths, normalize_source_name
from skilgen.parsers.sources import (
    SOURCE_TYPES,
    SkillSource,
    SourceRunResult,
    _call_parser,
    normalize_skill_sources,
    write_skill_sources,
)


def run_source_parsers(
    project_root: Path,
    source_names: Iterable[str] | None = None,
    *,
    explicit_paths: dict[str, list[str | Path]] | None = None,
    persist: bool = True,
    source_config: dict[str, SourceConfigValue] | None = None,
) -> SourceRunResult:
    """Run selected source parsers, optionally using explicit source paths."""
    root = project_root.resolve()
    detected = detect_source_paths(root, source_names, raw_sources=source_config)
    if explicit_paths:
        for source_type, paths in explicit_paths.items():
            canonical = normalize_source_name(source_type)
            if canonical not in SOURCE_TYPES:
                continue
            detected[canonical] = _resolved_paths(root, paths)

    selected = _selected_sources(source_names, detected)
    analysed: dict[str, list[str]] = {}
    failures: dict[str, str] = {}
    skill_sources: list[SkillSource] = []
    for source_type in selected:
        paths = detected.get(source_type, [])
        if not paths:
            failures[source_type] = f"No configured or detected paths for {source_type}."
            continue
        for source_path in paths:
            try:
                raw = _call_parser(source_type, source_path)
                sources = normalize_skill_sources(raw, source_type)
                if not sources:
                    failures[source_type] = f"Parser did not return any normalized skill sources for {source_path}."
                    continue
                skill_sources.extend(sources)
                analysed.setdefault(source_type, []).extend(source.domain for source in sources)
            except Exception as exc:
                failures[source_type] = f"Failed to parse {source_type} source {source_path}: {exc}"
    written = write_skill_sources(root, skill_sources) if persist else []
    return SourceRunResult(analysed=analysed, skill_sources=skill_sources, written_files=written, failures=failures)


def _selected_sources(source_names: Iterable[str] | None, detected: dict[str, list[Path]]) -> list[str]:
    requested = [normalize_source_name(str(source)) for source in (source_names or []) if str(source).strip()]
    if not requested or "all" in requested:
        return sorted(detected)
    return [source for source in requested if source in SOURCE_TYPES]


def _resolved_paths(root: Path, paths: list[str | Path]) -> list[Path]:
    resolved: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        resolved_path = path if path.is_absolute() else (root / path)
        resolved.append(resolved_path.resolve())
    return sorted(dict.fromkeys(resolved))
