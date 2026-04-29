from __future__ import annotations

import re
from collections import defaultdict
from itertools import combinations

from packages.db.models import Repo, Skill


def extract_file_references(content: str | None) -> list[str]:
    if not content:
        return []
    section = content
    match = re.search(r"^##\s+File references\s*$", content, flags=re.IGNORECASE | re.MULTILINE)
    if match:
        tail = content[match.end():]
        next_heading = re.search(r"^##\s+", tail, flags=re.MULTILINE)
        section = tail[: next_heading.start()] if next_heading else tail
    refs: list[str] = []
    for line in section.splitlines():
        stripped = line.strip().lstrip("-* ").strip().strip("`")
        token = stripped.split()[0].strip("`,") if stripped.split() else ""
        if "/" in token and "." in token and token not in refs:
            refs.append(token)
    return refs[:50]


def _skill_status(skill: Skill) -> str:
    if int(skill.load_count_30d or 0) == 0:
        return "never_loaded"
    if bool(skill.is_stale) or int(skill.score_freshness or 0) < 10:
        return "stale"
    if int(skill.score_total or 0) < 50:
        return "low_score"
    return "healthy"


def compute_repo_dependencies(repo: Repo, skills: list[Skill]) -> dict[str, list[dict]]:
    nodes = [
        {
            "id": skill.id,
            "label": skill.domain,
            "path": skill.skill_path,
            "score": int(skill.score_total or 0),
            "load_count": int(skill.load_count_30d or 0),
            "status": _skill_status(skill),
            "type": "skill",
        }
        for skill in skills
    ]
    refs_by_skill = {skill.id: extract_file_references(skill.content) for skill in skills}
    edges: list[dict] = []
    for left, right in combinations(skills, 2):
        shared = sorted(set(refs_by_skill.get(left.id, [])) & set(refs_by_skill.get(right.id, [])))
        if shared:
            edges.append({"source": left.id, "target": right.id, "weight": len(shared), "shared_files": shared[:8], "relationship": "shared_files"})
        elif left.domain.lower() in (right.content or "").lower() or right.domain.lower() in (left.content or "").lower():
            edges.append({"source": left.id, "target": right.id, "weight": 1, "shared_files": [], "relationship": "explicit_reference"})
    return {"nodes": nodes, "edges": edges}


def compute_cross_repo_dependencies(repos: list[Repo], skills: list[Skill]) -> dict[str, list[dict]]:
    repo_by_id = {repo.id: repo for repo in repos}
    nodes = [
        {
            "id": skill.id,
            "label": skill.domain,
            "repo_id": skill.repo_id,
            "repo_name": repo_by_id.get(skill.repo_id).name if repo_by_id.get(skill.repo_id) else "Repo",
            "score": int(skill.score_total or 0),
            "load_count": int(skill.load_count_30d or 0),
            "status": _skill_status(skill),
        }
        for skill in skills
    ]
    edges: list[dict] = []
    for left, right in combinations(skills, 2):
        if left.repo_id == right.repo_id:
            continue
        if left.domain == right.domain:
            edges.append({"source": left.id, "target": right.id, "weight": 1, "relationship": "same_domain", "shared_domain": left.domain})
        elif (repo_by_id.get(left.repo_id) and repo_by_id[left.repo_id].name.lower() in (right.content or "").lower()) or (repo_by_id.get(right.repo_id) and repo_by_id[right.repo_id].name.lower() in (left.content or "").lower()):
            edges.append({"source": left.id, "target": right.id, "weight": 1, "relationship": "package_dependency", "shared_domain": None})
    domains_by_repo: dict[str, set[str]] = defaultdict(set)
    best_by_domain: dict[str, Skill] = {}
    for skill in skills:
        domains_by_repo[skill.repo_id].add(skill.domain)
        current = best_by_domain.get(skill.domain)
        if current is None or int(skill.score_total or 0) > int(current.score_total or 0):
            best_by_domain[skill.domain] = skill
    opportunities: list[dict] = []
    for repo in repos:
        for domain, source_skill in best_by_domain.items():
            if source_skill.repo_id != repo.id and domain not in domains_by_repo.get(repo.id, set()):
                source_repo = repo_by_id.get(source_skill.repo_id)
                opportunities.append(
                    {
                        "missing_in_repo": repo.name,
                        "missing_in_repo_id": repo.id,
                        "available_from_repo": source_repo.name if source_repo else "another repo",
                        "source_skill_id": source_skill.id,
                        "domain": domain,
                        "recommendation": f"{source_repo.name if source_repo else 'Another repo'} has a {domain} skill that {repo.name} is missing. Generate an adapted skill.",
                    }
                )
    return {"nodes": nodes, "edges": edges, "opportunities": opportunities[:50]}
