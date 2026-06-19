"""Parse Confluence HTML, XML, directory, and zip exports into process sources."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import xml.etree.ElementTree as ET
import zipfile

from skilgen.parsers.runbook import ProcessParserError, ProcessSource, _dedupe


CONFLUENCE_EXTENSIONS = {".html", ".htm", ".xml"}
BLOCK_TAGS = {
    "article",
    "body",
    "br",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "ol",
    "p",
    "section",
    "table",
    "tbody",
    "td",
    "th",
    "tr",
    "ul",
}
URL_RE = re.compile(r"https?://[^\s)<>\]]+")


def parse_confluence_file(path: str | Path) -> ProcessSource:
    """Parse a single Confluence HTML or XML export file."""

    resolved = Path(path).resolve()
    if not resolved.exists():
        raise ProcessParserError(f"Confluence source does not exist: {resolved}")
    if not resolved.is_file():
        raise ProcessParserError(f"Confluence source is not a file: {resolved}")
    if resolved.suffix.lower() not in CONFLUENCE_EXTENSIONS:
        raise ProcessParserError(f"Confluence source must be HTML or XML: {resolved}")
    raw = resolved.read_text(encoding="utf-8", errors="ignore")
    if not raw.strip():
        raise ProcessParserError(f"Confluence source is empty: {resolved}")
    if resolved.suffix.lower() == ".xml":
        return _parse_confluence_xml(resolved, raw)
    return _parse_confluence_html(resolved, raw)


def parse_confluence_source(path: str | Path) -> list[ProcessSource]:
    """Parse a Confluence file, export directory, or zip archive."""

    resolved = Path(path).resolve()
    if not resolved.exists():
        raise ProcessParserError(f"Confluence source does not exist: {resolved}")
    if resolved.is_file() and resolved.suffix.lower() == ".zip":
        return _parse_confluence_zip(resolved)
    if resolved.is_file():
        return [parse_confluence_file(resolved)]
    if not resolved.is_dir():
        raise ProcessParserError(f"Confluence source is neither a file nor directory: {resolved}")
    files = [
        candidate
        for candidate in sorted(resolved.rglob("*"))
        if candidate.is_file() and candidate.suffix.lower() in CONFLUENCE_EXTENSIONS
    ]
    if not files:
        raise ProcessParserError(f"No Confluence HTML/XML files found under: {resolved}")
    return [parse_confluence_file(candidate) for candidate in files]


def _parse_confluence_zip(path: Path) -> list[ProcessSource]:
    try:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with zipfile.ZipFile(path) as archive:
                for member in archive.infolist():
                    if member.is_dir():
                        continue
                    target = (root / member.filename).resolve()
                    if not target.is_relative_to(root):
                        raise ProcessParserError(f"Confluence zip export contains an unsafe path: {member.filename}")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(member))
            return parse_confluence_source(root)
    except zipfile.BadZipFile as exc:
        raise ProcessParserError(f"Confluence zip export is malformed: {path}") from exc


def _parse_confluence_html(path: Path, raw: str) -> ProcessSource:
    parser = _ConfluenceHTMLExtractor()
    try:
        parser.feed(raw)
        parser.close()
    except Exception as exc:
        raise ProcessParserError(f"Could not parse Confluence HTML export: {path}") from exc

    body = _normalize_body(parser.text())
    title = parser.title() or _title_from_filename(path)
    description = _first_paragraph(body, title)
    labels = parser.labels()
    groups = _section_groups(body, parser.headings())
    steps = _ordered_items(body)
    patterns = _section_items(groups, ("steps", "procedure", "process", "checklist", "how to", "instructions"))
    anti_patterns = _section_items(groups, ("do not", "never", "avoid", "warning", "common mistake"))
    check_paths = _section_items(groups, ("verification", "validation", "confirm", "health check"))
    evidence = _dedupe(parser.code_blocks() + parser.table_rows() + URL_RE.findall(body))

    if not body and not evidence:
        raise ProcessParserError(f"Confluence source has no parseable body content: {path}")

    return ProcessSource(
        source_path=str(path),
        source_type="confluence",
        title=title,
        description=description,
        steps=steps,
        patterns=patterns,
        anti_patterns=anti_patterns,
        check_paths=check_paths,
        evidence=evidence,
        labels=labels,
        groups={**groups, **({"labels": labels} if labels else {})},
        metadata={"format": "html"},
    )


def _parse_confluence_xml(path: Path, raw: str) -> ProcessSource:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ProcessParserError(f"Could not parse Confluence XML export: {path}: {exc}") from exc

    text = _normalize_body("\n".join(part.strip() for part in root.itertext() if part and part.strip()))
    title = _xml_title(root) or _title_from_filename(path)
    labels = _xml_labels(root)
    code_blocks = _xml_code_blocks(root)
    table_rows = _xml_table_rows(root)
    description = _first_paragraph(text, title)
    groups = _section_groups(text, [])
    steps = _ordered_items(text)
    patterns = _section_items(groups, ("steps", "procedure", "process", "checklist", "how to", "instructions"))
    anti_patterns = _section_items(groups, ("do not", "never", "avoid", "warning", "common mistake"))
    check_paths = _section_items(groups, ("verification", "validation", "confirm", "health check"))
    evidence = _dedupe(code_blocks + table_rows + URL_RE.findall(text))

    if not text and not evidence:
        raise ProcessParserError(f"Confluence XML source has no parseable body content: {path}")

    return ProcessSource(
        source_path=str(path),
        source_type="confluence",
        title=title,
        description=description,
        steps=steps,
        patterns=patterns,
        anti_patterns=anti_patterns,
        check_paths=check_paths,
        evidence=evidence,
        labels=labels,
        groups={**groups, **({"labels": labels} if labels else {})},
        metadata={"format": "xml"},
    )


class _ConfluenceHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._title_parts: list[str] = []
        self._meta_title = ""
        self._headings: list[str] = []
        self._heading_parts: list[str] = []
        self._labels: list[str] = []
        self._code_blocks: list[str] = []
        self._code_parts: list[str] = []
        self._table_rows: list[str] = []
        self._row_cells: list[str] = []
        self._cell_parts: list[str] = []
        self._skip_depth = 0
        self._code_depth = 0
        self._heading_tag: str | None = None
        self._in_title = False
        self._in_row = False
        self._in_cell = False
        self._ol_stack: list[int] = []
        self._ul_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag in {"pre", "code"}:
            self._code_depth += 1
            if self._code_depth == 1:
                self._code_parts = []
        if tag == "tr":
            self._in_row = True
            self._row_cells = []
        if tag == "ol":
            self._ol_stack.append(1)
        if tag == "ul":
            self._ul_depth += 1
        if tag == "li":
            if self._ol_stack:
                current = self._ol_stack[-1]
                self._ol_stack[-1] = current + 1
                self._parts.append(f"\n{current}. ")
            elif self._ul_depth:
                self._parts.append("\n- ")
        if tag in {"td", "th"}:
            self._in_cell = True
            self._cell_parts = []
        if tag == "meta":
            self._extract_meta(attributes)
        if tag == "a":
            href = attributes.get("href", "").strip()
            if href.startswith(("http://", "https://")):
                self._parts.append(href)
            if "label" in attributes.get("class", "").lower():
                self._labels.append(attributes.get("title", "") or attributes.get("data-label", ""))
        if "data-label" in attributes:
            self._labels.append(attributes["data-label"])
        if tag in BLOCK_TAGS and tag != "li":
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag == self._heading_tag:
            heading = _clean_text(" ".join(self._heading_parts))
            if heading:
                self._headings.append(heading)
                self._parts.extend(["\n", heading, "\n"])
            self._heading_tag = None
            self._heading_parts = []
        if tag in {"pre", "code"} and self._code_depth:
            self._code_depth -= 1
            if self._code_depth == 0:
                code = "\n".join(part.rstrip() for part in "".join(self._code_parts).splitlines()).strip()
                if code:
                    self._code_blocks.append(f"```\n{code}\n```")
                self._code_parts = []
        if tag in {"td", "th"} and self._in_cell:
            cell = _clean_text(" ".join(self._cell_parts))
            if cell:
                self._row_cells.append(cell)
            self._in_cell = False
            self._cell_parts = []
        if tag == "tr" and self._in_row:
            if self._row_cells:
                self._table_rows.append(" | ".join(self._row_cells))
            self._in_row = False
            self._row_cells = []
        if tag == "ol" and self._ol_stack:
            self._ol_stack.pop()
        if tag == "ul" and self._ul_depth:
            self._ul_depth -= 1
        if tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        if self._heading_tag is not None:
            self._heading_parts.append(data)
        if self._code_depth:
            self._code_parts.append(data)
            return
        if self._in_cell:
            self._cell_parts.append(data)
        self._parts.append(data)

    def title(self) -> str:
        browser_title = _clean_text(" ".join(self._title_parts))
        if " - Confluence" in browser_title:
            browser_title = browser_title.split(" - Confluence", 1)[0].strip()
        return _clean_text(self._meta_title or " ".join(self._headings[:1]) or browser_title)

    def text(self) -> str:
        return "".join(self._parts)

    def headings(self) -> list[str]:
        return _dedupe(self._headings)

    def labels(self) -> list[str]:
        return _dedupe([label.strip() for label in self._labels if label.strip()])

    def code_blocks(self) -> list[str]:
        return _dedupe(self._code_blocks)

    def table_rows(self) -> list[str]:
        return _dedupe(self._table_rows)

    def _extract_meta(self, attributes: dict[str, str]) -> None:
        key = (attributes.get("name") or attributes.get("property") or "").lower()
        content = attributes.get("content", "").strip()
        if not content:
            return
        if key in {"ajs-page-title", "title", "og:title"}:
            self._meta_title = content
        if key in {"ajs-labels", "labels", "keywords"}:
            self._labels.extend(part.strip() for part in re.split(r"[,;]", content) if part.strip())


def _xml_title(root: ET.Element) -> str:
    for element in root.iter():
        if _local_name(element.tag) == "title" and element.text and element.text.strip():
            return _clean_text(element.text)
        if element.attrib.get("name") == "title" and element.text and element.text.strip():
            return _clean_text(element.text)
    return ""


def _xml_labels(root: ET.Element) -> list[str]:
    labels: list[str] = []
    for element in root.iter():
        local = _local_name(element.tag)
        if local in {"label", "labels"} and element.text:
            labels.extend(part.strip() for part in re.split(r"[,;]", element.text) if part.strip())
        if "label" in element.attrib:
            labels.append(element.attrib["label"])
    return _dedupe(labels)


def _xml_code_blocks(root: ET.Element) -> list[str]:
    blocks: list[str] = []
    for element in root.iter():
        if _local_name(element.tag) in {"code", "pre", "plain-text-body"}:
            code = "\n".join(part.rstrip() for part in "".join(element.itertext()).splitlines()).strip()
            if code:
                blocks.append(f"```\n{code}\n```")
    return _dedupe(blocks)


def _xml_table_rows(root: ET.Element) -> list[str]:
    rows: list[str] = []
    for row in root.iter():
        if _local_name(row.tag) != "tr":
            continue
        cells = [
            _clean_text(" ".join(cell.itertext()))
            for cell in list(row)
            if _local_name(cell.tag) in {"td", "th"} and _clean_text(" ".join(cell.itertext()))
        ]
        if cells:
            rows.append(" | ".join(cells))
    return _dedupe(rows)


def _section_groups(text: str, headings: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    current = "_preamble"
    heading_set = {heading.lower() for heading in headings}
    groups[current] = []
    for raw in text.splitlines():
        line = _clean_text(raw)
        if not line:
            continue
        if line.lower() in heading_set:
            current = line
            groups.setdefault(current, [])
            continue
        groups.setdefault(current, []).append(line)
    return {name: _dedupe(values) for name, values in groups.items() if values}


def _section_items(groups: dict[str, list[str]], prefixes: tuple[str, ...]) -> list[str]:
    items: list[str] = []
    for section, values in groups.items():
        lower = section.lower()
        if any(lower.startswith(prefix) for prefix in prefixes):
            items.extend(_clean_ordered_item(value) for value in values)
    return _dedupe(items)


def _ordered_items(text: str) -> list[str]:
    items: list[str] = []
    for raw in text.splitlines():
        cleaned = _clean_ordered_item(raw)
        if cleaned != _clean_text(raw):
            items.append(cleaned)
    return _dedupe(items)


def _clean_ordered_item(text: str) -> str:
    return re.sub(r"^\s*\d+[.)]\s*", "", _clean_text(text))


def _first_paragraph(text: str, title: str) -> str:
    for raw in text.splitlines():
        line = _clean_text(raw)
        if not line or line.lower() == title.lower():
            continue
        if re.match(r"^\d+[.)]\s+", line):
            continue
        return line
    return ""


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_body(text: str) -> str:
    lines = [_clean_text(raw) for raw in text.splitlines()]
    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if not previous_blank and cleaned:
                cleaned.append("")
            previous_blank = True
            continue
        cleaned.append(line)
        previous_blank = False
    return "\n".join(cleaned).strip()


def _title_from_filename(path: Path) -> str:
    return re.sub(r"[-_]+", " ", path.stem).strip().title() or path.name


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()
