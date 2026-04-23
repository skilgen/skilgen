from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    """Read a repository file for dashboard wiring assertions."""
    return (ROOT / path).read_text(encoding="utf-8")


def test_dashboard_routes_define_segment_error_boundaries() -> None:
    """Every dashboard route segment should render a graceful route error panel."""
    routes = [
        "apps/dashboard/app/dashboard/error.tsx",
        "apps/dashboard/app/dashboard/analytics/error.tsx",
        "apps/dashboard/app/dashboard/registry/error.tsx",
        "apps/dashboard/app/dashboard/repos/error.tsx",
        "apps/dashboard/app/dashboard/repos/[repoId]/error.tsx",
        "apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/error.tsx",
        "apps/dashboard/app/dashboard/settings/error.tsx",
        "apps/dashboard/app/dashboard/settings/billing/error.tsx",
        "apps/dashboard/app/dashboard/skills/error.tsx",
        "apps/dashboard/app/dashboard/upgrade/error.tsx",
    ]

    for route in routes:
        source = read(route)
        assert '"use client"' in source
        assert "DashboardRouteError" in source
        assert "reset={reset}" in source


def test_section_error_boundary_uses_shared_fallback_text() -> None:
    """Client-side section render errors should produce the required fallback copy."""
    boundary = read("apps/dashboard/src/components/section-error-boundary.tsx")
    route_error = read("apps/dashboard/src/components/dashboard-route-error.tsx")
    fallback = read("apps/dashboard/src/components/section-fallback.tsx")

    assert '"use client"' in boundary
    assert "static getDerivedStateFromError" in boundary
    assert "componentDidCatch" in boundary
    assert 'scope: "dashboard.section"' in boundary
    assert "<SectionFallback section={this.props.section} />" in boundary
    assert 'scope: "dashboard.route"' in route_error
    assert "Try again" in route_error
    assert "Unable to load {section}." in fallback
    assert "Refresh the page or contact support." in fallback


def test_dashboard_sections_are_wrapped_with_error_boundaries() -> None:
    """Main dashboard sections should be protected against client render failures."""
    expected = {
        "apps/dashboard/src/components/overview-live-data.tsx": [
            'section="overview metrics"',
            'section="score trend"',
            'section="repositories"',
        ],
        "apps/dashboard/app/dashboard/repos/page.tsx": ['section="repositories"'],
        "apps/dashboard/app/dashboard/repos/[repoId]/page.tsx": [
            'section="repository header"',
            'section="repository subscores"',
            'section="score history"',
            'section="dependencies"',
            'section="skills"',
        ],
        "apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/page.tsx": [
            'section="skill header"',
            'section="skill subscores"',
            'section="skill content"',
        ],
        "apps/dashboard/app/dashboard/analytics/page.tsx": [
            'section="analytics metrics"',
            'section="analytics activity"',
            'section="analytics skills"',
        ],
        "apps/dashboard/app/dashboard/registry/page.tsx": [
            'section="registry filters"',
            'section="registry skills"',
        ],
        "apps/dashboard/app/dashboard/settings/page.tsx": ['section={`${tab} settings`}'],
        "apps/dashboard/app/dashboard/settings/billing/page.tsx": [
            'section="billing success message"',
            'section="billing"',
        ],
        "apps/dashboard/app/dashboard/skills/page.tsx": ['section="skills"'],
        "apps/dashboard/app/dashboard/upgrade/page.tsx": ['section="pricing plans"'],
    }

    for path, snippets in expected.items():
        source = read(path)
        assert "SectionErrorBoundary" in source
        for snippet in snippets:
            assert snippet in source
