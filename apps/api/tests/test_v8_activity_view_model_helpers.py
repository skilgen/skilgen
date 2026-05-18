from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from apps.api.api.v8.activity.view_model import (
    normalized_outcome,
    risk_reasons,
    session_feed_event_view,
)


def test_normalized_outcome_standardizes_variants() -> None:
    assert normalized_outcome("succeeded") == "success"
    assert normalized_outcome("success") == "success"
    assert normalized_outcome("completed") == "success"
    assert normalized_outcome("allowed") == "success"
    assert normalized_outcome("failed") == "failed"
    assert normalized_outcome("error") == "failed"
    assert normalized_outcome("denied") == "denied"
    assert normalized_outcome("blocked") == "blocked"
    assert normalized_outcome("running") == "in_progress"
    assert normalized_outcome("in-progress") == "in_progress"
    # None + no end time => still in progress
    assert normalized_outcome(None, ended=None) == "in_progress"
    # None + end time => unknown
    assert normalized_outcome(None, ended=datetime(2026, 5, 1, 12, 0, 0)) == "unknown"


def test_risk_reasons_builds_explanation_list() -> None:
    reasons = risk_reasons(
        action_class="exec",
        sensitivity_tier="restricted",
        file_scope=["a.py", "b.py", "a.py"],  # duplicate dropped
        signature_status="unsigned",
        outcome="denied",
    )

    # action class is the first item
    assert reasons[0] == "exec activity"
    # sensitivity tier present because it's not "public"
    assert "restricted repository" in reasons
    # file count is pluralized and de-duplicated
    assert "2 file targets" in reasons
    # signature status is included because it is not "verified" / "none"
    assert "unsigned skill context" in reasons
    # outcome included because it is denied/blocked/failed
    assert "denied outcome" in reasons


def test_risk_reasons_omits_public_and_verified_and_allowed() -> None:
    reasons = risk_reasons(
        action_class="read",
        sensitivity_tier="public",
        file_scope=["single.py"],
        signature_status="verified",
        outcome="allowed",
    )

    assert reasons[0] == "read activity"
    # No sensitivity reason for public tier
    assert not any("public" in reason for reason in reasons)
    # Pluralization: exactly 1 file => "1 file target" (no 's')
    assert "1 file target" in reasons
    # No signature reason because it's verified
    assert not any("skill context" in reason for reason in reasons)
    # No outcome reason because it's allowed
    assert not any("outcome" in reason for reason in reasons)


def test_session_feed_event_view_enriches_session_snapshot() -> None:
    session = SimpleNamespace(
        id="sess_db",
        session_id="sess_ext",
        repo_id="repo_1",
        agent_runtime="claude_code",
        engineer_login="ravi",
        session_start=datetime(2026, 5, 5, 1, 0, 0),
        session_end=datetime(2026, 5, 5, 2, 0, 0),
        created_at=datetime(2026, 5, 5, 1, 0, 0),
        last_artifact_at=datetime(2026, 5, 5, 1, 30, 0),
        duration_minutes=60,
        files_touched=["src/app.py"],
        skills_loaded=["security"],
        skill_paths_loaded=[],
        produced_artifacts=[{"tool": "Write", "file_path": "src/app.py"}],
        code_produced="print('hi')",
        outcome="denied",
        task_description="Incident INC-91",
        notes=None,
    )
    repo = SimpleNamespace(id="repo_1", name="api", full_name="acme/api", sensitivity_tier="confidential")
    skill = SimpleNamespace(id="skill_1", domain="security", content_hash="abc", signature_status=None)
    compliance = {
        "tokens_total": 4242,
        "cost_usd": 1.23,
        "model": "claude-sonnet-4-7",
        "intelligence_tier": "high",
        "access_scope": "scoped",
        "activity_metrics": {"prompts": 3},
        "activity_details": {"notes": "ok"},
    }

    payload = session_feed_event_view(session, repo, {"security": skill}, compliance)

    # normalized outcome from "denied"
    assert payload["outcome"] == "denied"
    # risk_reasons must be a non-empty list and include the denied outcome
    assert isinstance(payload["risk_reasons"], list)
    assert "denied outcome" in payload["risk_reasons"]
    # tokens, cost, model surfaced from compliance dict
    assert payload["tokens_total"] == 4242
    assert payload["cost_usd"] == 1.23
    assert payload["model"] == "claude-sonnet-4-7"
    # session_feed_event_view always projects the session
    assert payload["id"] == "session:sess_db"
    assert payload["agent"] == "Claude Code"
