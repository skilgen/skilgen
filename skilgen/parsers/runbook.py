"""Parse Markdown runbooks and operational playbooks into process sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


RUNBOOK_DIRECTORY_HINTS = {
    "runbooks",
    "playbooks",
    "docs",
    "operations",
    "incident-response",
    "on-call",
}
STEP_SECTION_RE = re.compile(r"^(steps?|procedure|process|checklist|how\s+to|instructions?)\b", re.IGNORECASE)
ANTI_SECTION_RE = re.compile(
    r"^(do\s+not|never|avoid|warnings?|common\s+mistakes?)\b",
    re.IGNORECASE,
)
CHECK_SECTION_RE = re.compile(
    r"^(verification|validation|confirm|health\s+checks?)\b",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(?:\[[ xX]\]\s*)?(.+?)\s*$")
URL_RE = re.compile(r"https?://[^\s)<>\]]+")
CONFIG_RE = re.compile(r"^\s*(?:[A-Z][A-Z0-9_]{2,}|[A-Za-z0-9_.-]+)\s*(?::|=)\s*\S+")


class ProcessParserError(ValueError):
    """Raised when a process source cannot be parsed into useful guidance."""


@dataclass(frozen=True)
class ProcessSource:
    """Normalized process guidance extracted from a runbook/wiki source."""

    source_path: str
    source_type: str
    title: str
    description: str
    steps: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    check_paths: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    groups: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


def parse_runbook_file(path: str | Path) -> ProcessSource:
    """Parse one Markdown runbook file."""

    resolved = Path(path).resolve()
    if not resolved.exists():
        raise ProcessParserError(f"Runbook source does not exist: {resolved}")
    if not resolved.is_file():
        raise ProcessParserError(f"Runbook source is not a file: {resolved}")
    if resolved.suffix.lower() not in {".md", ".markdown", ".txt"}:
        raise ProcessParserError(f"Runbook source must be Markdown/text: {resolved}")
    return _parse_markdown_document(resolved, source_type="runbook")


def parse_runbook_source(path: str | Path) -> list[ProcessSource]:
    """Parse one runbook file or a directory of Markdown runbooks."""

    resolved = Path(path).resolve()
    if not resolved.exists():
        raise ProcessParserError(f"Runbook source does not exist: {resolved}")
    if resolved.is_file():
        return [parse_runbook_file(resolved)]
    if not resolved.is_dir():
        raise ProcessParserError(f"Runbook source is neither a file nor directory: {resolved}")

    files = [
        candidate
        for candidate in sorted(resolved.rglob("*"))
        if candidate.is_file()
        and candidate.suffix.lower() in {".md", ".markdown", ".txt"}
        and _looks_like_runbook_path(candidate)
    ]
    if not files:
        raise ProcessParserError(f"No Markdown runbooks found under: {resolved}")
    return [parse_runbook_file(candidate) for candidate in files]


def parse_runbook_dir(path: str | Path) -> list[ProcessSource]:
    """Backward-compatible alias for runbook directory parsing."""
    return parse_runbook_source(path)


def _parse_markdown_document(path: Path, *, source_type: str, labels: list[str] | None = None) -> ProcessSource:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return _parse_markdown_text(raw, path, source_type=source_type, labels=labels)


def _parse_markdown_text(text: str, path: Path, *, source_type: str, labels: list[str] | None = None) -> ProcessSource:
    raw = text
    if not raw.strip():
        raise ProcessParserError(f"{source_type.title()} source is empty: {path}")

    body, metadata = _strip_frontmatter(raw, path)
    body_without_code, code_blocks = _extract_code_blocks(body, path)
    if not body_without_code.strip() and not code_blocks:
        raise ProcessParserError(f"{source_type.title()} source has no parseable content: {path}")

    lines = body_without_code.splitlines()
    title = _extract_title(lines) or _title_from_filename(path)
    description = _extract_description(lines, title)
    sections = _section_map(lines)
    steps = _extract_steps(sections)
    patterns = _extract_patterns(sections)
    anti_patterns = _extract_anti_patterns(sections, lines)
    check_paths = _extract_check_paths(sections)
    evidence = _extract_evidence(body_without_code, code_blocks)

    if not description and not steps and not patterns and not evidence:
        raise ProcessParserError(f"{source_type.title()} source has no usable process guidance: {path}")

    return ProcessSource(
        source_path=str(path),
        source_type=source_type,
        title=title,
        description=description,
        steps=steps,
        patterns=patterns,
        anti_patterns=anti_patterns,
        check_paths=check_paths,
        evidence=evidence,
        labels=sorted(dict.fromkeys(labels or [])),
        groups={name: values for name, values in sections.items() if name != "_preamble" and values},
        metadata=metadata,
    )


def _looks_like_runbook_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(parts & RUNBOOK_DIRECTORY_HINTS) or "runbook" in path.stem.lower() or "playbook" in path.stem.lower()


def _title_from_filename(path: Path) -> str:
    title = re.sub(r"[-_]+", " ", path.stem).strip()
    return title.title() if title else path.name


def _strip_frontmatter(text: str, path: Path) -> tuple[str, dict[str, str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text, {}
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            metadata: dict[str, str] = {}
            for raw in lines[1:index]:
                if ":" not in raw:
                    continue
                key, value = raw.split(":", 1)
                cleaned_key = key.strip()
                cleaned_value = value.strip().strip("\"'")
                if cleaned_key and cleaned_value:
                    metadata[cleaned_key] = cleaned_value
            return "\n".join(lines[index + 1 :]), metadata
    raise ProcessParserError(f"Runbook frontmatter is not closed with '---': {path}")


def _extract_code_blocks(text: str, path: Path) -> tuple[str, list[str]]:
    output: list[str] = []
    blocks: list[str] = []
    active: list[str] = []
    fence: str | None = None

    for raw in text.splitlines():
        stripped = raw.strip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            active = [raw]
            output.append("")
            continue
        if fence is not None:
            active.append(raw)
            if stripped.startswith(fence):
                blocks.append("\n".join(active).strip())
                active = []
                fence = None
            output.append("")
            continue
        output.append(raw)

    if fence is not None:
        raise ProcessParserError(f"Markdown code fence is not closed in: {path}")
    return "\n".join(output), blocks


def _extract_title(lines: list[str]) -> str | None:
    for raw in lines:
        match = HEADING_RE.match(raw)
        if match and len(match.group(1)) == 1:
            return _clean_inline(match.group(2))
    return None


def _extract_description(lines: list[str], title: str) -> str:
    paragraph: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            if paragraph:
                break
            continue
        heading = HEADING_RE.match(stripped)
        if heading:
            if _clean_inline(heading.group(2)).lower() == title.lower():
                continue
            if paragraph:
                break
            continue
        if NUMBERED_RE.match(stripped) or BULLET_RE.match(stripped) or _is_table_line(stripped):
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    return _clean_inline(" ".join(paragraph))


def _section_map(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"_preamble": []}
    current = "_preamble"
    for raw in lines:
        heading = HEADING_RE.match(raw.strip())
        if heading:
            current = _clean_inline(heading.group(2))
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw.rstrip())
    return sections


def _extract_steps(sections: dict[str, list[str]]) -> list[str]:
    targeted: list[str] = []
    fallback: list[str] = []
    for section, lines in sections.items():
        values = _numbered_items(lines)
        if STEP_SECTION_RE.search(section):
            targeted.extend(values)
        fallback.extend(values)
    return _dedupe(targeted or fallback)


def _extract_patterns(sections: dict[str, list[str]]) -> list[str]:
    patterns: list[str] = []
    for section, lines in sections.items():
        if not STEP_SECTION_RE.search(section):
            continue
        for item in _list_or_paragraph_items(lines):
            patterns.append(f"{section}: {item}")
    return _dedupe(patterns)


def _extract_anti_patterns(sections: dict[str, list[str]], lines: list[str]) -> list[str]:
    anti_patterns: list[str] = []
    for section, section_lines in sections.items():
        if ANTI_SECTION_RE.search(section):
            anti_patterns.extend(_list_or_paragraph_items(section_lines))
    for raw in lines:
        cleaned = _clean_list_marker(raw)
        lower = cleaned.lower()
        if lower.startswith(("do not ", "never ", "avoid ")):
            anti_patterns.append(cleaned)
    return _dedupe(anti_patterns)


def _extract_check_paths(sections: dict[str, list[str]]) -> list[str]:
    checks: list[str] = []
    for section, lines in sections.items():
        if CHECK_SECTION_RE.search(section):
            checks.extend(_list_or_paragraph_items(lines))
    return _dedupe(checks)


def _extract_evidence(text: str, code_blocks: list[str]) -> list[str]:
    evidence: list[str] = []
    evidence.extend(code_blocks)
    evidence.extend(match.group(0).rstrip(".,") for match in URL_RE.finditer(text))
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if _is_table_line(stripped) or CONFIG_RE.match(stripped):
            evidence.append(stripped)
    return _dedupe(evidence)


def _numbered_items(lines: list[str]) -> list[str]:
    return [_clean_inline(match.group(1)) for raw in lines if (match := NUMBERED_RE.match(raw.strip()))]


def _list_or_paragraph_items(lines: list[str]) -> list[str]:
    items: list[str] = []
    paragraph: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            if paragraph:
                items.append(_clean_inline(" ".join(paragraph)))
                paragraph = []
            continue
        if _is_table_line(stripped):
            items.append(stripped)
            continue
        numbered = NUMBERED_RE.match(stripped)
        bullet = BULLET_RE.match(stripped)
        if numbered or bullet:
            if paragraph:
                items.append(_clean_inline(" ".join(paragraph)))
                paragraph = []
            items.append(_clean_inline((numbered or bullet).group(1)))
            continue
        paragraph.append(stripped)
    if paragraph:
        items.append(_clean_inline(" ".join(paragraph)))
    return [item for item in items if item]


def _clean_list_marker(text: str) -> str:
    stripped = text.strip()
    numbered = NUMBERED_RE.match(stripped)
    if numbered:
        return _clean_inline(numbered.group(1))
    bullet = BULLET_RE.match(stripped)
    if bullet:
        return _clean_inline(bullet.group(1))
    return _clean_inline(stripped)


def _clean_inline(text: str) -> str:
    cleaned = re.sub(r"`([^`]+)`", r"\1", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _is_table_line(line: str) -> bool:
    return line.count("|") >= 2 and not set(line.replace("|", "").strip()) <= {"-", ":"}


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result
