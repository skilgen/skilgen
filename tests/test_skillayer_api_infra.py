from __future__ import annotations

from datetime import datetime
import hashlib
import hmac

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from apps.api.api import auth
from apps.api.api.index import app
from apps.api.api.routes import metrics
from apps.api.api.routes.webhook import _verify_github_signature
from packages.db.config import settings
from packages.db.models import Base, Repo


class FakeMetricsResult:
    """Small SQLAlchemy result double for metrics route tests."""

    def __init__(self, value: object | None = None) -> None:
        self.value = value

    def scalar_one(self) -> object | None:
        """Return the configured scalar value."""
        return self.value

    def scalar_one_or_none(self) -> object | None:
        """Return the configured optional scalar value."""
        return self.value


class FakeMetricsDb:
    """Async database double that returns metrics query results in order."""

    def __init__(self, values: list[object | None]) -> None:
        self.values = values
        self.query_count = 0

    async def execute(self, _statement: object) -> FakeMetricsResult:
        """Return the next configured query result."""
        self.query_count += 1
        return FakeMetricsResult(self.values.pop(0))


class FakeMetricsSession:
    """Async context manager that yields a fake metrics database."""

    def __init__(self, db: FakeMetricsDb) -> None:
        self.db = db

    async def __aenter__(self) -> FakeMetricsDb:
        """Return the configured fake database."""
        return self.db

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        """Exit the fake context manager without suppressing errors."""
        return None


def test_health_reports_degraded_without_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["db"] == "error"


def test_health_endpoint_is_excluded_from_request_logs(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """Health probes should not emit structured request log records."""
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    caplog.set_level("INFO", logger="skillayer.api")

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert all('"/health"' not in record.getMessage() for record in caplog.records)


def test_metrics_endpoint_returns_public_cached_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """The metrics endpoint should be unauthenticated and reuse cached count data."""
    metrics._cached_metrics = None
    last_run_at = datetime(2026, 4, 23, 12, 30, 0)
    db = FakeMetricsDb([7, 11, 2, 4, 83.5, last_run_at])
    monkeypatch.setattr(metrics, "AsyncSessionLocal", lambda: FakeMetricsSession(db))
    try:
        client = TestClient(app)
        first = client.get("/metrics")
        second = client.get("/metrics")
    finally:
        metrics._cached_metrics = None

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["total_analysis_runs"] == 7
    assert first.json()["total_skills"] == 11
    assert first.json()["total_orgs"] == 2
    assert first.json()["total_repos"] == 4
    assert first.json()["avg_score"] == 83.5
    assert first.json()["last_run_at"] == "2026-04-23T12:30:00Z"
    assert db.query_count == 6


def test_metrics_endpoint_returns_structured_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Metrics failures should return a stable structured error payload."""
    metrics._cached_metrics = None
    monkeypatch.setattr(metrics, "AsyncSessionLocal", lambda: (_ for _ in ()).throw(RuntimeError("no db")))
    response = TestClient(app).get("/metrics")

    metrics._cached_metrics = None
    assert response.status_code == 503
    assert response.json() == {"detail": {"detail": "Unable to load metrics", "code": "METRICS_UNAVAILABLE"}}


def test_github_webhook_signature_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "GITHUB_WEBHOOK_SECRET", "secret")
    body = b'{"ok":true}'
    signature = "sha256=" + hmac.new(b"secret", body, hashlib.sha256).hexdigest()

    _verify_github_signature(body, signature)

    with pytest.raises(HTTPException) as exc:
        _verify_github_signature(body, "sha256=bad")
    assert exc.value.status_code == 401


def test_shared_db_metadata_contains_skillayer_tables() -> None:
    assert {"orgs", "repos", "analysis_runs", "skills", "score_history"}.issubset(Base.metadata.tables)
    assert hasattr(Repo, "github_installation_id")


def test_selfhosted_oidc_jwks_uri_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OIDC_ISSUER_URL", "https://auth.example.com/")
    monkeypatch.setattr(settings, "OIDC_JWKS_URI", "")

    assert auth._oidc_jwks_uri() == "https://auth.example.com/.well-known/jwks.json"


def test_selfhosted_oidc_requires_issuer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OIDC_ISSUER_URL", "")

    with pytest.raises(HTTPException) as exc:
        auth._oidc_jwks_uri()
    assert exc.value.status_code == 500


@pytest.mark.anyio
async def test_auth_mode_switches_to_selfhosted_oidc(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_verify_oidc_token(token: str) -> dict[str, str]:
        return {"sub": token}

    monkeypatch.setattr(settings, "DEPLOYMENT_MODE", "selfhosted")
    monkeypatch.setattr(auth, "_verify_oidc_token", fake_verify_oidc_token)

    claims = await auth.get_current_user(type("Credentials", (), {"credentials": "token"})())

    assert claims == {"sub": "token"}
