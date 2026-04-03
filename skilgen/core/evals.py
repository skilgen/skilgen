from __future__ import annotations

import json
from pathlib import Path


EXAMPLE_BASELINE = {
    "label": "baseline",
    "tasks_total": 10,
    "tasks_passed": 6,
    "success_rate": 0.6,
    "token_usage": 42000,
    "error_count": 9,
}

EXAMPLE_SKILGEN = {
    "label": "skilgen",
    "tasks_total": 10,
    "tasks_passed": 8,
    "success_rate": 0.8,
    "token_usage": 35500,
    "error_count": 4,
}


def scaffold_eval_framework(project_root: str | Path, output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(project_root).resolve()
    target = Path(output_dir).resolve() if output_dir is not None else root / ".skilgen" / "evals"
    tasks_dir = target / "tasks"
    results_dir = target / "results"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    example_task = {
        "id": "complex-refactor-001",
        "prompt": "Implement a non-trivial change in this codebase with and without Skilgen-generated skills loaded.",
        "success_criteria": [
            "All affected tests pass",
            "No new validation warnings",
            "Required files are updated consistently",
        ],
        "measurements": ["success_rate", "token_usage", "error_count"],
    }

    (tasks_dir / "example-task.json").write_text(json.dumps(example_task, indent=2), encoding="utf-8")
    (results_dir / "baseline.example.json").write_text(json.dumps(EXAMPLE_BASELINE, indent=2), encoding="utf-8")
    (results_dir / "skilgen.example.json").write_text(json.dumps(EXAMPLE_SKILGEN, indent=2), encoding="utf-8")
    (target / "README.md").write_text(
        "\n".join(
            [
                "# Skilgen Eval Framework",
                "",
                "Use this folder to benchmark an agent with and without Skilgen-generated skills on the same task set.",
                "",
                "## Suggested Flow",
                "1. Define one or more task files in `tasks/`.",
                "2. Run the same task with a baseline agent setup and save results in `results/baseline.*.json`.",
                "3. Run the same task with Skilgen-generated skills enabled and save results in `results/skilgen.*.json`.",
                "4. Compare them with `skilgen eval compare --baseline ... --skilgen ...`.",
                "",
                "## Result File Fields",
                "- `tasks_total`",
                "- `tasks_passed`",
                "- `success_rate` (0-1)",
                "- `token_usage`",
                "- `error_count`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(target),
        "files": [
            str(tasks_dir / "example-task.json"),
            str(results_dir / "baseline.example.json"),
            str(results_dir / "skilgen.example.json"),
            str(target / "README.md"),
        ],
    }


def compare_eval_results(baseline_path: str | Path, skilgen_path: str | Path) -> dict[str, object]:
    baseline = json.loads(Path(baseline_path).resolve().read_text(encoding="utf-8"))
    skilgen = json.loads(Path(skilgen_path).resolve().read_text(encoding="utf-8"))

    baseline_success = float(baseline.get("success_rate", 0.0))
    skilgen_success = float(skilgen.get("success_rate", 0.0))
    baseline_tokens = float(baseline.get("token_usage", 0.0))
    skilgen_tokens = float(skilgen.get("token_usage", 0.0))
    baseline_errors = float(baseline.get("error_count", 0.0))
    skilgen_errors = float(skilgen.get("error_count", 0.0))

    success_delta = skilgen_success - baseline_success
    token_delta = skilgen_tokens - baseline_tokens
    error_delta = skilgen_errors - baseline_errors
    error_reduction_pct = 0.0 if baseline_errors == 0 else ((baseline_errors - skilgen_errors) / baseline_errors) * 100
    token_delta_pct = 0.0 if baseline_tokens == 0 else ((skilgen_tokens - baseline_tokens) / baseline_tokens) * 100

    headline = (
        f"Agents using Skilgen skills improved success rate by {success_delta * 100:.1f} points, "
        f"changed token usage by {token_delta_pct:.1f}%, and reduced errors by {error_reduction_pct:.1f}%."
    )

    return {
        "baseline": baseline,
        "skilgen": skilgen,
        "comparison": {
            "success_rate_delta": round(success_delta, 4),
            "token_usage_delta": round(token_delta, 2),
            "token_usage_delta_pct": round(token_delta_pct, 2),
            "error_count_delta": round(error_delta, 2),
            "error_reduction_pct": round(error_reduction_pct, 2),
        },
        "headline": headline,
    }
