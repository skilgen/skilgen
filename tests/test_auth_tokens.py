from __future__ import annotations

import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from skilgen.core.auth_tokens import SignedTokenError, mint_signed_token, verify_signed_token


class SignedTokenTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
