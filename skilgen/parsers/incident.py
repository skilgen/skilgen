"""Parsers for incident, PIR, and postmortem source artifacts.

The parser keeps incident evidence structured enough for downstream skill
generation without assuming a single enterprise template. It supports Markdown
postmortems/PIRs and PagerDuty JSON exports, plus a small GitHub issue helper
that only uses the ``GITHUB_TOKEN`` environment variable when available.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from json import JSONDecodeError
import json
import os
from pathlib import Path
import re
import time
from typing import Iterable, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen


INCIDENT_MARKDOWN_RE = re.compile(r"(post[-_ ]?mortem|postmortem|incident|pir)", re.IGNORECASE)
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
PAGERDUTY_JSON_RE = re.compile(r"(pagerduty|pager_duty|pd[_-]?export|incident)", re.IGNORECASE)
GITHUB_TIMEOUT_SECONDS = 10
GITHUB_RETRY_ATTEMPTS = 3


class IncidentParseError(ValueError):
    """Raised when an incident source cannot be parsed safely."""


@dataclass(frozen=True)
class IncidentRecord:
    """A normalized incident record from Markdown, PagerDuty, or GitHub."""

    title: str
    source_path: str
    source_type: str
    description: str = ""
    service_domain: str | None = None
    incident_patterns: list[str] = field(default_factory=list)
    timeline_evidence: list[str] = field(default_factory=list)
    root_cause_patterns: list[str] = field(default_factory=list)
    contributing_factor_patterns: list[str] = field(default_factory=list)
    impact_evidence: list[str] = field(default_factory=list)
    check_paths: list[str] = field(default_factory=list)
    success_patterns: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    urgency: str | None = None
    duration_minutes: float | None = None
    created_month: str | None = None
    body_summary: str = ""


@dataclass(frozen=True)
class PagerDutyMetrics:
    """Aggregated PagerDuty incident patterns."""

    urgency_groups: dict[str, list[str]]
    mean_time_to_resolve_minutes: dict[str, float]
    common_title_clusters: list[str]
    incidents_per_month: dict[str, int]
    patterns: list[str]


@dataclass(frozen=True)
class IncidentSourceAnalysis:
    """Enterprise incident source analysis for skill generation."""

    source_paths: list[str]
    incidents: list[IncidentRecord]
    descriptions: list[str]
    timeline_evidence: list[str]
    root_cause_patterns: list[str]
    contributing_factor_patterns: list[str]
    impact_evidence: list[str]
    check_paths: list[str]
    success_patterns: list[str]
    anti_patterns: list[str]
    incident_patterns: list[str]
    pagerduty_metrics: PagerDutyMetrics | None = None

    @property
    def patterns(self) -> list[str]:
        """Return actionable recurring patterns discovered across sources."""

        return _dedupe(
            [
                *self.root_cause_patterns,
                *self.contributing_factor_patterns,
                *self.success_patterns,
                *self.incident_patterns,
                *(self.pagerduty_metrics.patterns if self.pagerduty_metrics else []),
            ]
        )


@dataclass(frozen=True)
class GitHubIncidentIssue:
    """Minimal GitHub incident issue data from the optional env-token helper."""

    title: str
    url: str
    state: str
    labels: list[str]
    body_summary: str


@dataclass(frozen=True)
class _MarkdownSection:
    title: str
    level: int
    lines: list[str]


def discover_incident_sources(source_paths: Sequence[str | Path]) -> list[Path]:
    """Find matching Markdown postmortems and PagerDuty JSON exports."""

    if not source_paths:
        raise IncidentParseError("No incident source paths were provided.")

    discovered: list[Path] = []
    for raw_source in source_paths:
        source = Path(raw_source)
        if not source.exists():
            raise IncidentParseError(f"Incident source path does not exist: {source}")
        if source.is_file():
            if _is_supported_source(source, explicit=True):
                discovered.append(source)
            else:
                raise IncidentParseError(f"Unsupported incident source type: {source}")
            continue
        for path in sorted(source.rglob("*")):
            if path.is_file() and _is_supported_source(path, explicit=False):
                discovered.append(path)

    unique = _dedupe_paths(discovered)
    if not unique:
        joined = ", ".join(str(Path(item)) for item in source_paths)
        raise IncidentParseError(f"No incident postmortem or PagerDuty export files were found under: {joined}")
    return unique


def parse_incident_sources(source_paths: Sequence[str | Path]) -> IncidentSourceAnalysis:
    """Parse Markdown postmortems/PIRs and PagerDuty exports from files or directories."""

    files = discover_incident_sources(source_paths)
    markdown_incidents: list[IncidentRecord] = []
    pagerduty_incidents: list[IncidentRecord] = []
    pagerduty_metrics: PagerDutyMetrics | None = None

    for path in files:
        try:
            if path.suffix.lower() in MARKDOWN_EXTENSIONS:
                markdown_incidents.append(parse_markdown_postmortem(path))
            elif path.suffix.lower() == ".json":
                export = parse_pagerduty_export(path)
                pagerduty_incidents.extend(export.incidents)
                pagerduty_metrics = _merge_pagerduty_metrics(pagerduty_metrics, export.pagerduty_metrics)
        except IncidentParseError as exc:
            raise IncidentParseError(f"{path}: {exc}") from exc

    incidents = [*markdown_incidents, *pagerduty_incidents]
    if not incidents:
        raise IncidentParseError("Incident sources were discovered but no incidents could be parsed.")

    return _analysis_from_incidents(files, incidents, pagerduty_metrics=pagerduty_metrics)


def parse_markdown_postmortem(path: str | Path) -> IncidentRecord:
    """Parse a structured Markdown postmortem, incident report, or PIR file."""

    source = Path(path)
    text = _read_text(source)
    if not text.strip():
        raise IncidentParseError("Markdown incident source is empty.")

    title = _extract_markdown_title(text, source)
    sections = _split_markdown_sections(text)
    if not sections:
        raise IncidentParseError("Markdown incident source does not contain recognizable headings.")

    description_lines = _section_lines(
        sections,
        {
            "summary",
            "overview",
            "executive summary",
            "description",
            "incident summary",
            "what happened",
        },
    )
    timeline = _section_lines(sections, {"timeline", "incident timeline", "detection timeline"})
    root_causes = _section_lines(sections, {"root cause", "root causes", "cause", "causes"})
    contributing = _section_lines(
        sections,
        {"contributing factors", "contributing factor", "trigger", "triggers", "detection gaps"},
    )
    impact = _section_lines(sections, {"impact", "customer impact", "blast radius", "user impact"})
    action_items = _section_lines(
        sections,
        {"action items", "action item", "follow-up", "follow up", "followups", "remediation", "preventive actions"},
    )
    went_well = _section_lines(sections, {"what went well", "went well", "successes"})
    went_wrong = _section_lines(
        sections,
        {"what went wrong", "lessons learned", "lessons", "gaps", "areas for improvement"},
    )

    if not any([description_lines, timeline, root_causes, contributing, impact, action_items, went_well, went_wrong]):
        raise IncidentParseError("Markdown incident source does not contain recognizable postmortem sections.")

    description = _first_paragraph(description_lines)
    body = "\n".join([title, text])
    service_domain = _derive_service_domain(title)
    incident_patterns = [] if service_domain else _derive_incident_patterns(body)

    return IncidentRecord(
        title=title,
        source_path=str(source),
        source_type="markdown",
        description=description,
        service_domain=service_domain,
        incident_patterns=incident_patterns,
        timeline_evidence=timeline,
        root_cause_patterns=root_causes,
        contributing_factor_patterns=contributing,
        impact_evidence=impact,
        check_paths=action_items,
        success_patterns=went_well,
        anti_patterns=went_wrong,
        body_summary=description,
    )


def parse_pagerduty_export(path: str | Path) -> IncidentSourceAnalysis:
    """Parse a PagerDuty JSON export and aggregate operational patterns."""

    source = Path(path)
    raw = _read_text(source)
    if not raw.strip():
        raise IncidentParseError("PagerDuty export is empty.")
    try:
        payload = json.loads(raw)
    except JSONDecodeError as exc:
        raise IncidentParseError(f"Invalid PagerDuty JSON export: {exc.msg}") from exc

    incident_payloads = _coerce_pagerduty_incidents(payload)
    if not incident_payloads:
        raise IncidentParseError("PagerDuty export does not contain incidents.")

    incidents: list[IncidentRecord] = []
    for index, item in enumerate(incident_payloads, start=1):
        if not isinstance(item, dict):
            raise IncidentParseError(f"PagerDuty incident #{index} is not an object.")
        incidents.append(_parse_pagerduty_incident(item, source, index))

    metrics = _pagerduty_metrics(incidents)
    return _analysis_from_incidents([source], incidents, pagerduty_metrics=metrics)


def fetch_github_incident_issues(
    repo: str,
    *,
    labels: Sequence[str] = ("incident", "postmortem", "pir"),
    state: str = "all",
    max_pages: int = 1,
) -> list[GitHubIncidentIssue]:
    """Fetch GitHub incident issues using only the ``GITHUB_TOKEN`` environment variable.

    The helper is intentionally small and side-effect free so future incident
    source wiring can opt in without accepting raw user-supplied tokens.
    """

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return []
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise IncidentParseError("GitHub repo must be in owner/name form.")
    if state not in {"open", "closed", "all"}:
        raise IncidentParseError("GitHub issue state must be one of: open, closed, all.")

    page_count = max(1, min(max_pages, 5))
    issues: dict[int, GitHubIncidentIssue] = {}
    for label in labels:
        if not label.strip():
            continue
        for page in range(1, page_count + 1):
            params = urlencode({"state": state, "labels": label, "per_page": 100, "page": page})
            url = f"https://api.github.com/repos/{quote(repo, safe='/')}/issues?{params}"
            payload = _github_get_json(url, token)
            if not isinstance(payload, list):
                raise IncidentParseError("GitHub issues response was not a list.")
            for item in payload:
                if not isinstance(item, dict) or "pull_request" in item:
                    continue
                number = item.get("number")
                if not isinstance(number, int) or number in issues:
                    continue
                issue_labels = [
                    str(label_item.get("name", "")).strip()
                    for label_item in item.get("labels", [])
                    if isinstance(label_item, dict) and str(label_item.get("name", "")).strip()
                ]
                issues[number] = GitHubIncidentIssue(
                    title=str(item.get("title", "")).strip(),
                    url=str(item.get("html_url", "")).strip(),
                    state=str(item.get("state", "")).strip(),
                    labels=issue_labels,
                    body_summary=_summarize(str(item.get("body", "") or ""), limit=300),
                )
    return list(issues.values())


def _analysis_from_incidents(
    source_paths: Sequence[Path],
    incidents: Sequence[IncidentRecord],
    *,
    pagerduty_metrics: PagerDutyMetrics | None,
) -> IncidentSourceAnalysis:
    return IncidentSourceAnalysis(
        source_paths=[str(path) for path in source_paths],
        incidents=list(incidents),
        descriptions=_dedupe(incident.description for incident in incidents if incident.description),
        timeline_evidence=_dedupe(_flatten(incident.timeline_evidence for incident in incidents)),
        root_cause_patterns=_dedupe(_flatten(incident.root_cause_patterns for incident in incidents)),
        contributing_factor_patterns=_dedupe(_flatten(incident.contributing_factor_patterns for incident in incidents)),
        impact_evidence=_dedupe(_flatten(incident.impact_evidence for incident in incidents)),
        check_paths=_dedupe(_flatten(incident.check_paths for incident in incidents)),
        success_patterns=_dedupe(_flatten(incident.success_patterns for incident in incidents)),
        anti_patterns=_dedupe(_flatten(incident.anti_patterns for incident in incidents)),
        incident_patterns=_dedupe(_flatten(incident.incident_patterns for incident in incidents)),
        pagerduty_metrics=pagerduty_metrics,
    )


def _is_supported_source(path: Path, *, explicit: bool) -> bool:
    suffix = path.suffix.lower()
    if suffix in MARKDOWN_EXTENSIONS:
        return explicit or _matches_incident_name(path)
    if suffix == ".json":
        return explicit or bool(PAGERDUTY_JSON_RE.search(path.name))
    return False


def _matches_incident_name(path: Path) -> bool:
    candidate = "/".join(path.parts[-4:])
    return bool(INCIDENT_MARKDOWN_RE.search(candidate))


def _read_text(path: Path) -> str:
    if not path.exists():
        raise IncidentParseError(f"Incident source does not exist: {path}")
    if not path.is_file():
        raise IncidentParseError(f"Incident source is not a file: {path}")
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        raise IncidentParseError(f"Could not read incident source: {exc}") from exc


def _extract_markdown_title(text: str, source: Path) -> str:
    for line in text.splitlines():
        match = re.match(r"^\s*#\s+(.+?)\s*#*\s*$", line)
        if match:
            return _clean_inline_markdown(match.group(1))
    for line in text.splitlines():
        match = re.match(r"^\s*#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            return _clean_inline_markdown(match.group(1))
    return source.stem.replace("_", " ").replace("-", " ").title()


def _split_markdown_sections(text: str) -> list[_MarkdownSection]:
    sections: list[_MarkdownSection] = []
    current_title: str | None = None
    current_level = 0
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        heading = re.match(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$", raw_line)
        if heading:
            if current_title is not None:
                sections.append(_MarkdownSection(current_title, current_level, current_lines))
            current_title = _clean_inline_markdown(heading.group(2))
            current_level = len(heading.group(1))
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(raw_line)

    if current_title is not None:
        sections.append(_MarkdownSection(current_title, current_level, current_lines))
    return sections


def _section_lines(sections: Sequence[_MarkdownSection], aliases: set[str]) -> list[str]:
    lines: list[str] = []
    for section in sections:
        key = _heading_key(section.title)
        if key in aliases or any(alias in key for alias in aliases if len(alias) > 5):
            lines.extend(_clean_evidence_lines(section.lines))
    return _dedupe(lines)


def _clean_evidence_lines(lines: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or re.fullmatch(r"[-:| ]+", line):
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells if cell):
                continue
            line = " | ".join(cell for cell in cells if cell)
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
        line = re.sub(r"^\[(?: |x|X)\]\s+", "", line)
        line = _clean_inline_markdown(line)
        if line:
            cleaned.append(line)
    return cleaned


def _clean_inline_markdown(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("*", "")
    return " ".join(value.split()).strip()


def _heading_key(value: str) -> str:
    value = _clean_inline_markdown(value).lower()
    value = re.sub(r"[^a-z0-9 /_-]+", "", value)
    return re.sub(r"[\s_-]+", " ", value).strip()


def _first_paragraph(lines: Sequence[str]) -> str:
    paragraph: list[str] = []
    for line in lines:
        if not line:
            if paragraph:
                break
            continue
        paragraph.append(line)
    return _summarize(" ".join(paragraph), limit=500)


def _derive_service_domain(title: str) -> str | None:
    patterns = [
        r"\bservice\s*[:=-]\s*([A-Za-z0-9][A-Za-z0-9_. -]{1,60})\b",
        r"\b([A-Za-z0-9][A-Za-z0-9_. -]{1,60}?)\s+service\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, flags=re.IGNORECASE)
        if not match:
            continue
        candidate = _strip_incident_words(match.group(1))
        slug = _slugify(candidate)
        if slug:
            return slug
    return None


def _derive_incident_patterns(text: str) -> list[str]:
    lowered = text.lower()
    patterns: list[str] = []
    signals = {
        "database outage": r"\b(database|postgres|mysql|mongo|redis)\b.*\b(outage|unavailable|connection|timeout)\b",
        "api latency": r"\b(api|endpoint|http|gateway)\b.*\b(latency|slow|timeout|5xx)\b",
        "deployment regression": r"\b(deploy|release|rollout|migration)\b.*\b(regression|rollback|failed|incident)\b",
        "queue backlog": r"\b(queue|worker|job|consumer)\b.*\b(backlog|lag|stuck|delayed)\b",
        "authentication failure": r"\b(auth|login|oauth|sso)\b.*\b(fail|error|outage|denied)\b",
        "cache failure": r"\b(cache|cdn|edge)\b.*\b(stale|purge|miss|outage|failure)\b",
        "third-party dependency": r"\b(vendor|third party|third-party|provider|dependency)\b.*\b(outage|degraded|failure)\b",
    }
    for label, pattern in signals.items():
        if re.search(pattern, lowered, flags=re.DOTALL):
            patterns.append(label)
    if not patterns:
        title_words = _cluster_title(text.splitlines()[0] if text.splitlines() else text)
        if title_words:
            patterns.append(title_words)
    return patterns


def _strip_incident_words(value: str) -> str:
    value = re.sub(
        r"\b(postmortem|post mortem|pir|incident|outage|degradation|degraded|latency|failure|sev[0-9]?|p[1-4])\b",
        " ",
        value,
        flags=re.IGNORECASE,
    )
    return " ".join(value.split())


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_. -]+", " ", value).strip().lower()
    cleaned = re.sub(r"[\s_.]+", "-", cleaned)
    return cleaned.strip("-")


def _coerce_pagerduty_incidents(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise IncidentParseError("PagerDuty export root must be an object or list.")
    for key in ("incidents", "data", "records", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    if "title" in payload or "summary" in payload or "description" in payload:
        return [payload]
    return []


def _parse_pagerduty_incident(item: dict[str, object], source: Path, index: int) -> IncidentRecord:
    title = _first_string(item, "title", "summary", "description", "name")
    if not title:
        raise IncidentParseError(f"PagerDuty incident #{index} is missing a title.")

    urgency = _extract_pagerduty_urgency(item)
    duration = _extract_duration_minutes(item)
    created = _first_string(item, "created_at", "createdAt", "started_at", "start_time")
    created_month = _month_key(created) if created else None
    body_summary = _extract_body_summary(item)
    service_domain = _derive_service_domain(title)
    incident_patterns = [] if service_domain else _derive_incident_patterns(f"{title}\n{body_summary}")

    return IncidentRecord(
        title=title,
        source_path=str(source),
        source_type="pagerduty",
        description=body_summary,
        service_domain=service_domain,
        incident_patterns=incident_patterns,
        urgency=urgency,
        duration_minutes=duration,
        created_month=created_month,
        body_summary=body_summary,
    )


def _first_string(item: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def _extract_pagerduty_urgency(item: dict[str, object]) -> str | None:
    candidates: list[str] = []
    for key in ("urgency", "severity", "priority"):
        value = item.get(key)
        if isinstance(value, str):
            candidates.append(value)
        elif isinstance(value, dict):
            for nested_key in ("summary", "name", "id", "label"):
                nested = value.get(nested_key)
                if isinstance(nested, str):
                    candidates.append(nested)
    for candidate in candidates:
        priority = re.search(r"\bP([1-4])\b", candidate, flags=re.IGNORECASE)
        if priority:
            return f"P{priority.group(1)}"
        normalized = candidate.strip().lower()
        if normalized in {"high", "low"}:
            return normalized
    return None


def _extract_duration_minutes(item: dict[str, object]) -> float | None:
    for key, divisor in (
        ("duration_minutes", 1.0),
        ("duration_min", 1.0),
        ("duration", 60.0),
        ("duration_seconds", 60.0),
        ("seconds_to_resolve", 60.0),
        ("resolved_in_seconds", 60.0),
        ("duration_ms", 60000.0),
    ):
        value = item.get(key)
        if isinstance(value, (int, float)) and value >= 0:
            return round(float(value) / divisor, 2)
        if isinstance(value, str):
            parsed = _parse_duration_string(value, numeric_divisor=divisor)
            if parsed is not None:
                return parsed

    start = _first_string(item, "created_at", "createdAt", "started_at", "start_time")
    end = _first_string(item, "resolved_at", "resolvedAt", "ended_at", "end_time")
    if start and end:
        start_dt = _parse_datetime(start)
        end_dt = _parse_datetime(end)
        if start_dt and end_dt and end_dt >= start_dt:
            return round((end_dt - start_dt).total_seconds() / 60.0, 2)
    return None


def _parse_duration_string(value: str, *, numeric_divisor: float = 60.0) -> float | None:
    stripped = value.strip().lower()
    if not stripped:
        return None
    if re.fullmatch(r"\d+(?:\.\d+)?", stripped):
        return round(float(stripped) / numeric_divisor, 2)
    match = re.fullmatch(r"(?:(\d+(?:\.\d+)?)h)?\s*(?:(\d+(?:\.\d+)?)m)?\s*(?:(\d+(?:\.\d+)?)s)?", stripped)
    if match and any(match.groups()):
        hours = float(match.group(1) or 0)
        minutes = float(match.group(2) or 0)
        seconds = float(match.group(3) or 0)
        return round(hours * 60 + minutes + seconds / 60, 2)
    match = re.search(r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|m)\b", stripped)
    if match:
        return round(float(match.group(1)), 2)
    match = re.search(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h)\b", stripped)
    if match:
        return round(float(match.group(1)) * 60, 2)
    return None


def _parse_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _month_key(value: str) -> str | None:
    parsed = _parse_datetime(value)
    if parsed is None:
        match = re.match(r"^(\d{4}-\d{2})", value)
        return match.group(1) if match else None
    return f"{parsed.year:04d}-{parsed.month:02d}"


def _extract_body_summary(item: dict[str, object]) -> str:
    for key in ("body", "incident_body", "details", "summary", "description"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return _summarize(value, limit=500)
        if isinstance(value, dict):
            flattened = _flatten_json(value)
            if flattened:
                return _summarize(" ".join(flattened), limit=500)
    return ""


def _flatten_json(value: object, *, prefix: str = "") -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        lines: list[str] = []
        for key, nested in value.items():
            nested_prefix = f"{prefix}.{key}" if prefix else str(key)
            lines.extend(_flatten_json(nested, prefix=nested_prefix))
        return lines
    if isinstance(value, list):
        lines: list[str] = []
        for index, nested in enumerate(value):
            nested_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            lines.extend(_flatten_json(nested, prefix=nested_prefix))
        return lines
    if isinstance(value, (str, int, float, bool)):
        rendered = str(value).strip()
        return [f"{prefix}: {rendered}" if prefix and rendered else rendered] if rendered else []
    return []


def _pagerduty_metrics(incidents: Sequence[IncidentRecord]) -> PagerDutyMetrics:
    groups: dict[str, list[str]] = {"high": [], "low": []}
    durations_by_urgency: dict[str, list[float]] = defaultdict(list)
    month_counts: Counter[str] = Counter()
    cluster_counts: Counter[str] = Counter()

    for incident in incidents:
        group = _urgency_group(incident.urgency)
        if group:
            groups[group].append(incident.title)
        if incident.urgency and incident.duration_minutes is not None:
            durations_by_urgency[incident.urgency].append(incident.duration_minutes)
        if incident.created_month:
            month_counts[incident.created_month] += 1
        cluster = _cluster_title(incident.title)
        if cluster:
            cluster_counts[cluster] += 1

    mttr = {
        urgency: round(sum(values) / len(values), 2)
        for urgency, values in sorted(durations_by_urgency.items())
        if values
    }
    clusters = [f"{label} ({count} incidents)" for label, count in cluster_counts.most_common(5)]
    incidents_per_month = dict(sorted(month_counts.items()))
    patterns = [
        *(f"PagerDuty {urgency} mean time to resolve: {minutes:g} minutes" for urgency, minutes in mttr.items()),
        *(f"Common PagerDuty title cluster: {cluster}" for cluster in clusters),
        *(f"PagerDuty incidents in {month}: {count}" for month, count in incidents_per_month.items()),
    ]

    return PagerDutyMetrics(
        urgency_groups={key: _dedupe(value) for key, value in groups.items()},
        mean_time_to_resolve_minutes=mttr,
        common_title_clusters=clusters,
        incidents_per_month=incidents_per_month,
        patterns=patterns,
    )


def _merge_pagerduty_metrics(
    current: PagerDutyMetrics | None,
    incoming: PagerDutyMetrics | None,
) -> PagerDutyMetrics | None:
    if current is None:
        return incoming
    if incoming is None:
        return current
    groups = {
        "high": _dedupe([*current.urgency_groups.get("high", []), *incoming.urgency_groups.get("high", [])]),
        "low": _dedupe([*current.urgency_groups.get("low", []), *incoming.urgency_groups.get("low", [])]),
    }
    mttr = {**current.mean_time_to_resolve_minutes, **incoming.mean_time_to_resolve_minutes}
    month_counts = Counter(current.incidents_per_month)
    month_counts.update(incoming.incidents_per_month)
    clusters = _dedupe([*current.common_title_clusters, *incoming.common_title_clusters])
    patterns = _dedupe([*current.patterns, *incoming.patterns])
    return PagerDutyMetrics(groups, mttr, clusters, dict(sorted(month_counts.items())), patterns)


def _urgency_group(urgency: str | None) -> str | None:
    if urgency in {"P1", "P2", "high"}:
        return "high"
    if urgency in {"P3", "P4", "low"}:
        return "low"
    return None


def _cluster_title(title: str) -> str:
    stopwords = {
        "a",
        "an",
        "and",
        "api",
        "degraded",
        "degradation",
        "failure",
        "incident",
        "latency",
        "outage",
        "p1",
        "p2",
        "p3",
        "p4",
        "postmortem",
        "service",
        "sev1",
        "sev2",
        "the",
    }
    tokens = [
        token
        for token in re.findall(r"[a-z0-9]+", title.lower())
        if len(token) > 2 and token not in stopwords
    ]
    return " ".join(tokens[:3])


def _github_get_json(url: str, token: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "skilgen-incident-parser",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    last_error: Exception | None = None
    for attempt in range(GITHUB_RETRY_ATTEMPTS):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=GITHUB_TIMEOUT_SECONDS) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, JSONDecodeError) as exc:
            last_error = exc
            if attempt < GITHUB_RETRY_ATTEMPTS - 1:
                time.sleep(0.25 * (attempt + 1))
    raise IncidentParseError(f"Failed to fetch GitHub incident issues: {last_error}") from last_error


def _summarize(value: str, *, limit: int) -> str:
    normalized = " ".join(value.split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "..."


def _flatten(groups: Iterable[Iterable[str]]) -> list[str]:
    flattened: list[str] = []
    for group in groups:
        flattened.extend(group)
    return flattened


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        rendered = str(value).strip()
        if not rendered or rendered in seen:
            continue
        seen.add(rendered)
        unique.append(rendered)
    return unique


def _dedupe_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique
