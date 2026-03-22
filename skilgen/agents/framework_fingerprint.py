from __future__ import annotations

from pathlib import Path

from skilgen.core.models import FrameworkFingerprint, FrameworkMatch


def _gather_files(project_root: Path) -> set[str]:
    names: set[str] = set()
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if ".skilgen" in path.relative_to(project_root).parts:
            continue
        names.add(path.name)
        names.add(path.as_posix().replace(f"{project_root.as_posix()}/", ""))
    return names


def _match(files: set[str], candidates: list[tuple[str, list[str]]]) -> FrameworkMatch | None:
    best: FrameworkMatch | None = None
    for name, evidence_patterns in candidates:
        matched = [pattern for pattern in evidence_patterns if any(pattern in file for file in files)]
        if not matched:
            continue
        confidence = min(0.99, 0.45 + 0.2 * len(matched))
        candidate = FrameworkMatch(name=name, confidence=confidence, evidence=matched)
        if best is None or candidate.confidence > best.confidence:
            best = candidate
    return best


def fingerprint_project(project_root: Path) -> FrameworkFingerprint:
    files = _gather_files(project_root)
    frontend = _match(
        files,
        [
            ("nextjs", ["next.config", "app/", "pages/"]),
            ("react", ["package.json", "src/", ".tsx", ".jsx"]),
            ("vue", ["vite.config", ".vue"]),
            ("svelte", ["svelte.config", ".svelte"]),
        ],
    )
    backend = _match(
        files,
        [
            ("fastapi", ["fastapi", "main.py", "app/api", "pyproject.toml"]),
            ("django", ["manage.py", "settings.py"]),
            ("flask", ["flask", "wsgi.py"]),
            ("express", ["package.json", "express"]),
        ],
    )
    test_framework = _match(
        files,
        [
            ("unittest", ["test_", "unittest"]),
            ("pytest", ["pytest", "conftest.py"]),
            ("jest", ["jest.config", ".test.ts", ".spec.ts"]),
        ],
    )
    build_tool = _match(
        files,
        [
            ("setuptools", ["pyproject.toml"]),
            ("vite", ["vite.config"]),
            ("webpack", ["webpack.config"]),
        ],
    )
    return FrameworkFingerprint(
        frontend=frontend,
        backend=backend,
        test_framework=test_framework,
        build_tool=build_tool,
    )
