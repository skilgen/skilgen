from __future__ import annotations

from pathlib import Path


GENERATED_OUTPUT_FILES = frozenset(
    {
        "AGENTS.md",
        "ANALYSIS.md",
        "ARCHITECTURE.md",
        "FEATURES.md",
        "REPORT.md",
        "TRACEABILITY.md",
        "skilgen-dashboard.html",
        "skilgen.yml",
    }
)

GENERATED_OUTPUT_DIRS = frozenset({".skilgen", "skills"})


def is_generated_output_path(relative_path: str | Path) -> bool:
    relative = Path(relative_path)
    parts = relative.parts
    if not parts:
        return False
    if parts[0] in GENERATED_OUTPUT_DIRS:
        return True
    return len(parts) == 1 and parts[0] in GENERATED_OUTPUT_FILES
