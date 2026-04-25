from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from apps.api.api.routes.repos import _improvement_plan, _skill_code_block_count, _skill_improvement_plan, _skill_word_count


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _skill(**overrides: object) -> SimpleNamespace:
    base = {
        "id": "skill_1",
        "score_total": 15,
        "score_groundedness": 4,
        "score_coverage": 4,
        "score_freshness": 4,
        "score_structure": 3,
        "content": "thin guidance",
        "created_at": datetime.utcnow() - timedelta(days=20),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_improvement_plan_for_score_15_flags_multiple_dimensions() -> None:
    plan = _skill_improvement_plan(_skill())  # type: ignore[arg-type]

    assert plan.current_score == 15
    assert len(plan.issues) >= 3
    assert {"Groundedness", "Coverage", "Freshness", "Structure"}.issubset({issue.dimension for issue in plan.issues})


def test_improvement_plan_for_score_75_returns_not_improvable_when_dimensions_are_strong() -> None:
    skill = _skill(
        score_total=75,
        score_groundedness=20,
        score_coverage=25,
        score_freshness=20,
        score_structure=20,
        content="# Overview\n\nPrefer patterns.\n\n## Anti-patterns\nAvoid stale examples.",
    )

    plan = _skill_improvement_plan(skill)  # type: ignore[arg-type]

    assert plan.is_improvable is False
    assert plan.issues == []


def test_improvement_plan_potential_score_never_exceeds_100() -> None:
    plan = _skill_improvement_plan(_skill(score_total=90))  # type: ignore[arg-type]

    assert plan.potential_score <= 100


def test_improvement_plan_quick_win_is_highest_impact_issue() -> None:
    plan = _skill_improvement_plan(_skill())  # type: ignore[arg-type]

    assert plan.quick_win == plan.issues[0]
    assert plan.quick_win is not None
    assert plan.quick_win.impact == "high"


def test_improve_endpoint_enhance_without_anthropic_key_is_graceful() -> None:
    source = _read("apps/api/api/routes/repos.py")

    assert 'mode: Literal["regenerate", "enhance"]' in source
    assert "ANTHROPIC_API_KEY" in source
    assert "AI improvement requires ANTHROPIC_API_KEY to be configured" in source
    assert "improved=False" in source


def test_improve_endpoint_enhance_with_mock_api_creates_new_version_contract() -> None:
    source = _read("apps/api/api/routes/repos.py")

    assert "await _anthropic_skill_improvement" in source
    assert "db.add(\n            SkillVersion(" in source
    assert "score_delta=float" in source
    assert "new_version=version_number" in source
    assert "content=new_content" in source


def test_setup_status_with_0_repos_contract_has_all_steps_false() -> None:
    source = _read("apps/api/api/routes/orgs.py")

    assert '@router.get("/{org_id}/setup-status", response_model=SetupStatusResponse)' in source
    assert "has_repos = repo_count > 0" in source
    assert 'id="connect_repo"' in source
    assert 'id="generate_skills"' in source
    assert 'id="connect_agent"' in source
    assert 'id="improve_skills"' in source
    assert "completion_percent=completed * 25" in source


def test_setup_status_with_repos_and_skills_but_no_loads_marks_connect_agent_false() -> None:
    source = _read("apps/api/api/routes/orgs.py")

    assert "has_skills = skill_count > 0" in source
    assert "has_agent_loads = load_count > 0" in source
    assert 'done=has_agent_loads' in source


def test_action_items_with_low_score_skills_returns_at_least_one_item_path() -> None:
    source = _read("apps/api/api/routes/orgs.py")

    assert '@router.get("/{org_id}/action-items", response_model=OrgActionItemsResponse)' in source
    assert 'type="improve"' in source
    assert "Agents are loading it but it only scores" in source
    assert 'action_url=f"/dashboard/repos/{skill.repo_id}/skills/{skill.id}"' in source


def test_action_items_with_all_scores_healthy_returns_fallback_suggestion() -> None:
    source = _read("apps/api/api/routes/orgs.py")

    assert 'id="review-healthy-skills"' in source
    assert 'priority="suggested"' in source


def test_word_and_code_block_counts_are_markdown_aware() -> None:
    content = "# Backend\n\nUse routes.\n\n```py\nprint('ok')\n```\n\n```ts\nconsole.log('ok')\n```"

    assert _skill_word_count(content) == len(content.split())
    assert _skill_code_block_count(content) == 2


def test_raw_improvement_plan_dict_contract_matches_response_model() -> None:
    plan = _improvement_plan(_skill(), None)  # type: ignore[arg-type]

    assert set(plan) == {
        "skill_id",
        "current_score",
        "potential_score",
        "score_gap",
        "issues",
        "word_count",
        "code_block_count",
        "is_improvable",
        "quick_win",
    }
