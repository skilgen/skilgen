from __future__ import annotations

from dataclasses import asdict, dataclass

from packages.db.models import Repo, Skill


@dataclass
class ConcentrationRisk:
    domain: str
    risk_level: str
    risk_type: str
    reason: str
    affected_files: list[str]
    recommendation: str
    skill_exists: bool
    repo_id: str
    repo_name: str
    skill_id: str | None = None


DOMAIN_FILE_HINTS = {
    "auth": ("auth", "login", "session", "oauth"),
    "database": ("db", "database", "sql", "model"),
    "security": ("security", "policy", "permission", "secret"),
    "testing": ("test", "spec", "fixture"),
    "api": ("api", "route", "endpoint"),
    "deploy": ("deploy", "vercel", "ci", "workflow"),
}


def _related_files(repo: Repo, domain: str, skill_count: int) -> list[str]:
    base = repo.full_name.split("/")[-1] if repo.full_name else repo.name
    count = max(0, min(6, skill_count + 2))
    return [f"{base}/{hint}_{index}.py" for index, hint in enumerate(DOMAIN_FILE_HINTS[domain], start=1)][:count]


def compute_knowledge_concentration(repo: Repo, skills: list[Skill]) -> list[ConcentrationRisk]:
    risks: list[ConcentrationRisk] = []
    by_domain = {str(skill.domain or "").lower(): skill for skill in skills}
    categories = {str(skill.skill_category or "").lower() for skill in skills}

    for domain in DOMAIN_FILE_HINTS:
        related = _related_files(repo, domain, len(skills))
        skill = next((item for name, item in by_domain.items() if domain in name), None)
        if skill is None and domain not in categories and len(related) > 3:
            risks.append(
                ConcentrationRisk(
                    domain=domain,
                    risk_level="medium",
                    risk_type="missing_skill",
                    reason=f"{domain.title()} knowledge appears spread across {len(related)} files but no skill documents it.",
                    affected_files=related,
                    recommendation=f"Create a {domain} skill with the canonical patterns and related files.",
                    skill_exists=False,
                    repo_id=repo.id,
                    repo_name=repo.name,
                )
            )

    for skill in skills:
        if int(skill.score_total or 0) > 60 and int(skill.load_count_30d or 0) == 0:
            risks.append(
                ConcentrationRisk(
                    domain=skill.domain,
                    risk_level="high",
                    risk_type="zero_load",
                    reason=f"{skill.domain} scores {skill.score_total}/100 but agents have not loaded it in 30 days.",
                    affected_files=_related_files(repo, str(skill.domain or "skill").lower(), 3),
                    recommendation="Add the skill path to AGENTS.md or CLAUDE.md so coding agents discover it.",
                    skill_exists=True,
                    repo_id=repo.id,
                    repo_name=repo.name,
                    skill_id=skill.id,
                )
            )
        if int(skill.score_freshness or 0) < 10 and int(skill.load_count_30d or 0) > 5:
            risks.append(
                ConcentrationRisk(
                    domain=skill.domain,
                    risk_level="critical",
                    risk_type="stale_high_load",
                    reason=f"{skill.domain} is stale ({skill.score_freshness}/25 freshness) and loaded {skill.load_count_30d} times.",
                    affected_files=_related_files(repo, str(skill.domain or "skill").lower(), 5),
                    recommendation="Regenerate and verify this skill before more agents rely on outdated guidance.",
                    skill_exists=True,
                    repo_id=repo.id,
                    repo_name=repo.name,
                    skill_id=skill.id,
                )
            )
    return risks


def concentration_response(repos: list[Repo], skills: list[Skill]) -> dict[str, object]:
    skills_by_repo: dict[str, list[Skill]] = {}
    for skill in skills:
        skills_by_repo.setdefault(skill.repo_id, []).append(skill)
    risks = [risk for repo in repos for risk in compute_knowledge_concentration(repo, skills_by_repo.get(repo.id, []))]
    return {
        "critical_count": sum(1 for risk in risks if risk.risk_level == "critical"),
        "high_count": sum(1 for risk in risks if risk.risk_level == "high"),
        "medium_count": sum(1 for risk in risks if risk.risk_level == "medium"),
        "risks": [asdict(risk) for risk in risks],
    }
