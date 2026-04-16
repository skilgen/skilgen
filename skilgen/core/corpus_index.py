from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from skilgen.agents.language_parsers import ParsedLanguageEvidence, parse_language_evidence
from skilgen.core.config import load_config
from skilgen.core.document_ingestion import extract_document_text
from skilgen.core.models import CorpusSettings, SkilgenConfig


SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".java",
    ".go",
    ".rs",
    ".cbl",
    ".cob",
    ".cpy",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cc",
    ".cxx",
    ".cs",
    ".rb",
    ".kt",
    ".kts",
    ".scala",
    ".php",
    ".swift",
    ".lua",
    ".zig",
    ".ps1",
    ".psm1",
    ".ex",
    ".exs",
    ".m",
    ".mm",
    ".dart",
    ".jl",
    ".sh",
    ".bash",
}
CONFIG_EXTENSIONS = {".yaml", ".yml", ".toml", ".json", ".ini", ".cfg", ".env", ".tf", ".hcl", ".bicep"}
DOCUMENTATION_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".adoc", ".asciidoc"}
ENTERPRISE_DOCUMENT_EXTENSIONS = {".docx", ".pdf", ".pptx", ".xlsx", ".html", ".htm", ".csv", ".tsv", ".xml"}
CONFIG_FILENAMES = {
    ".env",
    ".env.example",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Jenkinsfile",
    ".gitlab-ci.yml",
    "Chart.yaml",
    "values.yaml",
    "requirements.txt",
    "package.json",
    "pyproject.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Cargo.toml",
    "go.mod",
}
EXCLUDED_PARTS = {
    ".git",
    ".skilgen",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    "vendor",
    "third_party",
    "skills",
}
DEFAULT_EXCLUDE_PATTERNS = [
    "*.pb.go",
    "*_gen.go",
    "*_pb2.py",
    "*.generated.*",
    "*.min.js",
    "*.min.css",
    "*.lock",
    "**/migrations/[0-9]*.py",
]
BINARY_EXTENSIONS = {
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".whl",
    ".egg",
    ".pyc",
    ".class",
    ".jar",
    ".war",
}
GENERATED_SKILGEN_ARTIFACTS = {
    "AGENTS.md",
    "ANALYSIS.md",
    "ARCHITECTURE.md",
    "FEATURES.md",
    "REPORT.md",
    "TRACEABILITY.md",
    "skilgen-dashboard.html",
}
RUNTIME_HINTS = {
    "postgres": ("postgres", "postgresql", "psycopg"),
    "redis": ("redis",),
    "kafka": ("kafka",),
    "s3": ("s3", "aws s3"),
    "docker": ("docker", "container"),
    "kubernetes": ("kubernetes", "kubectl", "helm", "aks", "eks", "gke"),
    "slack": ("slack",),
    "datadog": ("datadog",),
    "snowflake": ("snowflake",),
    "terraform": ("terraform",),
}
ENV_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
DOC_PRIORITY_PATTERNS = {
    "architecture.md": 9.0,
    "architecture.mdx": 9.0,
    "adr-": 8.0,
    "decision-": 7.0,
    "runbook": 7.0,
    "design": 6.0,
    "spec": 6.0,
}
DOC_PRIORITY_DIRS = {
    "docs": 2.5,
    "architecture": 4.0,
    "runbooks": 3.5,
    "specs": 3.5,
    "adr": 4.0,
    "design": 3.0,
}
SMALL_TEXT_LIMIT = 120_000


def corpus_cache_path(project_root: Path, config: SkilgenConfig | None = None) -> Path:
    root = project_root.resolve()
    resolved = config or load_config(root)
    return root / resolved.corpus.cache_path


def load_corpus_index(project_root: Path, config: SkilgenConfig | None = None) -> dict[str, Any] | None:
    path = corpus_cache_path(project_root, config)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def ensure_corpus_index(project_root: Path, config: SkilgenConfig | None = None) -> dict[str, Any] | None:
    root = project_root.resolve()
    resolved = config or load_config(root)
    if not resolved.corpus.enabled:
        return None
    return build_corpus_index(root, resolved)


def build_corpus_index(project_root: Path, config: SkilgenConfig | None = None) -> dict[str, Any]:
    root = project_root.resolve()
    resolved = config or load_config(root)
    cache_path = corpus_cache_path(root, resolved)
    previous = load_corpus_index(root, resolved) or {}
    from skilgen.agents.codebase_signals import analyze_codebase

    previous_entries = {
        entry["path"]: entry
        for entry in previous.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    signals = analyze_codebase(root)
    signal_bonus = {
        path
        for bucket in [
            signals.backend_routes,
            signals.frontend_routes,
            signals.components,
            signals.services,
            signals.tests,
            signals.data_models,
            signals.persistence_layers,
            signals.background_jobs,
            signals.auth_files,
            signals.state_files,
            signals.design_system_files,
            signals.legacy_programs,
            signals.copybooks,
        ]
        for path in bucket
    }

    entries: list[dict[str, Any]] = []
    for path in _iter_indexable_files(root, resolved.corpus):
        relative = path.relative_to(root).as_posix()
        stat = path.stat()
        cached = previous_entries.get(relative)
        if cached is not None and cached.get("mtime_ns") == stat.st_mtime_ns and cached.get("size") == stat.st_size:
            entry = dict(cached)
        else:
            sha256 = _sha256(path)
            if cached is not None and cached.get("sha256") == sha256:
                entry = dict(cached)
                entry["mtime_ns"] = stat.st_mtime_ns
                entry["size"] = stat.st_size
            else:
                entry = _build_entry(root, path, relative, signal_bonus)
                entry["sha256"] = sha256
                entry["mtime_ns"] = stat.st_mtime_ns
                entry["size"] = stat.st_size
        entries.append(entry)

    import_graph = _build_import_graph(root, entries)
    _apply_source_importance(entries, import_graph, signal_bonus)
    clusters = _build_clusters(entries, import_graph)
    cluster_lookup = {path: cluster_id for cluster_id, paths in clusters.items() for path in paths}
    for entry in entries:
        if entry["category"] == "source":
            entry["cluster_id"] = cluster_lookup.get(entry["path"])
        else:
            entry.pop("cluster_id", None)

    payload = {
        "version": 1,
        "project_root": str(root),
        "cache_path": str(cache_path),
        "entries": sorted(entries, key=lambda entry: entry["path"]),
        "clusters": clusters,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _iter_indexable_files(project_root: Path, corpus: CorpusSettings) -> list[Path]:
    files: list[Path] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root).as_posix()
        if _is_excluded(relative, corpus):
            continue
        files.append(path)
    return sorted(files)


def _is_excluded(relative_path: str, corpus: CorpusSettings) -> bool:
    pure_path = PurePosixPath(relative_path)
    parts = set(pure_path.parts)
    if parts & EXCLUDED_PARTS:
        return True
    if len(pure_path.parts) == 1 and pure_path.name in GENERATED_SKILGEN_ARTIFACTS:
        return True
    lowered = relative_path.lower()
    if any(lowered.endswith(extension) for extension in BINARY_EXTENSIONS):
        return True
    if corpus.exclude_generated and any(_matches_pattern(relative_path, pattern) for pattern in [*DEFAULT_EXCLUDE_PATTERNS, *corpus.exclude_patterns]):
        return True
    return False


def _matches_pattern(relative_path: str, pattern: str) -> bool:
    posix_path = PurePosixPath(relative_path)
    return posix_path.match(pattern) or fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(posix_path.name, pattern)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(65_536):
            digest.update(chunk)
    return digest.hexdigest()


def _classify_path(relative_path: str, path: Path) -> str:
    name = path.name
    lower_name = name.lower()
    suffix = path.suffix.lower()
    if suffix in SOURCE_EXTENSIONS:
        return "source"
    if name in CONFIG_FILENAMES or lower_name in {item.lower() for item in CONFIG_FILENAMES}:
        return "config"
    if suffix in CONFIG_EXTENSIONS:
        return "config"
    if suffix in DOCUMENTATION_EXTENSIONS:
        return "documentation"
    if suffix in ENTERPRISE_DOCUMENT_EXTENSIONS:
        return "enterprise_document"
    if path.suffixes[-2:] == [".env", ".example"]:
        return "config"
    return "other"


def _safe_text(path: Path) -> str:
    try:
        if path.stat().st_size <= SMALL_TEXT_LIMIT:
            return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    try:
        return extract_document_text(path)
    except Exception:
        return ""


def _build_entry(project_root: Path, path: Path, relative: str, signal_bonus: set[str]) -> dict[str, Any]:
    category = _classify_path(relative, path)
    if category == "source":
        parsed = parse_language_evidence(path)
        extracted_terms = _source_terms(parsed)
        return {
            "path": relative,
            "category": category,
            "extracted_terms": extracted_terms,
            "importance_score": 0.2 if relative in signal_bonus else 0.0,
            "imports": parsed.imports,
            "language": parsed.language,
        }
    if category == "config":
        text = _safe_text(path)
        runtime_terms = _runtime_terms(text)
        return {
            "path": relative,
            "category": category,
            "extracted_terms": runtime_terms,
            "importance_score": float(len([term for term in runtime_terms if term.startswith("runtime:")])),
        }
    if category == "documentation":
        text = _safe_text(path)
        return {
            "path": relative,
            "category": category,
            "extracted_terms": _document_terms(text),
            "importance_score": _documentation_score(relative),
        }
    if category == "enterprise_document":
        text = _safe_text(path) if _enterprise_significant(relative) else ""
        return {
            "path": relative,
            "category": category,
            "extracted_terms": _document_terms(text),
            "importance_score": _enterprise_score(relative),
        }
    return {
        "path": relative,
        "category": category,
        "extracted_terms": [],
        "importance_score": 0.0,
    }


def _source_terms(parsed: ParsedLanguageEvidence) -> list[str]:
    combined = [*parsed.symbols, *parsed.imports, *parsed.calls]
    deduped: list[str] = []
    seen: set[str] = set()
    for term in combined:
        value = term.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(value[:180])
        if len(deduped) >= 40:
            break
    return deduped


def _runtime_terms(text: str) -> list[str]:
    terms: set[str] = set()
    if not text:
        return []
    lowered = text.lower()
    for env_name in ENV_PATTERN.findall(text):
        terms.add(f"env:{env_name}")
    for runtime, needles in RUNTIME_HINTS.items():
        if any(needle in lowered for needle in needles):
            terms.add(f"runtime:{runtime}")
    return sorted(terms)


def _document_terms(text: str) -> list[str]:
    if not text:
        return []
    terms: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip().lstrip("#*- ").strip()
        if not line:
            continue
        lowered = line.lower()
        if len(line) > 180:
            line = line[:180]
        if lowered in seen:
            continue
        seen.add(lowered)
        terms.append(line)
        if len(terms) >= 20:
            break
    return terms


def _documentation_score(relative_path: str) -> float:
    pure_path = PurePosixPath(relative_path)
    parts = [part.lower() for part in pure_path.parts]
    name = pure_path.name.lower()
    score = 1.0
    for keyword, bonus in DOC_PRIORITY_DIRS.items():
        if keyword in parts:
            score += bonus
    for needle, bonus in DOC_PRIORITY_PATTERNS.items():
        if needle.endswith("-"):
            if name.startswith(needle):
                score += bonus
        elif needle in name:
            score += bonus
    if "readme" in name and not {"docs", "architecture", "design"} & set(parts):
        score -= 0.5
    return max(score, 0.0)


def _enterprise_significant(relative_path: str) -> bool:
    parts = {part.lower() for part in PurePosixPath(relative_path).parts}
    return bool(parts & set(DOC_PRIORITY_DIRS))


def _enterprise_score(relative_path: str) -> float:
    if not _enterprise_significant(relative_path):
        return 0.0
    return _documentation_score(relative_path) + 1.5


def _build_import_graph(project_root: Path, entries: list[dict[str, Any]]) -> dict[str, list[str]]:
    source_paths = {entry["path"]: project_root / entry["path"] for entry in entries if entry["category"] == "source"}
    module_index = _module_index(source_paths)
    entry_lookup = entries_by_path(entries)
    graph: dict[str, list[str]] = {}
    for relative, path in source_paths.items():
        imports = []
        for raw_import in entry_lookup.get(relative, {}).get("imports", []):
            resolved = _resolve_import(project_root, path, str(raw_import), module_index, source_paths)
            if resolved is not None and resolved != relative:
                imports.append(resolved)
        graph[relative] = sorted(set(imports))
    return graph


def _module_index(source_paths: dict[str, Path]) -> dict[str, str]:
    modules: dict[str, str] = {}
    for relative in source_paths:
        pure = PurePosixPath(relative)
        stem_path = "/".join(pure.parts[:-1] + (pure.stem,))
        dotted_path = stem_path.replace("/", ".")
        modules[stem_path] = relative
        modules[dotted_path] = relative
        modules[pure.stem] = modules.get(pure.stem, relative)
    return modules


def _resolve_import(
    project_root: Path,
    source_path: Path,
    raw_import: str,
    module_index: dict[str, str],
    source_paths: dict[str, Path],
) -> str | None:
    cleaned = raw_import.strip().strip("\"'`")
    if not cleaned:
        return None
    if cleaned.startswith("from "):
        match = re.match(r"from\s+([A-Za-z0-9_./:-]+)", cleaned)
        if match:
            cleaned = match.group(1)
    elif cleaned.startswith("import "):
        match = re.match(r"import\s+([A-Za-z0-9_./:-]+)", cleaned)
        if match:
            cleaned = match.group(1)
    elif cleaned.startswith("use "):
        match = re.match(r"use\s+([A-Za-z0-9_./:-]+)", cleaned)
        if match:
            cleaned = match.group(1)
    elif cleaned.startswith("include "):
        match = re.match(r"include\s+([A-Za-z0-9_./:-]+)", cleaned)
        if match:
            cleaned = match.group(1)
    elif cleaned.startswith("COPY "):
        match = re.match(r"COPY\s+([A-Za-z0-9_./:-]+)", cleaned)
        if match:
            cleaned = match.group(1)
    elif cleaned.startswith("require("):
        match = re.search(r"""require\(\s*["']([^"']+)["']\s*\)""", cleaned)
        if match:
            cleaned = match.group(1)
    if cleaned.startswith(("./", "../")):
        candidate = (source_path.parent / cleaned).resolve()
        for resolved in _candidate_files(project_root, candidate):
            if resolved in source_paths.values():
                return resolved.relative_to(project_root).as_posix()
        return None
    if cleaned.startswith("."):
        parent = source_path.parent
        dots = len(cleaned) - len(cleaned.lstrip("."))
        remainder = cleaned.lstrip(".")
        base = parent
        for _ in range(max(dots - 1, 0)):
            base = base.parent
        if remainder:
            candidate = (base / remainder.replace(".", "/")).resolve()
            for resolved in _candidate_files(project_root, candidate):
                if resolved in source_paths.values():
                    return resolved.relative_to(project_root).as_posix()
        return None
    normalized = cleaned.replace("::", "/").replace(".", "/")
    return module_index.get(cleaned) or module_index.get(normalized) or module_index.get(cleaned.split("/")[-1])


def _candidate_files(project_root: Path, base: Path) -> list[Path]:
    candidates = [base]
    if not base.suffix:
        for extension in SOURCE_EXTENSIONS:
            candidates.append(base.with_suffix(extension))
        for index_name in ["index.ts", "index.tsx", "index.js", "index.jsx", "index.py", "__init__.py"]:
            candidates.append(base / index_name)
    resolved: list[Path] = []
    for candidate in candidates:
        try:
            candidate.relative_to(project_root)
        except ValueError:
            continue
        if candidate.exists() and candidate.is_file():
            resolved.append(candidate)
    return resolved


def _apply_source_importance(entries: list[dict[str, Any]], import_graph: dict[str, list[str]], signal_bonus: set[str]) -> None:
    fan_in: dict[str, int] = defaultdict(int)
    for imports in import_graph.values():
        for target in imports:
            fan_in[target] += 1
    for entry in entries:
        if entry["category"] != "source":
            continue
        path = entry["path"]
        fan_out = len(import_graph.get(path, []))
        entry["importance_score"] = round((fan_in.get(path, 0) * 0.5) + (fan_out * 0.3) + (0.2 if path in signal_bonus else 0.0), 4)


def _build_clusters(entries: list[dict[str, Any]], import_graph: dict[str, list[str]]) -> dict[str, list[str]]:
    source_paths = sorted(entry["path"] for entry in entries if entry["category"] == "source")
    adjacency: dict[str, set[str]] = {path: set(import_graph.get(path, [])) for path in source_paths}
    for source, imports in import_graph.items():
        for target in imports:
            adjacency.setdefault(target, set()).add(source)
    visited: set[str] = set()
    clusters: dict[str, list[str]] = {}
    cluster_number = 1
    for path in source_paths:
        if path in visited:
            continue
        stack = [path]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(sorted(adjacency.get(current, set()) - visited, reverse=True))
        cluster_id = f"cluster-{cluster_number:04d}"
        clusters[cluster_id] = sorted(component)
        cluster_number += 1
    return clusters


def entries_by_path(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {entry["path"]: entry for entry in entries}
