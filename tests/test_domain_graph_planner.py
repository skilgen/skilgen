from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from skilgen.agents.domain_graph_planner import build_domain_graph, build_domain_graph_native
from skilgen.core.requirements import load_requirements, synthesize_requirements_context


class DomainGraphPlannerTests(unittest.TestCase):
    def test_build_domain_graph_infers_platform_domains_for_tool_repo_shapes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "README.md"
            requirements.write_text("Skilgen style tooling repo with backend api and planning.\n", encoding="utf-8")
            (root / "skilgen").mkdir()
            (root / "skilgen" / "__init__.py").write_text("", encoding="utf-8")
            (root / "skilgen" / "sdk.py").write_text("VALUE = 1\n", encoding="utf-8")
            for area, file_name in [
                ("agents", "planner.py"),
                ("core", "score.py"),
                ("cli", "main.py"),
                ("generators", "skills.py"),
            ]:
                directory = root / "skilgen" / area
                directory.mkdir(parents=True)
                (directory / file_name).write_text("def run():\n    return None\n", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "run_requirements_pipeline.py").write_text("print('ok')\n", encoding="utf-8")

            graph = build_domain_graph(root, load_requirements(requirements))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("platform", graph_names)
            self.assertIn("platform-agents", graph_names)
            self.assertIn("platform-core", graph_names)
            self.assertIn("platform-cli", graph_names)
            self.assertIn("platform-generators", graph_names)
            self.assertIn("platform-scripts", graph_names)

    def test_build_domain_graph_uses_src_package_archetype_for_python_sdks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_root = root / "src" / "sample_sdk"
            package_root.mkdir(parents=True)
            for file_name in ["__init__.py", "client.py", "query.py", "types.py", "_errors.py", "version.py"]:
                (package_root / file_name).write_text("VALUE = 1\n", encoding="utf-8")
            (package_root / "_internal").mkdir()
            (package_root / "_internal" / "__init__.py").write_text("", encoding="utf-8")
            (package_root / "_internal" / "transport.py").write_text("def run():\n    return None\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_client.py").write_text("def test_client():\n    assert True\n", encoding="utf-8")
            (root / "e2e-tests").mkdir()
            (root / "e2e-tests" / "test_cli.py").write_text("def test_cli():\n    assert True\n", encoding="utf-8")
            (root / "examples").mkdir()
            (root / "examples" / "basic.py").write_text("from sample_sdk import client\n", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "release.py").write_text("print('release')\n", encoding="utf-8")

            graph = build_domain_graph_native(root, synthesize_requirements_context(root))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("sample-sdk-core", graph_names)
            self.assertIn("sample-sdk-client", graph_names)
            self.assertIn("sample-sdk-errors", graph_names)
            self.assertIn("sample-sdk-internal", graph_names)
            self.assertIn("sample-sdk-testing", graph_names)
            self.assertIn("sample-sdk-e2e", graph_names)
            self.assertIn("sample-sdk-examples", graph_names)
            self.assertIn("sample-sdk-scripts", graph_names)
            self.assertNotIn("backend", graph_names)
            self.assertNotIn("frontend", graph_names)
            self.assertNotIn("security", graph_names)
            self.assertTrue(any("python-package" in item for item in graph.recommendations))

    def test_build_domain_graph_preserves_repo_native_app_surfaces(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory, files in {
                "api": ["server.js", "routes/chat.js", "models/user.js"],
                "client": ["src/App.tsx", "src/components/Chat.tsx", "src/routes/Home.tsx"],
                "packages": ["ui/index.ts", "data/store.ts", "api-client/index.ts"],
                "config": ["i18n.ts"],
                "e2e": ["chat.spec.ts"],
            }.items():
                for file_name in files:
                    path = root / directory / file_name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("export const value = 1;\n", encoding="utf-8")

            graph = build_domain_graph_native(root, synthesize_requirements_context(root))

            graph_names = {node.name for node in graph.nodes}
            for expected in ["api", "client", "packages", "config", "e2e"]:
                self.assertIn(expected, graph_names)
            self.assertIn("client-src", graph_names)
            self.assertNotIn("backend", graph_names)
            self.assertNotIn("frontend", graph_names)
            self.assertTrue(any("repo-native-app" in item for item in graph.recommendations))

    def test_build_domain_graph_uses_workspace_packages_for_pnpm_monorepos(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pnpm-workspace.yaml").write_text("packages:\n  - apps/*\n  - packages/*\n", encoding="utf-8")
            (root / "apps" / "web" / "src").mkdir(parents=True)
            (root / "packages" / "ui" / "src").mkdir(parents=True)
            (root / "apps" / "web" / "package.json").write_text(
                '{"name":"@repo/web","dependencies":{"@repo/ui":"workspace:*"}}',
                encoding="utf-8",
            )
            (root / "packages" / "ui" / "package.json").write_text('{"name":"@repo/ui"}', encoding="utf-8")
            (root / "apps" / "web" / "src" / "index.tsx").write_text("export const App = () => null;\n", encoding="utf-8")
            (root / "packages" / "ui" / "src" / "button.tsx").write_text("export const Button = () => null;\n", encoding="utf-8")

            graph = build_domain_graph_native(root, synthesize_requirements_context(root))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("apps-web", graph_names)
            self.assertIn("packages-ui", graph_names)
            self.assertNotIn("backend", graph_names)
            self.assertNotIn("frontend", graph_names)
            self.assertTrue(any("pnpm-workspace" in item for item in graph.recommendations))

    def test_build_domain_graph_falls_back_to_folder_native_surfaces_for_unknown_repo_shapes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory, files in {
                "engine": ["runner.py", "pipeline/steps.py", "pipeline/graph.py"],
                "connectors": ["github/client.py", "slack/client.py", "registry.py"],
                "auth": ["session.py", "permissions.py", "tokens.py"],
            }.items():
                for file_name in files:
                    path = root / directory / file_name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("def run():\n    return None\n", encoding="utf-8")

            graph = build_domain_graph_native(root, synthesize_requirements_context(root))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("engine", graph_names)
            self.assertIn("engine-pipeline", graph_names)
            self.assertIn("connectors", graph_names)
            self.assertIn("auth", graph_names)
            self.assertNotIn("backend", graph_names)
            self.assertNotIn("frontend", graph_names)
            self.assertNotIn("security", graph_names)
            self.assertTrue(any("folder-native" in item for item in graph.recommendations))

    def test_build_domain_graph_keeps_python_libs_heuristic_as_fallback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "libs" / "alpha" / "alpha").mkdir(parents=True)
            (root / "libs" / "beta" / "beta").mkdir(parents=True)
            (root / "libs" / "alpha" / "alpha" / "__init__.py").write_text("", encoding="utf-8")
            (root / "libs" / "alpha" / "alpha" / "service.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (root / "libs" / "beta" / "beta" / "__init__.py").write_text("", encoding="utf-8")
            (root / "libs" / "beta" / "beta" / "service.py").write_text("def run():\n    return True\n", encoding="utf-8")

            graph = build_domain_graph_native(root, synthesize_requirements_context(root))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("libs-alpha", graph_names)
            self.assertIn("libs-beta", graph_names)
            self.assertTrue(any("python-monorepo" in item for item in graph.recommendations))

    def test_build_domain_graph_passes_code_evidence_to_llm_prompt(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            requirements = root / "requirements.md"
            requirements.write_text("Support COBOL transaction flows.\n", encoding="utf-8")
            (root / "cobol" / "transactions").mkdir(parents=True)
            (root / "cobol" / "transactions" / "customer_lookup.cbl").write_text(
                "IDENTIFICATION DIVISION.\nPROGRAM-ID. CUSTOMER-LOOKUP.\nPROCEDURE DIVISION.\nDISPLAY 'OK'.\n",
                encoding="utf-8",
            )
            (root / "copybooks").mkdir(parents=True)
            (root / "copybooks" / "customer_record.cpy").write_text(
                "01 CUSTOMER-RECORD.\n   05 CUSTOMER-ID PIC X(10).\n",
                encoding="utf-8",
            )

            captured: dict[str, str] = {}

            def fake_run_deep_json(task: str, prompt: str, fallback, *, project_root: str | Path = ".") -> dict[str, object]:
                captured["task"] = task
                captured["prompt"] = prompt
                return fallback()

            with patch("skilgen.agents.domain_graph_planner.run_deep_json", side_effect=fake_run_deep_json):
                graph = build_domain_graph(root, load_requirements(requirements))

            graph_names = {node.name for node in graph.nodes}
            self.assertIn("backend", graph_names)
            self.assertIn("backend-copybooks", graph_names)
            self.assertIn("Code evidence JSON:", captured["prompt"])
            self.assertIn("PROGRAM-ID. CUSTOMER-LOOKUP.", captured["prompt"])
            self.assertIn("customer_record.cpy", captured["prompt"])


if __name__ == "__main__":
    unittest.main()
