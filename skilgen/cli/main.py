from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
import threading
import time

from skilgen.api.server import run_server
from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, run_auto_update_worker, stop_auto_update_worker
from skilgen.api.service import analytics_payload, analyze_payload, architecture_payload, dashboard_payload, decision_payload, diff_payload, doctor_payload, preview_payload, report_payload, score_payload, status_payload, validate_payload
from skilgen import __version__
from skilgen.agents import build_import_graph, build_roadmap_plan, extract_features, fingerprint_project
from skilgen.agents.requirements_parser import parse_project_intent, parse_requirements_file
from skilgen.deep_agents_core import current_runtime_mode, runtime_diagnostics
from skilgen.core.analytics import log_skill_usage
from skilgen.core.dependency_risk import analyze_dependency_risks, render_dependency_risk_report
from skilgen.core.evals import compare_eval_results, scaffold_eval_framework
from skilgen.core.corpus_index import build_corpus_index
from skilgen.core.runtime_data import purge_runtime_data
from skilgen.core.score import ci_result, score_badge_markdown
from skilgen.registry_client import RegistryClientError, import_skill as import_registry_skill, publish_skill as publish_registry_skill
from skilgen.delivery import run_delivery, watch_delivery
from skilgen.core.config import load_config, render_default_config
from skilgen.enterprise_skills import (
    activate_mcp_connector,
    active_mcp_connectors,
    connector_catalog,
    deactivate_mcp_connector,
    generate_enterprise_skill,
    ingest_enterprise_skill,
    list_enterprise_skills,
    recommend_mcp_connectors,
)
from skilgen.external_skills import (
    activate_external_skill,
    active_external_skills,
    detect_external_skill_sources,
    external_skill_lock,
    external_skill_policy,
    deactivate_external_skill,
    export_external_skill_lock,
    get_external_skill,
    import_external_skill_candidates,
    import_external_skill_lock,
    install_external_skill,
    list_external_skills,
    ranked_external_skills,
    remove_external_skill,
    sync_all_external_skills,
    sync_external_skill,
)


def emit_progress(message: str) -> None:
    print(f"[skilgen] {message}", file=sys.stderr)


@dataclass(frozen=True)
class ProgressMilestone:
    prefix: str
    percent: int


class CliProgressReporter:
    _brand = "⬡⬢⬡"
    _bar_width = 24
    _frames = ("◜", "◠", "◝", "◞", "◡", "◟")
    _milestones = (
        ProgressMilestone("Starting delivery", 3),
        ProgressMilestone("Model-backed runtime is not ready", 6),
        ProgressMilestone("Reading your", 10),
        ProgressMilestone("Scanning the repository", 18),
        ProgressMilestone("Installed matching external skill packs", 24),
        ProgressMilestone("Using already-installed external skill packs", 24),
        ProgressMilestone("Ingested configured enterprise skill packs", 26),
        ProgressMilestone("Using configured enterprise skill packs", 26),
        ProgressMilestone("Activated recommended MCP connectors", 30),
        ProgressMilestone("Building project context", 42),
        ProgressMilestone("Inspecting the codebase", 54),
        ProgressMilestone("Detected changes in", 64),
        ProgressMilestone("No source changes were detected", 64),
        ProgressMilestone("Decision planner selected domains", 72),
        ProgressMilestone("Previewing the generated project docs", 78),
        ProgressMilestone("Generating project docs", 78),
        ProgressMilestone("Previewing the skill tree", 88),
        ProgressMilestone("Materializing backend, frontend, requirements, and roadmap skills", 88),
        ProgressMilestone("Decision planner recommends reusing", 88),
        ProgressMilestone("Decision planner did not identify any concrete domains", 88),
        ProgressMilestone("Finished delivery", 100),
    )

    def __init__(self) -> None:
        self._last_percent = 0
        self._current_message = ""
        self._start_time = time.monotonic()
        self._last_emit_at = 0.0
        self._frame_index = 0
        self._is_tty = sys.stderr.isatty()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._spinner_thread: threading.Thread | None = None
        if self._is_tty:
            self._spinner_thread = threading.Thread(target=self._spin, name="skilgen-progress", daemon=True)
            self._spinner_thread.start()

    def emit(self, message: str) -> None:
        with self._lock:
            percent = self._infer_percent(message)
            self._last_percent = max(self._last_percent, percent)
            self._current_message = message
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            now = time.monotonic()
            if not self._is_tty and now - self._last_emit_at < 0.5 and percent < 100:
                return
            self._last_emit_at = now
            line = self._render_line(self._last_percent, message, done=percent >= 100)
        if self._is_tty:
            print(f"\r{line}", file=sys.stderr, end="", flush=True)
            if self._last_percent >= 100:
                print(file=sys.stderr, flush=True)
        else:
            print(line, file=sys.stderr)

    def stop(self) -> None:
        self._stop_event.set()
        if self._spinner_thread is not None:
            self._spinner_thread.join(timeout=0.5)
        if self._is_tty and self._current_message and self._last_percent < 100:
            with self._lock:
                print(f"\r{self._render_line(self._last_percent, self._current_message, done=True)}", file=sys.stderr)

    def _infer_percent(self, message: str) -> int:
        for milestone in self._milestones:
            if message.startswith(milestone.prefix):
                return milestone.percent
        # Keep moving forward a bit for any uncatalogued progress messages.
        return min(98, self._last_percent + 4)

    def _elapsed(self) -> str:
        elapsed = int(time.monotonic() - self._start_time)
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _render_line(self, percent: int, message: str, *, done: bool = False) -> str:
        filled = round((percent / 100) * self._bar_width)
        bar = "█" * filled + "░" * max(0, self._bar_width - filled)
        frame = "●" if done else self._frames[self._frame_index]
        return f"[skilgen {self._brand} {frame} {self._elapsed()}] {percent:>3}% |{bar}| {message}"

    def _spin(self) -> None:
        while not self._stop_event.wait(0.12):
            with self._lock:
                if not self._current_message:
                    continue
                self._frame_index = (self._frame_index + 1) % len(self._frames)
                line = self._render_line(self._last_percent, self._current_message)
            print(f"\r{line}", file=sys.stderr, end="", flush=True)

def write_ci_workflow(project_root: Path) -> Path:
    """Write the default GitHub Actions workflow for Skilgen quality gates."""
    workflow_path = project_root / ".github" / "workflows" / "skilgen.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "name: Skilgen",
                "",
                "on:",
                "  pull_request:",
                "",
                "jobs:",
                "  skilgen:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/setup-python@v5",
                "        with:",
                "          python-version: '3.12'",
                "      - name: Install Skilgen",
                "        run: python -m pip install -e .",
                "      - name: Generate skills",
                "        run: skilgen deliver --project-root .",
                "      - name: Enforce Skilgen Score",
                "        run: skilgen score --ci --min-score 60 --min-groundedness 15 --min-coverage 15 --project-root .",
                "      - name: Enforce enterprise policy",
                "        run: skilgen enterprise policy check --project-root .",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return workflow_path


def _format_analytics_summary(payload: dict[str, object]) -> str:
    """Render analytics as readable CLI text instead of raw JSON."""
    usage_mode = str(payload.get("usage_mode", "none"))
    live_events = int(payload.get("live_event_count", 0) or 0)
    planner_events = int(payload.get("planner_event_count", 0) or 0)
    traced_agents = payload.get("traced_agents", [])
    if not isinstance(traced_agents, list):
        traced_agents = []
    lines = [
        "Skilgen Analytics",
        "",
        f"Usage mode: {usage_mode}",
        f"Live events: {live_events}",
        f"Planner warmups ignored: {planner_events}",
        f"Agents: {', '.join(str(agent) for agent in traced_agents) if traced_agents else 'none'}",
        "",
        "Top skills:",
    ]
    top_skills = payload.get("top_skills", [])
    if isinstance(top_skills, list) and top_skills:
        for index, item in enumerate(top_skills, start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "Skill")
            skill = str(item.get("skill") or "unknown")
            loads = int(item.get("loads", 0) or 0)
            mode = str(item.get("mode") or usage_mode)
            suffix = "s" if loads != 1 else ""
            lines.append(f"  {index}. {title} - {skill} - {loads} {mode} load{suffix}")
    else:
        lines.append("  No skill usage detected yet.")
    lines.extend(["", "Least used:"])
    least_used = payload.get("least_used", [])
    if isinstance(least_used, list) and least_used:
        for index, item in enumerate(least_used, start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "Skill")
            skill = str(item.get("skill") or "unknown")
            loads = int(item.get("loads", 0) or 0)
            suffix = "s" if loads != 1 else ""
            lines.append(f"  {index}. {title} - {skill} - {loads} load{suffix}")
    else:
        lines.append("  No low-usage skills detected.")
    return "\n".join(lines)


def write_ci_workflow(project_root: Path) -> Path:
    """Write the default GitHub Actions workflow for Skilgen quality gates."""
    workflow_path = project_root / ".github" / "workflows" / "skilgen.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "name: Skilgen",
                "",
                "on:",
                "  pull_request:",
                "",
                "jobs:",
                "  skilgen:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/setup-python@v5",
                "        with:",
                "          python-version: '3.12'",
                "      - name: Install Skilgen",
                "        run: python -m pip install -e .",
                "      - name: Generate skills",
                "        run: skilgen deliver --project-root .",
                "      - name: Enforce Skilgen Score",
                "        run: skilgen score --ci --min-score 60 --min-groundedness 15 --min-coverage 15 --project-root .",
                "      - name: Enforce enterprise policy",
                "        run: skilgen enterprise policy check --project-root .",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return workflow_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skilgen", description="Requirements-driven skill and scaffold generator.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Write a default skilgen.yml to the project root.")
    init.add_argument("--project-root", default=".")
    init.add_argument("--ci", action="store_true", help="Write a GitHub Actions workflow for Skilgen CI checks.")
    init.add_argument(
        "--provider",
        choices=[
            "openai",
            "anthropic",
            "gemini",
            "google",
            "google_genai",
            "huggingface",
            "hugging_face",
            "hf",
            "azure_openai",
            "bedrock",
            "ollama",
            "openai_compatible",
        ],
        help="Optionally scaffold provider-specific model defaults instead of a neutral template.",
    )

    index = subparsers.add_parser("index", help="Build or refresh the full-corpus index used for deep evidence selection.")
    index.add_argument("--project-root", default=".")

    scan = subparsers.add_parser("scan", help="Generate docs and skills from a requirements file.")
    scan.add_argument("--requirements")
    scan.add_argument("--project-root", default=".")
    scan.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    scan.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    scan.add_argument("--dry-run", action="store_true")
    scan.add_argument("--skip-index", action="store_true")

    deliver = subparsers.add_parser("deliver", help="Alias for scan for now; intended to grow into full delivery automation.")
    deliver.add_argument("--requirements")
    deliver.add_argument("--project-root", default=".")
    deliver.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    deliver.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    deliver.add_argument("--dry-run", action="store_true")
    deliver.add_argument("--skip-index", action="store_true")

    update = subparsers.add_parser("update", help="Refresh generated outputs for all or selected domains.")
    update.add_argument("--requirements")
    update.add_argument("--project-root", default=".")
    update.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    update.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--skip-index", action="store_true")

    watch = subparsers.add_parser("watch", help="Watch the project and rerun generation when files change.")
    watch.add_argument("--requirements")
    watch.add_argument("--project-root", default=".")
    watch.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    watch.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])
    watch.add_argument("--interval", type=float, default=2.0)
    watch.add_argument("--cycles", type=int, default=0)
    watch.add_argument("--once", action="store_true")

    autoupdate = subparsers.add_parser("autoupdate", help="Manage Skilgen's background skill auto-update worker.")
    autoupdate_subparsers = autoupdate.add_subparsers(dest="autoupdate_command", required=True)

    autoupdate_enable = autoupdate_subparsers.add_parser("enable", help="Start the repo-local auto-update worker.")
    autoupdate_enable.add_argument("--project-root", default=".")
    autoupdate_enable.add_argument("--requirements")
    autoupdate_enable.add_argument("--interval", type=float, default=2.0)

    autoupdate_status_parser = autoupdate_subparsers.add_parser("status", help="Show the current auto-update worker status.")
    autoupdate_status_parser.add_argument("--project-root", default=".")

    autoupdate_disable = autoupdate_subparsers.add_parser("disable", help="Stop the repo-local auto-update worker.")
    autoupdate_disable.add_argument("--project-root", default=".")

    autoupdate_worker = autoupdate_subparsers.add_parser("worker", help=argparse.SUPPRESS)
    autoupdate_worker.add_argument("--project-root", default=".")
    autoupdate_worker.add_argument("--interval", type=float, default=2.0)

    preview = subparsers.add_parser("preview", help="Preview which generated files would be written without changing the project.")
    preview.add_argument("--requirements")
    preview.add_argument("--project-root", default=".")
    preview.add_argument("--target", choices=["all", "docs", "skills"], default="all")
    preview.add_argument("--domain", action="append", choices=["requirements", "backend", "frontend", "roadmap"])

    fingerprint = subparsers.add_parser("fingerprint", help="Detect the current project's likely frameworks.")
    fingerprint.add_argument("--project-root", default=".")

    mapping = subparsers.add_parser("map", help="Build a simple import relationship map for the project.")
    mapping.add_argument("--project-root", default=".")

    analyze = subparsers.add_parser("analyze", help="Assemble framework, signal, and relationship analysis for the project.")
    analyze.add_argument("--project-root", default=".")
    analyze.add_argument("--requirements")
    analyze.add_argument("--deps", action="store_true", help="Show dependency CVE, version drift, and upgrade guidance.")

    diff = subparsers.add_parser("diff", help="Show what changed since the last generation and which skills are stale.")
    diff.add_argument("--project-root", default=".")
    diff.add_argument("--requirements")
    diff.add_argument("--json", action="store_true")

    architecture = subparsers.add_parser("architecture", help="Synthesize an evidence-backed architecture blueprint for the project.")
    architecture.add_argument("--project-root", default=".")
    architecture.add_argument("--requirements")
    architecture.add_argument("--json", action="store_true", help="Emit the raw architecture payload as JSON.")
    architecture.add_argument("--graph-file", help="Write the architecture graph export to a file.")
    architecture.add_argument("--graph-format", choices=["mermaid", "json", "html"], default="mermaid")
    architecture.add_argument("--skip-index", action="store_true")

    dashboard = subparsers.add_parser("dashboard", help="Generate a branded HTML dashboard for the current Skilgen project state.")
    dashboard.add_argument("--project-root", default=".")
    dashboard.add_argument("--requirements")
    dashboard.add_argument("--output", help="Write the dashboard HTML to a file. Defaults to <project-root>/skilgen-dashboard.html.")
    dashboard.add_argument("--json", action="store_true", help="Emit the raw dashboard payload as JSON instead of writing HTML.")

    decide = subparsers.add_parser("decide", help="Recommend whether to refresh skills, which skills to prioritize, and which run memory to load.")
    decide.add_argument("--project-root", default=".")
    decide.add_argument("--requirements")

    skills = subparsers.add_parser("skills", help="Discover and install external skill collections through Skilgen.")
    skills_subparsers = skills.add_subparsers(dest="skills_command", required=True)

    skills_list = skills_subparsers.add_parser("list", help="List curated external skill sources available through Skilgen.")
    skills_list.add_argument("--project-root", default=".")
    skills_list.add_argument("--ecosystem")
    skills_list.add_argument("--search")

    skills_show = skills_subparsers.add_parser("show", help="Show details for a curated external skill source.")
    skills_show.add_argument("slug")
    skills_show.add_argument("--project-root", default=".")

    skills_detect = skills_subparsers.add_parser("detect", help="Detect external skill ecosystems that match the current repository.")
    skills_detect.add_argument("--project-root", default=".")

    skills_active = skills_subparsers.add_parser("active", help="List the currently active external skill packs for this project.")
    skills_active.add_argument("--project-root", default=".")

    skills_lock = skills_subparsers.add_parser("lock", help="Show the resolved external-skills lockfile for this project.")
    skills_lock.add_argument("--project-root", default=".")

    skills_lock_export = skills_subparsers.add_parser("lock-export", help="Export the resolved external-skills lockfile for reuse in another repo.")
    skills_lock_export.add_argument("--project-root", default=".")
    skills_lock_export.add_argument("--output-path")

    skills_lock_import = skills_subparsers.add_parser("lock-import", help="Import an exported external-skills lockfile into this project.")
    skills_lock_import.add_argument("--project-root", default=".")
    skills_lock_import.add_argument("--input-path", required=True)
    skills_lock_import.add_argument("--sync-existing", action="store_true")

    skills_policy = skills_subparsers.add_parser("policy", help="Show the external-skills policy currently applied to this project.")
    skills_policy.add_argument("--project-root", default=".")

    skills_rank = skills_subparsers.add_parser("rank", help="Rank active external skill packs by trust and relevance for the current project.")
    skills_rank.add_argument("--project-root", default=".")

    skills_install = skills_subparsers.add_parser("install", help="Install a curated or custom external skill source into the local project.")
    skills_install.add_argument("slug", nargs="?")
    skills_install.add_argument("--git-url")
    skills_install.add_argument("--name")
    skills_install.add_argument("--project-root", default=".")
    skills_install.add_argument("--force", action="store_true")
    skills_install.add_argument("--ref")
    skills_install.add_argument("--activate", action=argparse.BooleanOptionalAction, default=None)

    skills_import = skills_subparsers.add_parser("import", help="Import downstream repos from an installed directory-style external skill source.")
    skills_import.add_argument("slug")
    skills_import.add_argument("--project-root", default=".")
    skills_import.add_argument("--limit", type=int, default=5)
    skills_import.add_argument("--activate", action=argparse.BooleanOptionalAction, default=None)
    skills_import.add_argument("--target-dir", help="Import a Skillayer registry skill into this existing directory as SKILL.md.")
    skills_import.add_argument("--api-url", default="https://api.skillayer.com")

    skills_publish = skills_subparsers.add_parser("publish", help="Publish a generated SKILL.md to the Skillayer registry.")
    skills_publish.add_argument("skill_file")
    skills_publish.add_argument("--project-root", default=".")
    skills_publish.add_argument("--skill-id", required=True)
    skills_publish.add_argument("--name", required=True)
    skills_publish.add_argument("--description", required=True)
    skills_publish.add_argument("--tag", action="append", default=[])
    skills_publish.add_argument("--private", action="store_true")
    skills_publish.add_argument("--api-url", default="https://api.skillayer.com")

    skills_sync = skills_subparsers.add_parser("sync", help="Sync an installed external skill source with its upstream repository.")
    skills_sync.add_argument("slug", nargs="?")
    skills_sync.add_argument("--project-root", default=".")
    skills_sync.add_argument("--all", action="store_true")

    skills_remove = skills_subparsers.add_parser("remove", help="Remove an installed external skill source from the local project.")
    skills_remove.add_argument("slug")
    skills_remove.add_argument("--project-root", default=".")

    skills_activate = skills_subparsers.add_parser("activate", help="Mark an installed external skill source as active for agent loading.")
    skills_activate.add_argument("slug")
    skills_activate.add_argument("--project-root", default=".")

    skills_deactivate = skills_subparsers.add_parser("deactivate", help="Mark an installed external skill source as inactive for agent loading.")
    skills_deactivate.add_argument("slug")
    skills_deactivate.add_argument("--project-root", default=".")

    enterprise = subparsers.add_parser("enterprise", help="Ingest and generate enterprise-wide skill packs for coding agents.")
    enterprise_subparsers = enterprise.add_subparsers(dest="enterprise_command", required=True)

    enterprise_list = enterprise_subparsers.add_parser("list", help="List enterprise skill packs installed for this project.")
    enterprise_list.add_argument("--project-root", default=".")

    enterprise_ingest = enterprise_subparsers.add_parser("ingest", help="Ingest an existing enterprise skill pack from a local path or git repo.")
    enterprise_ingest.add_argument("--project-root", default=".")
    enterprise_ingest.add_argument("--name", required=True)
    enterprise_ingest.add_argument("--path")
    enterprise_ingest.add_argument("--git-url")
    enterprise_ingest.add_argument("--url")
    enterprise_ingest.add_argument("--ref")
    enterprise_ingest.add_argument("--kind", default="enterprise")
    enterprise_ingest.add_argument("--activate", action=argparse.BooleanOptionalAction, default=None)

    enterprise_generate = enterprise_subparsers.add_parser("generate", help="Generate an enterprise skill from docs, code, or runbooks.")
    enterprise_generate.add_argument("--project-root", default=".")
    enterprise_generate.add_argument("--name", required=True)
    enterprise_generate.add_argument("--kind", default="domain")
    enterprise_generate.add_argument("--source-path", action="append", required=True)
    enterprise_generate.add_argument("--activate", action=argparse.BooleanOptionalAction, default=True)

    connectors = subparsers.add_parser("connectors", help="Discover and manage approved MCP connector capabilities.")
    connectors_subparsers = connectors.add_subparsers(dest="connectors_command", required=True)

    connectors_list = connectors_subparsers.add_parser("list", help="List supported MCP connectors.")
    connectors_list.add_argument("--system")
    connectors_list.add_argument("--search")

    connectors_recommend = connectors_subparsers.add_parser("recommend", help="Recommend MCP connectors for the current project.")
    connectors_recommend.add_argument("--project-root", default=".")

    connectors_active = connectors_subparsers.add_parser("active", help="List active MCP connectors for the current project.")
    connectors_active.add_argument("--project-root", default=".")

    connectors_activate = connectors_subparsers.add_parser("activate", help="Activate an MCP connector for this project.")
    connectors_activate.add_argument("slug")
    connectors_activate.add_argument("--project-root", default=".")

    connectors_deactivate = connectors_subparsers.add_parser("deactivate", help="Deactivate an MCP connector for this project.")
    connectors_deactivate.add_argument("slug")
    connectors_deactivate.add_argument("--project-root", default=".")

    intent = subparsers.add_parser("intent", help="Parse a requirements file into a structured project intent.")
    intent.add_argument("--requirements", required=True)
    features = subparsers.add_parser("features", help="Extract a feature inventory from requirements and project context.")
    features.add_argument("--requirements")
    features.add_argument("--project-root", default=".")
    plan = subparsers.add_parser("plan", help="Build a roadmap plan from requirements and model config.")
    plan.add_argument("--requirements")
    plan.add_argument("--project-root", default=".")

    score = subparsers.add_parser("score", help="Compute the Skilgen Score quality metric for the current skill tree.")
    score.add_argument("--project-root", default=".")
    score.add_argument("--badge-file")
    score.add_argument("--badge", action="store_true", help="Print a shields.io Markdown badge instead of JSON.")
    score.add_argument("--ci", action="store_true", help="Exit non-zero when score thresholds are not met.")
    score.add_argument("--min-score", type=int, default=60)
    score.add_argument("--min-groundedness", type=int, default=15)
    score.add_argument("--min-coverage", type=int, default=15)
    score.add_argument("--history", action="store_true", help="Show recent score history and score trends instead of only the current score.")
    score.add_argument("--history-limit", type=int, default=10)

    eval_cmd = subparsers.add_parser("eval", help="Scaffold or compare Skilgen evaluation runs.")
    eval_subparsers = eval_cmd.add_subparsers(dest="eval_command", required=True)
    eval_scaffold = eval_subparsers.add_parser("scaffold", help="Create a starter eval framework for with-vs-without-Skilgen comparisons.")
    eval_scaffold.add_argument("--project-root", default=".")
    eval_scaffold.add_argument("--output-dir")
    eval_compare = eval_subparsers.add_parser("compare", help="Compare baseline and Skilgen eval results.")
    eval_compare.add_argument("--baseline", required=True)
    eval_compare.add_argument("--skilgen", required=True)

    status = subparsers.add_parser("status", help="Show the current generated output status for a project root.")
    status.add_argument("--project-root", default=".")

    report = subparsers.add_parser("report", help="Show a summary report for a project root.")
    report.add_argument("--project-root", default=".")

    purge = subparsers.add_parser("purge", help="Delete Skilgen runtime data stored under .skilgen for a project.")
    purge.add_argument("--project-root", default=".")

    analytics = subparsers.add_parser("analytics", help="Summarize generated skill usage and load history.")
    analytics.add_argument("--project-root", default=".")
    analytics.add_argument("--limit", type=int, default=10)
    analytics.add_argument("--record-skill", action="append", default=[], help="Record a real skill-load event for a repo skill path such as skills/backend/api/SKILL.md.")
    analytics.add_argument("--event", default="loaded")
    analytics.add_argument("--agent")
    analytics.add_argument("--context", default="agent_runtime")
    analytics.add_argument("--session-id")
    analytics.add_argument("--task")
    analytics.add_argument("--json", action="store_true", help="Output the raw analytics JSON payload.")

    validate = subparsers.add_parser("validate", help="Validate generated outputs and skill references.")
    validate.add_argument("--project-root", default=".")

    doctor = subparsers.add_parser("doctor", help="Diagnose runtime readiness, model configuration, and API-key setup.")
    doctor.add_argument("--project-root", default=".")

    serve = subparsers.add_parser("serve", help="Run the HTTP API server.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        project_root = Path(args.project_root).resolve()
        project_root.mkdir(parents=True, exist_ok=True)
        config_path = project_root / "skilgen.yml"
        if not config_path.exists():
            config_path.write_text(render_default_config(args.provider), encoding="utf-8")
        ci_workflow_path = write_ci_workflow(project_root) if args.ci else None
        worker = ensure_auto_update_worker(project_root)
        payload = {"config_path": str(config_path), "auto_update": worker}
        if ci_workflow_path is not None:
            payload["ci_workflow_path"] = str(ci_workflow_path)
        print(json.dumps(payload, indent=2))
        return
    if args.command == "index":
        root = Path(args.project_root).resolve()
        emit_progress("Indexing the full repository corpus so Skilgen can sample architectural hubs, configs, docs, and isolated subsystems.")
        payload = build_corpus_index(root)
        counts = {"source": 0, "config": 0, "documentation": 0, "enterprise_document": 0, "other": 0}
        for entry in payload["entries"]:
            category = str(entry.get("category", "other"))
            counts[category] = counts.get(category, 0) + 1
        print(
            json.dumps(
                {
                    "index_path": payload["cache_path"],
                    "entry_count": len(payload["entries"]),
                    "cluster_count": len(payload.get("clusters", {})),
                    "counts": counts,
                },
                indent=2,
            )
        )
        return
    if args.command == "autoupdate":
        root = Path(args.project_root).resolve()
        if args.autoupdate_command == "enable":
            payload = ensure_auto_update_worker(
                root,
                requirements_path=Path(args.requirements).resolve() if args.requirements else None,
                interval_seconds=args.interval,
            )
            print(json.dumps(payload, indent=2))
            return
        if args.autoupdate_command == "status":
            print(json.dumps(auto_update_status(root), indent=2))
            return
        if args.autoupdate_command == "disable":
            print(json.dumps(stop_auto_update_worker(root), indent=2))
            return
        if args.autoupdate_command == "worker":
            run_auto_update_worker(root, interval_seconds=args.interval)
            return
    if args.command == "fingerprint":
        result = fingerprint_project(Path(args.project_root).resolve())
        print(
            json.dumps(
                {
                    "frontend": result.frontend.__dict__ if result.frontend else None,
                    "backend": result.backend.__dict__ if result.backend else None,
                    "test_framework": result.test_framework.__dict__ if result.test_framework else None,
                    "build_tool": result.build_tool.__dict__ if result.build_tool else None,
                },
                indent=2,
            )
        )
        return
    if args.command == "map":
        print(json.dumps({"import_graph": build_import_graph(Path(args.project_root).resolve())}, indent=2))
        return
    if args.command == "analyze":
        if args.deps:
            report = analyze_dependency_risks(Path(args.project_root).resolve())
            print(render_dependency_risk_report(report))
            return
        print(json.dumps(analyze_payload(Path(args.project_root).resolve(), Path(args.requirements).resolve() if args.requirements else None), indent=2))
        return
    if args.command == "diff":
        payload = diff_payload(Path(args.project_root).resolve(), Path(args.requirements).resolve() if args.requirements else None)
        if args.json:
            print(json.dumps(payload, indent=2))
        elif payload["reason"] == "no_source_changes":
            print(
                "\n".join(
                    [
                        "Skilgen Diff - no source changes detected",
                        "",
                        f"  All skills are current. Freshness: {int(round(payload['freshness_score']))}/{payload['freshness_max']}",
                    ]
                )
            )
        elif payload["reason"] == "missing_freshness_state":
            print(
                "\n".join(
                    [
                        "Skilgen Diff - no previous generation found",
                        "",
                        "  Run `skilgen deliver` first to establish a baseline.",
                    ]
                )
            )
        else:
            lines = [f"Skilgen Diff - {payload['changed_file_count']} files changed since last generation", ""]
            lines.append("  Changed files:")
            for item in payload["changed_files"]:
                lines.append(f"    {item['change_type']:<9} {item['path']}")
            lines.append("")
            lines.append("  Impacted domains:")
            for item in payload["impacted_domain_details"]:
                if item["domain"] not in payload["impacted_domains"]:
                    continue
                marker = "STALE" if item["stale"] else "CURRENT"
                path = item["skill_path"] or "-"
                lines.append(f"    {item['domain']:<16} -> {path:<36} {marker}")
            lines.append("")
            lines.append(f"  Current: {', '.join(payload['current_domains']) or 'none'}")
            lines.append(f"  Freshness: {int(round(payload['freshness_score']))}/{payload['freshness_max']}")
            lines.append("")
            lines.append("  Run `skilgen deliver` to refresh stale skills.")
            print("\n".join(lines))
        return
    if args.command == "architecture":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Collecting code, config, and requirements evidence with the {current_runtime_mode(root)} runtime before synthesizing the architecture blueprint."
        )
        payload = architecture_payload(root, Path(args.requirements).resolve() if args.requirements else None, skip_index=args.skip_index)
        if args.graph_file:
            graph_content = payload["graph_export"][args.graph_format]
            graph_path = Path(args.graph_file).resolve()
            graph_path.parent.mkdir(parents=True, exist_ok=True)
            if args.graph_format == "json":
                graph_path.write_text(json.dumps(graph_content, indent=2), encoding="utf-8")
            else:
                graph_path.write_text(str(graph_content), encoding="utf-8")
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(payload["report_markdown"])
        return
    if args.command == "dashboard":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Building the branded Skilgen dashboard with the {current_runtime_mode(root)} runtime so you can inspect score, freshness, graphs, and agent readiness in one place."
        )
        payload = dashboard_payload(root, Path(args.requirements).resolve() if args.requirements else None)
        if args.json:
            print(json.dumps(payload, indent=2))
            return
        output_path = Path(args.output).resolve() if args.output else (root / "skilgen-dashboard.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(str(payload["html"]), encoding="utf-8")
        architecture = payload.get("architecture")
        headline = f"Dashboard for {root.name}"
        if isinstance(architecture, dict):
            headline = str(architecture.get("headline") or headline)
        score_info = payload.get("score")
        score_value = 0
        if isinstance(score_info, dict):
            score_value = score_info.get("score", 0)
        elif isinstance(score_info, (int, float)):
            score_value = score_info
        diff_info = payload.get("diff")
        stale_skill_count = 0
        if isinstance(diff_info, dict):
            stale_skill_count = len(diff_info.get("stale_skill_paths", []))
        graph_payload = payload.get("graph_export")
        if not isinstance(graph_payload, dict):
            graph_payload = payload.get("graphs")
        graph_panels = sorted(graph_payload.keys()) if isinstance(graph_payload, dict) else []
        print(
            json.dumps(
                {
                    "dashboard_file": str(output_path),
                    "headline": headline,
                    "score": score_value,
                    "stale_skill_count": stale_skill_count,
                    "graph_panels": graph_panels,
                },
                indent=2,
            )
        )
        return
    if args.command == "decide":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting agent decision planning with the {current_runtime_mode(root)} runtime. Skilgen is deciding whether the skill tree should refresh and what the agent should load first."
        )
        print(json.dumps(decision_payload(root, Path(args.requirements).resolve() if args.requirements else None), indent=2))
        return
    if args.command == "skills":
        root = Path(args.project_root).resolve()
        if args.skills_command == "list":
            emit_progress("Loading the curated Skilgen skills catalog across supported ecosystems.")
            print(json.dumps(list_external_skills(root, ecosystem=args.ecosystem, search=args.search), indent=2))
            return
        if args.skills_command == "show":
            emit_progress(f"Loading details for the external skill source '{args.slug}'.")
            print(json.dumps({"skill": get_external_skill(args.slug, root)}, indent=2))
            return
        if args.skills_command == "detect":
            emit_progress("Scanning the repository for supported external skill ecosystems.")
            print(json.dumps(detect_external_skill_sources(root), indent=2))
            return
        if args.skills_command == "active":
            emit_progress("Listing the currently active external skill packs for this project.")
            print(json.dumps({"skills": active_external_skills(root)}, indent=2))
            return
        if args.skills_command == "lock":
            emit_progress("Loading the resolved external-skills lockfile.")
            print(json.dumps(external_skill_lock(root), indent=2))
            return
        if args.skills_command == "lock-export":
            emit_progress("Exporting the resolved external-skills lockfile for reuse in another project.")
            print(json.dumps(export_external_skill_lock(project_root=root, output_path=args.output_path), indent=2))
            return
        if args.skills_command == "lock-import":
            emit_progress("Importing external skills from an exported lockfile into this project.")
            print(json.dumps(import_external_skill_lock(project_root=root, input_path=args.input_path, sync_existing=args.sync_existing), indent=2))
            return
        if args.skills_command == "policy":
            emit_progress("Loading the external-skills policy for this project.")
            print(json.dumps(external_skill_policy(root), indent=2))
            return
        if args.skills_command == "rank":
            emit_progress("Ranking active external skill packs by trust, detection signals, and repo fit.")
            print(json.dumps(ranked_external_skills(root), indent=2))
            return
        if args.skills_command == "install":
            emit_progress("Installing the external skill source into .skilgen/external-skills so it can be managed through Skilgen.")
            print(
                json.dumps(
                    {
                        "installed_skill": install_external_skill(
                            project_root=root,
                            slug=args.slug,
                            git_url=args.git_url,
                            name=args.name,
                            force=args.force,
                            ref=args.ref,
                            active=args.activate,
                        )
                    },
                    indent=2,
                )
            )
            return
        if args.skills_command == "import":
            if args.target_dir:
                try:
                    emit_progress("Importing a public Skillayer registry skill into the target skill directory.")
                    print(
                        json.dumps(
                            {
                                "imported_skill": import_registry_skill(
                                    api_url=args.api_url,
                                    registry_id=args.slug,
                                    target_dir=Path(args.target_dir).resolve(),
                                )
                            },
                            indent=2,
                        )
                    )
                    return
                except RegistryClientError as exc:
                    print(f"skilgen skills import failed: {exc}", file=sys.stderr)
                    sys.exit(1)
            emit_progress("Importing downstream repositories from the selected directory-style skill source.")
            print(json.dumps(import_external_skill_candidates(project_root=root, slug=args.slug, limit=args.limit, active=args.activate), indent=2))
            return
        if args.skills_command == "publish":
            try:
                emit_progress("Publishing a generated SKILL.md to the Skillayer registry.")
                print(
                    json.dumps(
                        {
                            "published_skill": publish_registry_skill(
                                api_url=args.api_url,
                                skill_file=Path(args.skill_file).resolve(),
                                skill_id=args.skill_id,
                                name=args.name,
                                description=args.description,
                                tags=list(args.tag or []),
                                is_public=not args.private,
                            )
                        },
                        indent=2,
                    )
                )
                return
            except RegistryClientError as exc:
                print(f"skilgen skills publish failed: {exc}", file=sys.stderr)
                sys.exit(1)
        if args.skills_command == "sync":
            if args.all:
                emit_progress("Syncing all installed external skill sources with their upstream repositories.")
                print(json.dumps(sync_all_external_skills(project_root=root), indent=2))
            else:
                emit_progress(f"Syncing the external skill source '{args.slug}' with its upstream repository.")
                print(json.dumps({"synced_skill": sync_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
        if args.skills_command == "remove":
            emit_progress(f"Removing the external skill source '{args.slug}' from the local Skilgen registry.")
            print(json.dumps({"removed_skill": remove_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
        if args.skills_command == "activate":
            emit_progress(f"Activating the external skill source '{args.slug}' for agent loading.")
            print(json.dumps({"activated_skill": activate_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
        if args.skills_command == "deactivate":
            emit_progress(f"Deactivating the external skill source '{args.slug}' for agent loading.")
            print(json.dumps({"deactivated_skill": deactivate_external_skill(project_root=root, slug=args.slug)}, indent=2))
            return
    if args.command == "enterprise":
        root = Path(args.project_root).resolve()
        if args.enterprise_command == "list":
            emit_progress("Loading enterprise skill packs installed for this project.")
            print(json.dumps({"skills": list_enterprise_skills(root)}, indent=2))
            return
        if args.enterprise_command == "ingest":
            emit_progress("Ingesting an existing enterprise skill pack into .skilgen/enterprise-skills.")
            print(
                json.dumps(
                    {
                        "enterprise_skill": ingest_enterprise_skill(
                            root,
                            name=args.name,
                            path=args.path,
                            git_url=args.git_url,
                            url=args.url,
                            ref=args.ref,
                            activate=args.activate,
                            kind=args.kind,
                        )
                    },
                    indent=2,
                )
            )
            return
        if args.enterprise_command == "generate":
            emit_progress("Generating a reusable enterprise skill from the provided docs, code, or runbooks.")
            print(
                json.dumps(
                    {
                        "enterprise_skill": generate_enterprise_skill(
                            root,
                            name=args.name,
                            source_paths=args.source_path,
                            kind=args.kind,
                            activate=args.activate,
                        )
                    },
                    indent=2,
                )
            )
            return
    if args.command == "connectors":
        root = Path(args.project_root).resolve() if hasattr(args, "project_root") else Path(".").resolve()
        if args.connectors_command == "list":
            emit_progress("Loading supported MCP connectors for enterprise coding workflows.")
            print(json.dumps(connector_catalog(system=args.system, search=args.search), indent=2))
            return
        if args.connectors_command == "recommend":
            emit_progress("Scanning the repo for enterprise systems and recommending useful MCP connectors.")
            print(json.dumps(recommend_mcp_connectors(root), indent=2))
            return
        if args.connectors_command == "active":
            emit_progress("Listing active MCP connectors configured for this project.")
            print(json.dumps({"connectors": active_mcp_connectors(root)}, indent=2))
            return
        if args.connectors_command == "activate":
            emit_progress(f"Activating the MCP connector '{args.slug}' for this project.")
            print(json.dumps({"connector": activate_mcp_connector(root, args.slug)}, indent=2))
            return
        if args.connectors_command == "deactivate":
            emit_progress(f"Deactivating the MCP connector '{args.slug}' for this project.")
            print(json.dumps({"connector": deactivate_mcp_connector(root, args.slug)}, indent=2))
            return
    if args.command == "intent":
        result = parse_requirements_file(Path(args.requirements).resolve())
        print(
            json.dumps(
                {
                    "features": result.features,
                    "domain_concepts": result.domain_concepts,
                    "entities": result.entities,
                    "endpoints": result.endpoints,
                    "ui_flows": result.ui_flows,
                },
                indent=2,
            )
        )
        return
    if args.command == "features":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting feature synthesis with the {current_runtime_mode(root)} runtime. Skilgen is reading the project context to identify the capabilities that matter."
        )
        emit_progress("Reading the codebase and optional requirements to identify product capabilities.")
        requirements = Path(args.requirements).resolve() if args.requirements else None
        features = extract_features(requirements, root)
        emit_progress("Grouping detected backend, frontend, and planning signals into a reusable feature inventory.")
        print(json.dumps({"features": [feature.__dict__ for feature in features]}, indent=2))
        return
    if args.command == "plan":
        root = Path(args.project_root).resolve()
        emit_progress(
            f"Starting roadmap planning with the {current_runtime_mode(root)} runtime. Skilgen is turning project context into a staged implementation plan."
        )
        emit_progress("Reading project scope and available inputs for roadmap planning.")
        config = load_config(root)
        plan = build_roadmap_plan(
            config,
            parse_project_intent(root, Path(args.requirements).resolve() if args.requirements else None),
            root,
        )
        emit_progress("Synthesizing implementation phases and sequencing the next delivery steps.")
        print(
            json.dumps(
                {
                    "model": plan.model.__dict__,
                    "steps": [step.__dict__ for step in plan.steps],
                },
                indent=2,
            )
        )
        return
    if args.command == "score":
        emit_progress("Computing the Skilgen Score from groundedness, coverage, freshness, and structure signals.")
        payload = score_payload(Path(args.project_root).resolve(), args.badge_file, history=args.history, history_limit=args.history_limit)
        score_payload_for_checks = payload["current"] if args.history and isinstance(payload.get("current"), dict) else payload
        if args.badge:
            print(score_badge_markdown(score_payload_for_checks))
            return
        if args.ci:
            passed, message = ci_result(
                score_payload_for_checks,
                min_score=args.min_score,
                min_groundedness=args.min_groundedness,
                min_coverage=args.min_coverage,
            )
            print(message)
            if not passed:
                sys.exit(1)
            return
        print(json.dumps(payload, indent=2))
        return
    if args.command == "eval":
        if args.eval_command == "scaffold":
            emit_progress("Creating a starter eval framework for baseline-vs-Skilgen comparisons.")
            print(json.dumps(scaffold_eval_framework(Path(args.project_root).resolve(), args.output_dir), indent=2))
            return
        if args.eval_command == "compare":
            emit_progress("Comparing baseline and Skilgen eval results.")
            print(json.dumps(compare_eval_results(args.baseline, args.skilgen), indent=2))
            return
    if args.command == "status":
        print(json.dumps(status_payload(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "report":
        print(json.dumps(report_payload(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "purge":
        print(json.dumps(purge_runtime_data(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "analytics":
        root = Path(args.project_root).resolve()
        if args.record_skill:
            log_skill_usage(
                root,
                list(args.record_skill),
                event=args.event,
                agent=args.agent,
                context=args.context,
                session_id=args.session_id,
                task=args.task,
            )
            print(
                json.dumps(
                    {
                        "recorded": len(args.record_skill),
                        "skills": list(args.record_skill),
                        "event": args.event,
                        "agent": args.agent,
                        "context": args.context,
                        "session_id": args.session_id,
                        "task": args.task,
                    },
                    indent=2,
                )
            )
            return
        payload = analytics_payload(root, limit=args.limit)
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(_format_analytics_summary(payload))
        return
    if args.command == "doctor":
        payload = doctor_payload(Path(args.project_root).resolve())
        print(json.dumps(payload, indent=2))
        return
    if args.command == "validate":
        print(json.dumps(validate_payload(Path(args.project_root).resolve()), indent=2))
        return
    if args.command == "serve":
        run_server(args.host, args.port)
        return

    targets = ("docs", "skills") if getattr(args, "target", "all") == "all" else (args.target,)
    domains = tuple(getattr(args, "domain", None) or [])

    if args.command == "preview":
        print(
            json.dumps(
                preview_payload(
                    Path(args.requirements).resolve() if args.requirements else None,
                    Path(args.project_root),
                    targets=targets,
                    domains=domains,
                ),
                indent=2,
            )
        )
        return

    if args.command == "watch":
        root = Path(args.project_root).resolve()
        watch_progress = CliProgressReporter()
        emit_progress(
            f"Starting watch mode with the {current_runtime_mode(root)} runtime. Skilgen will explain each refresh as changes are detected."
        )
        try:
            runs = watch_delivery(
                Path(args.requirements).resolve() if args.requirements else None,
                root,
                targets=targets,
                domains=domains,
                interval_seconds=args.interval,
                cycles=args.cycles,
                once=args.once,
                progress_callback=watch_progress.emit,
            )
        finally:
            watch_progress.stop()
        print(json.dumps({"runtime": current_runtime_mode(root), "runs": [[str(path) for path in generated] for generated in runs]}, indent=2))
        return

    root = Path(args.project_root).resolve()
    ensure_auto_update_worker(root, requirements_path=Path(args.requirements).resolve() if args.requirements else None)
    diagnostics = runtime_diagnostics(root)
    progress = CliProgressReporter()
    try:
        progress.emit(
            f"Starting delivery with the {current_runtime_mode(root)} runtime. This may take a bit while Skilgen builds project context and generates the final skill tree."
        )
        if diagnostics["runtime"] != "model_backed":
            progress.emit(f"Model-backed runtime is not ready: {diagnostics['reason']}")
        generated = run_delivery(
            Path(args.requirements).resolve() if args.requirements else None,
            root,
            targets=targets,
            domains=domains,
            dry_run=args.dry_run,
            skip_index=args.skip_index,
            progress_callback=progress.emit,
        )
    finally:
        progress.stop()
    print(
        json.dumps(
            {
                "runtime": current_runtime_mode(root),
                "runtime_diagnostics": diagnostics,
                "generated_files": [str(path) for path in generated],
            },
            indent=2,
        )
    )


def console_main() -> None:
    main()


if __name__ == "__main__":
    console_main()
