"""Parse Notion Markdown exports and API JSON payloads into process sources."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any

from skilgen.parsers.runbook import (
    ProcessParserError,
    ProcessSource,
    _parse_markdown_document,
    _parse_markdown_text as _parse_markdown_text_source,
)


NOTION_MARKDOWN_EXTENSIONS = {".md", ".markdown"}
NOTION_API_VERSION = "2022-06-28"
_LAST_NOTION_REQUEST = 0.0


def parse_notion_file(path: str | Path) -> ProcessSource:
    """Parse one Notion Markdown export or saved Notion API JSON payload."""

    resolved = Path(path).resolve()
    if not resolved.exists():
        raise ProcessParserError(f"Notion source does not exist: {resolved}")
    if not resolved.is_file():
        raise ProcessParserError(f"Notion source is not a file: {resolved}")
    if resolved.suffix.lower() in NOTION_MARKDOWN_EXTENSIONS:
        return _parse_markdown_document(resolved, source_type="notion")
    if resolved.suffix.lower() == ".json":
        try:
            payload = json.loads(resolved.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ProcessParserError(f"Could not parse Notion JSON export: {resolved}: {exc}") from exc
        return parse_notion_api_json(payload, source_path=str(resolved))
    raise ProcessParserError(f"Notion source must be Markdown or JSON: {resolved}")


def parse_notion_source(path: str | Path) -> list[ProcessSource]:
    """Parse a Notion export file or directory containing Markdown/JSON exports."""

    resolved = Path(path).resolve()
    if not resolved.exists():
        raise ProcessParserError(f"Notion source does not exist: {resolved}")
    if resolved.is_file():
        return [parse_notion_file(resolved)]
    if not resolved.is_dir():
        raise ProcessParserError(f"Notion source is neither a file nor directory: {resolved}")
    files = [
        candidate
        for candidate in sorted(resolved.rglob("*"))
        if candidate.is_file() and candidate.suffix.lower() in (NOTION_MARKDOWN_EXTENSIONS | {".json"})
    ]
    if not files:
        raise ProcessParserError(f"No Notion Markdown/JSON exports found under: {resolved}")
    return [parse_notion_file(candidate) for candidate in files]


def parse_notion_api_json(payload: dict[str, Any], *, source_path: str = "<notion-api>") -> ProcessSource:
    """Parse a Notion API page payload with optional block children."""

    if not isinstance(payload, dict) or not payload:
        raise ProcessParserError("Notion API payload is empty or not an object.")

    page = payload.get("page") if isinstance(payload.get("page"), dict) else payload
    blocks = payload.get("blocks", [])
    if isinstance(blocks, dict):
        blocks = blocks.get("results", [])
    if not isinstance(blocks, list):
        raise ProcessParserError("Notion API payload 'blocks' must be a list or results object.")

    title = _notion_title(page) or "Notion Page"
    markdown = _blocks_to_markdown(title, blocks)
    if not markdown.strip():
        raise ProcessParserError(f"Notion API payload has no parseable block content: {source_path}")

    synthetic = Path(source_path) if source_path != "<notion-api>" else Path("notion-api.md")
    temp_path = synthetic.with_suffix(".md")
    source = _source_from_markdown_text(markdown, temp_path, source_path)
    labels = _notion_labels(page)
    return ProcessSource(
        source_path=source_path,
        source_type="notion",
        title=source.title,
        description=source.description,
        steps=source.steps,
        patterns=source.patterns,
        anti_patterns=source.anti_patterns,
        check_paths=source.check_paths,
        evidence=source.evidence,
        labels=labels,
        groups=source.groups,
        metadata={"format": "api-json"},
    )


def fetch_notion_page_json(page_id: str) -> dict[str, Any]:
    """Fetch a Notion page and first-page block children using env-only auth by default."""

    key = os.environ.get("NOTION_API_KEY")
    if not key:
        raise ProcessParserError("NOTION_API_KEY is required to fetch Notion API content.")
    if not page_id.strip():
        raise ProcessParserError("A Notion page_id is required.")
    try:
        import httpx
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ProcessParserError("httpx is required for Notion API fetching.") from exc

    headers = {
        "Authorization": f"Bearer {key}",
        "Notion-Version": NOTION_API_VERSION,
        "Accept": "application/json",
    }
    base = "https://api.notion.com/v1"
    with httpx.Client(headers=headers, timeout=10.0) as client:
        page = _notion_get(client, f"{base}/pages/{page_id}")
        children = _notion_get(client, f"{base}/blocks/{page_id}/children?page_size=100")
    return {"page": page, "blocks": children.get("results", [])}


def _notion_get(client: Any, url: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(3):
        _rate_limit()
        try:
            response = client.get(url)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload
            raise ProcessParserError(f"Notion API returned non-object JSON for {url}")
        except Exception as exc:  # pragma: no cover - exercised only with network
            last_error = exc
            if attempt == 2:
                break
            time.sleep(0.5 * (attempt + 1))
    raise ProcessParserError(f"Notion API request failed for {url}: {last_error}") from last_error


def _rate_limit() -> None:
    global _LAST_NOTION_REQUEST
    now = time.monotonic()
    wait_for = (1.0 / 3.0) - (now - _LAST_NOTION_REQUEST)
    if wait_for > 0:
        time.sleep(wait_for)
    _LAST_NOTION_REQUEST = time.monotonic()


def _source_from_markdown_text(text: str, path: Path, source_path: str) -> ProcessSource:
    source = _parse_markdown_text_source(text, path, source_type="notion")
    return ProcessSource(
        source_path=source_path,
        source_type=source.source_type,
        title=source.title,
        description=source.description,
        steps=source.steps,
        patterns=source.patterns,
        anti_patterns=source.anti_patterns,
        check_paths=source.check_paths,
        evidence=source.evidence,
        labels=source.labels,
        groups=source.groups,
        metadata=source.metadata,
    )


def _notion_title(page: dict[str, Any]) -> str:
    properties = page.get("properties", {}) if isinstance(page, dict) else {}
    if isinstance(properties, dict):
        for value in properties.values():
            if not isinstance(value, dict) or value.get("type") != "title":
                continue
            title_parts = value.get("title", [])
            rendered = _rich_text(title_parts)
            if rendered:
                return rendered
    for key in ("title", "name"):
        value = page.get(key) if isinstance(page, dict) else None
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _notion_labels(page: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    properties = page.get("properties", {}) if isinstance(page, dict) else {}
    if not isinstance(properties, dict):
        return []
    for value in properties.values():
        if not isinstance(value, dict):
            continue
        if value.get("type") == "multi_select":
            labels.extend(item.get("name", "") for item in value.get("multi_select", []) if isinstance(item, dict))
        if value.get("type") == "select" and isinstance(value.get("select"), dict):
            labels.append(value["select"].get("name", ""))
    return sorted(dict.fromkeys(label.strip() for label in labels if label and label.strip()))


def _blocks_to_markdown(title: str, blocks: list[Any]) -> str:
    lines = [f"# {title}", ""]
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = str(block.get("type", ""))
        value = block.get(block_type, {}) if isinstance(block.get(block_type, {}), dict) else {}
        text = _rich_text(value.get("rich_text", []))
        if block_type.startswith("heading_"):
            level = block_type.rsplit("_", 1)[-1]
            depth = int(level) if level.isdigit() else 2
            lines.append(f"{'#' * max(2, min(depth + 1, 6))} {text}")
        elif block_type == "numbered_list_item" and text:
            lines.append(f"1. {text}")
        elif block_type == "to_do" and text:
            checked = "x" if value.get("checked") else " "
            lines.append(f"- [{checked}] {text}")
        elif block_type == "bulleted_list_item" and text:
            lines.append(f"- {text}")
        elif block_type == "code":
            language = value.get("language", "") or ""
            lines.extend([f"```{language}", text, "```"])
        elif text:
            lines.append(text)
        if block.get("has_children") and isinstance(block.get("children"), list):
            child_text = _blocks_to_markdown("", block["children"])
            lines.extend(line for line in child_text.splitlines() if line and not line.startswith("# "))
    return "\n".join(lines)


def _rich_text(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    parts: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("plain_text"), str):
            parts.append(item["plain_text"])
        elif isinstance(item.get("text"), dict) and isinstance(item["text"].get("content"), str):
            parts.append(item["text"]["content"])
    return " ".join(part.strip() for part in parts if part and part.strip()).strip()
