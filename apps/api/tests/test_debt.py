from __future__ import annotations

from apps.api.api.routes.orgs import DebtGapGenerateRequest, _coverage_gap_id


def test_coverage_gap_id_is_stable() -> None:
    first = _coverage_gap_id("org-1", "repo-1", "security_compliance", "missing")
    second = _coverage_gap_id("org-1", "repo-1", "security_compliance", "missing")

    assert first == second


def test_debt_gap_generate_request_modes() -> None:
    preview = DebtGapGenerateRequest(mode="preview")
    push = DebtGapGenerateRequest(mode="push")

    assert preview.mode == "preview"
    assert push.mode == "push"
