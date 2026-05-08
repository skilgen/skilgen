import pytest
from fastapi import HTTPException

from apps.api.api import auth


def test_workos_jwks_uri_uses_api_issuer(monkeypatch):
    monkeypatch.setattr(auth.settings, "WORKOS_CLIENT_ID", "client_123")

    assert auth._workos_jwks_uri_for_issuer("https://api.workos.com/") == "https://api.workos.com/sso/jwks/client_123"


def test_workos_jwks_uri_accepts_authkit_issuer(monkeypatch):
    monkeypatch.setattr(auth.settings, "WORKOS_CLIENT_ID", "client_123")

    assert auth._workos_jwks_uri_for_issuer("https://inspired-lake-18-staging.authkit.app") == "https://inspired-lake-18-staging.authkit.app/oauth2/jwks"


def test_workos_jwks_uri_rejects_unknown_issuer(monkeypatch):
    monkeypatch.setattr(auth.settings, "WORKOS_CLIENT_ID", "client_123")

    with pytest.raises(HTTPException):
        auth._workos_jwks_uri_for_issuer("https://not-workos.example.com")
