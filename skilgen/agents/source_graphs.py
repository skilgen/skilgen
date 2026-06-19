from __future__ import annotations

import ast
from functools import lru_cache
import re
from pathlib import Path

from skilgen.agents.codebase_signals import _iter_code_files, _is_test, _language_for_path, _language_structure
from skilgen.agents.language_parsers import parse_language_evidence
from skilgen.agents.relationship_mapper import build_import_graph
from skilgen.core.models import SymbolRelationship


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


@lru_cache(maxsize=8192)
def _safe_text_cached(path_value: str) -> str:
    return _safe_text(Path(path_value))


@lru_cache(maxsize=8192)
def _parsed_language_evidence(path_value: str):
    return parse_language_evidence(Path(path_value))


def _cached_text(path: Path) -> str:
    return _safe_text_cached(str(path))


def _cached_parse(path: Path):
    return _parsed_language_evidence(str(path))


def clear_source_graph_caches() -> None:
    _safe_text_cached.cache_clear()
    _parsed_language_evidence.cache_clear()


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
        parsed = _cached_parse(path)
        text = _cached_text(path)
        native_symbols = _language_structure(path, text)
        if parsed.backend == "python-ast" and native_symbols:
            symbols = native_symbols
        elif parsed.symbols and native_symbols:
            symbols = list(dict.fromkeys([*native_symbols, *parsed.symbols]))
        else:
            symbols = parsed.symbols or native_symbols
        if symbols:
            graph[path.relative_to(root).as_posix()] = symbols[:20]
    return graph


def build_call_graph(project_root: Path) -> dict[str, list[str]]:
    root = project_root.resolve()
    graph: dict[str, list[str]] = {}
    for path in _iter_code_files(root):
        text = _cached_text(path)
        if not text:
            continue
        parsed = _cached_parse(path)
        if parsed.calls:
            calls = parsed.calls
        elif path.suffix.lower() == ".py":
            calls = _python_call_names(path)
        else:
            calls = _regex_call_names(text)
        if calls:
            graph[path.relative_to(root).as_posix()] = calls[:24]
    return graph


def build_parser_summary(project_root: Path) -> dict[str, dict[str, object]]:
    root = project_root.resolve()
    summary: dict[str, dict[str, object]] = {}
    for path in _iter_code_files(root):
        relative = path.relative_to(root).as_posix()
        parsed = _cached_parse(path)
        summary[relative] = {
            "language": parsed.language,
            "backend": parsed.backend,
            "symbol_count": len(parsed.symbols),
            "call_count": len(parsed.calls),
            "import_count": len(parsed.imports),
            "relationship_count": len(parsed.relationships),
        }
    return summary


def _import_candidates(import_graph: dict[str, list[str]], source: str) -> set[str]:
    candidates: set[str] = set()
    for entry in import_graph.get(source, []):
        if "/" in entry and "." in Path(entry).name:
            candidates.add(entry)
            continue
        module_path = entry.replace(".", "/")
        candidates.update(
            {
                f"{module_path}.py",
                f"{module_path}.ts",
                f"{module_path}.tsx",
                f"{module_path}.js",
                f"{module_path}.jsx",
            }
        )
    return candidates


def build_symbol_relationships(project_root: Path) -> list[SymbolRelationship]:
    root = project_root.resolve()
    import_graph = build_import_graph(root)
    symbol_index: dict[str, list[str]] = {}
    parsed_by_path: dict[str, object] = {}
    for path in _iter_code_files(root):
        relative = path.relative_to(root).as_posix()
        parsed = _cached_parse(path)
        parsed_by_path[relative] = parsed
        for symbol in parsed.symbols:
            symbol_index.setdefault(symbol, []).append(relative)

    relationships: list[SymbolRelationship] = []
    for relative, parsed in parsed_by_path.items():
        candidates = _import_candidates(import_graph, relative)
        for relation in parsed.relationships:
            for target in relation.targets:
                candidate_paths = symbol_index.get(target, [])
                resolved_path = None
                confidence = 0.35
                for candidate in candidate_paths:
                    if candidate in candidates:
                        resolved_path = candidate
                        confidence = 0.95
                        break
                if resolved_path is None and len(candidate_paths) == 1:
                    resolved_path = candidate_paths[0]
                    confidence = 0.7
                relationships.append(
                    SymbolRelationship(
                        source_path=relative,
                        source_symbol=relation.symbol,
                        relationship=relation.relationship,
                        target_symbol=target,
                        target_path=resolved_path,
                        confidence=round(confidence, 2),
                    )
                )
    return relationships


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
        text = _cached_text(path)
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
    token_index: dict[str, list[str]] = {}
    source_relatives = {path: path.relative_to(root).as_posix() for path in sources}
    for source_path, tokens in source_tokens.items():
        relative = source_relatives[source_path]
        for token in tokens:
            token_index.setdefault(token, []).append(relative)
    for test_path in tests:
        test_tokens = _tokenize_stem(test_path.stem) | _tokenize_stem(test_path.parent.name)
        scored: dict[str, int] = {}
        for token in test_tokens:
            for relative in token_index.get(token, []):
                scored[relative] = scored.get(relative, 0) + 1
        if scored:
            mapping[test_path.relative_to(root).as_posix()] = [
                path for path, _score in sorted(scored.items(), key=lambda item: (-item[1], item[0]))[:6]
            ]
    return mapping


def summarize_source_graphs(project_root: Path) -> dict[str, object]:
    root = project_root.resolve()
    symbol_graph = build_symbol_graph(root)
    symbol_relationships = build_symbol_relationships(root)
    call_graph = build_call_graph(root)
    config_runtime_graph = build_config_runtime_graph(root)
    test_mapping = build_test_mapping(root)
    parser_summary = build_parser_summary(root)
    return {
        "symbol_graph": symbol_graph,
        "symbol_relationships": [relationship.__dict__ for relationship in symbol_relationships],
        "call_graph": call_graph,
        "config_runtime_graph": config_runtime_graph,
        "test_mapping": test_mapping,
        "parser_summary": parser_summary,
        "symbol_file_count": len(symbol_graph),
        "symbol_relationship_count": len(symbol_relationships),
        "call_file_count": len(call_graph),
        "config_file_count": len(config_runtime_graph),
        "mapped_test_count": len(test_mapping),
    }
