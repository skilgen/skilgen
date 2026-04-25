from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest

from apps.api.api.services import policy


def _policy(rule_type: str, config: dict[str, object], severity: str = "error"):
    return SimpleNamespace(id=f"p_{rule_type}", name=rule_type, rule_type=rule_type, rule_config=config, severity=severity)


def _repo():
    return SimpleNamespace(id="repo_1", name="payments-service", last_analysed_at=datetime.utcnow())


def _skill(**overrides: object):
    values = {
        "id": "skill_1",
        "domain": "auth",
        "skill_category": "codebase_architecture",
        "score_total": 75,
        "score_freshness": 25,
        "load_count_30d": 1,
        "last_loaded_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class PolicyEngineTests(unittest.TestCase):
    def test_require_skill_category_flags_missing_security(self) -> None:
        violations = policy._evaluate_rule(_policy("require_skill_category", {"category": "security_compliance"}), {}, _repo(), [_skill()], None, datetime.utcnow())
        self.assertEqual(len(violations), 1)
        self.assertIn("security compliance", violations[0].description)

    def test_require_skill_category_passes_when_present(self) -> None:
        violations = policy._evaluate_rule(_policy("require_skill_category", {"category": "security_compliance"}), {"category": "security_compliance"}, _repo(), [_skill(skill_category="security_compliance")], None, datetime.utcnow())
        self.assertEqual(violations, [])

    def test_max_skill_age_days_flags_old_skill(self) -> None:
        old = datetime.utcnow() - timedelta(days=60)
        violations = policy._evaluate_rule(_policy("max_skill_age_days", {"max_days": 30}), {"max_days": 30}, _repo(), [_skill(created_at=old)], None, datetime.utcnow())
        self.assertEqual(violations[0].skill_domain, "auth")

    def test_min_skill_score_flags_low_score(self) -> None:
        violations = policy._evaluate_rule(_policy("min_skill_score", {"min_score": 40}), {"min_score": 40}, _repo(), [_skill(score_total=25)], None, datetime.utcnow())
        self.assertIn("score 25/100 < 40", violations[0].description)

    def test_min_freshness_score_flags_low_freshness(self) -> None:
        violations = policy._evaluate_rule(_policy("min_freshness_score", {"min_freshness": 15}), {"min_freshness": 15}, _repo(), [_skill(score_freshness=5)], None, datetime.utcnow())
        self.assertIn("freshness 5/25 < 15", violations[0].description)

    def test_require_analysis_recency_flags_stale_repo(self) -> None:
        repo = SimpleNamespace(id="repo_1", name="old-api", last_analysed_at=datetime.utcnow() - timedelta(days=90))
        violations = policy._evaluate_rule(_policy("require_analysis_recency", {"max_days": 14}), {"max_days": 14}, repo, [], None, datetime.utcnow())
        self.assertEqual(violations[0].repo_name, "old-api")

    def test_no_dead_skills_flags_unloaded_skill(self) -> None:
        old = datetime.utcnow() - timedelta(days=45)
        violations = policy._evaluate_rule(_policy("no_dead_skills", {"grace_period_days": 30}), {"grace_period_days": 30}, _repo(), [_skill(load_count_30d=0, last_loaded_at=None, created_at=old)], None, datetime.utcnow())
        self.assertEqual(violations[0].rule_type, "no_dead_skills")

    def test_min_coverage_score_flags_low_coverage(self) -> None:
        violations = policy._evaluate_rule(_policy("min_coverage_score", {"min_coverage": 70}), {"min_coverage": 70}, _repo(), [_skill(skill_category="security_compliance")], None, datetime.utcnow())
        self.assertTrue(violations)

    def test_rule_types_include_all_enterprise_rules(self) -> None:
        self.assertEqual(
            policy.POLICY_RULE_TYPES,
            {"require_skill_category", "max_skill_age_days", "min_skill_score", "min_freshness_score", "require_analysis_recency", "no_dead_skills", "min_coverage_score"},
        )

    def test_ci_endpoint_returns_422_on_violation_source(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn("status_code=422", source)
        self.assertIn("policy.check_failed", source)


if __name__ == "__main__":
    unittest.main()
