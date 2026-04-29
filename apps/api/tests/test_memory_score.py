from __future__ import annotations

from types import SimpleNamespace

from apps.api.api.routes.orgs import build_memory_score_response, _memory_grade


def _repo(repo_id: str):
    return SimpleNamespace(id=repo_id)


def _skill(repo_id: str, category: str, score: int, freshness: int, loads: int = 0):
    return SimpleNamespace(
        repo_id=repo_id,
        skill_category=category,
        source_type="code",
        score_total=score,
        score_freshness=freshness,
        load_count_30d=loads,
    )


def test_memory_score_zero() -> None:
    response = build_memory_score_response([_repo("repo_1")], [], 0)

    assert response.score == 0
    assert response.grade == "F"
    assert response.breakdown.coverage == 0
    assert response.breakdown.load_frequency == 0


def test_memory_score_full() -> None:
    categories = [
        "codebase_architecture",
        "code_style",
        "testing_conventions",
        "internal_tools",
        "security_compliance",
        "design_system",
        "data_schema",
        "operational_knowledge",
    ]
    skills = [_skill("repo_1", category, 100, 25, 125) for category in categories]

    response = build_memory_score_response([_repo("repo_1")], skills, 1000)

    assert response.score == 100
    assert response.grade == "A"
    assert response.breakdown.coverage == 1
    assert response.breakdown.load_frequency == 1
    assert response.breakdown.quality == 1
    assert response.breakdown.freshness == 1


def test_memory_score_grade() -> None:
    assert _memory_grade(85) == "A"
    assert _memory_grade(65) == "B"
    assert _memory_grade(45) == "C"
