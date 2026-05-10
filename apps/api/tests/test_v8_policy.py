from __future__ import annotations

import importlib
import asyncio
import statistics

import pytest
from fastapi.testclient import TestClient

from apps.api.api.index import app
from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
import apps.api.api.v8.policy.routes as policy_routes
from apps.api.api.v8.flags import request_flag_cache
from apps.api.api.v8.policy.dsl import PolicyDSLParseError, context_from_mapping, evaluate_rules, parse_policy_yaml
from apps.api.api.v8.policy.dsl.models import DOWNGRADE_DECISION_MAP, PolicyRule
from apps.api.api.v8.policy.packs import load_starter_packs
from apps.api.api.v8.policy.routes import ApprovalDecisionPayload, ViolationResponse, _approval_review_state, _open_approvals
from apps.api.api.v8.policy.rbac import settings_rbac_available
from packages.db.models import Org


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
        "agent-compliance",
        "fedramp-mod",
        "hipaa",
        "internal-ip",
        "license-hygiene",
        "production-safety",
        "soc2",
    }
    assert all("yaml" in pack for pack in packs)
    agent_pack = next(pack for pack in packs if pack["pack_id"] == "agent-compliance")
    assert agent_pack["predicate_count"] == 5
    assert {"provider", "intelligence_tier", "access_scope", "tool_permissions", "repo_sensitivity"}.issubset(set(agent_pack["match_fields"]))


def test_agent_compliance_predicates_match_normalized_metadata_aliases() -> None:
    rule = parse_policy_yaml(
        """
id: agent-compliance-full-access
title: "Very-high intelligence agents with full access require review"
scope:
  provider: ["Codex CLI", "Claude Code", "Cursor"]
match:
  intelligence_tier: "very-high"
  access_scope: "full-access"
  tool_permissions: ["shell", "apply_patch", "settings.write"]
  repo_sensitivity: ["confidential", "restricted"]
decision: require_approval
notify: ["#sec-aiops"]
compliance_tags: ["agent-compliance"]
"""
    )
    context = context_from_mapping(
        {
            "metadata": {
                "source_provider": "Codex CLI",
                "reasoning_tier": "very-high",
                "grant_scope": "full-access",
                "mcp_tools": ["filesystem.read", "apply_patch"],
                "sensitivity_tier": "restricted",
            }
        }
    )

    decision = evaluate_rules([rule], context)

    assert decision.decision == "require_approval"
    assert decision.matched_rule_ids == ("agent-compliance-full-access",)
    assert decision.compliance_tags == ("agent-compliance",)


def test_agent_compliance_predicates_do_not_match_lower_access_scope() -> None:
    rule = PolicyRule(
        id="full-access-only",
        title="Full access only",
        scope={"provider": "Codex CLI"},
        match={"full_access": True, "mcp_tool": "apply_patch"},
        decision="deny",
    )
    context = context_from_mapping(
        {
            "provider": "Codex CLI",
            "access_scope": "workspace-write",
            "tool_name": "apply_patch",
        }
    )

    assert evaluate_rules([rule], context).decision == "allow"


def test_agent_compliance_mcp_tool_matches_plural_metadata() -> None:
    rule = PolicyRule(
        id="mcp-tool",
        title="MCP tool",
        scope={"provider": "Codex CLI"},
        match={"mcp_tool": "apply_patch"},
        decision="require_approval",
    )
    context = context_from_mapping({"provider": "Codex CLI", "mcp_tools": ["filesystem.read", "apply_patch"]})

    assert evaluate_rules([rule], context).decision == "require_approval"


def test_starter_pack_endpoint_returns_predicate_metadata(monkeypatch) -> None:
    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def db_override():
        yield object()

    app.dependency_overrides[get_current_org_id] = lambda: "org-1"
    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[request_flag_cache] = lambda: None
    monkeypatch.setattr(policy_routes, "_ensure_v8", ensure_v8)
    try:
        response = TestClient(app).get("/v8/orgs/org-1/policy/rules/starter-packs")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    agent_pack = next(pack for pack in response.json() if pack["pack_id"] == "agent-compliance")
    assert agent_pack["predicate_count"] == 5
    assert "tool_permissions" in agent_pack["match_fields"]


def test_evaluate_endpoint_applies_agent_compliance_predicates(monkeypatch) -> None:
    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def load_enabled_rules(org_id, db):
        assert org_id == "org-1"
        return []

    async def db_override():
        yield object()

    app.dependency_overrides[get_current_org_id] = lambda: "org-1"
    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[request_flag_cache] = lambda: None
    monkeypatch.setattr(policy_routes, "_ensure_v8", ensure_v8)
    monkeypatch.setattr(policy_routes, "_load_enabled_rules", load_enabled_rules)
    try:
        response = TestClient(app).post(
            "/v8/orgs/org-1/policy/evaluate",
            json={
                "event": {
                    "metadata": {
                        "source_provider": "Codex CLI",
                        "reasoning_tier": "very-high",
                        "grant_scope": "full-access",
                        "mcp_tools": ["apply_patch"],
                        "sensitivity_tier": "restricted",
                    }
                },
                "policies": [
                    {
                        "id": "agent-compliance-full-access",
                        "title": "Very-high intelligence agents with full access require review",
                        "scope": {"provider": ["Codex CLI"]},
                        "match": {
                            "intelligence_tier": "very-high",
                            "access_scope": "full-access",
                            "mcp_tool": "apply_patch",
                            "repo_sensitivity": "restricted",
                        },
                        "decision": "require_approval",
                        "compliance_tags": ["agent-compliance"],
                    }
                ],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "require_approval"
    assert payload["matched_rule_ids"] == ["agent-compliance-full-access"]


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


def test_approval_review_state_filters_terminal_decisions_from_queue() -> None:
    base = {
        "id": "approval-1",
        "policy_id": "policy-1",
        "policy_name": "Production deploy approval",
        "decision": "require_approval",
        "severity": "warning",
        "repo_id": "repo-1",
        "repo_name": "payments",
        "skill_id": None,
        "skill_domain": None,
        "description": "Production deployment needs approval",
        "flagged": True,
        "sla_started_at": "2026-05-10T10:00:00",
        "sla_due_at": "2026-05-10T12:00:00",
        "sla_minutes_remaining": 90,
    }

    open_item = ViolationResponse(**base)
    request_info = ViolationResponse(**{**base, "id": "approval-2", "review_decision": "request_info"})
    approved = ViolationResponse(**{**base, "id": "approval-3", "review_decision": "approve"})
    denied = ViolationResponse(**{**base, "id": "approval-4", "review_decision": "deny"})

    assert [item.id for item in _open_approvals([open_item, request_info, approved, denied])] == ["approval-1", "approval-2"]


def test_approval_review_state_parses_recorded_decision_timestamp() -> None:
    decision, reviewed_at = _approval_review_state(
        {"approval-1": {"decision": "request_info", "recorded_at": "2026-05-10T10:15:00"}},
        "approval-1",
    )

    assert decision == "request_info"
    assert reviewed_at is not None
    assert reviewed_at.minute == 15


def test_decide_approval_persists_decision_for_queue_state(monkeypatch) -> None:
    approval = ViolationResponse(
        id="approval-1",
        policy_id="policy-1",
        policy_name="Production deploy approval",
        decision="require_approval",
        severity="warning",
        repo_id="repo-1",
        repo_name="payments",
        skill_id=None,
        skill_domain=None,
        description="Production deployment needs approval",
        flagged=True,
        sla_started_at="2026-05-10T10:00:00",
        sla_due_at="2026-05-10T12:00:00",
        sla_minutes_remaining=90,
    )
    org = Org(id="org-1", github_org_id=1, login="acme", name="Acme")

    class Db:
        committed = False

        async def get(self, model, row_id):
            assert model is Org
            assert row_id == "org-1"
            return org

        async def commit(self):
            self.committed = True

    async def ensure_v8(org_id, current_org_id, db):
        assert org_id == current_org_id == "org-1"

    async def approval_decisions(org_id, db):
        return {}

    async def violations(org_id, db, *, approval_decisions=None):
        return [approval]

    monkeypatch.setattr(policy_routes, "_ensure_v8", ensure_v8)
    monkeypatch.setattr(policy_routes, "_approval_decisions", approval_decisions)
    monkeypatch.setattr(policy_routes, "_violations", violations)

    db = Db()
    result = asyncio.run(
        policy_routes.decide_approval(
            "org-1",
            "approval-1",
            ApprovalDecisionPayload(decision="approve", note="ship it"),
            db=db,
            current_org_id="org-1",
        )
    )

    stored = org.settings["v8_policy_approval_decisions"]["approval-1"]
    assert result == {"recorded": True, "approval_id": "approval-1", "decision": "approve"}
    assert stored["decision"] == "approve"
    assert stored["note"] == "ship it"
    assert db.committed is True
