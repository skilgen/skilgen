from __future__ import annotations

import json
from pathlib import Path
import re
from xml.etree import ElementTree

from skilgen.core.models import RuntimeSignalArtifact, RuntimeSignals


_RUNTIME_FILE_NAMES = {
    "coverage.xml",
    "lcov.info",
}
_RUNTIME_SUFFIXES = {".sarif", ".xml", ".info", ".json"}
_RESULT_HINTS = ("junit", "pytest", "test-results", "surefire", "failsafe")
_TRACE_HINTS = ("trace", "traces", "spans", "otel")
_CODE_PATH_HINTS = ("code.filepath", "code.file_path", "source.file", "filepath", "file", "path")


def _safe_relative(project_root: Path, raw_path: str | None) -> str | None:
    if not raw_path:
        return None
    candidate = Path(str(raw_path).strip())
    if not candidate.as_posix():
        return None
    resolved = (project_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        return resolved.relative_to(project_root).as_posix()
    except ValueError:
        return candidate.as_posix().lstrip("./")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _looks_like_runtime_artifact(path: Path) -> bool:
    lowered = path.name.lower()
    return (
        lowered in _RUNTIME_FILE_NAMES
        or lowered.endswith(".sarif.json")
        or any(hint in lowered for hint in _RESULT_HINTS)
        or any(hint in lowered for hint in _TRACE_HINTS)
    )


def _parse_junit_xml(project_root: Path, path: Path) -> tuple[RuntimeSignalArtifact, dict[str, dict[str, object]]]:
    root = ElementTree.fromstring(_read_text(path))
    total = failures = errors = skipped = 0
    related_paths: set[str] = set()
    test_results: dict[str, dict[str, object]] = {}
    for suite in root.findall(".//testsuite") + ([root] if root.tag == "testsuite" else []):
        total += int(suite.attrib.get("tests", "0") or 0)
        failures += int(suite.attrib.get("failures", "0") or 0)
        errors += int(suite.attrib.get("errors", "0") or 0)
        skipped += int(suite.attrib.get("skipped", "0") or 0)
    for case in root.findall(".//testcase"):
        raw_file = case.attrib.get("file") or case.attrib.get("classname") or case.attrib.get("name")
        related = _safe_relative(project_root, raw_file)
        if related:
            related_paths.add(related)
            status = "passed"
            if case.find("failure") is not None:
                status = "failed"
            elif case.find("error") is not None:
                status = "error"
            elif case.find("skipped") is not None:
                status = "skipped"
            bucket = test_results.setdefault(related, {"passed": 0, "failed": 0, "error": 0, "skipped": 0})
            bucket[status] = int(bucket.get(status, 0)) + 1
    artifact = RuntimeSignalArtifact(
        path=path.relative_to(project_root).as_posix(),
        kind="test_results",
        format="junit-xml",
        signal_count=max(total, len(test_results)),
        related_paths=sorted(related_paths)[:16],
        summary=f"{total} test cases, {failures} failures, {errors} errors, {skipped} skipped",
    )
    return artifact, test_results


def _parse_coverage_xml(project_root: Path, path: Path) -> tuple[RuntimeSignalArtifact, dict[str, float]]:
    root = ElementTree.fromstring(_read_text(path))
    coverage_by_path: dict[str, float] = {}
    related_paths: list[str] = []
    for class_node in root.findall(".//class"):
        filename = _safe_relative(project_root, class_node.attrib.get("filename"))
        if not filename:
            continue
        line_rate = class_node.attrib.get("line-rate") or class_node.attrib.get("line_rate")
        if line_rate:
            try:
                coverage_by_path[filename] = round(float(line_rate), 4)
            except ValueError:
                continue
        else:
            lines = class_node.findall(".//line")
            if lines:
                hit_count = sum(1 for line in lines if int(line.attrib.get("hits", "0") or 0) > 0)
                coverage_by_path[filename] = round(hit_count / max(1, len(lines)), 4)
        related_paths.append(filename)
    overall = round(sum(coverage_by_path.values()) / max(1, len(coverage_by_path)), 4)
    artifact = RuntimeSignalArtifact(
        path=path.relative_to(project_root).as_posix(),
        kind="coverage",
        format="coverage-xml",
        signal_count=len(coverage_by_path),
        related_paths=sorted(dict.fromkeys(related_paths))[:16],
        summary=f"Coverage data for {len(coverage_by_path)} files, average line coverage {overall:.2%}",
    )
    return artifact, coverage_by_path


def _parse_lcov(project_root: Path, path: Path) -> tuple[RuntimeSignalArtifact, dict[str, float]]:
    coverage_by_path: dict[str, float] = {}
    current_path: str | None = None
    found = hits = 0
    for line in _read_text(path).splitlines():
        if line.startswith("SF:"):
            if current_path and found:
                coverage_by_path[current_path] = round(hits / max(1, found), 4)
            current_path = _safe_relative(project_root, line[3:].strip())
            found = hits = 0
        elif line.startswith("DA:"):
            found += 1
            try:
                if int(line.split(",", 1)[1]) > 0:
                    hits += 1
            except (IndexError, ValueError):
                continue
    if current_path and found:
        coverage_by_path[current_path] = round(hits / max(1, found), 4)
    overall = round(sum(coverage_by_path.values()) / max(1, len(coverage_by_path)), 4)
    artifact = RuntimeSignalArtifact(
        path=path.relative_to(project_root).as_posix(),
        kind="coverage",
        format="lcov",
        signal_count=len(coverage_by_path),
        related_paths=sorted(coverage_by_path)[:16],
        summary=f"LCOV coverage for {len(coverage_by_path)} files, average line coverage {overall:.2%}",
    )
    return artifact, coverage_by_path


def _json_load(path: Path) -> object | None:
    text = _read_text(path)
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _parse_sarif(project_root: Path, path: Path) -> tuple[RuntimeSignalArtifact, dict[str, list[str]]]:
    payload = _json_load(path)
    findings: dict[str, list[str]] = {}
    if not isinstance(payload, dict):
        artifact = RuntimeSignalArtifact(
            path=path.relative_to(project_root).as_posix(),
            kind="sast",
            format="sarif",
            signal_count=0,
            related_paths=[],
            summary="No parseable SARIF findings were detected",
        )
        return artifact, findings
    for run in payload.get("runs", []):
        if not isinstance(run, dict):
            continue
        for result in run.get("results", []):
            if not isinstance(result, dict):
                continue
            level = str(result.get("level", "warning")).strip() or "warning"
            rule_id = str(result.get("ruleId", "finding")).strip() or "finding"
            locations = result.get("locations", [])
            if not isinstance(locations, list):
                locations = []
            for location in locations:
                uri = (
                    location.get("physicalLocation", {})
                    .get("artifactLocation", {})
                    .get("uri")
                    if isinstance(location, dict)
                    else None
                )
                related = _safe_relative(project_root, uri)
                if related:
                    findings.setdefault(related, []).append(f"{level}:{rule_id}")
    artifact = RuntimeSignalArtifact(
        path=path.relative_to(project_root).as_posix(),
        kind="sast",
        format="sarif",
        signal_count=sum(len(values) for values in findings.values()),
        related_paths=sorted(findings)[:16],
        summary=f"SAST findings across {len(findings)} files",
    )
    return artifact, findings


def _collect_trace_paths(project_root: Path, payload: object) -> tuple[list[str], list[str], int]:
    services: set[str] = set()
    related_paths: set[str] = set()
    span_count = 0

    def walk(node: object) -> None:
        nonlocal span_count
        if isinstance(node, dict):
            if "spans" in node and isinstance(node["spans"], list):
                for span in node["spans"]:
                    span_count += 1
                    walk(span)
            attributes = node.get("attributes")
            if isinstance(attributes, list):
                for entry in attributes:
                    if not isinstance(entry, dict):
                        continue
                    key = str(entry.get("key", "")).strip()
                    value = entry.get("value")
                    string_value = ""
                    if isinstance(value, dict):
                        string_value = str(value.get("stringValue", "") or value.get("value", "")).strip()
                    elif value is not None:
                        string_value = str(value).strip()
                    if key == "service.name" and string_value:
                        services.add(string_value)
                    if key in _CODE_PATH_HINTS:
                        related = _safe_relative(project_root, string_value)
                        if related:
                            related_paths.add(related)
            for key, value in node.items():
                if key == "service" and isinstance(value, str):
                    services.add(value)
                if key in _CODE_PATH_HINTS and isinstance(value, str):
                    related = _safe_relative(project_root, value)
                    if related:
                        related_paths.add(related)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return sorted(services), sorted(related_paths), span_count


def _parse_trace_json(project_root: Path, path: Path) -> tuple[RuntimeSignalArtifact, list[str]]:
    payload = _json_load(path)
    if payload is None:
        artifact = RuntimeSignalArtifact(
            path=path.relative_to(project_root).as_posix(),
            kind="traces",
            format="json",
            signal_count=0,
            related_paths=[],
            summary="No parseable trace spans were detected",
        )
        return artifact, []
    services, related_paths, span_count = _collect_trace_paths(project_root, payload)
    artifact = RuntimeSignalArtifact(
        path=path.relative_to(project_root).as_posix(),
        kind="traces",
        format="json",
        signal_count=span_count,
        related_paths=related_paths[:16],
        summary=f"{span_count} spans across {len(services)} services",
    )
    return artifact, services


def collect_runtime_signals(project_root: Path) -> RuntimeSignals:
    root = project_root.resolve()
    artifacts: list[RuntimeSignalArtifact] = []
    coverage_by_path: dict[str, float] = {}
    test_results: dict[str, dict[str, object]] = {}
    sast_findings: dict[str, list[str]] = {}
    trace_services: set[str] = set()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith((".git/", ".skilgen/", "skills/")):
            continue
        lowered = path.name.lower()
        if not (_looks_like_runtime_artifact(path) or path.suffix.lower() in _RUNTIME_SUFFIXES):
            continue
        try:
            if lowered == "coverage.xml":
                artifact, coverage = _parse_coverage_xml(root, path)
                artifacts.append(artifact)
                coverage_by_path.update(coverage)
            elif lowered == "lcov.info":
                artifact, coverage = _parse_lcov(root, path)
                artifacts.append(artifact)
                coverage_by_path.update(coverage)
            elif lowered.endswith(".sarif") or lowered.endswith(".sarif.json"):
                artifact, findings = _parse_sarif(root, path)
                artifacts.append(artifact)
                for target, signals in findings.items():
                    sast_findings.setdefault(target, []).extend(signals)
            elif path.suffix.lower() == ".xml" and any(hint in lowered for hint in _RESULT_HINTS):
                artifact, results = _parse_junit_xml(root, path)
                artifacts.append(artifact)
                for target, payload in results.items():
                    bucket = test_results.setdefault(target, {"passed": 0, "failed": 0, "error": 0, "skipped": 0})
                    for key, value in payload.items():
                        bucket[key] = int(bucket.get(key, 0)) + int(value)
            elif path.suffix.lower() == ".json" and any(hint in lowered for hint in _TRACE_HINTS):
                artifact, services = _parse_trace_json(root, path)
                artifacts.append(artifact)
                trace_services.update(services)
        except (ElementTree.ParseError, ValueError):
            continue
    recommendations: list[str] = []
    if coverage_by_path:
        low_coverage = [path for path, ratio in sorted(coverage_by_path.items(), key=lambda item: item[1]) if ratio < 0.5][:5]
        if low_coverage:
            recommendations.append(
                f"Low runtime coverage surfaced for: {', '.join(low_coverage)}."
            )
    if sast_findings:
        recommendations.append("Treat SARIF findings as first-class evidence when prioritizing skill hardening and security guidance.")
    if trace_services:
        recommendations.append(f"Runtime traces reference these services: {', '.join(sorted(trace_services)[:6])}.")
    if test_results:
        failing = [path for path, payload in test_results.items() if int(payload.get('failed', 0)) or int(payload.get('error', 0))]
        if failing:
            recommendations.append(f"Active failing test artifacts point at: {', '.join(failing[:6])}.")
    return RuntimeSignals(
        artifacts=artifacts,
        coverage_by_path=coverage_by_path,
        test_results=test_results,
        sast_findings={path: values[:12] for path, values in sast_findings.items()},
        trace_services=sorted(trace_services),
        recommendations=recommendations,
    )
