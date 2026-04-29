from __future__ import annotations

import asyncio

from apps.api.api.index import app
from apps.api.api.routes import health as health_route


def test_health_degrades_without_database_url(monkeypatch) -> None:
    monkeypatch.setattr(health_route.settings, "DATABASE_URL", "")
    monkeypatch.setattr(health_route.settings, "DEPLOYMENT_MODE", "test")

    response = asyncio.run(health_route.health())

    assert response["status"] == "degraded"
    assert response["db"] == "error"
    assert response["deployment_mode"] == "test"
    assert "timestamp" in response


def test_health_route_registered() -> None:
    assert "/health" in {route.path for route in app.routes}
