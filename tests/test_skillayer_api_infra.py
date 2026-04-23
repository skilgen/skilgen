from __future__ import annotations

import hashlib
import hmac

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from apps.api.api import auth
from apps.api.api.index import app
from apps.api.api.routes.webhook import _verify_github_signature
from packages.db.config import settings
from packages.db.models import Base, Org, Repo


def test_health_reports_degraded_without_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["db"] == "error"


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
    assert hasattr(Org, "score_threshold")


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
