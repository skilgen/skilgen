import os
import unittest

from skilgen.agents.model_registry import resolve_model_settings
from skilgen.core.models import SkilgenConfig


class ModelRegistryTests(unittest.TestCase):
    def test_resolve_model_settings_uses_provider_defaults(self) -> None:
        config = SkilgenConfig(
            include_paths=["."],
            exclude_paths=[],
            domains_override=[],
            skill_depth=2,
            update_trigger="manual",
            langsmith_project=None,
            model_provider="openai",
            model="gpt-5",
            api_key_env=None,
            model_retry_attempts=4,
            model_retry_base_delay_seconds=1.5,
        )
        settings = resolve_model_settings(config)
        self.assertEqual(settings.provider, "openai")
        self.assertEqual(settings.model, "gpt-5")
        self.assertEqual(settings.api_key_env, "OPENAI_API_KEY")
        self.assertEqual(settings.retry_attempts, 4)
        self.assertEqual(settings.retry_base_delay_seconds, 1.5)

    def test_resolve_model_settings_reports_api_key_presence(self) -> None:
        os.environ["TEST_MODEL_KEY"] = "present"
        config = SkilgenConfig(
            include_paths=["."],
            exclude_paths=[],
            domains_override=[],
            skill_depth=2,
            update_trigger="manual",
            langsmith_project=None,
            model_provider="custom",
            model="local-model",
            api_key_env="TEST_MODEL_KEY",
            model_retry_attempts=3,
            model_retry_base_delay_seconds=1.0,
        )
        settings = resolve_model_settings(config)
        self.assertTrue(settings.api_key_present)


if __name__ == "__main__":
    unittest.main()
