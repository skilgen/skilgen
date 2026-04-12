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
    in_frontmatter = False
    generic_titles = {"overview", "summary", "skill"}
    for line in lines:
        if line == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if line.startswith("#"):
            candidate = line.lstrip("#").strip()
            if candidate and candidate.lower() not in generic_titles:
                title = candidate
            continue
        if line and line not in {"```", "~~~"} and not line.startswith(("references:", "inputs:", "outputs:")):
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


def _modeled_attention_score(*, depth: int, richness: int, metrics: dict[str, int], kind: str) -> int:
    base = 35 if kind == "repo" else 16
    score = (
        base
        + depth * 18
        + richness * 4
        + int(metrics.get("headings", 0)) * 6
        + int(metrics.get("bullets", 0)) * 2
        + max(0, int(metrics.get("references", 0)) // 2)
        + max(0, int(metrics.get("words", 0)) // 18)
    )
    if kind == "external":
        score = max(12, score // 3)
    return score


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
    live_events = [event for event in events if str(event.get("context", "")) != "decision_planner"]
    planner_events = [event for event in events if str(event.get("context", "")) == "decision_planner"]
    counts = Counter(str(event.get("skill", "")) for event in live_events if event.get("skill"))
    skill_usage: list[dict[str, object]] = []
    repo_skill_files = _iter_repo_skill_files(project_root)
    for skill_path in repo_skill_files:
        rel = skill_path.relative_to(Path(project_root).resolve()).as_posix()
        title, summary = _skill_title_and_summary(skill_path)
        metrics = _skill_content_metrics(skill_path)
        loads = counts.get(rel, 0)
        parts = Path(rel).parts
        family = parts[1] if len(parts) > 2 else "other"
        depth = max(1, len(parts) - 2)
        richness = metrics["headings"] + metrics["bullets"] + max(1, metrics["references"] // 4)
        modeled_loads = _modeled_attention_score(depth=depth, richness=richness, metrics=metrics, kind="repo")
        skill_usage.append(
            {
                "skill": rel,
                "title": title,
                "summary": summary,
                "family": family,
                "loads": loads,
                "depth": depth,
                "richness": richness,
                "metrics": metrics,
                "modeled_loads": modeled_loads,
                "kind": "repo",
            }
        )
    for external in active_external_skills(project_root):
        slug = str(external.get("slug", "external-skill"))
        key = f"external::{slug}"
        loads = counts.get(key, counts.get(slug, 0))
        metrics = {"headings": 0, "bullets": 0, "references": 0, "words": 0}
        skill_usage.append(
            {
                "skill": key,
                "title": slug,
                "summary": str(external.get("summary") or "Installed external skill pack available to the repo."),
                "family": "external",
                "loads": loads,
                "depth": 1,
                "richness": 2,
                "metrics": metrics,
                "modeled_loads": _modeled_attention_score(depth=1, richness=2, metrics=metrics, kind="external"),
                "kind": "external",
            }
        )
    live_loads = [int(item["loads"]) for item in skill_usage]
    non_zero_live = [value for value in live_loads if value > 0]
    live_mode = bool(non_zero_live) and (max(non_zero_live) - min(non_zero_live) > 1 or len(set(non_zero_live)) > 1)
    usage_mode = "live" if live_mode else "modeled"
    for item in skill_usage:
        effective_loads = int(item["loads"]) if usage_mode == "live" else int(item["modeled_loads"])
        item["effective_loads"] = effective_loads
    max_effective = max((int(item["effective_loads"]) for item in skill_usage), default=1)
    for item in skill_usage:
        item["load_share"] = round(int(item["effective_loads"]) / max_effective, 3) if max_effective else 0.0
        item["usage_label"] = "Live usage" if usage_mode == "live" else "Modeled attention"
    skill_usage.sort(key=lambda item: (-int(item["effective_loads"]), -int(item["richness"]), str(item["skill"])))
    top_skills = [
        {"skill": str(item["skill"]), "loads": int(item["effective_loads"]), "mode": usage_mode, "title": str(item["title"])}
        for item in skill_usage[:limit]
    ]
    least_used = [
        {"skill": str(item["skill"]), "loads": int(item["effective_loads"]), "mode": usage_mode, "title": str(item["title"])}
        for item in sorted(skill_usage, key=lambda item: (int(item["effective_loads"]), int(item["richness"]), str(item["skill"])))[:limit]
    ]
    return {
        "events": events[-limit:],
        "live_events": live_events[-limit:],
        "top_skills": top_skills,
        "least_used": least_used,
        "event_count": len(events),
        "live_event_count": len(live_events),
        "planner_event_count": len(planner_events),
        "usage_mode": usage_mode,
        "skill_usage": skill_usage,
    }
