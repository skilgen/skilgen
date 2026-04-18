from __future__ import annotations

import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from skilgen.core.auth_tokens import (
    SignedTokenError,
    clear_remote_verifier_caches,
    mint_signed_token,
    verify_jwks_token,
    verify_oidc_token,
    verify_signed_token,
)
from tests.oidc_test_utils import LocalOidcServer, generate_rsa_signing_material, mint_rs256_token


class SignedTokenTests(unittest.TestCase):
    def tearDown(self) -> None:
        clear_remote_verifier_caches()

    def test_round_trip_signed_token(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            token = mint_signed_token(
                "secret-signing-key",
                principal="ci-service",
                scope="write",
                ttl_seconds=300,
                allowed_project_roots=[root],
                tenant="tenant-a",
                issuer="skilgen-tests",
                audience="skilgen-api",
            )
            claims = verify_signed_token(
                token,
                "secret-signing-key",
                issuer="skilgen-tests",
                audience="skilgen-api",
            )
            self.assertEqual(claims["sub"], "ci-service")
            self.assertEqual(claims["scope"], "write")
            self.assertEqual(claims["tenant"], "tenant-a")
            self.assertEqual(claims["roots"], [str(root.resolve())])

    def test_expired_signed_token_is_rejected(self) -> None:
        token = mint_signed_token(
            "secret-signing-key",
            principal="ci-service",
            scope="read",
            expires_at=time.time() - 60,
        )
        with self.assertRaises(SignedTokenError):
            verify_signed_token(token, "secret-signing-key")

    def test_wrong_issuer_or_audience_is_rejected(self) -> None:
        token = mint_signed_token(
            "secret-signing-key",
            principal="ci-service",
            scope="admin",
            ttl_seconds=300,
            issuer="issuer-a",
            audience="audience-a",
        )
        with self.assertRaises(SignedTokenError):
            verify_signed_token(token, "secret-signing-key", issuer="issuer-b", audience="audience-a")
        with self.assertRaises(SignedTokenError):
            verify_signed_token(token, "secret-signing-key", issuer="issuer-a", audience="audience-b")

    def test_round_trip_jwks_token(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_key, jwks = generate_rsa_signing_material(kid="kid-1")
            token = mint_rs256_token(
                private_key,
                kid="kid-1",
                principal="oidc-service",
                scope="admin",
                ttl_seconds=300,
                allowed_project_roots=[root],
                tenant="tenant-oidc",
                issuer="https://issuer.example.com",
                audience="skilgen-api",
            )
            claims = verify_jwks_token(
                token,
                jwks,
                issuer="https://issuer.example.com",
                audience="skilgen-api",
            )
            self.assertEqual(claims["sub"], "oidc-service")
            self.assertEqual(claims["scope"], "admin")
            self.assertEqual(claims["tenant"], "tenant-oidc")
            self.assertEqual(claims["roots"], [str(root.resolve())])

    def test_round_trip_oidc_token_via_discovery(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_key, jwks = generate_rsa_signing_material(kid="kid-2")
            with LocalOidcServer(jwks=jwks) as oidc:
                token = mint_rs256_token(
                    private_key,
                    kid="kid-2",
                    principal="federated-admin",
                    scope="write",
                    ttl_seconds=300,
                    allowed_project_roots=[root],
                    tenant="tenant-federated",
                    issuer=oidc.issuer,
                    audience="skilgen-api",
                )
                claims = verify_oidc_token(
                    token,
                    issuer=oidc.issuer,
                    audience="skilgen-api",
                    timeout_seconds=2,
                    cache_ttl_seconds=60,
                )
                self.assertEqual(claims["sub"], "federated-admin")
                self.assertEqual(claims["scope"], "write")
                self.assertEqual(claims["tenant"], "tenant-federated")

    def test_oidc_rejects_non_https_non_loopback_metadata(self) -> None:
        private_key, _jwks = generate_rsa_signing_material(kid="kid-3")
        token = mint_rs256_token(
            private_key,
            kid="kid-3",
            principal="federated-admin",
            scope="admin",
            ttl_seconds=300,
            issuer="http://identity.example.com/issuer",
            audience="skilgen-api",
        )
        with self.assertRaises(SignedTokenError):
            verify_oidc_token(
                token,
                issuer="http://identity.example.com/issuer",
                audience="skilgen-api",
                jwks_url="http://identity.example.com/jwks.json",
                timeout_seconds=1,
                cache_ttl_seconds=0,
            )


if __name__ == "__main__":
    unittest.main()
