from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AnalysisRun, OrgPolicy, Repo, Skill


POLICY_RULE_TYPES = {
    "require_skill_category",
    "max_skill_age_days",
    "min_skill_score",
    "min_freshness_score",
    "require_analysis_recency",
    "no_dead_skills",
    "min_coverage_score",
}

SKILL_CATEGORIES = [
    "codebase_architecture",
    "code_style",
    "testing_conventions",
    "internal_tools",
    "security_compliance",
    "design_system",
    "data_schema",
    "operational_knowledge",
]


@dataclass
class PolicyViolation:
    policy_id: str
    policy_name: str
    rule_type: str
    severity: str
    repo_id: str | None
    repo_name: str | None
    skill_id: str | None
    skill_domain: str | None
    description: str
    fix_url: str | None


async def evaluate_policies(
    org_id: str,
    db: AsyncSession,
    repo_ids: list[str] | None = None,
) -> list[PolicyViolation]:
    policies = await _load_enabled_policies(db, org_id)
    repos = await _load_repos(db, org_id, repo_ids)
    skills_by_repo = await _load_skills_by_repo(db, [repo.id for repo in repos])
    latest_runs = await _load_latest_runs(db, [repo.id for repo in repos])
    now = datetime.now(UTC).replace(tzinfo=None)

    violations: list[PolicyViolation] = []
    for policy in policies:
        cfg = policy.rule_config or {}
        for repo in repos:
            violations.extend(_evaluate_rule(policy, cfg, repo, skills_by_repo.get(repo.id, []), latest_runs.get(repo.id), now))
    return sorted(violations, key=lambda v: (0 if v.severity == "error" else 1, v.repo_name or "", v.skill_domain or ""))


async def _load_enabled_policies(db: AsyncSession, org_id: str) -> list[OrgPolicy]:
    return (
        await db.execute(select(OrgPolicy).where(OrgPolicy.org_id == org_id, OrgPolicy.enabled.is_(True)))
    ).scalars().all()


async def _load_repos(db: AsyncSession, org_id: str, repo_ids: list[str] | None) -> list[Repo]:
    filters = [Repo.org_id == org_id, Repo.is_active.is_(True)]
    if repo_ids:
        filters.append(Repo.id.in_(repo_ids))
    return (await db.execute(select(Repo).where(*filters).order_by(Repo.name))).scalars().all()


async def _load_skills_by_repo(db: AsyncSession, repo_ids: list[str]) -> dict[str, list[Skill]]:
    if not repo_ids:
        return {}
    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all()
    grouped: dict[str, list[Skill]] = {repo_id: [] for repo_id in repo_ids}
    for skill in skills:
        grouped.setdefault(skill.repo_id, []).append(skill)
    return grouped


async def _load_latest_runs(db: AsyncSession, repo_ids: list[str]) -> dict[str, AnalysisRun]:
    latest: dict[str, AnalysisRun] = {}
    if not repo_ids:
        return latest
    runs = (
        await db.execute(select(AnalysisRun).where(AnalysisRun.repo_id.in_(repo_ids)).order_by(AnalysisRun.repo_id, desc(AnalysisRun.created_at)))
    ).scalars().all()
    for run in runs:
        latest.setdefault(run.repo_id, run)
    return latest


def _violation(policy: OrgPolicy, repo: Repo, description: str, *, skill: Skill | None = None) -> PolicyViolation:
    return PolicyViolation(
        policy_id=policy.id,
        policy_name=policy.name,
        rule_type=policy.rule_type,
        severity=policy.severity,
        repo_id=repo.id,
        repo_name=repo.name,
        skill_id=skill.id if skill else None,
        skill_domain=skill.domain if skill else None,
        description=description,
        fix_url=f"/dashboard/repos/{repo.id}/skills/{skill.id}" if skill else f"/dashboard/repos/{repo.id}",
    )


def _skill_age_days(skill: Skill, now: datetime) -> int:
    updated = getattr(skill, "updated_at", None) or skill.created_at
    if updated is None:
        return 0
    if updated.tzinfo is not None:
        updated = updated.astimezone(UTC).replace(tzinfo=None)
    return max(0, (now - updated).days)


def _evaluate_rule(policy: OrgPolicy, cfg: dict[str, object], repo: Repo, skills: list[Skill], latest_run: AnalysisRun | None, now: datetime) -> list[PolicyViolation]:
    rule = policy.rule_type
    violations: list[PolicyViolation] = []

    if rule == "require_skill_category":
        cat = str(cfg.get("category") or "security_compliance")
        has = any((skill.skill_category or "") == cat for skill in skills)
        if not has:
            violations.append(_violation(policy, repo, f"{repo.name} has no {cat.replace('_', ' ')} skill"))

    elif rule == "max_skill_age_days":
        max_days = int(cfg.get("max_days") or 30)
        for skill in skills:
            age = _skill_age_days(skill, now)
            if age > max_days:
                violations.append(_violation(policy, repo, f"{repo.name}/{skill.domain} is {age}d old (max {max_days}d)", skill=skill))

    elif rule == "min_skill_score":
        min_score = int(cfg.get("min_score") or 50)
        cat_filter = cfg.get("category")
        for skill in skills:
            if cat_filter and (skill.skill_category or "") != str(cat_filter):
                continue
            score = int(skill.score_total or 0)
            if score < min_score:
                violations.append(_violation(policy, repo, f"{repo.name}/{skill.domain} score {score}/100 < {min_score}", skill=skill))

    elif rule == "min_freshness_score":
        min_freshness = int(cfg.get("min_freshness") or 15)
        for skill in skills:
            freshness = int(skill.score_freshness or 0)
            if freshness < min_freshness:
                violations.append(_violation(policy, repo, f"{repo.name}/{skill.domain} freshness {freshness}/25 < {min_freshness}", skill=skill))

    elif rule == "require_analysis_recency":
        max_days = int(cfg.get("max_days") or 30)
        analysed_at = (latest_run.completed_at or latest_run.created_at) if latest_run else repo.last_analysed_at
        stale = analysed_at is None
        if analysed_at is not None:
            if analysed_at.tzinfo is not None:
                analysed_at = analysed_at.astimezone(UTC).replace(tzinfo=None)
            stale = analysed_at < (now - timedelta(days=max_days))
        if stale:
            violations.append(_violation(policy, repo, f"{repo.name} has no analysis run in the last {max_days}d"))

    elif rule == "no_dead_skills":
        grace = int(cfg.get("grace_period_days") or 30)
        cutoff = now - timedelta(days=grace)
        for skill in skills:
            loaded = skill.last_loaded_at
            if loaded is not None and loaded.tzinfo is not None:
                loaded = loaded.astimezone(UTC).replace(tzinfo=None)
            never_loaded = loaded is None or loaded < cutoff
            if int(skill.load_count_30d or 0) == 0 and never_loaded:
                violations.append(_violation(policy, repo, f"{repo.name}/{skill.domain} has no agent loads after {grace}d", skill=skill))

    elif rule == "min_coverage_score":
        min_coverage = int(cfg.get("min_coverage") or 70)
        covered = {(skill.skill_category or "") for skill in skills if skill.skill_category in SKILL_CATEGORIES}
        coverage_score = round((len(covered) / len(SKILL_CATEGORIES)) * 100) if SKILL_CATEGORIES else 0
        if coverage_score < min_coverage:
            violations.append(_violation(policy, repo, f"{repo.name} coverage score {coverage_score}/100 < {min_coverage}"))

    return violations
