import unittest

from skilgen.deep_agents_core import _classify_model_error


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


if __name__ == "__main__":
    unittest.main()
