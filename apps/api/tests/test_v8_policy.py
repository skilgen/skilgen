from __future__ import annotations

import importlib
import statistics

import pytest

from apps.api.api.index import app
from apps.api.api.v8.policy.dsl import PolicyDSLParseError, context_from_mapping, evaluate_rules, parse_policy_yaml
from apps.api.api.v8.policy.dsl.models import DOWNGRADE_DECISION_MAP, PolicyRule
from apps.api.api.v8.policy.packs import load_starter_packs
from apps.api.api.v8.policy.rbac import settings_rbac_available


MIGRATION = importlib.import_module("apps.api.alembic.versions.20260505_0005_policy_verbs_dsl")


def test_policy_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/policy/rules" in paths
    assert "/v8/orgs/{org_id}/policy/violations" in paths
    assert "/v8/orgs/{org_id}/policy/approvals" in paths
    assert "/v8/orgs/{org_id}/policy/quarantine" in paths


def test_parser_accepts_prd_yaml_and_canonicalizes_legacy_verb() -> None:
    rule = parse_policy_yaml(
        """
id: payments-no-rm
title: "Coding agents cannot run rm in payments-svc"
scope:
  repo: "toyota/payments-svc"
  agent: ["claude-code", "codex"]
  action_class: shell_exec
match:
  command_regex: "^\\\\s*rm\\\\b"
decision: block
notify: ["#sec-aiops"]
compliance_tags: ["SOC2:CC8.1"]
"""
    )

    assert rule.id == "payments-no-rm"
    assert rule.decision == "deny"
    assert rule.deprecated_decision == "block"


def test_parser_rejects_rego_escape_hatch_for_pr3() -> None:
    with pytest.raises(PolicyDSLParseError):
        parse_policy_yaml(
            """
id: power-user
title: "Rego policy"
match:
  command_regex: ".*"
decision: allow
rego: "package policy"
"""
        )


def test_starter_packs_are_loadable_not_auto_applied() -> None:
    packs = load_starter_packs()

    assert {pack["pack_id"] for pack in packs} == {
        "fedramp-mod",
        "hipaa",
        "internal-ip",
        "license-hygiene",
        "production-safety",
        "soc2",
    }
    assert all("yaml" in pack for pack in packs)


def test_evaluator_is_deterministic_and_most_restrictive_wins() -> None:
    rules = [
        PolicyRule(id="allow-shell", title="Allow shell", scope={"action_class": "shell_exec"}, match={"command_regex": "rm"}, decision="allow"),
        PolicyRule(id="approve-rm", title="Approve rm", scope={"action_class": "shell_exec"}, match={"command_regex": "rm"}, decision="require_approval"),
        PolicyRule(id="deny-payments-rm", title="Deny payments rm", scope={"repo": "toyota/payments-svc"}, match={"command_regex": "rm"}, decision="deny"),
    ]
    context = context_from_mapping({"repo": "toyota/payments-svc", "action_class": "shell_exec", "command": "rm -rf tmp"})

    first = evaluate_rules(rules, context)
    second = evaluate_rules(list(reversed(rules)), context)

    assert first.decision == "deny"
    assert second.decision == "deny"
    assert first.matched_rule_ids[0] == "deny-payments-rm"
    assert second.matched_rule_ids[0] == "deny-payments-rm"


def test_evaluator_property_permutation_keeps_most_restrictive_decision() -> None:
    base_rules = [
        PolicyRule(id="r0", title="Log", scope={}, match={"command_regex": "deploy"}, decision="log_only"),
        PolicyRule(id="r1", title="Redact", scope={}, match={"command_regex": "deploy"}, decision="redact"),
        PolicyRule(id="r2", title="DLP", scope={}, match={"command_regex": "deploy"}, decision="route_to_dlp"),
        PolicyRule(id="r3", title="Approval", scope={}, match={"command_regex": "deploy"}, decision="require_approval"),
    ]
    context = context_from_mapping({"command": "deploy production"})

    expected = evaluate_rules(base_rules, context).decision
    for offset in range(len(base_rules)):
        rotated = base_rules[offset:] + base_rules[:offset]
        assert evaluate_rules(rotated, context).decision == expected


def test_evaluator_p95_under_50ms_for_100_rule_corpus() -> None:
    rules = [
        PolicyRule(
            id=f"rule-{index}",
            title=f"Rule {index}",
            scope={"repo": "toyota/payments-svc" if index % 2 == 0 else "toyota/*"},
            match={"command_regex": "kubectl|terraform|rm", "file_glob": ["**/prod/**", "**/staging/**"]},
            decision="deny" if index == 99 else "log_only",
            priority=index,
        )
        for index in range(100)
    ]
    context = context_from_mapping(
        {
            "repo": "toyota/payments-svc",
            "action_class": "shell_exec",
            "command": "kubectl apply -f k8s/prod/service.yaml",
            "files": ["k8s/prod/service.yaml"],
        }
    )

    samples = [evaluate_rules(rules, context).elapsed_ms for _ in range(200)]
    p95 = statistics.quantiles(samples, n=20)[18]

    assert p95 < 50


def test_policy_verb_migration_has_reversible_maps(monkeypatch) -> None:
    monkeypatch.setattr(MIGRATION, "_has_table", lambda table_name: False)

    MIGRATION.upgrade()
    MIGRATION.downgrade()

    assert DOWNGRADE_DECISION_MAP["deny"] == "block"
    assert DOWNGRADE_DECISION_MAP["require_approval"] == "warn"
    assert DOWNGRADE_DECISION_MAP["log_only"] == "log"


def test_settings_rbac_dependency_is_available_after_settings_lands() -> None:
    assert settings_rbac_available() is True
