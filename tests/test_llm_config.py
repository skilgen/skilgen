from __future__ import annotations

import unittest

from apps.api.api.services import llm_config


class LLMConfigTests(unittest.TestCase):
    def test_key_hint_shows_last_four_chars_only(self) -> None:
        self.assertEqual(llm_config.key_hint("sk-ant-test"), "...test")

    def test_key_is_encrypted_and_decryptable(self) -> None:
        encrypted = llm_config.encrypt_key("sk-ant-test")
        self.assertNotEqual(encrypted, b"sk-ant-test")
        self.assertEqual(llm_config.decrypt_key(encrypted), "sk-ant-test")

    def test_skillayer_save_clears_key_source(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn('payload.provider == "skillayer"', source)
        self.assertIn("config.api_key_encrypted = None", source)
        self.assertIn("config.api_key_hint = None", source)

    def test_save_without_api_key_preserves_key_source(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn("elif payload.api_key", source)
        self.assertIn("bool(config.api_key_encrypted or payload.endpoint_url)", source)

    def test_raw_api_key_is_not_in_response_schema(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        schema = source[source.index("class OrgLLMConfigResponse"):source.index("class LLMConfigUpdate")]
        self.assertNotIn("api_key:", schema)
        self.assertNotIn("api_key_encrypted", schema)

    def test_audit_metadata_uses_hint_not_key(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn('"api_key_hint": config.api_key_hint', source)
        self.assertNotIn('"api_key": payload.api_key', source)

    def test_anthropic_test_connection_uses_httpx(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn("https://api.anthropic.com/v1/messages", source)
        self.assertIn("httpx.AsyncClient(timeout=10.0)", source)

    def test_analysis_uses_configured_llm_environment(self) -> None:
        source = open("apps/api/api/analysis.py", encoding="utf-8").read()
        self.assertIn("get_repo_llm_config", source)
        self.assertIn("configured_llm_environment", source)


if __name__ == "__main__":
    unittest.main()
