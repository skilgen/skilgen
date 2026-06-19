from __future__ import annotations

from types import SimpleNamespace

from apps.api.api.services.dependency_analyzer import compute_cross_repo_dependencies, compute_repo_dependencies, extract_file_references


def _repo(repo_id: str, name: str):
    return SimpleNamespace(id=repo_id, name=name)


def _skill(
    skill_id: str,
    repo_id: str,
    domain: str,
    content: str,
    score: int = 80,
    loads: int = 3,
    stale: bool = False,
):
    return SimpleNamespace(
        id=skill_id,
        repo_id=repo_id,
        domain=domain,
        skill_path=f".skillayer/skills/{domain}/SKILL.md",
        content=content,
        score_total=score,
        load_count_30d=loads,
        score_freshness=20,
        is_stale=stale,
    )


def test_extract_file_references_from_section() -> None:
    content = """# auth
## File references
- `src/auth/login.py`
- src/auth/session.py - session helpers

## Anti-patterns
- Do not store tokens in localStorage
"""
    assert extract_file_references(content) == ["src/auth/login.py", "src/auth/session.py"]


def test_compute_repo_dependencies_shared_files() -> None:
    repo = _repo("repo-1", "skilgen")
    skills = [
        _skill("skill-auth", repo.id, "auth", "## File references\n- src/auth/login.py\n- src/auth/session.py"),
        _skill("skill-security", repo.id, "security", "## File references\n- src/auth/login.py\n- src/security/policy.py"),
    ]

    graph = compute_repo_dependencies(repo, skills)

    assert len(graph["nodes"]) == 2
    assert graph["edges"] == [
        {
            "source": "skill-auth",
            "target": "skill-security",
            "weight": 1,
            "shared_files": ["src/auth/login.py"],
            "relationship": "shared_files",
        }
    ]


def test_compute_cross_repo_opportunities_for_missing_domain() -> None:
    repos = [_repo("repo-a", "payments"), _repo("repo-b", "checkout")]
    skills = [
        _skill("skill-a-auth", "repo-a", "auth", "## File references\n- src/auth/login.py", score=90),
        _skill("skill-b-testing", "repo-b", "testing", "## File references\n- tests/test_checkout.py", score=70),
    ]

    graph = compute_cross_repo_dependencies(repos, skills)

    assert any(edge["relationship"] == "same_domain" for edge in graph["edges"]) is False
    assert any(
        opportunity["missing_in_repo"] == "checkout" and opportunity["domain"] == "auth"
        for opportunity in graph["opportunities"]
    )
