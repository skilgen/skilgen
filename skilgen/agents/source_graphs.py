from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from skilgen.agents.codebase_signals import _iter_code_files, _is_test, _language_for_path, _language_structure


CONFIG_RUNTIME_NAMES = {
    "pyproject.toml",
    "package.json",
    "skilgen.yml",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
    ".env",
    ".env.example",
    "requirements.txt",
}
ENV_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
RUNTIME_HINTS = {
    "postgres": ("postgres", "postgresql", "psycopg"),
    "redis": ("redis",),
    "kafka": ("kafka",),
    "s3": ("s3", "aws s3"),
    "docker": ("docker", "container"),
    "kubernetes": ("kubernetes", "kubectl", "helm", "aks", "eks", "gke"),
    "jira": ("jira", "atlassian"),
    "confluence": ("confluence",),
    "sharepoint": ("sharepoint", "microsoft graph"),
    "snowflake": ("snowflake",),
    "datadog": ("datadog",),
    "slack": ("slack",),
}
STOP_CALL_NAMES = {
    "if",
    "for",
    "while",
    "switch",
    "return",
    "catch",
    "new",
    "super",
    "this",
    "println",
    "print",
}
COMMON_TEST_TOKENS = {"test", "tests", "spec", "suite", "integration", "unit", "e2e"}


def _safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _python_call_names(path: Path) -> list[str]:
    try:
        tree = ast.parse(_safe_text(path), filename=str(path))
    except (SyntaxError, ValueError):
        return []
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
    return sorted(calls)


def _regex_call_names(text: str) -> list[str]:
    calls = {
        match.group(1)
        for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", text)
        if match.group(1) not in STOP_CALL_NAMES
    }
    return sorted(calls)


def build_symbol_graph(project_root: Path) -> dict[str, list[str]]:
    root = project_root.resolve()
    graph: dict[str, list[str]] = {}
    for path in _iter_code_files(root):
        text = _safe_text(path)
        if not text:
            continue
        symbols = _language_structure(path, text)
        if symbols:
            graph[path.relative_to(root).as_posix()] = symbols[:20]
    return graph


def build_call_graph(project_root: Path) -> dict[str, list[str]]:
    root = project_root.resolve()
    graph: dict[str, list[str]] = {}
    for path in _iter_code_files(root):
        text = _safe_text(path)
        if not text:
            continue
        if path.suffix.lower() == ".py":
            calls = _python_call_names(path)
        else:
            calls = _regex_call_names(text)
        if calls:
            graph[path.relative_to(root).as_posix()] = calls[:24]
    return graph


def build_config_runtime_graph(project_root: Path) -> dict[str, list[str]]:
    root = project_root.resolve()
    graph: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith((".git/", ".skilgen/", "skills/", "__pycache__/")):
            continue
        if path.name not in CONFIG_RUNTIME_NAMES and path.suffix.lower() not in {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".tf"}:
            continue
        text = _safe_text(path)
        if not text:
            continue
        entries: set[str] = set()
        for env_var in ENV_PATTERN.findall(text):
            entries.add(f"env:{env_var}")
        lowered = text.lower()
        for name, needles in RUNTIME_HINTS.items():
            if any(needle in lowered for needle in needles):
                entries.add(f"runtime:{name}")
        if entries:
            graph[relative] = sorted(entries)
    return graph


def _tokenize_stem(value: str) -> set[str]:
    tokens = {
        token
        for token in re.split(r"[^a-zA-Z0-9]+", value.lower())
        if token and token not in COMMON_TEST_TOKENS and len(token) > 1
    }
    return tokens


def build_test_mapping(project_root: Path) -> dict[str, list[str]]:
    root = project_root.resolve()
    tests: list[Path] = []
    sources: list[Path] = []
    for path in _iter_code_files(root):
        relative = path.relative_to(root).as_posix()
        if _is_test(relative, path.stem):
            tests.append(path)
        else:
            sources.append(path)
    mapping: dict[str, list[str]] = {}
    source_tokens = {
        path: _tokenize_stem(path.stem) | _tokenize_stem(path.parent.name)
        for path in sources
    }
    for test_path in tests:
        test_tokens = _tokenize_stem(test_path.stem) | _tokenize_stem(test_path.parent.name)
        scored: list[tuple[int, str]] = []
        for source_path, tokens in source_tokens.items():
            overlap = len(test_tokens & tokens)
            if overlap == 0:
                continue
            scored.append((overlap, source_path.relative_to(root).as_posix()))
        if scored:
            mapping[test_path.relative_to(root).as_posix()] = [path for _score, path in sorted(scored, key=lambda item: (-item[0], item[1]))[:6]]
    return mapping


def summarize_source_graphs(project_root: Path) -> dict[str, object]:
    root = project_root.resolve()
    symbol_graph = build_symbol_graph(root)
    call_graph = build_call_graph(root)
    config_runtime_graph = build_config_runtime_graph(root)
    test_mapping = build_test_mapping(root)
    return {
        "symbol_graph": symbol_graph,
        "call_graph": call_graph,
        "config_runtime_graph": config_runtime_graph,
        "test_mapping": test_mapping,
        "symbol_file_count": len(symbol_graph),
        "call_file_count": len(call_graph),
        "config_file_count": len(config_runtime_graph),
        "mapped_test_count": len(test_mapping),
    }
