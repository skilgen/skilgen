from __future__ import annotations

from types import SimpleNamespace

from apps.api.api.services.manifest import build_manifest, verify_manifest


def _objects():
    pr = SimpleNamespace(github_pr_number=42, title="Add auth guard")
    repo = SimpleNamespace(full_name="acme/api")
    attribution = SimpleNamespace(
        primary_agent="codex",
        confidence=0.9,
        sessions=["session_1"],
        skills_loaded=["auth", "testing"],
        skills_violated=[
            {
                "skill_name": "auth",
                "severity": "critical",
                "file_path": "src/auth.py",
                "line_number": 12,
                "message": "JWT stored client-side",
            }
        ],
        risk_score=80,
        risk_tier="red",
        risk_breakdown={"violations": {"points": 40}},
    )
    return pr, repo, attribution


def test_manifest_build_and_verify() -> None:
    pr, repo, attribution = _objects()

    manifest = build_manifest(pr=pr, repo=repo, attribution=attribution, org_api_key="sk-test", policy_outcome="blocked")

    assert manifest["version"] == "1"
    assert manifest["policy_outcome"] == "blocked"
    assert manifest["signature"]
    assert verify_manifest(manifest, "sk-test") is True


def test_manifest_wrong_key_fails_without_mutating_payload() -> None:
    pr, repo, attribution = _objects()
    manifest = build_manifest(pr=pr, repo=repo, attribution=attribution, org_api_key="sk-test")
    original_signature = manifest["signature"]

    assert verify_manifest(manifest, "wrong-key") is False
    assert manifest["signature"] == original_signature
