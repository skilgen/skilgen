from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable

from skilgen.agents.codebase_signals import analyze_codebase
from skilgen.agents.feature_extractor import extract_features, extract_features_native
from skilgen.agents.framework_fingerprint import fingerprint_project
from skilgen.agents.model_registry import resolve_model_settings
from skilgen.agents.relationship_mapper import build_import_graph
from skilgen.agents.requirements_parser import parse_project_intent, parse_project_intent_native, parse_requirements_file, parse_requirements_file_native
from skilgen.agents.roadmap_planner import build_roadmap_plan, build_roadmap_plan_native
from skilgen.core.config import load_config
from skilgen.core.context import build_codebase_context
from skilgen.core.requirements import load_project_context, load_requirements
from skilgen.core.validation import validate_project
from skilgen.core.score import compute_skillgen_score
from skilgen.generators.package import (
    project_doc_paths,
    render_analysis_report,
    render_feature_inventory,
    render_project_report,
    render_traceability_report,
    write_project_docs,
)
from skilgen.generators.skills import planned_skill_paths, write_skills
from skilgen.deep_agents_core import _build_chat_model, _close_model, _normalize_json_with_model, deep_agents_unavailable_reason
from skilgen.deep_agents_core import _classify_model_error, _invoke_with_retry, runtime_diagnostics
from skilgen.external_skills import ensure_external_skills_for_project

try:
    from deepagents import create_deep_agent
    from langchain.chat_models import init_chat_model
    from langchain_core.tools import tool
except ImportError:  # pragma: no cover - exercised implicitly in local env without deps
    create_deep_agent = None
    init_chat_model = None
    tool = None


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(val) for key, val in asdict(value).items()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _serialize(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def _extract_json_block(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("Agent response did not contain a JSON object")


def _message_text(message: object) -> str:
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")
    if isinstance(content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content).strip()
    return str(content).strip()


class DeepAgentsRuntime:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root).resolve()
        self.config = load_config(self.project_root)
        self.model_settings = resolve_model_settings(self.config)

    @property
    def enabled(self) -> bool:
        return (
            create_deep_agent is not None
            and init_chat_model is not None
            and tool is not None
            and deep_agents_unavailable_reason(self.project_root) is None
        )

    def _build_model(self) -> Any:
        return _build_chat_model(self.project_root)

    def _make_tools(self) -> list[Any]:
        if tool is None:
            return []

        @tool
        def read_requirements(requirements_path: str) -> dict[str, Any]:
            """Read and structure the project requirements file."""
            return _serialize(parse_requirements_file_native(Path(requirements_path).resolve()))

        @tool
        def scan_project(project_root: str) -> dict[str, Any]:
            """Scan the project and return framework and codebase signals."""
            root = Path(project_root).resolve()
            return {
                "framework_fingerprint": _serialize(fingerprint_project(root)),
                "signals": _serialize(analyze_codebase(root)),
                "import_graph": _serialize(build_import_graph(root)),
            }

        @tool
        def build_project_context(project_root: str, requirements_path: str | None = None) -> dict[str, Any]:
            """Build the combined codebase context for the given project and requirements."""
            root = Path(project_root).resolve()
            requirements = load_project_context(root, Path(requirements_path).resolve() if requirements_path else None)
            return _serialize(build_codebase_context(root, requirements))

        @tool
        def feature_inventory(requirements_path: str | None, project_root: str) -> dict[str, Any]:
            """Extract the current feature inventory."""
            return {"features": _serialize(extract_features_native(Path(requirements_path).resolve() if requirements_path else None, Path(project_root).resolve()))}

        @tool
        def roadmap_plan(requirements_path: str | None, project_root: str) -> dict[str, Any]:
            """Build a roadmap plan from the requirements and config."""
            config = load_config(Path(project_root).resolve())
            intent = parse_project_intent_native(Path(project_root).resolve(), Path(requirements_path).resolve() if requirements_path else None)
            plan = build_roadmap_plan_native(config, intent)
            return _serialize(plan)

        @tool
        def project_status(project_root: str) -> dict[str, Any]:
            """Return the project status from generated artifacts."""
            root = Path(project_root).resolve()
            skills_root = root / "skills"
            skill_files = sorted(str(path.relative_to(root)) for path in skills_root.rglob("SKILL.md")) if skills_root.exists() else []
            summary_files = sorted(str(path.relative_to(root)) for path in skills_root.rglob("SUMMARY.md")) if skills_root.exists() else []
            return {
                "project_root": str(root),
                "config_exists": (root / "skilgen.yml").exists(),
                "analysis_exists": (root / "ANALYSIS.md").exists(),
                "report_exists": (root / "REPORT.md").exists(),
                "traceability_exists": (root / "TRACEABILITY.md").exists(),
                "agents_exists": (root / "AGENTS.md").exists(),
                "features_exists": (root / "FEATURES.md").exists(),
                "graph_exists": (root / "skills" / "GRAPH.md").exists(),
                "manifest_exists": (root / "skills" / "MANIFEST.md").exists(),
                "skill_count": len(skill_files),
                "skill_files": skill_files,
                "summary_count": len(summary_files),
                "summary_files": summary_files,
            }

        @tool
        def validate_outputs(project_root: str) -> dict[str, Any]:
            """Validate generated project outputs."""
            return _serialize(validate_project(project_root))

        @tool
        def execute_delivery(
            requirements_path: str | None,
            project_root: str,
            targets: list[str] | None = None,
            domains: list[str] | None = None,
            dry_run: bool = False,
        ) -> dict[str, Any]:
            """Execute or preview Skilgen delivery artifacts for a project."""
            generated = native_run_delivery(
                requirements_path,
                project_root,
                targets=tuple(targets or ("docs", "skills")),
                domains=tuple(domains or ()),
                dry_run=dry_run,
            )
            return {"generated_files": [str(path) for path in generated]}

        return [
            read_requirements,
            scan_project,
            build_project_context,
            feature_inventory,
            roadmap_plan,
            project_status,
            validate_outputs,
            execute_delivery,
        ]

    def run(self, task: str, prompt: str, fallback: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        require_agent = os.getenv("SKILGEN_DEEPAGENTS_REQUIRED") == "1"
        if self.config.auto_install_external_skills:
            ensure_external_skills_for_project(self.project_root)
        if not self.enabled:
            if require_agent:
                raise RuntimeError(
                    deep_agents_unavailable_reason(self.project_root)
                    or "Model-backed runtime is required but dependencies or model credentials are unavailable"
                )
            return fallback()

        model = self._build_model()
        agent = create_deep_agent(
            model=model,
            tools=self._make_tools(),
            system_prompt=(
                "You are Skilgen's internal model-backed runtime for analyzing software projects and generating "
                "agent-ready skills, plans, and project reports.\n"
                "You have tool access for requirements interpretation, codebase scanning, roadmap planning, "
                "status inspection, validation, and delivery execution.\n"
                "Operating rules:\n"
                "1. Use tools before making claims about the repository.\n"
                "2. Prefer grounded evidence from requirements files, code signals, and generated artifacts.\n"
                "3. Preserve complete technical detail when summarizing findings.\n"
                "4. Return exactly one valid JSON object with no markdown fences or extra prose.\n"
                "5. If a task requests outputs or planned files, include paths explicitly.\n"
                "6. Avoid speculative architecture claims that are not supported by tool results."
            ),
        )
        result = _invoke_with_retry(
            lambda: agent.invoke({"messages": [{"role": "user", "content": f"Task: {task}\n\n{prompt}"}]}),
            attempts=self.model_settings.retry_attempts,
            delay_seconds=self.model_settings.retry_base_delay_seconds,
            provider=self.model_settings.provider,
            api_key_env=self.model_settings.api_key_env,
        )
        messages = result.get("messages", []) if isinstance(result, dict) else []
        if not messages:
            return fallback()
        try:
            collected = []
            for message in reversed(messages):
                text = _message_text(message)
                if not text:
                    continue
                collected.append(text)
                try:
                    return _extract_json_block(text)
                except Exception:
                    continue
            normalized_source = "\n\n".join(reversed(collected))
            if normalized_source:
                    return _normalize_json_with_model(task, normalized_source, self.project_root)
            raise ValueError("Agent response did not contain a usable JSON object")
        except Exception as exc:
            if require_agent:
                error = _classify_model_error(exc, self.model_settings.provider, self.model_settings.api_key_env)
                raise RuntimeError(
                    f"{error['message']} Task=`{task}` Category={error['category']} "
                    f"Recommendations={' | '.join(error['recommendations'])}"
                ) from exc
            return fallback()
        finally:
            _close_model(model)


def native_fingerprint_payload(project_root: str | Path) -> dict[str, Any]:
    return _serialize(fingerprint_project(Path(project_root).resolve()))


def native_map_payload(project_root: str | Path) -> dict[str, Any]:
    return {"import_graph": build_import_graph(Path(project_root).resolve())}


def native_analyze_payload(project_root: str | Path, requirements: str | Path | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    fingerprint = fingerprint_project(root)
    signals = analyze_codebase(root)
    mapping = build_import_graph(root)
    payload: dict[str, Any] = {
        "project_root": str(root),
        "framework_fingerprint": _serialize(fingerprint),
        "signals": _serialize(signals),
        "import_graph": mapping,
    }
    if requirements is not None:
        context = load_requirements(Path(requirements).resolve())
        codebase_context = build_codebase_context(root, context)
        payload["domain_graph"] = _serialize(codebase_context.domain_graph)
        payload["detected_domains"] = _serialize(codebase_context.detected_domains)
        payload["skill_tree"] = _serialize(codebase_context.skill_tree)
    return payload


def native_intent_payload(requirements: str | Path) -> dict[str, Any]:
    return _serialize(parse_requirements_file(Path(requirements).resolve()))


def native_plan_payload(requirements: str | Path, project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    req = Path(requirements).resolve() if requirements is not None else None
    plan = build_roadmap_plan(load_config(root), parse_project_intent(root, req))
    return _serialize(plan)


def native_features_payload(requirements: str | Path, project_root: str | Path) -> dict[str, Any]:
    return {"features": _serialize(extract_features(Path(requirements).resolve() if requirements is not None else None, Path(project_root).resolve()))}


def native_preview_payload(
    requirements: str | Path | None,
    project_root: str | Path,
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    context = load_project_context(root, Path(requirements).resolve() if requirements is not None else None)
    planned: list[Path] = []
    if "docs" in targets:
        planned.extend(
            [
                root / "ANALYSIS.md",
                root / "FEATURES.md",
                root / "REPORT.md",
                root / "TRACEABILITY.md",
                root / "skilgen.yml",
            ]
        )
    if "skills" in targets:
        planned.extend(planned_skill_paths(context, root / "skills", set(domains)))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in planned:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return {
        "project_root": str(root),
        "planned_files": [str(path) for path in unique],
        "existing_files": [str(path) for path in unique if path.exists()],
        "missing_files": [str(path) for path in unique if not path.exists()],
        "targets": list(targets),
        "domains": list(domains),
    }


def native_validate_payload(project_root: str | Path) -> dict[str, Any]:
    return _serialize(validate_project(project_root))


def native_status_payload(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    skills_root = root / "skills"
    skill_files = sorted(str(path.relative_to(root)) for path in skills_root.rglob("SKILL.md")) if skills_root.exists() else []
    summary_files = sorted(str(path.relative_to(root)) for path in skills_root.rglob("SUMMARY.md")) if skills_root.exists() else []
    return {
        "project_root": str(root),
        "config_exists": (root / "skilgen.yml").exists(),
        "analysis_exists": (root / "ANALYSIS.md").exists(),
        "report_exists": (root / "REPORT.md").exists(),
        "traceability_exists": (root / "TRACEABILITY.md").exists(),
        "agents_exists": (root / "AGENTS.md").exists(),
        "features_exists": (root / "FEATURES.md").exists(),
        "graph_exists": (root / "skills" / "GRAPH.md").exists(),
        "manifest_exists": (root / "skills" / "MANIFEST.md").exists(),
        "skill_count": len(skill_files),
        "skill_files": skill_files,
        "summary_count": len(summary_files),
        "summary_files": summary_files,
        "runtime_diagnostics": runtime_diagnostics(root),
    }


def native_report_payload(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    status = native_status_payload(root)
    signals = analyze_codebase(root)
    skill_domains = sorted({Path(path).parts[1] for path in status["skill_files"]}) if status["skill_files"] else []
    return {
        "status": status,
        "skilgen_score": compute_skillgen_score(root),
        "domains": skill_domains,
        "signal_counts": {
            "backend_routes": len(signals.backend_routes),
            "frontend_routes": len(signals.frontend_routes),
            "components": len(signals.components),
            "services": len(signals.services),
            "tests": len(signals.tests),
            "data_models": len(signals.data_models),
            "persistence_layers": len(signals.persistence_layers),
            "background_jobs": len(signals.background_jobs),
            "auth_files": len(signals.auth_files),
            "state_files": len(signals.state_files),
            "design_system_files": len(signals.design_system_files),
        },
        "summary": f"Detected {status['skill_count']} skill files and {status['summary_count']} summary files across {len(skill_domains)} domains.",
    }


def native_doc_payloads(requirements: str | Path | None, project_root: str | Path) -> dict[str, str]:
    context = load_project_context(Path(project_root).resolve(), Path(requirements).resolve() if requirements is not None else None)
    root = Path(project_root).resolve()
    return {
        "analysis": render_analysis_report(context, root),
        "features": render_feature_inventory(context),
        "report": render_project_report(context, root),
        "traceability": render_traceability_report(context, root),
    }


def native_run_delivery(
    requirements_path: str | Path | None = None,
    project_root: str | Path = ".",
    *,
    targets: tuple[str, ...] = ("docs", "skills"),
    domains: tuple[str, ...] = (),
    dry_run: bool = False,
) -> list[Path]:
    root = Path(project_root).resolve()
    load_config(root)
    context = load_project_context(root, Path(requirements_path).resolve() if requirements_path is not None else None)
    fingerprint_project(root)
    build_codebase_context(root, context)
    generated: list[Path] = []
    if "docs" in targets:
        if dry_run:
            generated.extend(project_doc_paths(root))
        else:
            generated.extend(write_project_docs(context, root))
    if "skills" in targets:
        if dry_run:
            generated.extend(planned_skill_paths(context, root / "skills", set(domains)))
        else:
            generated.extend(write_skills(context, root / "skills", set(domains)))
    return generated
