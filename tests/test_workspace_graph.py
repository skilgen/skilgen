from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.agents.workspace_graph import build_workspace_graph


class WorkspaceGraphTests(unittest.TestCase):
    def test_build_workspace_graph_parses_pnpm_workspaces(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pnpm-workspace.yaml").write_text("packages:\n  - apps/*\n  - packages/*\n", encoding="utf-8")
            (root / "apps" / "web").mkdir(parents=True)
            (root / "packages" / "ui").mkdir(parents=True)
            (root / "apps" / "web" / "package.json").write_text(
                '{"name":"@repo/web","dependencies":{"@repo/ui":"workspace:*"}}',
                encoding="utf-8",
            )
            (root / "packages" / "ui" / "package.json").write_text('{"name":"@repo/ui"}', encoding="utf-8")

            graph = build_workspace_graph(root)

            self.assertEqual(graph.tool, "pnpm")
            self.assertEqual({package.root_path for package in graph.packages}, {"apps/web", "packages/ui"})
            self.assertEqual(graph.entrypoints, ["apps-web"])
            self.assertEqual([(edge.source, edge.target) for edge in graph.dependencies], [("apps-web", "packages-ui")])

    def test_build_workspace_graph_parses_nx_projects(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nx.json").write_text('{"workspaceLayout":{"appsDir":"apps","libsDir":"libs"}}', encoding="utf-8")
            (root / "apps" / "api").mkdir(parents=True)
            (root / "libs" / "shared").mkdir(parents=True)
            (root / "apps" / "api" / "project.json").write_text(
                '{"name":"api","projectType":"application","implicitDependencies":["shared"]}',
                encoding="utf-8",
            )
            (root / "apps" / "api" / "package.json").write_text('{"name":"api"}', encoding="utf-8")
            (root / "libs" / "shared" / "project.json").write_text(
                '{"name":"shared","projectType":"library"}',
                encoding="utf-8",
            )
            (root / "libs" / "shared" / "package.json").write_text('{"name":"shared"}', encoding="utf-8")

            graph = build_workspace_graph(root)

            self.assertEqual(graph.tool, "nx")
            self.assertEqual({package.root_path for package in graph.packages}, {"apps/api", "libs/shared"})
            self.assertEqual([(edge.source, edge.target) for edge in graph.dependencies], [("apps-api", "libs-shared")])

    def test_build_workspace_graph_parses_turbo_workspaces(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "turbo.json").write_text('{"pipeline":{"build":{"dependsOn":["^build"]}}}', encoding="utf-8")
            (root / "package.json").write_text('{"workspaces":["apps/*","packages/*"]}', encoding="utf-8")
            (root / "apps" / "docs").mkdir(parents=True)
            (root / "packages" / "config").mkdir(parents=True)
            (root / "apps" / "docs" / "package.json").write_text(
                '{"name":"@repo/docs","dependencies":{"@repo/config":"workspace:*"}}',
                encoding="utf-8",
            )
            (root / "packages" / "config" / "package.json").write_text('{"name":"@repo/config"}', encoding="utf-8")

            graph = build_workspace_graph(root)

            self.assertEqual(graph.tool, "turbo")
            self.assertEqual({package.root_path for package in graph.packages}, {"apps/docs", "packages/config"})
            self.assertEqual([(edge.source, edge.target) for edge in graph.dependencies], [("apps-docs", "packages-config")])

    def test_build_workspace_graph_parses_bazel_packages(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "WORKSPACE").write_text('workspace(name = "demo")\n', encoding="utf-8")
            (root / "services" / "api").mkdir(parents=True)
            (root / "libs" / "util").mkdir(parents=True)
            (root / "services" / "api" / "BUILD.bazel").write_text(
                'py_library(name = "api", deps = ["//libs/util:util"])\n',
                encoding="utf-8",
            )
            (root / "libs" / "util" / "BUILD.bazel").write_text('py_library(name = "util")\n', encoding="utf-8")

            graph = build_workspace_graph(root)

            self.assertEqual(graph.tool, "bazel")
            self.assertEqual({package.root_path for package in graph.packages}, {"services/api", "libs/util"})
            self.assertEqual([(edge.source, edge.target) for edge in graph.dependencies], [("services-api", "libs-util")])

    def test_build_workspace_graph_falls_back_to_python_libs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "libs" / "alpha" / "alpha").mkdir(parents=True)
            (root / "libs" / "beta" / "beta").mkdir(parents=True)
            (root / "libs" / "alpha" / "alpha" / "__init__.py").write_text("", encoding="utf-8")
            (root / "libs" / "beta" / "beta" / "__init__.py").write_text("", encoding="utf-8")

            graph = build_workspace_graph(root)

            self.assertIsNone(graph.tool)
            self.assertEqual({package.root_path for package in graph.packages}, {"libs/alpha", "libs/beta"})
            self.assertEqual(graph.detection_evidence, ["libs/"])

    def test_build_workspace_graph_degrades_gracefully_for_malformed_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pnpm-workspace.yaml").write_text("packages: [\n", encoding="utf-8")

            graph = build_workspace_graph(root)

            self.assertEqual(graph.tool, "pnpm")
            self.assertEqual(graph.packages, [])
            self.assertEqual(graph.dependencies, [])


if __name__ == "__main__":
    unittest.main()
