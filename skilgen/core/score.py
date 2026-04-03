from __future__ import annotations

import json
import re
from pathlib import Path

from skilgen.core.context import build_codebase_context
from skilgen.core.freshness import compute_freshness_report, load_freshness_state
from skilgen.core.requirements import load_project_context
from skilgen.core.validation import validate_project


GENERIC_MARKERS = (
    "best practice",
    "consider",
    "appropriate",
    "where applicable",
    "generally",
    "typically",
)


def _iter_source_files(project_root: Path) -> list[Path]:
    ignored_roots = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".skilgen", "skills"}
    ignored_files = {"AGENTS.md", "ANALYSIS.md", "FEATURES.md", "REPORT.md", "TRACEABILITY.md"}
    files: list[Path] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root)
        if set(relative.parts) & ignored_roots:
            continue
        if path.name in ignored_files:
            continue
        files.append(path)
    return sorted(files)


def _skill_files(project_root: Path) -> list[Path]:
    skills_root = project_root / "skills"
    if not skills_root.exists():
        return []
    return sorted(skills_root.rglob("SKILL.md"))


def _parse_references(skill: Path) -> list[str]:
    refs: list[str] = []
    lines = skill.read_text(encoding="utf-8").splitlines()
    in_refs = False
    for line in lines:
        stripped = line.strip()
        if stripped == "references:":
            in_refs = True
            continue
        if in_refs and stripped.startswith("- "):
            refs.append(stripped[2:].strip())
        elif in_refs and stripped and not stripped.startswith("- "):
            in_refs = False
    return refs


def _parse_check_paths(skill: Path) -> list[str]:
    checks: list[str] = []
    lines = skill.read_text(encoding="utf-8").splitlines()
    in_checks = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Check These Paths First":
            in_checks = True
            continue
        if in_checks and stripped.startswith("## "):
            break
        if in_checks and stripped.startswith("- "):
            checks.append(stripped[2:].strip())
    return checks


def _resolve_placeholder_path(raw: str, project_root: Path, skill_path: Path) -> Path:
    normalized = raw.replace("{{project_root}}", str(project_root)).replace("{{skill_dir}}", str(skill_path.parent))
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (skill_path.parent / normalized).resolve()


def _skill_domain(skill: Path, project_root: Path) -> str | None:
    try:
        relative = skill.relative_to(project_root / "skills")
    except ValueError:
        return None
    return relative.parts[0] if relative.parts else None


def _nodes_by_domain(project_root: Path) -> dict[str, list[object]]:
    context = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, context)
    grouped: dict[str, list[object]] = {}
    for node in codebase_context.domain_graph.nodes:
        grouped.setdefault(node.name, []).append(node)
    return grouped


def _domain_key_files(project_root: Path) -> dict[str, list[str]]:
    grouped = _nodes_by_domain(project_root)
    return {
        domain: list(dict.fromkeys(file for node in nodes for file in node.key_files))
        for domain, nodes in grouped.items()
    }


def _skill_content(skill: Path) -> str:
    return skill.read_text(encoding="utf-8").lower()


def _evidence_hits_for_skill(skill: Path, project_root: Path, key_files: list[str]) -> dict[str, int]:
    content = _skill_content(skill)
    references = _parse_references(skill)
    checks = _parse_check_paths(skill)
    valid_references = sum(1 for ref in references if (skill.parent / ref).resolve().exists())
    valid_checks = sum(1 for check in checks if _resolve_placeholder_path(check, project_root, skill).exists())
    evidence_targets = min(3, len(key_files))
    evidence_mentions = 0
    covered_key_files: set[str] = set()
    for key_file in key_files:
        file_name = Path(key_file).name.lower()
        if key_file.lower() in content or file_name in content:
            covered_key_files.add(key_file)
    for key_file in key_files[:3]:
        file_name = Path(key_file).name.lower()
        if key_file.lower() in content or file_name in content:
            evidence_mentions += 1
    generic_markers = sum(content.count(marker) for marker in GENERIC_MARKERS)
    return {
        "valid_references": valid_references,
        "total_references": len(references),
        "valid_check_paths": valid_checks,
        "total_check_paths": len(checks),
        "evidence_mentions": evidence_mentions,
        "evidence_targets": evidence_targets,
        "generic_advice_markers": generic_markers,
        "covered_key_files": len(covered_key_files),
        "total_key_files": len(key_files),
    }


def _groundedness_score(project_root: Path) -> tuple[float, dict[str, object]]:
    skill_files = _skill_files(project_root)
    if not skill_files:
        return 0.0, {
            "score": 0.0,
            "max_score": 25,
            "valid_references": 0,
            "valid_check_paths": 0,
            "evidence_mentions": 0,
            "generic_advice_markers": 0,
        }

    context = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, context)
    nodes_by_domain: dict[str, list[object]] = {}
    for node in codebase_context.domain_graph.nodes:
        nodes_by_domain.setdefault(node.name, []).append(node)

    valid_references = 0
    total_references = 0
    valid_checks = 0
    total_checks = 0
    evidence_mentions = 0
    evidence_targets = 0
    generic_markers = 0

    for skill in skill_files:
        content = skill.read_text(encoding="utf-8").lower()
        references = _parse_references(skill)
        total_references += len(references)
        for ref in references:
            if (skill.parent / ref).resolve().exists():
                valid_references += 1

        checks = _parse_check_paths(skill)
        total_checks += len(checks)
        for check in checks:
            resolved = _resolve_placeholder_path(check, project_root, skill)
            if resolved.exists():
                valid_checks += 1

        domain = _skill_domain(skill, project_root)
        nodes = nodes_by_domain.get(domain or "", [])
        domain_key_files = list(dict.fromkeys(file for node in nodes for file in node.key_files))
        evidence_targets += min(3, len(domain_key_files))
        for key_file in domain_key_files[:3]:
            if key_file.lower() in content or Path(key_file).name.lower() in content:
                evidence_mentions += 1

        generic_markers += sum(content.count(marker) for marker in GENERIC_MARKERS)

    possible = total_references + total_checks + evidence_targets
    raw_ratio = (valid_references + valid_checks + evidence_mentions) / max(1, possible)
    generic_penalty = min(0.35, generic_markers / max(20, len(skill_files) * 12))
    score = max(0.0, min(25.0, round(25 * raw_ratio * (1 - generic_penalty), 2)))
    return score, {
        "score": score,
        "max_score": 25,
        "valid_references": valid_references,
        "total_references": total_references,
        "valid_check_paths": valid_checks,
        "total_check_paths": total_checks,
        "evidence_mentions": evidence_mentions,
        "evidence_targets": evidence_targets,
        "generic_advice_markers": generic_markers,
    }


def _groundedness_score_for_skills(project_root: Path, skill_files: list[Path], domain_key_files: dict[str, list[str]]) -> tuple[float, dict[str, object]]:
    if not skill_files:
        return 0.0, {
            "score": 0.0,
            "max_score": 25,
            "valid_references": 0,
            "total_references": 0,
            "valid_check_paths": 0,
            "total_check_paths": 0,
            "evidence_mentions": 0,
            "evidence_targets": 0,
            "generic_advice_markers": 0,
        }

    totals = {
        "valid_references": 0,
        "total_references": 0,
        "valid_check_paths": 0,
        "total_check_paths": 0,
        "evidence_mentions": 0,
        "evidence_targets": 0,
        "generic_advice_markers": 0,
    }
    for skill in skill_files:
        domain = _skill_domain(skill, project_root) or ""
        hits = _evidence_hits_for_skill(skill, project_root, domain_key_files.get(domain, []))
        for key in totals:
            totals[key] += hits[key]

    possible = totals["total_references"] + totals["total_check_paths"] + totals["evidence_targets"]
    raw_ratio = (totals["valid_references"] + totals["valid_check_paths"] + totals["evidence_mentions"]) / max(1, possible)
    generic_penalty = min(0.35, totals["generic_advice_markers"] / max(20, len(skill_files) * 12))
    score = max(0.0, min(25.0, round(25 * raw_ratio * (1 - generic_penalty), 2)))
    return score, {
        "score": score,
        "max_score": 25,
        **totals,
    }


def _coverage_score(project_root: Path) -> tuple[float, dict[str, object]]:
    source_files = _iter_source_files(project_root)
    if not source_files:
        return 25.0, {
            "score": 25.0,
            "max_score": 25,
            "source_file_count": 0,
            "mapped_file_count": 0,
            "coverage_ratio": 1.0,
        }

    context = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, context)
    source_paths = {path.relative_to(project_root).as_posix() for path in source_files}
    mapped_files = {
        key_file
        for node in codebase_context.domain_graph.nodes
        for key_file in node.key_files
        if key_file in source_paths
    }
    ratio = len(mapped_files) / max(1, len(source_paths))
    score = round(25 * ratio, 2)
    return score, {
        "score": score,
        "max_score": 25,
        "source_file_count": len(source_paths),
        "mapped_file_count": len(mapped_files),
        "coverage_ratio": round(ratio, 4),
    }


def _freshness_score(project_root: Path) -> tuple[float, dict[str, object]]:
    context = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, context)
    previous = load_freshness_state(project_root)
    if previous is None:
        return 5.0, {
            "score": 5.0,
            "max_score": 25,
            "reason": "missing_freshness_state",
            "changed_files": 0,
            "stale_skill_paths": 0,
        }
    freshness = compute_freshness_report(project_root, context, codebase_context.domain_graph, previous)
    if freshness.reason == "no_source_changes":
        score = 25.0
    elif freshness.reason == "initial_generation":
        score = 18.0
    else:
        changed_penalty = min(15.0, len(freshness.changed_files) * 1.5)
        stale_penalty = min(10.0, len(freshness.stale_skill_paths) * 0.75)
        score = max(0.0, round(25 - changed_penalty - stale_penalty, 2))
    return score, {
        "score": score,
        "max_score": 25,
        "reason": freshness.reason,
        "changed_files": len(freshness.changed_files),
        "stale_skill_paths": len(freshness.stale_skill_paths),
    }


def _freshness_score_for_skill(
    skill_path: Path,
    changed_files: list[str],
    stale_skill_paths: list[str],
    domain_key_files: list[str],
    project_root: Path,
    base_reason: str,
) -> tuple[float, dict[str, object]]:
    relative_skill = skill_path.relative_to(project_root).as_posix()
    stale = relative_skill in stale_skill_paths
    domain_changed = sum(1 for path in changed_files if path in set(domain_key_files))
    if base_reason == "missing_freshness_state":
        score = 5.0
    elif not stale and domain_changed == 0:
        score = 25.0
    else:
        score = max(0.0, round(25 - (8.0 if stale else 0.0) - min(17.0, domain_changed * 4.0), 2))
    return score, {
        "score": score,
        "max_score": 25,
        "reason": base_reason if base_reason == "missing_freshness_state" else ("stale" if stale else "changed_domain"),
        "domain_changed_files": domain_changed,
        "stale": stale,
    }


def _structure_score(project_root: Path) -> tuple[float, dict[str, object]]:
    validation = validate_project(project_root)
    requirements = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, requirements)
    required = [
        project_root / "AGENTS.md",
        project_root / "FEATURES.md",
        project_root / "TRACEABILITY.md",
        project_root / "skills" / "MANIFEST.md",
        project_root / "skills" / "GRAPH.md",
    ]
    existing_required = sum(1 for item in required if item.exists())
    base = 15 * (existing_required / len(required))
    cross_reference_count = sum(len(node.cross_references) + len(node.child_skills) for node in codebase_context.skill_tree)
    density = cross_reference_count / max(1, len(codebase_context.skill_tree))
    density_bonus = min(6.0, round(density * 3, 2))
    tree_bonus = min(4.0, float(len(codebase_context.skill_tree)))
    structure_errors = len(validation["errors"])
    structure_warnings = len(validation["warnings"])
    penalty = min(10.0, structure_errors * 2.5 + structure_warnings * 0.5)
    score = max(0.0, min(25.0, round(base + density_bonus + tree_bonus - penalty, 2)))
    return score, {
        "score": score,
        "max_score": 25,
        "required_artifacts_present": existing_required,
        "required_artifacts_total": len(required),
        "cross_reference_density": round(density, 4),
        "validation_errors": structure_errors,
        "validation_warnings": structure_warnings,
    }


def _structure_score_for_skills(project_root: Path, skill_files: list[Path]) -> tuple[float, dict[str, object]]:
    if not skill_files:
        return 0.0, {
            "score": 0.0,
            "max_score": 25,
            "skill_count": 0,
            "cross_reference_density": 0.0,
            "summary_siblings_present": 0,
        }
    cross_reference_count = 0
    summary_siblings_present = 0
    for skill in skill_files:
        refs = _parse_references(skill)
        cross_reference_count += len(refs)
        if (skill.parent / "SUMMARY.md").exists():
            summary_siblings_present += 1
    density = cross_reference_count / max(1, len(skill_files))
    density_bonus = min(10.0, round(density * 4, 2))
    summary_bonus = min(10.0, round((summary_siblings_present / len(skill_files)) * 10, 2))
    base = 5.0
    score = max(0.0, min(25.0, round(base + density_bonus + summary_bonus, 2)))
    return score, {
        "score": score,
        "max_score": 25,
        "skill_count": len(skill_files),
        "cross_reference_density": round(density, 4),
        "summary_siblings_present": summary_siblings_present,
    }


def _quality_gates(subscores: dict[str, object]) -> tuple[list[dict[str, object]], float | None]:
    gates: list[dict[str, object]] = []
    groundedness = subscores["groundedness"]
    coverage = subscores["coverage"]
    freshness = subscores["freshness"]
    structure = subscores["structure"]

    if groundedness["score"] < 10 or (
        groundedness.get("valid_references", 0) + groundedness.get("valid_check_paths", 0) + groundedness.get("evidence_mentions", 0)
    ) < 4:
        gates.append(
            {
                "name": "groundedness_gate",
                "cap": 59.0,
                "reason": "Skill guidance is not grounded enough in real files, real check paths, or inferred domain evidence.",
            }
        )
    elif groundedness["score"] < 16:
        gates.append(
            {
                "name": "groundedness_gate_soft",
                "cap": 74.0,
                "reason": "Skill guidance still needs more concrete repo evidence before it should count as strong.",
            }
        )

    if coverage["coverage_ratio"] < 0.2:
        gates.append(
            {
                "name": "coverage_gate",
                "cap": 59.0,
                "reason": "Too little of the codebase is mapped into inferred skill domains.",
            }
        )
    elif coverage["coverage_ratio"] < 0.4:
        gates.append(
            {
                "name": "coverage_gate_soft",
                "cap": 74.0,
                "reason": "Coverage is still partial; major parts of the repo are not yet represented by the skill tree.",
            }
        )

    freshness_reason = freshness.get("reason")
    if freshness_reason == "missing_freshness_state":
        gates.append(
            {
                "name": "freshness_state_gate",
                "cap": 74.0,
                "reason": "Freshness state is missing, so Skilgen cannot verify whether the skills are current.",
            }
        )
    elif freshness.get("changed_files", 0) > 0 or freshness.get("stale_skill_paths", 0) > 0:
        gates.append(
            {
                "name": "freshness_gate",
                "cap": 59.0,
                "reason": "Skills are stale relative to current source changes.",
            }
        )

    required_present = structure.get("required_artifacts_present", structure.get("summary_siblings_present", 0))
    required_total = structure.get("required_artifacts_total", structure.get("skill_count", 0))
    if required_total > 0 and required_present < required_total:
        gates.append(
            {
                "name": "structure_gate",
                "cap": 69.0,
                "reason": "Core skill-system artifacts are missing, so the tree is not structurally complete.",
            }
        )
    elif structure.get("validation_errors", 0) > 0:
        gates.append(
            {
                "name": "validation_gate",
                "cap": 74.0,
                "reason": "Validation errors are present in the generated skill system.",
            }
        )

    cap = min((gate["cap"] for gate in gates), default=None)
    return gates, cap


def _score_rating(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "strong"
    if score >= 60:
        return "fair"
    return "needs-work"


def _badge_color(score: float) -> str:
    if score >= 90:
        return "#2ea043"
    if score >= 75:
        return "#3fb950"
    if score >= 60:
        return "#d29922"
    return "#cf222e"


def build_score_recommendations(scorecard: dict[str, object]) -> list[str]:
    recommendations: list[str] = []
    subscores = scorecard["subscores"]
    if subscores["groundedness"]["score"] < 18:
        recommendations.append("Increase groundedness by adding more real file references and concrete check paths inside generated skills.")
    if subscores["coverage"]["score"] < 18:
        recommendations.append("Improve coverage by mapping more source files into inferred domains and regenerating the skill tree.")
    if subscores["freshness"]["score"] < 18:
        recommendations.append("Refresh stale skills with `skilgen deliver` or enable `update_trigger: auto` so the freshness score stays high.")
    if subscores["structure"]["score"] < 18:
        recommendations.append("Strengthen structure by keeping AGENTS.md, MANIFEST.md, GRAPH.md, TRACEABILITY.md, and cross-references in sync.")
    if not recommendations:
        recommendations.append("Skilgen Score looks healthy. Keep the repo-local skill tree refreshed and preserve grounded references as the code evolves.")
    return recommendations


def _assemble_scorecard(
    *,
    score_scope: str,
    score_id: str,
    project_root: Path,
    subscores: dict[str, object],
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    raw_total = round(sum(component["score"] for component in subscores.values()), 2)
    gates, cap = _quality_gates(subscores)
    total = raw_total if cap is None else round(min(raw_total, cap), 2)
    scorecard = {
        "scope": score_scope,
        "id": score_id,
        "project_root": str(project_root),
        "score": total,
        "raw_score": raw_total,
        "max_score": 100,
        "rating": _score_rating(total),
        "subscores": subscores,
        "quality_gates": gates,
    }
    if extra:
        scorecard.update(extra)
    scorecard["recommendations"] = build_score_recommendations(scorecard)
    return scorecard


def _domain_scorecards(project_root: Path) -> list[dict[str, object]]:
    domain_files = _domain_key_files(project_root)
    previous = load_freshness_state(project_root)
    context = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, context)
    freshness = compute_freshness_report(project_root, context, codebase_context.domain_graph, previous)
    all_skills = _skill_files(project_root)
    scorecards: list[dict[str, object]] = []
    for domain, key_files in sorted(domain_files.items()):
        domain_skills = [skill for skill in all_skills if _skill_domain(skill, project_root) == domain]
        groundedness_score, groundedness = _groundedness_score_for_skills(project_root, domain_skills, domain_files)
        coverage_ratio = min(1.0, len(key_files) / max(1, len(_iter_source_files(project_root))))
        coverage = {
            "score": round(25 * coverage_ratio, 2),
            "max_score": 25,
            "source_file_count": len(key_files),
            "mapped_file_count": len(key_files),
            "coverage_ratio": round(coverage_ratio, 4),
        }
        stale_domain_skills = [path for path in freshness.stale_skill_paths if path.startswith(f"skills/{domain}/")]
        freshness_score = max(0.0, round(25 - min(10.0, len(stale_domain_skills) * 4.0), 2))
        freshness_payload = {
            "score": freshness_score,
            "max_score": 25,
            "reason": freshness.reason if stale_domain_skills else "current",
            "changed_files": sum(1 for file in freshness.changed_files if file in set(key_files)),
            "stale_skill_paths": len(stale_domain_skills),
        }
        structure_score, structure = _structure_score_for_skills(project_root, domain_skills)
        scorecards.append(
            _assemble_scorecard(
                score_scope="domain",
                score_id=domain,
                project_root=project_root,
                subscores={
                    "groundedness": groundedness,
                    "coverage": coverage,
                    "freshness": freshness_payload,
                    "structure": structure,
                },
                extra={
                    "domain": domain,
                    "skill_count": len(domain_skills),
                    "key_file_count": len(key_files),
                },
            )
        )
    return scorecards


def _skill_scorecards(project_root: Path) -> list[dict[str, object]]:
    domain_files = _domain_key_files(project_root)
    previous = load_freshness_state(project_root)
    context = load_project_context(project_root, None)
    codebase_context = build_codebase_context(project_root, context)
    freshness = compute_freshness_report(project_root, context, codebase_context.domain_graph, previous)
    scorecards: list[dict[str, object]] = []
    for skill in _skill_files(project_root):
        domain = _skill_domain(skill, project_root) or "unscoped"
        key_files = domain_files.get(domain, [])
        groundedness_score, groundedness = _groundedness_score_for_skills(project_root, [skill], domain_files)
        hits = _evidence_hits_for_skill(skill, project_root, key_files)
        coverage_ratio = hits["covered_key_files"] / max(1, hits["total_key_files"])
        coverage = {
            "score": round(25 * coverage_ratio, 2),
            "max_score": 25,
            "source_file_count": hits["total_key_files"],
            "mapped_file_count": hits["covered_key_files"],
            "coverage_ratio": round(coverage_ratio, 4),
        }
        freshness_score, freshness_payload = _freshness_score_for_skill(
            skill,
            freshness.changed_files,
            freshness.stale_skill_paths,
            key_files,
            project_root,
            freshness.reason,
        )
        structure_score, structure = _structure_score_for_skills(project_root, [skill])
        scorecards.append(
            _assemble_scorecard(
                score_scope="skill",
                score_id=skill.relative_to(project_root).as_posix(),
                project_root=project_root,
                subscores={
                    "groundedness": groundedness,
                    "coverage": coverage,
                    "freshness": freshness_payload,
                    "structure": structure,
                },
                extra={
                    "path": skill.relative_to(project_root).as_posix(),
                    "domain": domain,
                },
            )
        )
    return scorecards


def compute_skillgen_score(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    groundedness_score, groundedness = _groundedness_score(root)
    coverage_score, coverage = _coverage_score(root)
    freshness_score, freshness = _freshness_score(root)
    structure_score, structure = _structure_score(root)
    scorecard = _assemble_scorecard(
        score_scope="repo",
        score_id="repo",
        project_root=root,
        subscores={
            "groundedness": groundedness,
            "coverage": coverage,
            "freshness": freshness,
            "structure": structure,
        },
    )
    scorecard["domains"] = _domain_scorecards(root)
    scorecard["skills"] = _skill_scorecards(root)
    scorecard["badge"] = {
        "label": "Skilgen Score",
        "message": f"{int(round(scorecard['score']))}/100",
        "color": _badge_color(scorecard["score"]),
        "markdown_example": "![Skilgen Score](https://skilgen.com/badge/your-repo)",
    }
    return scorecard


def render_score_badge_svg(score_payload: dict[str, object]) -> str:
    label = "Skilgen Score"
    message = score_payload["badge"]["message"]
    color = score_payload["badge"]["color"]
    label_width = 108
    value_width = 58
    width = label_width + value_width
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{label}: {message}">
<linearGradient id="smooth" x2="0" y2="100%">
  <stop offset="0" stop-color="#fff" stop-opacity=".7"/>
  <stop offset=".1" stop-color="#aaa" stop-opacity=".1"/>
  <stop offset=".9" stop-color="#000" stop-opacity=".3"/>
  <stop offset="1" stop-color="#000" stop-opacity=".5"/>
</linearGradient>
<mask id="round">
  <rect width="{width}" height="20" rx="3" fill="#fff"/>
</mask>
<g mask="url(#round)">
  <rect width="{label_width}" height="20" fill="#24292f"/>
  <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
  <rect width="{width}" height="20" fill="url(#smooth)"/>
</g>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
  <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
  <text x="{label_width / 2}" y="14">{label}</text>
  <text x="{label_width + value_width / 2}" y="15" fill="#010101" fill-opacity=".3">{message}</text>
  <text x="{label_width + value_width / 2}" y="14">{message}</text>
</g>
</svg>"""


def write_score_badge(project_root: str | Path, output_path: str | Path | None = None) -> dict[str, object]:
    root = Path(project_root).resolve()
    payload = compute_skillgen_score(root)
    path = Path(output_path).resolve() if output_path is not None else root / ".skilgen" / "score" / "badge.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_score_badge_svg(payload), encoding="utf-8")
    return {
        "path": str(path),
        "score": payload["score"],
        "rating": payload["rating"],
    }


def score_summary_markdown(project_root: str | Path) -> str:
    payload = compute_skillgen_score(project_root)
    return "\n".join(
        [
            f"## Skilgen Score: {int(round(payload['score']))}/100",
            "",
            f"- Groundedness: {payload['subscores']['groundedness']['score']}/25",
            f"- Coverage: {payload['subscores']['coverage']['score']}/25",
            f"- Freshness: {payload['subscores']['freshness']['score']}/25",
            f"- Structure: {payload['subscores']['structure']['score']}/25",
        ]
    )


def export_score_json(project_root: str | Path, output_path: str | Path | None = None) -> dict[str, object]:
    root = Path(project_root).resolve()
    payload = compute_skillgen_score(root)
    path = Path(output_path).resolve() if output_path is not None else root / ".skilgen" / "score" / "score.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "path": str(path),
        "score": payload["score"],
    }
