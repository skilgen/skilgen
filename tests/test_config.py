from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_config_reads_lists_and_scalars(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skilgen.yml").write_text(
                "\n".join(
                    [
                        "include_paths:",
                        "  - src",
                        "exclude_paths:",
                        "  - .git",
                        "domains_override:",
                        "  - backend",
                        "skill_depth: 3",
                        "update_trigger: watch",
                        "langsmith_project: skilgen-dev",
                        "model_provider: gemini",
                        "model: gpt-5",
                        "api_key_env: CUSTOM_OPENAI_KEY",
                        "model_temperature: 0.2",
                        "model_max_tokens: 2048",
                        "model_retry_attempts: 5",
                        "model_retry_base_delay_seconds: 2.5",
                    ]
                ),
                encoding="utf-8",
            )
            config = load_config(root)
            self.assertEqual(config.include_paths, ["src"])
            self.assertEqual(config.exclude_paths, [".git"])
            self.assertEqual(config.domains_override, ["backend"])
            self.assertEqual(config.skill_depth, 3)
            self.assertEqual(config.update_trigger, "watch")
            self.assertEqual(config.langsmith_project, "skilgen-dev")
            self.assertEqual(config.model_provider, "gemini")
            self.assertEqual(config.model, "gpt-5")
            self.assertEqual(config.api_key_env, "CUSTOM_OPENAI_KEY")
            self.assertEqual(config.model_temperature, 0.2)
            self.assertEqual(config.model_max_tokens, 2048)
            self.assertEqual(config.model_retry_attempts, 5)
            self.assertEqual(config.model_retry_base_delay_seconds, 2.5)


if __name__ == "__main__":
    unittest.main()
