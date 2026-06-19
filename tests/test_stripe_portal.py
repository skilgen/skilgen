from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id
from apps.api.api.routes import stripe
from packages.db.database import get_db


class FakeDb:
    def __init__(self, org: object | None) -> None:
        self.org = org
        self.rollback_count = 0

    async def get(self, model: object, key: str) -> object | None:
        return self.org

    async def rollback(self) -> None:
        self.rollback_count += 1


def _client(org: object | None) -> TestClient:
    app = FastAPI()
    app.include_router(stripe.router)

    async def override_org_id() -> str:
        return "org_123"

    async def override_db() -> Any:
        yield FakeDb(org)

    app.dependency_overrides[get_current_org_id] = override_org_id
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def _unauthenticated_client(org: object | None) -> TestClient:
    app = FastAPI()
    app.include_router(stripe.router)

    async def override_db() -> Any:
        yield FakeDb(org)

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_portal_session_returns_url(monkeypatch: pytest.MonkeyPatch) -> None:
    created: dict[str, str] = {}

    class FakePortalSession:
        @staticmethod
        def create(customer: str, return_url: str) -> object:
            created["customer"] = customer
            created["return_url"] = return_url
            return SimpleNamespace(url="https://billing.stripe.test/session")

    fake_stripe = SimpleNamespace(
        billing_portal=SimpleNamespace(Session=FakePortalSession),
    )
    monkeypatch.setattr(stripe, "stripe", fake_stripe)

    response = _client(SimpleNamespace(stripe_customer_id="cus_123")).post(
        "/stripe/create-portal-session",
        json={"return_url": "https://app.skillayer.com/dashboard/settings/billing"},
    )

    assert response.status_code == 200
    assert response.json() == {"portal_url": "https://billing.stripe.test/session"}
    assert created == {
        "customer": "cus_123",
        "return_url": "https://app.skillayer.com/dashboard/settings/billing",
    }


def test_portal_session_returns_400_when_no_stripe_customer_id() -> None:
    response = _client(SimpleNamespace(stripe_customer_id=None)).post(
        "/stripe/create-portal-session",
        json={"return_url": "https://app.skillayer.com/dashboard/settings/billing"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "No billing account", "code": "NO_BILLING_ACCOUNT"}


def test_portal_session_requires_auth() -> None:
    response = _unauthenticated_client(SimpleNamespace(stripe_customer_id="cus_123")).post(
        "/stripe/create-portal-session",
        json={"return_url": "https://app.skillayer.com/dashboard/settings/billing"},
    )

    assert response.status_code in {401, 403}
    assert "detail" in response.json()


def test_portal_session_rolls_back_on_stripe_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingPortalSession:
        @staticmethod
        def create(customer: str, return_url: str) -> object:
            raise RuntimeError("stripe unavailable")

    fake_stripe = SimpleNamespace(
        billing_portal=SimpleNamespace(Session=FailingPortalSession),
    )
    monkeypatch.setattr(stripe, "stripe", fake_stripe)

    response = _client(SimpleNamespace(stripe_customer_id="cus_123")).post(
        "/stripe/create-portal-session",
        json={"return_url": "https://app.skillayer.com/dashboard/settings/billing"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Could not create Stripe portal session",
        "code": "STRIPE_PORTAL_FAILED",
    }


def test_subscription_returns_current_plan_status() -> None:
    response = _client(
        SimpleNamespace(
            plan="team",
            stripe_subscription_status="active",
            seat_count=5,
            plan_seat_limit=999999,
            stripe_customer_id="cus_123",
        )
    ).get("/stripe/subscription")

    assert response.status_code == 200
    assert response.json() == {
        "plan": "team",
        "status": "active",
        "seat_count": 5,
        "seat_limit": 999999,
        "stripe_customer_id": "cus_123",
    }


def test_subscription_requires_auth() -> None:
    response = _unauthenticated_client(
        SimpleNamespace(
            plan="team",
            stripe_subscription_status="active",
            seat_count=5,
            plan_seat_limit=999999,
            stripe_customer_id="cus_123",
        )
    ).get("/stripe/subscription")

    assert response.status_code in {401, 403}
    assert "detail" in response.json()
