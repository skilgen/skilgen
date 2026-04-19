from __future__ import annotations

import ast
import re
import warnings
from pathlib import Path

from skilgen.agents.codebase_signals import _iter_code_files

IGNORED_PARTS = {".git", ".skilgen", "external-skills", "__pycache__", ".venv", "venv", "node_modules"}

_JS_IMPORT_RE = re.compile(r"""(?:import|export)\s+(?:[^;]*?\s+from\s+)?["']([^"']+)["']""")
_JS_REQUIRE_RE = re.compile(r"""require\(\s*["']([^"']+)["']\s*\)""")
_JAVA_IMPORT_RE = re.compile(r"""^\s*import\s+([a-zA-Z0-9_.*]+)\s*;""", re.MULTILINE)
_GO_IMPORT_BLOCK_RE = re.compile(r'import\s*\((.*?)\)', re.DOTALL)
_GO_IMPORT_LINE_RE = re.compile(r'"([^"]+)"')
_RUST_USE_RE = re.compile(r"""^\s*(?:use|mod)\s+([a-zA-Z0-9_:]+)""", re.MULTILINE)
_COBOL_COPY_RE = re.compile(r"""^\s*COPY\s+([A-Z0-9_-]+)""", re.MULTILINE)
_RESOLUTION_EXTENSIONS = ("", ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs", ".cbl", ".cob", ".cpy")
_RESOLUTION_INDEXES = ("index.ts", "index.tsx", "index.js", "index.jsx", "page.tsx", "page.jsx", "page.ts", "page.js")


def _relative_text_imports(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    imports: list[str] = []
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}:
        imports.extend(_JS_IMPORT_RE.findall(text))
        imports.extend(_JS_REQUIRE_RE.findall(text))
    elif suffix == ".java":
        imports.extend(_JAVA_IMPORT_RE.findall(text))
    elif suffix == ".go":
        for block in _GO_IMPORT_BLOCK_RE.findall(text):
            imports.extend(_GO_IMPORT_LINE_RE.findall(block))
        imports.extend(_GO_IMPORT_LINE_RE.findall(text))
    elif suffix == ".rs":
        imports.extend(_RUST_USE_RE.findall(text))
    elif suffix in {".cbl", ".cob", ".cpy"}:
        imports.extend(_COBOL_COPY_RE.findall(text))
    return sorted({entry.strip() for entry in imports if entry.strip()})


def _resolve_repo_local_import(project_root: Path, source_path: Path, raw_import: str) -> str:
    if raw_import.startswith(("./", "../")):
        base = (source_path.parent / raw_import).resolve()
        candidates = [base]
        candidates.extend(base.with_suffix(ext) for ext in _RESOLUTION_EXTENSIONS[1:] if not base.suffix)
        if base.is_dir():
            candidates.extend(base / name for name in _RESOLUTION_INDEXES)
        for candidate in candidates:
            try:
                if candidate.exists() and candidate.is_file():
                    return candidate.relative_to(project_root).as_posix()
            except ValueError:
                continue
    return raw_import


def _resolve_python_import(project_root: Path, source_path: Path, module: str | None, level: int) -> str:
    if level > 0:
        current = source_path.parent
        for _ in range(max(0, level - 1)):
            current = current.parent
        base = current / (module.replace(".", "/") if module else "")
        candidates = [base]
        if not base.suffix:
            candidates.extend(base.with_suffix(ext) for ext in _RESOLUTION_EXTENSIONS[1:])
        if base.is_dir() or (not base.suffix and (base / "__init__.py").exists()):
            candidates.append(base / "__init__.py")
        for candidate in candidates:
            try:
                if candidate.exists() and candidate.is_file():
                    return candidate.relative_to(project_root).as_posix()
            except ValueError:
                continue
        return f"{current.relative_to(project_root).as_posix()}/{module.replace('.', '/')}".strip("/")
    raw_import = module or ""
    if raw_import:
        absolute_base = project_root / raw_import.replace(".", "/")
        candidates = [absolute_base]
        if not absolute_base.suffix:
            candidates.extend(absolute_base.with_suffix(ext) for ext in _RESOLUTION_EXTENSIONS[1:])
            candidates.append(absolute_base / "__init__.py")
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate.relative_to(project_root).as_posix()
    return _resolve_repo_local_import(project_root, source_path, raw_import)


def _resolve_python_from_import(project_root: Path, source_path: Path, module: str | None, level: int, alias_name: str) -> str:
    base = _resolve_python_import(project_root, source_path, module, level)
    base_path = project_root / base if base and "/" in base else None
    if base_path is not None:
        if base_path.is_file() and base_path.name == "__init__.py":
            package_dir = base_path.parent
        elif base_path.is_dir():
            package_dir = base_path
        else:
            package_dir = base_path.parent
        candidates = [
            package_dir / f"{alias_name}.py",
            package_dir / alias_name / "__init__.py",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate.relative_to(project_root).as_posix()
    if base and base not in {module or "", ""}:
        return base
    if module:
        return module
    return alias_name


def build_import_graph(project_root: Path) -> dict[str, list[str]]:
    root = project_root.resolve()
    graph: dict[str, list[str]] = {}
    for path in _iter_code_files(root):
        rel = path.relative_to(root).as_posix()
        imports: list[str] = []
        if path.suffix.lower() == ".py":
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))
            except (SyntaxError, OSError, UnicodeDecodeError):
                graph[rel] = imports
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.extend(
                        _resolve_python_from_import(root, path, node.module, node.level, alias.name)
                        for alias in node.names
                    )
                elif isinstance(node, ast.ImportFrom):
                    imports.extend(
                        _resolve_python_from_import(root, path, None, node.level, alias.name)
                        for alias in node.names
                    )
        else:
            imports.extend(_relative_text_imports(path))
        normalized_imports = [_resolve_repo_local_import(root, path, entry) for entry in imports]
        graph[rel] = sorted(set(normalized_imports))
    return graph
