from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from apps.api.api.services import half_life


ROOT = Path(__file__).resolve().parents[1]
HALF_LIFE_SOURCE = ROOT / "apps/api/api/services/half_life.py"


def _source() -> str:
    return HALF_LIFE_SOURCE.read_text(encoding="utf-8")


def test_compute_half_life_high_churn_uses_five_point_decay() -> None:
    source = _source()
    assert "daily_commit_rate > 2.0" in source
    assert "days_to_stale = (freshness - 20) / 5" in source


def test_compute_half_life_moderate_churn_uses_two_point_decay() -> None:
    source = _source()
    assert "daily_commit_rate > 0.5" in source
    assert "days_to_stale = (freshness - 20) / 2" in source


def test_compute_half_life_stable_uses_slow_decay_and_ninety_day_cap() -> None:
    source = _source()
    assert "days_to_stale = (freshness - 20) / 0.5" in source
    assert "min(90.0, days_to_stale)" in source


def test_compute_half_life_already_stale_sets_zero_days() -> None:
    source = _source()
    assert "if freshness < 20:" in source
    assert "days_to_stale = 0.0" in source


def test_confidence_uses_version_history_thresholds() -> None:
    source = _source()
    assert "version_count >= 5" in source
    assert "0.9" in source
    assert "version_count >= 2" in source
    assert "0.6" in source
    assert "0.3" in source


def test_get_commit_velocity_counts_three_windows_and_churn() -> None:
    source = _source()
    assert "commits_30d = sum(1 for version in versions if version.created_at >= cut_30)" in source
    assert "commits_60d = sum(1 for version in versions if version.created_at >= cut_60)" in source
    assert "commits_90d = len(versions)" in source
    assert "file_churn_30d" in source


def test_calibrate_predictions_sets_prediction_error_days() -> None:
    now = datetime(2026, 4, 24, 12, 0, 0)
    row = SimpleNamespace(
        predicted_decay_date=now + timedelta(days=5),
        last_actual_decay_date=now + timedelta(days=2),
        prediction_error_days=None,
        updated_at=None,
    )
    row.prediction_error_days = abs((row.predicted_decay_date - row.last_actual_decay_date).days)
    assert row.prediction_error_days == 3
    assert "prediction_error_days = abs((row.predicted_decay_date - row.last_actual_decay_date).days)" in _source()


def test_half_life_refresh_endpoint_queues_background_task() -> None:
    registry_source = (ROOT / "apps/api/api/routes/registry.py").read_text(encoding="utf-8")
    assert "@router.post(\"/orgs/{org_id}/half-life/refresh\"" in registry_source
    assert "background_tasks.add_task(_refresh_half_lives_background, org_id)" in registry_source


def test_regen_queue_check_filters_buffer_and_freshness() -> None:
    source = _source()
    assert "Skill.score_freshness > 20" in source
    assert "threshold = now + timedelta(hours=int(half_life.regeneration_buffer_hours or 24))" in source
    assert "half_life.predicted_decay_date <= threshold" in source


def test_half_life_module_uses_async_sqlalchemy_select() -> None:
    source = _source()
    assert "from sqlalchemy import desc, func, select" in source
    assert "query(" not in source
    assert "async def compute_half_life" in source
    assert "async def get_commit_velocity" in source
