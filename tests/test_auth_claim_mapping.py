from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from skilgen.api.server import (
    _claims_allowed_roots,
    _claims_principal,
    _claims_scope,
    _claims_tenant,
    _provider_claim_mapping,
)


class OidcClaimMappingTests(unittest.TestCase):
    def test_okta_group_scope_and_roots_mapping(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            env = {
                "SKILGEN_API_OIDC_PROVIDER": "okta",
                "SKILGEN_API_OIDC_GROUP_SCOPE_MAP": '{"Skilgen-Admins":"admin"}',
                "SKILGEN_API_OIDC_GROUP_ROOTS_MAP": json_dumps({"RepoAccess": [str(root)]}),
            }
            claims = {
                "preferred_username": "okta.user@example.com",
                "groups": ["Skilgen-Admins", "RepoAccess"],
                "sub": "okta-subject",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                mapping = _provider_claim_mapping()
                self.assertEqual(_claims_principal(claims, mapping), "okta.user@example.com")
                self.assertEqual(_claims_scope(claims, mapping), "admin")
                self.assertEqual(_claims_allowed_roots(claims, mapping), (root,))

    def test_entra_roles_and_tenant_mapping(self) -> None:
        claims = {
            "preferred_username": "entra.user@example.com",
            "roles": ["Skilgen.Admin"],
            "tid": "tenant-entra",
            "sub": "entra-subject",
        }
        with mock.patch.dict(os.environ, {"SKILGEN_API_OIDC_PROVIDER": "entra"}, clear=False):
            mapping = _provider_claim_mapping()
            self.assertEqual(_claims_principal(claims, mapping), "entra.user@example.com")
            self.assertEqual(_claims_scope(claims, mapping), "admin")
            self.assertEqual(_claims_tenant(claims, mapping), "tenant-entra")

    def test_auth0_namespaced_claims_mapping(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            namespace = "https://skilgen.example.com"
            claims = {
                "email": "auth0.user@example.com",
                f"{namespace}/roles": ["platform-admin"],
                f"{namespace}/roots": [str(root)],
                f"{namespace}/tenant": "tenant-auth0",
                "sub": "auth0|123",
            }
            env = {
                "SKILGEN_API_OIDC_PROVIDER": "auth0",
                "SKILGEN_API_OIDC_AUTH0_NAMESPACE": namespace,
                "SKILGEN_API_OIDC_GROUP_SCOPE_MAP": '{"platform-admin":"admin"}',
            }
            with mock.patch.dict(os.environ, env, clear=False):
                mapping = _provider_claim_mapping()
                self.assertEqual(_claims_principal(claims, mapping), "auth0.user@example.com")
                self.assertEqual(_claims_scope(claims, mapping), "admin")
                self.assertEqual(_claims_allowed_roots(claims, mapping), (root,))
                self.assertEqual(_claims_tenant(claims, mapping), "tenant-auth0")


def json_dumps(value: object) -> str:
    import json

    return json.dumps(value)


if __name__ == "__main__":
    unittest.main()
