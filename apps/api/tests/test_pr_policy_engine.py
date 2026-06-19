from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps.api.api.services.policy_engine import _evaluate_one, validate_pr_policy_config


def _policy(rule_type: str, config: dict[str, object] | None = None):
    return SimpleNamespace(id=f"p_{rule_type}", name=rule_type, rule_type=rule_type, rule_config=config or {})


def _attr(**overrides: object):
    values = {
        "primary_agent": "codex",
        "risk_tier": "green",
        "skills_loaded": ["auth"],
        "skills_violated": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_block_on_red_fails_red_risk() -> None:
    failure = _evaluate_one(_policy("block_on_red"), _attr(risk_tier="red"))
    assert failure is not None
    assert failure["rule_type"] == "block_on_red"


def test_block_on_red_passes_non_red_risk() -> None:
    assert _evaluate_one(_policy("block_on_red"), _attr(risk_tier="yellow")) is None


def test_require_skill_load_fails_when_agent_loaded_no_skills() -> None:
    failure = _evaluate_one(_policy("require_skill_load", {"agent_runtimes": ["codex"]}), _attr(skills_loaded=[]))
    assert failure is not None
    assert "No skills" in failure["message"]


def test_require_skill_load_skips_agents_outside_scope() -> None:
    assert _evaluate_one(_policy("require_skill_load", {"agent_runtimes": ["claude_code"]}), _attr(skills_loaded=[])) is None


def test_min_compliance_fails_when_error_violation_exists() -> None:
    attr = _attr(skills_violated=[{"severity": "critical", "skill_name": "auth"}])
    failure = _evaluate_one(_policy("min_compliance", {"threshold": 80}), attr)
    assert failure is not None
    assert "below required 80%" in failure["message"]


def test_min_compliance_passes_clean_pr() -> None:
    assert _evaluate_one(_policy("min_compliance", {"threshold": 80}), _attr()) is None


def test_validate_pr_policy_config_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError):
        validate_pr_policy_config("min_compliance", {"threshold": 140})


def test_validate_pr_policy_config_normalizes_require_skill_load() -> None:
    assert validate_pr_policy_config("require_skill_load", {"agent_runtimes": ["codex"]}) == {"agent_runtimes": ["codex"]}
