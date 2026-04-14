from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
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


def _normalize_skill_path(project_root: str | Path, skill_path: str) -> str:
    raw = skill_path.strip()
    if not raw:
        return raw
    if raw.startswith("external::"):
        return raw
    root = Path(project_root).resolve()
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(root).as_posix()
        except ValueError:
            return candidate.as_posix()
    return raw.removeprefix("./").replace("\\", "/")


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
    if not summary.strip() or summary.strip() == "---":
        summary = f"{title} guidance grounded in repo evidence and reusable implementation nuance."
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
    session_id: str | None = None,
    task: str | None = None,
) -> None:
    if not skill_paths:
        return
    path = _analytics_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    agent_name = agent or os.getenv("SKILGEN_AGENT_NAME") or "skilgen"
    session = session_id or os.getenv("SKILGEN_SESSION_ID")
    task_name = task or os.getenv("SKILGEN_TASK_NAME")
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    for skill_path in skill_paths:
        normalized_skill = _normalize_skill_path(project_root, skill_path)
        existing.append(
            json.dumps(
                {
                    "timestamp": _timestamp(),
                    "skill": normalized_skill,
                    "event": event,
                    "agent": agent_name,
                    "context": context,
                    "session_id": session,
                    "task": task_name,
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
    live_counts = Counter(str(event.get("skill", "")) for event in live_events if event.get("skill"))
    planner_counts = Counter(str(event.get("skill", "")) for event in planner_events if event.get("skill"))
    agents_by_skill: dict[str, set[str]] = defaultdict(set)
    contexts_by_skill: dict[str, set[str]] = defaultdict(set)
    sessions_by_skill: dict[str, set[str]] = defaultdict(set)
    last_loaded_at: dict[str, str] = {}
    for event in live_events:
        skill = str(event.get("skill", "")).strip()
        if not skill:
            continue
        agent = str(event.get("agent", "")).strip()
        context = str(event.get("context", "")).strip()
        session_id = str(event.get("session_id", "")).strip()
        timestamp = str(event.get("timestamp", "")).strip()
        if agent:
            agents_by_skill[skill].add(agent)
        if context:
            contexts_by_skill[skill].add(context)
        if session_id:
            sessions_by_skill[skill].add(session_id)
        if timestamp and timestamp > last_loaded_at.get(skill, ""):
            last_loaded_at[skill] = timestamp
    skill_usage: list[dict[str, object]] = []
    repo_skill_files = _iter_repo_skill_files(project_root)
    for skill_path in repo_skill_files:
        rel = skill_path.relative_to(Path(project_root).resolve()).as_posix()
        title, summary = _skill_title_and_summary(skill_path)
        metrics = _skill_content_metrics(skill_path)
        loads = live_counts.get(rel, 0)
        planner_loads = planner_counts.get(rel, 0)
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
                "live_loads": loads,
                "planner_loads": planner_loads,
                "depth": depth,
                "richness": richness,
                "metrics": metrics,
                "modeled_loads": modeled_loads,
                "agents": sorted(agents_by_skill.get(rel, set())),
                "contexts": sorted(contexts_by_skill.get(rel, set())),
                "session_count": len(sessions_by_skill.get(rel, set())),
                "last_loaded_at": last_loaded_at.get(rel),
                "kind": "repo",
            }
        )
    for external in active_external_skills(project_root):
        slug = str(external.get("slug", "external-skill"))
        key = f"external::{slug}"
        loads = live_counts.get(key, live_counts.get(slug, 0))
        planner_loads = planner_counts.get(key, planner_counts.get(slug, 0))
        metrics = {"headings": 0, "bullets": 0, "references": 0, "words": 0}
        skill_usage.append(
            {
                "skill": key,
                "title": slug,
                "summary": str(external.get("summary") or "Installed external skill pack available to the repo."),
                "family": "external",
                "loads": loads,
                "live_loads": loads,
                "planner_loads": planner_loads,
                "depth": 1,
                "richness": 2,
                "metrics": metrics,
                "modeled_loads": _modeled_attention_score(depth=1, richness=2, metrics=metrics, kind="external"),
                "agents": sorted(agents_by_skill.get(key, set())),
                "contexts": sorted(contexts_by_skill.get(key, set())),
                "session_count": len(sessions_by_skill.get(key, set())),
                "last_loaded_at": last_loaded_at.get(key),
                "kind": "external",
            }
        )
    usage_mode = "live" if live_events else "modeled"
    for item in skill_usage:
        effective_loads = int(item["live_loads"]) if usage_mode == "live" else int(item["modeled_loads"])
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
        "traced_agents": sorted({str(event.get("agent", "")).strip() for event in live_events if str(event.get("agent", "")).strip()}),
        "traced_contexts": sorted({str(event.get("context", "")).strip() for event in live_events if str(event.get("context", "")).strip()}),
        "traced_session_count": len({str(event.get("session_id", "")).strip() for event in live_events if str(event.get("session_id", "")).strip()}),
        "skill_usage": skill_usage,
    }
