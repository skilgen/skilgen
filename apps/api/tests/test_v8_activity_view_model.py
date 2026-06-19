from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from apps.api.api.v8.activity.view_model import feed_event_view, replay_timeline, repo_sensitivity_tier, risk_band, risk_score, session_view


def test_repo_sensitivity_defaults_to_internal() -> None:
    assert repo_sensitivity_tier(SimpleNamespace(name="demo")) == "internal"
    assert repo_sensitivity_tier(SimpleNamespace(settings={"sensitivity_tier": "restricted"})) == "restricted"


def test_feed_event_view_enriches_skill_and_risk_context() -> None:
    event = SimpleNamespace(id="evt_1", repo_id="repo_1", skill_id="skill_1", agent_runtime="codex", session_id="sess_ext", loaded_at=datetime(2026, 5, 5, 4, 0, 0))
    repo = SimpleNamespace(id="repo_1", full_name="acme/payments", sensitivity_tier="confidential")
    skill = SimpleNamespace(id="skill_1", domain="deploy-staging@v3.1.0", content_hash="abc")
    session = SimpleNamespace(id="sess_db", engineer_login="ravi", files_touched=["k8s/staging/app.yaml"], task_description="Jira PAY-4421", notes=None)

    payload = feed_event_view(event, repo, skill, session)

    assert payload["agent"] == "Codex"
    assert payload["skill_id"] == "skill_1"
    assert payload["skill_signature_status"] == "verified"
    assert payload["repo_sensitivity_tier"] == "confidential"
    assert payload["trigger"] == {"label": "PAY-4421", "url": None}
    assert payload["risk_score"] > 0


def test_session_view_builds_replay_url_and_risk_band() -> None:
    session = SimpleNamespace(
        id="sess_db",
        session_id="sess_ext",
        repo_id="repo_1",
        agent_runtime="claude_code",
        engineer_login="ravi",
        session_start=datetime(2026, 5, 5, 1, 0, 0),
        session_end=None,
        created_at=datetime(2026, 5, 5, 1, 0, 0),
        duration_minutes=9,
        files_touched=["src/app.py", "infra/main.tf"],
        skills_loaded=["security"],
        skill_paths_loaded=[],
        produced_artifacts=[{"tool": "Write"}],
        outcome="success",
        task_description="Incident INC-91",
        notes=None,
    )
    repo = SimpleNamespace(id="repo_1", name="api", sensitivity_tier="restricted")
    skill = SimpleNamespace(id="skill_1", domain="security", skill_path="skills/security/SKILL.md", content_hash=None)

    payload = session_view(session, repo, {"security": skill})

    assert payload["agent"] == "Claude Code"
    assert payload["replay_url"] == "/activity/replay/sess_db?repo=repo_1"
    assert payload["risk_band"] in {"medium", "high"}


def test_replay_timeline_uses_artifact_steps() -> None:
    session = SimpleNamespace(
        produced_artifacts=[
            {"tool": "Write", "file_path": "src/app.py", "diff": "+print('hi')", "after_hash": "abc", "ts": "2026-05-05T01:00:00Z"},
        ],
        outcome="success",
        transcript_summary="Wrote the app entrypoint.",
        created_at=datetime(2026, 5, 5, 1, 0, 0),
    )
    repo = SimpleNamespace(sensitivity_tier="internal")

    timeline = replay_timeline(session, repo)

    assert timeline[0]["type"] == "session_start"
    edit_step = next(step for step in timeline if step["type"] == "edit")
    assert edit_step["action_class"] == "write"
    assert edit_step["policy_decision"] == "allowed"


def test_risk_score_band_boundaries() -> None:
    assert risk_band(risk_score("read", "internal", [], "verified")) == "low"
    assert risk_band(risk_score("exec", "restricted", ["prod.yaml"] * 10, "unsigned")) == "high"
