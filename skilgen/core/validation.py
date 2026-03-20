from __future__ import annotations

from pathlib import Path

from skilgen.agents.codebase_signals import analyze_codebase
from skilgen.deep_agents_core import runtime_diagnostics


def _parse_references(skill: Path) -> list[str]:
    references: list[str] = []
    lines = skill.read_text(encoding="utf-8").splitlines()
    in_refs = False
    for line in lines:
        stripped = line.strip()
        if stripped == "references:":
            in_refs = True
            continue
        if in_refs and stripped.startswith("- "):
            references.append(stripped[2:].strip())
        elif in_refs and stripped and not stripped.startswith("- "):
            in_refs = False
    return references


def _needs_bidirectional_check(root: Path, source: Path, target: Path) -> bool:
    try:
        source_parts = source.relative_to(root).parts
        target_parts = target.relative_to(root).parts
    except ValueError:
        return False
    if len(source_parts) < 3 or len(target_parts) < 3:
        return False
    if source_parts[0] != "skills" or target_parts[0] != "skills":
        return False
    source_domain = source_parts[1]
    target_domain = target_parts[1]
    if source_domain != target_domain:
        return False
    return True


def validate_project(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []
    manifest = root / "skills" / "MANIFEST.md"
    agents_contract = root / "AGENTS.md"
    if not manifest.exists():
        errors.append("skills/MANIFEST.md is missing")
    if not (root / "skills" / "GRAPH.md").exists():
        errors.append("skills/GRAPH.md is missing")
    if not (root / "TRACEABILITY.md").exists():
        warnings.append("TRACEABILITY.md is missing")
    if not agents_contract.exists():
        errors.append("AGENTS.md is missing")

    resolved_refs: dict[Path, set[Path]] = {}
    if (root / "skills").exists():
        for skill in (root / "skills").rglob("SKILL.md"):
            refs: set[Path] = set()
            for reference in _parse_references(skill):
                target = (skill.parent / reference).resolve()
                refs.add(target)
                if not target.exists():
                    errors.append(f"Missing reference from {skill.relative_to(root)} to {reference}")
            resolved_refs[skill.resolve()] = refs

    for skill, targets in resolved_refs.items():
        for target in targets:
            if target.name != "SKILL.md" or target not in resolved_refs:
                continue
            if not _needs_bidirectional_check(root, skill, target):
                continue
            if skill not in resolved_refs[target]:
                errors.append(
                    f"Missing bidirectional reference between {skill.relative_to(root)} and {target.relative_to(root)}"
                )

    signals = analyze_codebase(root)
    diagnostics = runtime_diagnostics(root)
    if diagnostics["runtime"] != "model_backed":
        warnings.append(f"Model-backed runtime is not ready: {diagnostics['reason']}")
        recommendations.extend(diagnostics["recommendations"])
    if signals.backend_routes and not (root / "skills" / "backend" / "routes" / "SKILL.md").exists():
        warnings.append("Backend route files were detected but skills/backend/routes/SKILL.md is missing")
    if signals.services and not (root / "skills" / "backend" / "services" / "SKILL.md").exists():
        warnings.append("Service files were detected but skills/backend/services/SKILL.md is missing")
    if signals.backend_routes and not signals.tests:
        warnings.append("Backend route files were detected but no test files were found")
    if signals.frontend_routes and not (root / "skills" / "frontend" / "routes" / "SKILL.md").exists():
        warnings.append("Frontend route files were detected but skills/frontend/routes/SKILL.md is missing")
    if signals.data_models and not (root / "TRACEABILITY.md").exists():
        warnings.append("Data model files were detected but TRACEABILITY.md is missing")
    if signals.persistence_layers and not (root / "skills" / "backend" / "services" / "SKILL.md").exists():
        warnings.append("Persistence files were detected but backend service guidance is missing")
    if signals.auth_files and not (root / "skills" / "backend" / "SKILL.md").exists():
        warnings.append("Auth files were detected but backend guidance is missing")
    if signals.state_files and not (root / "skills" / "frontend" / "SKILL.md").exists():
        warnings.append("State files were detected but frontend guidance is missing")
    if signals.design_system_files and not (root / "skills" / "frontend" / "components" / "SKILL.md").exists():
        warnings.append("Design system files were detected but frontend component guidance is missing")
    if agents_contract.exists():
        contract_text = agents_contract.read_text(encoding="utf-8")
        required_refs = [
            "skills/MANIFEST.md",
            "skills/requirements/SKILL.md",
            "skills/roadmap/SKILL.md",
        ]
        if signals.backend_routes or signals.services or signals.auth_files:
            required_refs.append("skills/backend/SKILL.md")
        if signals.frontend_routes or signals.components or signals.state_files:
            required_refs.append("skills/frontend/SKILL.md")
        for required_ref in required_refs:
            if required_ref not in contract_text:
                warnings.append(f"AGENTS.md does not reference {required_ref}")

    coverage = {
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
    }
    expected_checks = [
        (bool(signals.backend_routes), (root / "skills" / "backend" / "routes" / "SKILL.md").exists()),
        (bool(signals.services), (root / "skills" / "backend" / "services" / "SKILL.md").exists()),
        (bool(signals.frontend_routes), (root / "skills" / "frontend" / "routes" / "SKILL.md").exists()),
        (bool(signals.components), (root / "skills" / "frontend" / "components" / "SKILL.md").exists()),
        (True, (root / "TRACEABILITY.md").exists()),
        (True, manifest.exists()),
        (True, (root / "skills" / "GRAPH.md").exists()),
    ]
    applicable = [matched for required, matched in expected_checks if required]
    satisfied = sum(1 for matched in applicable if matched)
    base_score = int((satisfied / len(applicable)) * 100) if applicable else 100
    completeness_score = max(0, base_score - (len(warnings) * 5) - (len(errors) * 20))
    if signals.backend_routes and signals.tests:
        completeness_score = min(100, completeness_score + 5)
    if agents_contract.exists():
        completeness_score = min(100, completeness_score + 5)
    if not recommendations:
        recommendations.append("Runtime, agent contract, and generated skill coverage look healthy.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "coverage": coverage,
        "completeness_score": completeness_score,
        "runtime_diagnostics": diagnostics,
        "recommendations": recommendations,
    }
