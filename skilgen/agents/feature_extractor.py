from __future__ import annotations

from pathlib import Path

from skilgen.agents.codebase_signals import analyze_codebase
from skilgen.agents.requirements_parser import parse_project_intent, parse_project_intent_native
from skilgen.deep_agents_core import run_deep_json
from skilgen.core.models import FeatureRecord


def extract_features_native(requirements_path: Path | None, project_root: Path) -> list[FeatureRecord]:
    intent = parse_project_intent_native(project_root, requirements_path)
    signals = analyze_codebase(project_root)
    features: list[FeatureRecord] = []
    if requirements_path is not None:
        features.append(
            FeatureRecord(
                name="Requirements-driven scan",
                domain="requirements",
                location=requirements_path.name,
                description="Parse the requirements input and generate skills and project docs.",
                status="active",
                last_modified="current",
            )
        )
    features.append(
        FeatureRecord(
            name="Project folder analysis",
            domain="analysis",
            location=str(project_root.name or "."),
            description="Analyze the input folder and generate outputs into that same folder.",
            status="active",
            last_modified="current",
        )
    )

    for route in signals.backend_routes[:4]:
        features.append(
            FeatureRecord(
                name=f"Backend route: {route}",
                domain="backend",
                location=route,
                description="Detected route or handler implementation in the scanned codebase.",
                status="active",
                last_modified="current",
            )
        )

    for route in signals.frontend_routes[:4]:
        features.append(
            FeatureRecord(
                name=f"Frontend route: {route}",
                domain="frontend",
                location=route,
                description="Detected route or page implementation in the scanned codebase.",
                status="active",
                last_modified="current",
            )
        )

    for component in signals.components[:4]:
        features.append(
            FeatureRecord(
                name=f"Component: {component}",
                domain="frontend",
                location=component,
                description="Detected reusable UI component in the scanned codebase.",
                status="active",
                last_modified="current",
            )
        )

    for endpoint in intent.endpoints[:6]:
        features.append(
            FeatureRecord(
                name=endpoint[:80],
                domain="backend",
                location="requirements" if requirements_path is not None else "codebase",
                description=(
                    "Endpoint or route intent extracted from the requirements source."
                    if requirements_path is not None
                    else "Endpoint or route intent synthesized from the scanned codebase."
                ),
                status="planned",
                last_modified="current",
            )
        )

    for flow in intent.ui_flows[:6]:
        features.append(
            FeatureRecord(
                name=flow[:80],
                domain="frontend",
                location="requirements" if requirements_path is not None else "codebase",
                description=(
                    "User-facing flow extracted from the requirements source."
                    if requirements_path is not None
                    else "User-facing flow synthesized from the scanned codebase."
                ),
                status="planned",
                last_modified="current",
            )
        )

    return features


def extract_features(requirements_path: Path | None, project_root: Path) -> list[FeatureRecord]:
    resolved_requirements = requirements_path.resolve() if requirements_path is not None else None
    resolved_root = project_root.resolve()
    native_features = extract_features_native(resolved_requirements, resolved_root)
    signals = analyze_codebase(resolved_root)
    intent = parse_project_intent(resolved_root, resolved_requirements)
    payload = run_deep_json(
        "feature model synthesis",
        (
            "Synthesize a feature model for Skilgen from requirements intent and concrete code signals. Return JSON "
            "with key `features`, where features is a list of objects with name, domain, location, description, "
            "status, last_modified. Favor features that would materially influence skill generation, implementation "
            "planning, or agent guidance. Group features into realistic engineering domains, prefer file-backed "
            "locations when possible, and keep descriptions actionable for coding agents rather than product-marketing summaries.\n\n"
            f"Requirements path: {resolved_requirements}\n"
            f"Intent features: {intent.features}\n"
            f"Intent endpoints: {intent.endpoints}\n"
            f"Intent ui_flows: {intent.ui_flows}\n"
            f"Backend routes: {signals.backend_routes}\n"
            f"Frontend routes: {signals.frontend_routes}\n"
            f"Components: {signals.components}\n"
            f"Services: {signals.services}\n"
        ),
        lambda: {"features": [feature.__dict__ for feature in native_features]},
    )
    items = payload.get("features", [])
    features: list[FeatureRecord] = []
    for item in items:
        features.append(
            FeatureRecord(
                name=str(item.get("name", "Unnamed feature")),
                domain=str(item.get("domain", "requirements")),
                location=str(item.get("location", "requirements")),
                description=str(item.get("description", "")),
                status=str(item.get("status", "planned")),
                last_modified=str(item.get("last_modified", "current")),
            )
        )
    return features or native_features
