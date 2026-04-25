from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from packages.db.models import Repo, Skill

RedFlagType = Literal["stale_but_active", "dead_high_quality", "conflict", "missing_security", "freshness_critical"]


@dataclass
class RedFlag:
    flag_type: RedFlagType
    severity: Literal["critical", "high", "medium"]
    repo_id: str
    repo_name: str
    skill_id: str | None
    domain: str | None
    title: str
    description: str
    loads_30d: int
    action: str
    action_url: str | None


_CONFLICT_PAIRS = [
    (["never use raw sql", "no raw sql", "avoid raw sql"], ["use raw sql", "raw sql is fine", "raw sql for performance"]),
    (["always use transactions", "wrap in transaction"], ["avoid transactions", "no transactions needed"]),
    (["use snake_case", "snake_case naming"], ["use camelCase", "camelCase naming"]),
    (["never store secrets in env", "no env secrets"], ["store in .env", "use .env file"]),
    (["use async functions", "always async"], ["use synchronous", "avoid async here"]),
]


def compute_repo_red_flags(repo: Repo, skills: list[Skill]) -> list[RedFlag]:
    flags: list[RedFlag] = []
    now = datetime.now(UTC).replace(tzinfo=None)

    for skill in skills:
        freshness = int(skill.score_freshness or 0)
        loads = int(skill.load_count_30d or 0)
        score = int(skill.score_total or 0)
        if freshness < 20 and loads > 10:
            flags.append(
                RedFlag(
                    flag_type="stale_but_active",
                    severity="critical",
                    repo_id=str(repo.id),
                    repo_name=str(repo.name),
                    skill_id=str(skill.id),
                    domain=str(skill.domain),
                    title=f"{skill.domain} is stale and active",
                    description=f"Freshness {freshness}/25 — agents loaded this skill {loads}x in the last 30 days. They are acting on outdated context right now.",
                    loads_30d=loads,
                    action="Re-analyse this domain to refresh the skill",
                    action_url=f"/dashboard/repos/{repo.id}/skills/{skill.id}",
                )
            )
        if freshness == 0 and loads > 0:
            flags.append(
                RedFlag(
                    flag_type="freshness_critical",
                    severity="critical",
                    repo_id=str(repo.id),
                    repo_name=str(repo.name),
                    skill_id=str(skill.id),
                    domain=str(skill.domain),
                    title=f"{skill.domain} has zero freshness",
                    description=f"Freshness score is 0/25 — no recency signals at all. Loaded {loads}x this month.",
                    loads_30d=loads,
                    action="Edit this skill to add version references and re-analyse",
                    action_url=f"/dashboard/repos/{repo.id}/skills/{skill.id}",
                )
            )
        last_loaded_at = skill.last_loaded_at.replace(tzinfo=None) if skill.last_loaded_at and skill.last_loaded_at.tzinfo else skill.last_loaded_at
        never_loaded = (last_loaded_at is None or (now - last_loaded_at).days > 30) and loads == 0
        if never_loaded and score > 70:
            flags.append(
                RedFlag(
                    flag_type="dead_high_quality",
                    severity="medium",
                    repo_id=str(repo.id),
                    repo_name=str(repo.name),
                    skill_id=str(skill.id),
                    domain=str(skill.domain),
                    title=f"{skill.domain} is high-quality but never loaded",
                    description=f"Score {score}/100 — excellent quality but zero agent loads in 30d. Agents may not be discovering this skill.",
                    loads_30d=0,
                    action="Check your CLAUDE.md or agent config references this skill path",
                    action_url=f"/dashboard/repos/{repo.id}/skills/{skill.id}",
                )
            )

    has_security = any((skill.skill_category or "") == "security_compliance" for skill in skills)
    if not has_security and skills:
        flags.append(
            RedFlag(
                flag_type="missing_security",
                severity="high",
                repo_id=str(repo.id),
                repo_name=str(repo.name),
                skill_id=None,
                domain=None,
                title=f"{repo.name} has no security skill",
                description="No security_compliance skill exists for this repo. Agents have no context about approved libraries, forbidden patterns, or PII rules.",
                loads_30d=0,
                action="Run skilgen analyse to generate security skills from SAST/policy files",
                action_url=f"/dashboard/repos/{repo.id}",
            )
        )
    flags.extend(_detect_conflicts(repo, skills))
    return sorted(flags, key=lambda flag: (0 if flag.severity == "critical" else 1 if flag.severity == "high" else 2))


def _detect_conflicts(repo: Repo, skills: list[Skill]) -> list[RedFlag]:
    if len(skills) > 200:
        return []
    flags: list[RedFlag] = []
    contents = [(skill, (skill.content or "").lower()) for skill in skills if skill.content]
    for pair_a, pair_b in _CONFLICT_PAIRS:
        skills_a = [skill for skill, content in contents if any(keyword in content for keyword in pair_a)]
        skills_b = [skill for skill, content in contents if any(keyword in content for keyword in pair_b)]
        for skill_a in skills_a:
            for skill_b in skills_b:
                if skill_a.id == skill_b.id:
                    continue
                flags.append(
                    RedFlag(
                        flag_type="conflict",
                        severity="high",
                        repo_id=str(repo.id),
                        repo_name=str(repo.name),
                        skill_id=str(skill_a.id),
                        domain=str(skill_a.domain),
                        title=f"Conflict: {skill_a.domain} vs {skill_b.domain}",
                        description=f"Skills '{skill_a.domain}' and '{skill_b.domain}' contain contradicting instructions. Agents loading both will produce inconsistent code.",
                        loads_30d=int(skill_a.load_count_30d or 0) + int(skill_b.load_count_30d or 0),
                        action=f"Review and reconcile '{skill_a.domain}' and '{skill_b.domain}' skills",
                        action_url=f"/dashboard/repos/{repo.id}/skills/{skill_a.id}",
                    )
                )
    return flags
