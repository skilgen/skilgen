import asyncio

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


def test_workos_token_verification_does_not_require_audience_match(monkeypatch):
    decode_calls = []

    monkeypatch.setattr(auth.jwt, "get_unverified_header", lambda token: {"kid": "kid_1", "alg": "RS256"})
    monkeypatch.setattr(auth.jwt, "get_unverified_claims", lambda token: {"iss": "https://tenant.authkit.app", "aud": "different-audience"})

    async def fake_workos_jwks(issuer):
        return [{"kid": "kid_1"}]

    monkeypatch.setattr(auth, "_workos_jwks", fake_workos_jwks)
    monkeypatch.setattr(auth, "_verify_signature", lambda token, signing_key: None)

    def decode(token, signing_key, **kwargs):
        decode_calls.append(kwargs)
        return {"iss": "https://tenant.authkit.app", "aud": "different-audience", "email": "dev@example.com"}

    monkeypatch.setattr(auth.jwt, "decode", decode)

    payload = asyncio.run(auth._verify_workos_token("signed.workos.token"))

    assert payload["email"] == "dev@example.com"
    assert decode_calls[0]["options"] == {"verify_aud": False}
