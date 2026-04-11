from __future__ import annotations

import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


def _analytics_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "analytics" / "usage.jsonl"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


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
    if not path.exists():
        return {"events": [], "top_skills": [], "least_used": []}
    events: list[dict[str, object]] = []
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
    return {
        "events": events[-limit:],
        "top_skills": top_skills,
        "least_used": least_used,
        "event_count": len(events),
    }
