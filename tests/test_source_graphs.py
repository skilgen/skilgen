from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.source_graphs import (
    build_call_graph,
    build_config_runtime_graph,
    build_parser_summary,
    build_symbol_graph,
    build_symbol_relationships,
    build_test_mapping,
)
from skilgen.agents.language_parsers import parse_language_evidence


class SourceGraphTests(unittest.TestCase):
    def test_source_graphs_capture_symbols_calls_runtime_and_tests(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "billing_service.py").write_text(
                "import os\n\nclass BillingService:\n    pass\n\ndef run_sync():\n    notify_slack()\n    return True\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_billing_service.py").write_text(
                "from src.billing_service import run_sync\n\ndef test_run_sync():\n    assert run_sync()\n",
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                'name = "demo"\n[tool.demo]\nservice = "postgres"\napi_key = "OPENAI_API_KEY"\n',
                encoding="utf-8",
            )

            symbols = build_symbol_graph(root)
            calls = build_call_graph(root)
            runtime = build_config_runtime_graph(root)
            mapping = build_test_mapping(root)
            parser_summary = build_parser_summary(root)

            self.assertIn("src/billing_service.py", symbols)
            self.assertIn("class BillingService", symbols["src/billing_service.py"])
            self.assertIn("function run_sync", symbols["src/billing_service.py"])
            self.assertIn("src/billing_service.py", calls)
            self.assertIn("notify_slack", calls["src/billing_service.py"])
            self.assertIn("src/billing_service.py", parser_summary)
            self.assertEqual(parser_summary["src/billing_service.py"]["language"], "python")
            self.assertIn(parser_summary["src/billing_service.py"]["backend"], {"python-ast", "tree-sitter", "regex"})
            self.assertIn("pyproject.toml", runtime)
            self.assertIn("env:OPENAI_API_KEY", runtime["pyproject.toml"])
            self.assertIn("runtime:postgres", runtime["pyproject.toml"])
            self.assertIn("tests/test_billing_service.py", mapping)
            self.assertIn("src/billing_service.py", mapping["tests/test_billing_service.py"])

    def test_symbol_relationships_resolve_cross_file_inheritance(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "base.py").write_text("class BaseService:\n    pass\n", encoding="utf-8")
            (root / "src" / "billing.py").write_text(
                "from .base import BaseService\n\nclass BillingService(BaseService):\n    pass\n",
                encoding="utf-8",
            )

            relationships = build_symbol_relationships(root)

            self.assertTrue(relationships)
            extends = relationships[0]
            self.assertEqual(extends.source_symbol, "BillingService")
            self.assertEqual(extends.relationship, "extends")
            self.assertEqual(extends.target_symbol, "BaseService")
            self.assertEqual(extends.target_path, "src/base.py")

    def test_parser_supports_long_tail_languages(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "analysis.r": "score <- function(x) { x + 1 }\n",
                "Pipeline.hs": "module Pipeline where\nrun value = value\n",
                "core.ml": "type model = { id: int }\nlet run value = value\n",
                "App.fs": "type BillingService() = class end\n",
            }
            for name, content in files.items():
                path = root / name
                path.write_text(content, encoding="utf-8")
                parsed = parse_language_evidence(path)
                self.assertNotEqual(parsed.language, "unknown")


if __name__ == "__main__":
    unittest.main()
