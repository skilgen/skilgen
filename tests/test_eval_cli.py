from __future__ import annotations

import sys

import pytest

from skilgen.cli import main as cli


def run_cli(monkeypatch: pytest.MonkeyPatch, args: list[str], response: object) -> str:
    monkeypatch.setenv("SKILLAYER_API_KEY", "sk-test")
    monkeypatch.setattr(cli, "_eval_api_request", lambda *a, **k: response)
    monkeypatch.setattr(sys, "argv", ["skilgen", *args])
    cli.main()
    return ""


def test_eval_record_success_posts(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli(monkeypatch, ["eval", "record", "--outcome", "success", "--repo-id", "repo_1"], {"task_id": "t1", "gaps_detected": False})
    assert "Task recorded (success)" in capsys.readouterr().out


def test_eval_record_failure_warns_on_gap(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli(monkeypatch, ["eval", "record", "--outcome", "failure", "--repo-id", "repo_1"], {"task_id": "t1", "gaps_detected": True})
    assert "New skill gap detected" in capsys.readouterr().out


def test_eval_status_prints_roi(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli(monkeypatch, ["eval", "status", "--repo-id", "repo_1"], {"total_tasks": 47, "success_rate": 0.72, "high_skill_success_rate": 0.91, "low_skill_success_rate": 0.38, "multiplier": 2.4, "skill_gaps": []})
    assert "Tasks (30d): 47" in capsys.readouterr().out


def test_eval_gaps_lists_commands(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli(monkeypatch, ["eval", "gaps", "--repo-id", "repo_1"], [{"domain": "auth", "failure_count": 3, "gap_type": "weak_skill", "suggested_action": "Improve skill quality"}])
    assert "Improve skill quality" in capsys.readouterr().out
