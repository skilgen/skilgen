from __future__ import annotations

import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import re

from skilgen.external_skills import active_external_skills


def _analytics_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "analytics" / "usage.jsonl"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _iter_repo_skill_files(project_root: str | Path) -> list[Path]:
    root = Path(project_root).resolve() / "skills"
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("SKILL.md") if path.is_file())


def _skill_title_and_summary(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines()]
    title = path.parent.name.replace("-", " ").replace("_", " ").title()
    summary = "No summary captured yet."
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("#").strip() or title
            continue
        if line:
            summary = line
            break
    return title, summary


def _skill_content_metrics(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = sum(1 for line in lines if line.strip().startswith("#"))
    bullets = sum(1 for line in lines if line.strip().startswith(("- ", "* ")))
    references = text.count("`")
    words = len(re.findall(r"\w+", text))
    return {
        "headings": headings,
        "bullets": bullets,
        "references": references,
        "words": words,
    }


def log_skill_usage(
    project_root: str | Path,
    skill_paths: list[str],
    *,
    event: str = "loaded",
    agent: str | None = None,
    context: str = "skilgen",
) -> None:
    if not skill_paths:
        return
    path = _analytics_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    agent_name = agent or os.getenv("SKILGEN_AGENT_NAME") or "skilgen"
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    for skill_path in skill_paths:
        existing.append(
            json.dumps(
                {
                    "timestamp": _timestamp(),
                    "skill": skill_path,
                    "event": event,
                    "agent": agent_name,
                    "context": context,
                }
            )
        )
    path.write_text("\n".join(existing[-2000:]) + "\n", encoding="utf-8")


def analytics_summary(project_root: str | Path, *, limit: int = 10) -> dict[str, object]:
    path = _analytics_path(project_root)
    events: list[dict[str, object]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    counts = Counter(str(event.get("skill", "")) for event in events if event.get("skill"))
    top_skills = [{"skill": skill, "loads": count} for skill, count in counts.most_common(limit)]
    least_used = [{"skill": skill, "loads": count} for skill, count in sorted(counts.items(), key=lambda item: (item[1], item[0]))[:limit]]
    skill_usage: list[dict[str, object]] = []
    repo_skill_files = _iter_repo_skill_files(project_root)
    max_load = max(counts.values(), default=1)
    for skill_path in repo_skill_files:
        rel = skill_path.relative_to(Path(project_root).resolve()).as_posix()
        title, summary = _skill_title_and_summary(skill_path)
        metrics = _skill_content_metrics(skill_path)
        loads = counts.get(rel, 0)
        parts = Path(rel).parts
        family = parts[1] if len(parts) > 2 else "other"
        depth = max(1, len(parts) - 2)
        richness = metrics["headings"] + metrics["bullets"] + max(1, metrics["references"] // 4)
        skill_usage.append(
            {
                "skill": rel,
                "title": title,
                "summary": summary,
                "family": family,
                "loads": loads,
                "load_share": round(loads / max_load, 3) if max_load else 0.0,
                "depth": depth,
                "richness": richness,
                "metrics": metrics,
                "kind": "repo",
            }
        )
    for external in active_external_skills(project_root):
        slug = str(external.get("slug", "external-skill"))
        key = f"external::{slug}"
        loads = counts.get(key, counts.get(slug, 0))
        skill_usage.append(
            {
                "skill": key,
                "title": slug,
                "summary": str(external.get("summary") or "Installed external skill pack available to the repo."),
                "family": "external",
                "loads": loads,
                "load_share": round(loads / max_load, 3) if max_load else 0.0,
                "depth": 1,
                "richness": 2,
                "metrics": {"headings": 0, "bullets": 0, "references": 0, "words": 0},
                "kind": "external",
            }
        )
    skill_usage.sort(key=lambda item: (-int(item["loads"]), -int(item["richness"]), str(item["skill"])))
    return {
        "events": events[-limit:],
        "top_skills": top_skills,
        "least_used": least_used,
        "event_count": len(events),
        "skill_usage": skill_usage,
    }
