from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from apps.api.api.analysis import _source_skill_files
from skilgen.cli.main import _render_source_summary
from skilgen.parsers.auto_detect import detect_source_paths
from skilgen.parsers.runner import run_source_parsers


def test_detect_source_paths_honors_sparse_sources_config_and_aliases() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "openapi.yaml").write_text("openapi: 3.0.0\ninfo:\n  title: Demo\n  version: 1.0.0\npaths: {}\n", encoding="utf-8")
        (root / "runbooks").mkdir()
        (root / "runbooks" / "deploy.md").write_text("# Deploy\n\n## Steps\n1. Ship it\n", encoding="utf-8")
        (root / "SECURITY.md").write_text("# Security Policy\n\nReport to security@example.com\n", encoding="utf-8")
        (root / "skilgen.yml").write_text(
            "\n".join(
                [
                    "sources:",
                    "  runbooks: runbooks/",
                    "  security_policy: SECURITY.md",
                    "  openapi: false",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        detected = detect_source_paths(root)

        assert sorted(detected) == ["runbook", "security_policy"]
        assert detected["runbook"][0].name == "runbooks"
        assert detected["security_policy"][0].name == "SECURITY.md"


def test_run_source_parsers_supports_explicit_paths_without_persisting() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "docs" / "SECURITY.md").write_text(
            "# Security Policy\n\nReport vulnerabilities to security@example.com within 2 business days.\n",
            encoding="utf-8",
        )

        result = run_source_parsers(
            root,
            ["security_policy"],
            explicit_paths={"security_policy": ["docs/SECURITY.md"]},
            persist=False,
        )

        assert result.failures == {}
        assert result.written_files == []
        assert len(result.skill_sources) == 1
        assert result.skill_sources[0].source_type == "security_policy"


def test_explicit_source_selection_overrides_disabled_config_entry() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "openapi.yaml").write_text("openapi: 3.0.0\ninfo:\n  title: Demo\n  version: 1.0.0\npaths: {}\n", encoding="utf-8")
        (root / "skilgen.yml").write_text("sources:\n  openapi: false\n", encoding="utf-8")

        detected = detect_source_paths(root, ["openapi"])

        assert "openapi" in detected
        assert detected["openapi"][0].name == "openapi.yaml"


def test_render_source_summary_reports_failures_and_generated_counts() -> None:
    class Result:
        analysed = {"security_policy": ["security_policy"]}
        failures = {"runbook": "No configured or detected paths for runbook."}
        written_files = [Path("skills/security_policy/SKILL.md")]

    rendered = _render_source_summary(Result())

    assert "security_policy" in rendered
    assert "Parser warnings:" in rendered
    assert "Generated 1 additional SKILL.md files" in rendered


def test_source_skill_files_build_persistable_payloads() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "SECURITY.md").write_text(
            "# Security Policy\n\nPlease report vulnerabilities to security@example.com.\n",
            encoding="utf-8",
        )

        payloads = _source_skill_files(
            root,
            {"total": 80, "groundedness": 20, "coverage": 20, "freshness": 20, "structure": 20},
            source_type="security_policy",
            source_path="SECURITY.md",
        )

        assert payloads[0]["source_type"] == "security_policy"
        assert payloads[0]["skill_category"] == "security_compliance"
        assert payloads[0]["skill_path"] == ".skilgen/skills/security_policy/SKILL.md"


def test_cli_main_declares_source_runner_flags() -> None:
    source = Path("skilgen/cli/main.py").read_text(encoding="utf-8")

    assert 'analyze.add_argument("--source"' in source
    assert 'analyze.add_argument("--all"' in source
    assert 'analyze.add_argument("--auto-detect"' in source
    assert "from skilgen.parsers.runner import run_source_parsers" in source
