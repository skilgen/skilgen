import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.deep_agents_core import _build_chat_model, _classify_model_error, runtime_diagnostics


class RuntimeHardeningTests(unittest.TestCase):
    def test_classify_model_error_marks_rate_limit_as_retryable(self) -> None:
        error = _classify_model_error(RuntimeError("429 insufficient_quota"), "openai", "OPENAI_API_KEY")
        self.assertEqual(error["category"], "rate_limit_error")
        self.assertTrue(error["retryable"])
        self.assertIn("quota", " ".join(error["recommendations"]).lower())

    def test_classify_model_error_reports_authentication_fix(self) -> None:
        error = _classify_model_error(RuntimeError("authentication failed: invalid api key"), "anthropic", "ANTHROPIC_API_KEY")
        self.assertEqual(error["category"], "authentication_error")
        self.assertFalse(error["retryable"])
        self.assertIn("ANTHROPIC_API_KEY", error["message"])

    def test_classify_model_error_reports_model_configuration_issue(self) -> None:
        error = _classify_model_error(RuntimeError("model not found"), "google_genai", "GOOGLE_API_KEY")
        self.assertEqual(error["category"], "model_configuration_error")
        self.assertFalse(error["retryable"])
        self.assertIn("google_genai", error["message"])

    def test_runtime_diagnostics_respects_project_provider_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skilgen.yml").write_text(
                "\n".join(
                    [
                        "model_provider: anthropic",
                        "model: claude-sonnet-4-5",
                        "api_key_env: ANTHROPIC_API_KEY",
                    ]
                ),
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
                os.environ.pop("OPENAI_API_KEY", None)
                diagnostics = runtime_diagnostics(root)
            self.assertEqual(diagnostics["provider"], "anthropic")
            self.assertEqual(diagnostics["api_key_env"], "ANTHROPIC_API_KEY")
            self.assertNotEqual(diagnostics["reason"], "Missing model credential environment variable: OPENAI_API_KEY")

    def test_build_chat_model_uses_huggingface_router_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skilgen.yml").write_text(
                "\n".join(
                    [
                        "model_provider: huggingface",
                        "model: meta-llama/Llama-3.1-70B-Instruct",
                        "api_key_env: HUGGINGFACEHUB_API_TOKEN",
                    ]
                ),
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"HUGGINGFACEHUB_API_TOKEN": "test-key"}, clear=False), patch(
                "skilgen.deep_agents_core.init_chat_model"
            ) as mock_init_chat_model:
                mock_init_chat_model.return_value = object()
                _build_chat_model(root)
            mock_init_chat_model.assert_called_once()
            args, kwargs = mock_init_chat_model.call_args
            self.assertEqual(args[0], "openai:meta-llama/Llama-3.1-70B-Instruct")
            self.assertEqual(kwargs["base_url"], "https://router.huggingface.co/v1")
            self.assertEqual(kwargs["api_key"], "test-key")
            self.assertFalse(kwargs["use_responses_api"])


if __name__ == "__main__":
    unittest.main()
