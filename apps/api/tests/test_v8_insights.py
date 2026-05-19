from __future__ import annotations

import importlib
from datetime import datetime, timedelta
from types import SimpleNamespace

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from apps.api.api.auth import get_current_org_id
from apps.api.api.v8.insights import router as insights_router
from packages.db.database import get_db
from packages.db.models import PRAttribution, PullRequest


insights = importlib.import_module("apps.api.api.v8.insights.router")
migration = importlib.import_module("apps.api.alembic.versions.20260505_0006_v8_insights_risk_views")

NOW = datetime(2026, 5, 4, 12, 0, 0)


class Result:
    def __init__(self, rows=None, scalar=0) -> None:
        self.rows = rows or []
        self._scalar = scalar

    def scalar(self):
        return self._scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows

    def mappings(self):
        return self


class Db:
    def __init__(self, results=None, *, fail_first=False, org=None) -> None:
        self.results = list(results or [])
        self.fail_first = fail_first
        self.rolled_back = False
        self.org = org

    async def execute(self, statement, params=None):
        if self.fail_first:
            self.fail_first = False
            raise SQLAlchemyError("view missing")
        if not self.results:
            raise AssertionError(f"Unexpected query: {statement}")
        return self.results.pop(0)

    async def rollback(self):
        self.rolled_back = True

    async def get(self, model, row_id):
        return self.org


def _repo(repo_id: str, name: str, tier: str | None = "internal"):
    return SimpleNamespace(
        id=repo_id,
        org_id="org_1",
        name=name,
        full_name=f"acme/{name}",
        is_active=True,
        sensitivity_tier=tier,
        last_analysed_at=None,
    )


def _pr(pr_id: str, repo_id: str, days_old: int = 1) -> PullRequest:
    pr = PullRequest(repo_id=repo_id, github_pr_number=int(pr_id.split("_")[-1]))
    pr.id = pr_id
    pr.opened_at = NOW - timedelta(days=days_old)
    return pr


def _attr(pr_id: str, agent: str, violated: bool = False) -> PRAttribution:
    attr = PRAttribution(pr_id=pr_id, primary_agent=agent, confidence=0.9)
    attr.skills_violated = [{"severity": "critical", "skill_name": "security"}] if violated else []
    return attr


def _client(db: Db, monkeypatch, *, enabled: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(insights_router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_org_id] = lambda: "org_1"

    async def fake_is_v8(org_id, db=None):
        return enabled

    monkeypatch.setattr(insights, "is_v8", fake_is_v8)
    monkeypatch.setattr(insights, "_utc_now", lambda: NOW)
    return TestClient(app)


def test_insights_router_paths_are_registered() -> None:
    app = FastAPI()
    app.include_router(insights_router)
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/insights/overview" in paths
    assert "/v8/orgs/{org_id}/insights/fleet-kpis" in paths
    assert "/v8/orgs/{org_id}/insights/risky-agents" in paths
    assert "/v8/orgs/{org_id}/insights/risky-repos" in paths
    assert "/v8/orgs/{org_id}/insights/coverage-sla" in paths
    assert "/v8/orgs/{org_id}/insights/intelligence-usage" in paths
    assert "/v8/orgs/{org_id}/insights/access-grants" in paths
    assert "/v8/orgs/{org_id}/insights/agent-compliance-metrics" in paths
    assert "/v8/orgs/{org_id}/insights/codex-runs" in paths
    assert "/v8/orgs/{org_id}/insights/provider-coverage" in paths
    assert "/v8/orgs/{org_id}/insights/developer-track" in paths


def test_insights_routes_404_when_ia_v8_disabled(monkeypatch) -> None:
    response = _client(Db(), monkeypatch, enabled=False).get("/v8/orgs/org_1/insights/risky-agents")

    assert response.status_code == 404


def test_fleet_kpis_contract_includes_prior_period_comparison(monkeypatch) -> None:
    approved = SimpleNamespace(status="approved", created_at=NOW - timedelta(hours=2), reviewed_at=NOW - timedelta(hours=1))
    rejected = SimpleNamespace(status="rejected", created_at=NOW - timedelta(hours=3), reviewed_at=NOW - timedelta(hours=1))
    current_quarantine = SimpleNamespace(tags=["quarantined"], is_deprecated=False)
    previous_retired = SimpleNamespace(tags=[], is_deprecated=True)
    org = SimpleNamespace(settings={
        "v8_policy_approval_decisions": {
            "policy-1:repo_1:skill_1": {"decision": "approve", "recorded_at": (NOW - timedelta(hours=2)).isoformat()},
            "policy-2:repo_1:skill_2": {"decision": "deny", "recorded_at": (NOW - timedelta(days=31)).isoformat()},
            "policy-open:repo_1:skill_3": {"decision": "request_info", "recorded_at": (NOW - timedelta(hours=1)).isoformat()},
        }
    })
    current_policy = SimpleNamespace(id="policy-1", created_at=NOW - timedelta(hours=6))
    previous_policy = SimpleNamespace(id="policy-2", created_at=NOW - timedelta(days=31, hours=8))
    open_policy = SimpleNamespace(id="policy-open", created_at=NOW - timedelta(hours=2))
    current_pr = _pr("pr_1", "repo_1")
    previous_pr = _pr("pr_2", "repo_1", days_old=31)
    db = Db(
        [
            Result([approved, rejected]),
            Result([]),
            Result(scalar=10),
            Result(scalar=5),
            Result(["repo_1"]),
            Result([current_pr]),
            Result([_attr("pr_1", "codex", violated=True)]),
            Result(["repo_1"]),
            Result([previous_pr]),
            Result([_attr("pr_2", "codex", violated=False)]),
            Result(scalar=1),
            Result(scalar=0),
            Result([current_quarantine, previous_retired]),
            Result([previous_retired]),
            Result([current_policy, previous_policy, open_policy]),
            Result([current_policy, previous_policy, open_policy]),
            Result(["repo_1"]),
            Result([current_pr]),
            Result([_attr("pr_1", "codex", violated=True)]),
            Result(["repo_1"]),
            Result([previous_pr]),
            Result([]),
            Result(["ravi"]),
            Result(["ravi", "sam"]),
        ],
        org=org,
    )
    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/fleet-kpis")

    assert response.status_code == 200
    payload = response.json()
    metrics = {metric["key"]: metric for metric in payload["metrics"]}
    assert metrics["total_agent_actions"]["current"] == 10
    assert metrics["total_agent_actions"]["previous"] == 5
    assert metrics["deny_rate"]["current"] == 1.0
    assert metrics["approval_rate"]["current"] == 0.5
    assert metrics["median_time_to_approve"]["current"] == 60
    assert metrics["quarantined_skills"]["status"] == "available"
    assert metrics["quarantined_skills"]["source"] == "skill_registry_entries"
    assert metrics["quarantined_skills"]["current"] == 2
    assert metrics["quarantined_skills"]["previous"] == 1
    assert metrics["mttr_violations"]["status"] == "available"
    assert metrics["mttr_violations"]["source"] == "org.settings.v8_policy_approval_decisions"
    assert metrics["mttr_violations"]["current"] == 4
    assert metrics["mttr_violations"]["previous"] == 8
    assert metrics["attributed_agent_commits"]["previous"] == 0.0


def test_quarantine_kpi_uses_registry_publisher_ownership() -> None:
    statement = sa.select(insights.SkillRegistryEntry.id).where(insights._registry_entry_owned_by_org("org_1"))
    compiled = str(statement.compile(compile_kwargs={"literal_binds": True}))

    assert "skill_registry_entries.org_id = 'org_1'" in compiled
    assert "skill_registry_entries.publisher_org_id = 'org_1'" in compiled


def test_risky_agent_fallback_sorts_by_prd_formula(monkeypatch) -> None:
    db = Db(
        [
            Result([_repo("repo_1", "payments", "regulated"), _repo("repo_2", "docs", "internal")]),
            Result([_pr("pr_1", "repo_1"), _pr("pr_2", "repo_1"), _pr("pr_3", "repo_2")]),
            Result([_attr("pr_1", "codex", True), _attr("pr_2", "codex", True), _attr("pr_3", "cursor", True)]),
        ],
        fail_first=True,
    )
    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/risky-agents")

    assert response.status_code == 200
    rows = response.json()["rows"]
    assert rows[0]["name"] == "codex"
    assert rows[0]["composite_risk"] == 6.0
    assert rows[1]["name"] == "cursor"
    assert db.rolled_back is True


def test_risky_view_sql_snapshot_contains_required_formula() -> None:
    sql = migration.risky_agents_view_sql("postgresql", has_sensitivity_tier=True)

    assert "CREATE VIEW v8_insights_risky_agents AS" in sql
    assert "SUM(denied) * 1.0 / COUNT(*)" in sql
    assert "AVG(scope_weight) * COUNT(*) AS composite_risk" in sql
    assert "CURRENT_TIMESTAMP - interval '30 days'" in sql


def test_risky_views_migration_upgrade_and_downgrade(monkeypatch) -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE repos (id TEXT PRIMARY KEY, org_id TEXT, full_name TEXT, sensitivity_tier TEXT, is_active BOOLEAN)"))
        connection.execute(sa.text("CREATE TABLE pull_requests (id TEXT PRIMARY KEY, repo_id TEXT, opened_at DATETIME)"))
        connection.execute(sa.text("CREATE TABLE pr_attributions (id TEXT PRIMARY KEY, pr_id TEXT, primary_agent TEXT, skills_violated TEXT)"))
        context = MigrationContext.configure(connection)
        monkeypatch.setattr(migration, "op", Operations(context))

        migration.upgrade()
        views = {row[0] for row in connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='view'")).all()}
        assert "v8_insights_risky_agents" in views
        assert "v8_insights_risky_repos" in views

        migration.downgrade()
        views = {row[0] for row in connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='view'")).all()}
        assert "v8_insights_risky_agents" not in views
        assert "v8_insights_risky_repos" not in views


def test_one_million_event_fixture_limitation_is_documented() -> None:
    path = "docs/v8-refactor/insights-pr6-fixture-limitations.md"
    assert "1M-event" in open(path, encoding="utf-8").read()


def test_coverage_sla_reads_critical_ops_from_yaml(monkeypatch, tmp_path) -> None:
    yaml_path = tmp_path / "critical_ops.yaml"
    yaml_path.write_text(
        """
product_review_required: false
product_review_note: ""
operations:
  - id: commit-signing
    label: Commit signing enforced
    required_skill_categories: ["security_compliance"]
    evidence_requirements: ["signed commits"]
    sla_hours: 24
  - id: production-data-access
    label: Production data access
    required_skill_categories: ["data_governance"]
    repo_sensitivity_tiers: ["sensitive", "regulated"]
  - id: policy-controlled-agent-action
    label: Policy controlled agent action
    required_skill_categories: ["ai_governance"]
    repo_sensitivity_tiers: ["internal", "sensitive", "regulated"]
""".lstrip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(insights, "_critical_ops_path", lambda: yaml_path)
    insights._load_critical_ops_config.cache_clear()

    repo = _repo("repo_1", "payments", "internal")
    skill = SimpleNamespace(
        id="skill_1",
        repo_id="repo_1",
        domain="security",
        skill_category="security_compliance",
        score_total=82,
        updated_at=NOW,
        created_at=NOW,
    )
    policy = SimpleNamespace(name="SOC2", enabled=True, rule_config={})
    db = Db([Result([repo]), Result([skill]), Result([policy])])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/coverage-sla")

    assert response.status_code == 200
    payload = response.json()
    assert payload["product_review_required"] is False
    assert payload["repos"][0]["critical_operations"][0]["operation_id"] == "commit-signing"
    assert payload["repos"][0]["critical_operations"][0]["sla_hours"] == 24
    assert "signed commits" in payload["repos"][0]["critical_operations"][0]["evidence_requirements"]
    assert payload["repos"][0]["critical_operations"][0]["skills"][0]["id"] == "skill_1"
    operation_ids = {operation["operation_id"] for operation in payload["repos"][0]["critical_operations"]}
    assert "production-data-access" not in operation_ids
    assert "policy-controlled-agent-action" in operation_ids


def test_coverage_sla_falls_back_when_critical_ops_yaml_invalid(monkeypatch, tmp_path) -> None:
    yaml_path = tmp_path / "critical_ops.yaml"
    yaml_path.write_text("operations: definitely-not-a-list", encoding="utf-8")

    monkeypatch.setattr(insights, "_critical_ops_path", lambda: yaml_path)
    insights._load_critical_ops_config.cache_clear()

    repo = _repo("repo_1", "payments", "internal")
    db = Db([Result([repo]), Result([]), Result([])])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/coverage-sla")

    assert response.status_code == 200
    payload = response.json()
    assert payload["product_review_required"] is True
    assert payload["repos"][0]["critical_operations"][0]["operation_id"] == "critical-operations-placeholder"


def test_coverage_sla_defaults_unclassified_repo_to_internal_taxonomy(monkeypatch) -> None:
    insights._load_critical_ops_config.cache_clear()
    repo = _repo("repo_1", "unclassified", None)
    db = Db([Result([repo]), Result([]), Result([])])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/coverage-sla")

    assert response.status_code == 200
    payload = response.json()
    operation_ids = {operation["operation_id"] for operation in payload["repos"][0]["critical_operations"]}
    assert "commit-signing" in operation_ids
    assert "policy-controlled-agent-action" in operation_ids
    assert "production-data-access" not in operation_ids


def test_intelligence_usage_rolls_up_metadata_only_compliance_events(monkeypatch) -> None:
    events = [
        SimpleNamespace(
            org_id="org_1",
            event_type="settings.updated",
            actor_login="admin",
            repo_name="acme/payments",
            resource_type="settings",
            created_at=NOW,
            metadata_json={
                "provider": "Unrelated Admin Tool",
                "model": "not-an-agent",
                "intelligence_tier": "very-high",
                "access_scope": "full-access",
                "full_access": True,
                "tool_permissions": ["settings.write"],
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="acme/payments",
            resource_type="codex",
            created_at=NOW,
            metadata_json={
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
                "access_scope": "full-access",
                "full_access": True,
                "autonomous_access": True,
                "tool_permissions": ["shell", "apply_patch"],
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="sam",
            repo_name="acme/payments",
            resource_type="cursor",
            created_at=NOW - timedelta(minutes=5),
            metadata_json={
                "provider": "Cursor",
                "model": "claude-sonnet-4-5",
                "model_tier": "high",
                "access_scope": "workspace-write",
                "tool_calls": 3,
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="acme/payments",
            resource_type="codex",
            created_at=NOW - timedelta(minutes=10),
            metadata_json={
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
            },
        ),
    ]
    db = Db([Result(events)])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/intelligence-usage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_retention"] == "metadata-only"
    assert payload["tier_usage"][0]["provider"] == "Codex CLI"
    assert payload["tier_usage"][0]["intelligence_tier"] == "very-high"
    assert payload["tier_usage"][0]["events"] == 2
    assert payload["tier_usage"][0]["users"] == 1
    assert all(row["provider"] != "Unrelated Admin Tool" for row in payload["tier_usage"])
    assert all(row["provider"] != "Unrelated Admin Tool" for row in payload["access_grants"])
    assert payload["access_grants"][0]["actor_login"] == "ravi"
    assert payload["access_grants"][0]["full_access_events"] == 1
    assert payload["access_grants"][0]["autonomous_events"] == 1
    assert payload["access_grants"][0]["tool_permission_events"] == 2


def test_access_grants_endpoint_returns_metadata_only_exposure_rows(monkeypatch) -> None:
    events = [
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="acme/payments",
            resource_type="codex",
            created_at=NOW,
            metadata_json={
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
                "access_scope": "full-access",
                "full_access": True,
                "tool_permissions": ["shell", "apply_patch"],
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.telemetry",
            actor_login="sam",
            repo_name="acme/web",
            resource_type="cursor",
            created_at=NOW - timedelta(minutes=5),
            metadata_json={
                "provider": "Cursor",
                "access_scope": "workspace-write",
                "autonomous_access": True,
                "tool_calls": 1,
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="maya",
            repo_name="acme/docs",
            resource_type="claude",
            created_at=NOW - timedelta(minutes=10),
            metadata_json={
                "provider": "Claude Code",
                "model": "claude-sonnet-4-5",
                "intelligence_tier": "high",
            },
        ),
    ]
    db = Db([Result(events)])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/access-grants")

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_retention"] == "metadata-only"
    assert payload["source"] == "audit_events.metadata"
    assert len(payload["grants"]) == 2
    assert payload["grants"][0]["actor_login"] == "ravi"
    assert payload["grants"][0]["access_scope"] == "full-access"
    assert payload["grants"][0]["full_access_events"] == 1
    assert payload["grants"][0]["tool_permission_events"] == 2
    assert all(row["actor_login"] != "maya" for row in payload["grants"])


def test_agent_compliance_metrics_consolidates_all_ingested_metadata(monkeypatch) -> None:
    events = [
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="acme/payments",
            resource_type="codex_cli",
            created_at=NOW,
            metadata_json={
                "connector_id": "codex-cli",
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
                "access_scope": "full-access",
                "full_access": True,
                "autonomous_access": True,
                "tool_permissions": ["shell", "apply_patch"],
                "mcp_tools": ["github:create_pr"],
                "file_targets": ["apps/dashboard/page.tsx", "apps/api/router.py"],
                "policy_decision": "deny",
                "approval_status": "rejected",
                "violations": ["full-access-prod"],
                "warnings": 2,
                "tokens_input": 1200,
                "tokens_output": 800,
                "cost_usd": 0.42,
                "latency_ms": 1500,
                "error_count": 1,
                "session_id": "sess-1",
                "source_record_type": "operational-telemetry",
                "content_retention": "metadata-only",
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.telemetry",
            actor_login="maya",
            repo_name="acme/api",
            resource_type="openai_compliance",
            created_at=NOW - timedelta(minutes=5),
            metadata_json={
                "connector_id": "openai-compliance",
                "provider": "OpenAI Compliance Platform",
                "model": "gpt-5.2",
                "intelligence_tier": "high",
                "tool_calls": 3,
                "mcp_tools": ["linear:create_issue", "github:create_pr"],
                "file_targets": ["apps/api/router.py"],
                "policy_decision": "allow",
                "approval_status": "approved",
                "tokens_total": 900,
                "cost_usd": "0.18",
                "latency_ms": "500",
                "session_id": "sess-2",
                "source_record_type": "formal-compliance",
                "redaction_state": "raw-content-dropped",
            },
        ),
    ]
    db = Db([Result(events)])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/agent-compliance-metrics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_retention"] == "metadata-only"
    assert payload["summary"] == {
        "events": 2,
        "users": 2,
        "providers": 2,
        "sessions": 2,
        "repos": 2,
        "file_targets": 3,
        "tool_permission_events": 5,
        "mcp_tool_events": 3,
        "full_access_events": 1,
        "autonomous_events": 1,
        "approvals": 1,
        "denials": 2,
        "warnings": 2,
        "violations": 1,
        "errors": 1,
        "tokens_input": 1200,
        "tokens_output": 800,
        "tokens_total": 2900,
        "cost_usd": 0.6,
        "avg_latency_ms": 1000.0,
    }
    provider_rows = {row["label"]: row for row in payload["by_provider"]}
    assert provider_rows["Codex CLI"]["full_access_events"] == 1
    assert provider_rows["OpenAI Compliance Platform"]["tool_permission_events"] == 3
    assert payload["top_tools"][0] == {"key": "apply_patch", "label": "apply_patch", "count": 1}
    assert {"key": "github:create_pr", "label": "github:create_pr", "count": 2} in payload["top_mcp_tools"]
    assert {"key": "apps/api/router.py", "label": "apps/api/router.py", "count": 2} in payload["top_files"]
    assert payload["policy_decisions"] == [
        {"key": "allow", "label": "allow", "count": 1},
        {"key": "deny", "label": "deny", "count": 1},
    ]
    assert {"key": "formal-compliance", "label": "formal-compliance", "count": 1} in payload["source_record_types"]


def test_overview_compares_coding_platforms_and_cost_provenance(monkeypatch) -> None:
    events = [
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="ravichanduummadisetti/skilgen",
            resource_type="agent_run",
            created_at=NOW,
            metadata_json={
                "provider": "Codex",
                "model": "gpt-5.5",
                "session_id": "codex-1",
                "access_scope": "full-access",
                "full_access": True,
                "activity_metrics": {"edited_files": 2, "explored_files": 4, "searches": 1, "commands": 3, "tool_calls": 5},
                "tokens_total": 2_000_000,
                "cost_usd": 12.5,
                "cost_source": "estimated_from_provider_token_usage",
                "warnings": 1,
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.telemetry",
            actor_login="maya",
            repo_name="ravichanduummadisetti/skilgen",
            resource_type="claude_code",
            created_at=NOW - timedelta(minutes=5),
            metadata_json={
                "provider": "Claude Code",
                "model": "claude-opus-4-7",
                "session_id": "claude-1",
                "activity_metrics": {"explored_files": 3, "commands": 2, "tool_calls": 4},
                "mcp_tools": ["github:create_pr"],
                "tokens_total": 1_000_000,
                "cost_usd": 9.25,
                "cost_source": "provider_reported",
            },
        ),
    ]
    db = Db([Result(events)])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_retention"] == "metadata-only"
    assert payload["summary"]["providers"] == 2
    assert payload["summary"]["sessions"] == 2
    assert payload["summary"]["tokens_total"] == 3_000_000
    assert payload["summary"]["cost_usd"] == 21.75
    assert payload["summary"]["provider_reported_cost_usd"] == 9.25
    assert payload["summary"]["skillayer_estimated_cost_usd"] == 12.5
    assert payload["summary"]["top_provider"] == "Codex"
    rows = {row["provider"]: row for row in payload["platforms"]}
    assert rows["Codex"]["full_access_events"] == 1
    assert rows["Codex"]["risk_signals"] == 1
    assert rows["Claude Code"]["mcp_tool_calls"] == 1
    assert any(item["title"] == "Cost provenance" for item in payload["insights"])


def test_developer_track_rolls_up_metadata_only_agent_work_by_actor(monkeypatch) -> None:
    events = [
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="acme/payments",
            resource_type="codex_cli",
            created_at=NOW,
            metadata_json={
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
                "session_id": "sess-1",
                "access_scope": "full-access",
                "full_access": True,
                "autonomous_access": True,
                "tool_permissions": ["shell", "apply_patch"],
                "mcp_tools": ["github:create_pr"],
                "file_targets": ["apps/api/router.py", "apps/dashboard/page.tsx"],
                "policy_decision": "deny",
                "violations": ["full-access-prod"],
                "warnings": 2,
                "tokens_input": 1200,
                "tokens_output": 800,
                "cost_usd": 0.42,
                "latency_ms": 1500,
                "error_count": 1,
                "source_record_type": "operational-telemetry",
                "raw_prompt": "must not be returned",
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.telemetry",
            actor_login="ravi",
            repo_name="acme/api",
            resource_type="codex_cli",
            created_at=NOW - timedelta(minutes=3),
            metadata_json={
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "session_id": "sess-1",
                "tool_calls": 3,
                "file_targets": ["apps/api/router.py"],
                "policy_decision": "allow",
                "tokens_total": 500,
                "source_record_type": "compliance-log",
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="maya",
            repo_name="acme/docs",
            resource_type="cursor",
            created_at=NOW - timedelta(minutes=5),
            metadata_json={
                "provider": "Cursor",
                "model": "claude-sonnet",
                "session_id": "sess-2",
                "tool_calls": 1,
                "policy_decision": "allow",
                "tokens_total": 100,
            },
        ),
    ]
    db = Db([Result(events)])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/developer-track")

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_retention"] == "metadata-only"
    assert payload["summary"]["developers"] == 2
    assert payload["summary"]["events"] == 3
    assert payload["summary"]["sessions"] == 2
    ravi = payload["developers"][0]
    assert ravi["actor_login"] == "ravi"
    assert ravi["events"] == 2
    assert ravi["sessions"] == 1
    assert ravi["providers"] == ["Codex CLI"]
    assert sorted(ravi["repos"]) == ["acme/api", "acme/payments"]
    assert ravi["tool_calls"] == 5
    assert ravi["mcp_tool_calls"] == 1
    assert ravi["file_targets"] == 2
    assert ravi["full_access_events"] == 1
    assert ravi["autonomous_events"] == 1
    assert ravi["denials"] == 1
    assert ravi["approvals"] == 1
    assert ravi["warnings"] == 2
    assert ravi["violations"] == 1
    assert ravi["errors"] == 1
    assert ravi["tokens_total"] == 2500
    assert ravi["risk_band"] == "high"
    assert ravi["top_tools"][0]["key"] == "apply_patch"
    assert "raw_prompt" not in ravi


def test_codex_runs_show_background_activity_metrics(monkeypatch) -> None:
    events = [
        SimpleNamespace(
            id="audit-1",
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_id="repo_1",
            repo_name="ravichanduummadisetti/skilgen",
            resource_type="agent_run",
            resource_id="turn-1",
            created_at=NOW,
            metadata_json={
                "provider": "Codex Desktop",
                "model": "gpt-5.5",
                "reasoning_tier": "medium",
                "reasoning_mode": "normal",
                "session_id": "turn-1",
                "access_scope": "full-access",
                "full_access": True,
                "activity_metrics": {"edited_files": 3, "explored_files": 8, "searches": 4, "lists": 2, "commands": 7, "tool_calls": 9, "mcp_tools": 1},
                "activity_details": {"edited_files": ["apps/api/router.py"], "explored_files": ["apps/api/models.py"], "searches": ["rg TODO apps"], "commands": ["rg TODO apps"], "tools": ["exec_command"]},
                "tool_permissions": ["exec_command", "apply_patch"],
                "mcp_tools": ["browser"],
                "file_targets": ["apps/api/router.py", "apps/dashboard/page.tsx"],
                "tokens_input": 1000,
                "tokens_output": 500,
                "cost_usd": 0.25,
                "task_type": "coding-agent-session",
                "outcome": "success",
                "raw_prompt": "must not be returned",
            },
        )
    ]
    db = Db([Result(events)])

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/codex-runs")

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_retention"] == "metadata-only"
    assert payload["summary"]["runs"] == 1
    assert payload["summary"]["edited_files"] == 3
    assert payload["summary"]["explored_files"] == 8
    assert payload["summary"]["searches"] == 4
    assert payload["summary"]["lists"] == 2
    assert payload["summary"]["commands"] == 7
    assert payload["summary"]["tool_calls"] == 9
    run = payload["runs"][0]
    assert run["activity_metrics"]["commands"] == 7
    assert run["activity_details"]["edited_files"] == ["apps/api/router.py"]
    assert run["activity_details"]["searches"] == ["rg TODO apps"]
    assert run["full_access"] is True
    assert run["replay_url"] == "/activity/replay/turn-1?repo=repo_1"
    assert run["git_url"] is None
    assert "raw_prompt" not in run


def test_provider_coverage_rolls_up_configured_connectors_and_retention_risk(monkeypatch) -> None:
    org = SimpleNamespace(
        id="org_1",
        settings={
            "v8_agent_compliance_connectors": {
                "openai-compliance": {
                    "enabled": True,
                    "cursor": "cursor-1",
                    "last_sync_status": "success",
                    "last_sync_requested_at": "2026-05-04T10:00:00",
                },
                "codex-cli": {
                    "enabled": True,
                    "cursor": "cursor-2",
                    "last_sync_status": "success",
                },
                "cursor": {
                    "enabled": True,
                    "last_sync_status": "pending",
                },
            }
        },
    )
    events = [
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="ravi",
            repo_name="acme/payments",
            resource_type="openai_compliance",
            created_at=NOW - timedelta(days=29),
            metadata_json={
                "connector_id": "openai-compliance",
                "provider": "OpenAI Compliance Platform",
                "model": "gpt-5.2",
                "intelligence_tier": "very-high",
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.compliance",
            actor_login="maya",
            repo_name="acme/api",
            resource_type="codex_cli",
            created_at=NOW - timedelta(hours=2),
            metadata_json={
                "connector_id": "codex-cli",
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "high",
            },
        ),
        SimpleNamespace(
            org_id="org_1",
            event_type="agent.telemetry",
            actor_login="maya",
            repo_name="acme/api",
            resource_type="codex_cli",
            created_at=NOW - timedelta(hours=3),
            metadata_json={
                "connector_id": "codex-cli",
                "provider": "Codex CLI",
                "model": "gpt-5.2",
                "intelligence_tier": "high",
            },
        ),
    ]
    db = Db([Result(events)], org=org)

    response = _client(db, monkeypatch).get("/v8/orgs/org_1/insights/provider-coverage")

    assert response.status_code == 200
    payload = response.json()
    rows = {row["connector_id"]: row for row in payload["rows"]}
    assert payload["content_retention"] == "metadata-only"
    assert rows["openai-compliance"]["status"] == "retention-risk"
    assert rows["openai-compliance"]["retention_days_remaining"] == 1
    assert rows["openai-compliance"]["last_cursor"] == "cursor-1"
    assert rows["codex-cli"]["status"] == "active"
    assert rows["codex-cli"]["events"] == 2
    assert rows["codex-cli"]["users"] == 1
    assert rows["codex-cli"]["intelligence_tiers"] == {"high": 2}
    assert rows["cursor"]["status"] == "silent"
    assert rows["anthropic-compliance"]["status"] == "unconfigured"
