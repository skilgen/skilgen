from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from skilgen.core.identity_policy_store import (
    get_identity_policy,
    identity_policy_store_path,
    list_identity_policies,
    resolve_identity_policy,
    upsert_identity_policy,
)


class IdentityPolicyStoreTests(unittest.TestCase):
    def test_store_can_persist_and_resolve_provider_policy(self) -> None:
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "identity.sqlite"
            with mock.patch.dict(os.environ, {"SKILGEN_API_IDENTITY_POLICY_DB": str(db_path)}, clear=False):
                upsert_identity_policy(
                    {
                        "provider": "generic",
                        "group_scope_map": {"platform-admin": "admin"},
                    }
                )
                upsert_identity_policy(
                    {
                        "provider": "auth0",
                        "principal_claims": ["email", "sub"],
                        "group_roots_map": {"repo-access": [str(Path(tmp).resolve())]},
                    }
                )
                self.assertEqual(identity_policy_store_path(), db_path.resolve())
                resolved = resolve_identity_policy("auth0")
                self.assertEqual(resolved["provider"], "auth0")
                self.assertEqual(resolved["group_scope_map"], {"platform-admin": "admin"})
                self.assertIn("repo-access", resolved["group_roots_map"])
                stored = get_identity_policy("auth0")
                self.assertIsNotNone(stored)
                self.assertEqual(stored["principal_claims"], ["email", "sub"])
                listed = [item["provider"] for item in list_identity_policies()]
                self.assertEqual(listed, ["auth0", "generic"])


if __name__ == "__main__":
    unittest.main()
