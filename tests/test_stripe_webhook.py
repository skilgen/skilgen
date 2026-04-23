from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes import stripe as stripe_routes
from packages.db.database import get_db
from packages.db.models import Org


class FakeDB:
    """Tiny async DB double for route unit tests."""

    def __init__(self, org: Org | None = None) -> None:
        self.org = org
        self.flush_count = 0
        self.commit_count = 0
        self.rollback_count = 0

    async def get(self, model: object, key: str) -> Org | None:
        """Return the configured org."""
        return self.org

    async def flush(self) -> None:
        """Record that a flush would happen."""
        self.flush_count += 1

    async def commit(self) -> None:
        """Record that a commit would happen."""
        self.commit_count += 1

    async def rollback(self) -> None:
        """Record that a rollback would happen."""
        self.rollback_count += 1


class FakeRequest:
    """Request double that exposes raw body and headers."""

    def __init__(self, body: bytes = b"{}", headers: dict[str, str] | None = None) -> None:
        self._body = body
        self.headers = headers or {}

    async def body(self) -> bytes:
        """Return the raw request body."""
        return self._body


def _subscription(price_id: str, status: str = "active") -> dict[str, Any]:
    """Build a Stripe subscription payload."""
    return {
        "id": "sub_123",
        "customer": "cus_123",
        "status": status,
        "items": {"data": [{"price": {"id": price_id}, "quantity": 5}]},
    }


def _json_response_body(response: object) -> dict[str, object]:
    """Decode a route-level JSONResponse returned by direct route calls."""
    return dict(json.loads(response.body.decode("utf-8")))  # type: ignore[attr-defined]


def _client(org: Org | None, with_auth: bool = True) -> TestClient:
    """Build a FastAPI test client with optional auth overrides."""
    app = FastAPI()
    app.include_router(stripe_routes.router)

    async def override_org_id() -> str:
        return "org_123"

    async def override_user() -> dict[str, str]:
        return {"email": "dev@example.com"}

    async def override_db() -> Any:
        yield FakeDB(org)

    app.dependency_overrides[get_db] = override_db
    if with_auth:
        app.dependency_overrides[get_current_org_id] = override_org_id
        app.dependency_overrides[get_current_user] = override_user
    return TestClient(app)


@pytest.mark.anyio
async def test_subscription_created_updates_org_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    """Subscription create events update org plan and Stripe fields."""
    monkeypatch.setenv("STRIPE_PRICE_TEAM", "price_team_monthly")
    org = Org(github_org_id=1, login="acme", name="Acme", stripe_customer_id="cus_123")

    async def fake_find_org(db: FakeDB, customer_id: str | None) -> Org | None:
        return org

    monkeypatch.setattr(stripe_routes, "_find_org_by_customer_id", fake_find_org)
    db = FakeDB(org)

    await stripe_routes._apply_subscription_created_or_updated(db, _subscription("price_team_monthly"))

    assert org.plan == "team"
    assert org.plan_seat_limit == 999999
    assert org.seat_count == 5
    assert org.stripe_subscription_id == "sub_123"
    assert org.stripe_subscription_status == "active"
    assert db.flush_count == 1


@pytest.mark.anyio
async def test_subscription_deleted_downgrades_to_free(monkeypatch: pytest.MonkeyPatch) -> None:
    """Subscription delete events downgrade an org to the free plan."""
    org = Org(
        github_org_id=1,
        login="acme",
        name="Acme",
        plan="team",
        plan_seat_limit=999999,
        stripe_customer_id="cus_123",
    )

    async def fake_find_org(db: FakeDB, customer_id: str | None) -> Org | None:
        return org

    monkeypatch.setattr(stripe_routes, "_find_org_by_customer_id", fake_find_org)
    db = FakeDB(org)

    await stripe_routes._apply_subscription_deleted(db, {"id": "sub_123", "customer": "cus_123"})

    assert org.plan == "free"
    assert org.plan_seat_limit == 3
    assert org.stripe_subscription_status == "canceled"
    assert db.flush_count == 1


@pytest.mark.anyio
async def test_invalid_signature_returns_400(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid Stripe webhook signatures return structured HTTP 400."""

    def fail_construct_event(body: bytes, signature: str | None, secret: str) -> dict[str, object]:
        raise ValueError("bad signature")

    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(stripe_routes.stripe.Webhook, "construct_event", fail_construct_event)

    response = await stripe_routes.stripe_webhook(FakeRequest(headers={"stripe-signature": "bad"}), FakeDB())

    assert response.status_code == 400  # type: ignore[attr-defined]
    assert _json_response_body(response) == {
        "detail": "Invalid Stripe signature",
        "code": "STRIPE_SIGNATURE_INVALID",
    }


@pytest.mark.anyio
async def test_webhook_rolls_back_on_processing_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Webhook processing errors rollback and return structured JSON."""

    def construct_event(body: bytes, signature: str | None, secret: str) -> dict[str, object]:
        return {"type": "customer.subscription.created", "data": {"object": _subscription("price_team_monthly")}}

    async def fail_apply(db: FakeDB, subscription: dict[str, Any]) -> Org | None:
        raise RuntimeError("db unavailable")

    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setattr(stripe_routes.stripe.Webhook, "construct_event", construct_event)
    monkeypatch.setattr(stripe_routes, "_apply_subscription_created_or_updated", fail_apply)
    db = FakeDB()

    response = await stripe_routes.stripe_webhook(FakeRequest(headers={"stripe-signature": "valid"}), db)

    assert response.status_code == 400  # type: ignore[attr-defined]
    assert db.rollback_count == 1
    assert _json_response_body(response) == {
        "detail": "Could not process Stripe webhook",
        "code": "STRIPE_WEBHOOK_PROCESSING_FAILED",
    }


@pytest.mark.anyio
async def test_create_checkout_session_returns_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Checkout session creation returns the Stripe checkout URL."""
    monkeypatch.setenv("STRIPE_PRICE_TEAM", "price_team_monthly")
    org = Org(id="org_123", github_org_id=1, login="acme", name="Acme")
    db = FakeDB(org)

    def fake_customer_create(**kwargs: object) -> SimpleNamespace:
        assert kwargs["email"] == "dev@example.com"
        assert kwargs["metadata"] == {"org_id": "org_123", "org_login": "acme"}
        return SimpleNamespace(id="cus_123")

    def fake_session_create(**kwargs: object) -> SimpleNamespace:
        assert kwargs["customer"] == "cus_123"
        assert kwargs["line_items"] == [{"price": "price_team_monthly", "quantity": 5}]
        assert kwargs["success_url"] == "https://app.skillayer.com/success"
        assert kwargs["cancel_url"] == "https://app.skillayer.com/cancel"
        assert kwargs["metadata"] == {"org_id": "org_123", "plan": "team"}
        return SimpleNamespace(url="https://checkout.stripe.test/session")

    monkeypatch.setattr(stripe_routes.stripe.Customer, "create", fake_customer_create)
    monkeypatch.setattr(stripe_routes.stripe.checkout.Session, "create", fake_session_create)

    result = await stripe_routes.create_checkout_session(
        stripe_routes.CheckoutSessionRequest(
            plan="team",
            seat_count=5,
            success_url="https://app.skillayer.com/success",
            cancel_url="https://app.skillayer.com/cancel",
        ),
        db=db,  # type: ignore[arg-type]
        current_org_id="org_123",
        current_user={"email": "dev@example.com"},
    )

    assert result == {"checkout_url": "https://checkout.stripe.test/session"}
    assert org.stripe_customer_id == "cus_123"
    assert db.commit_count == 1


@pytest.mark.anyio
async def test_create_checkout_session_returns_structured_error_when_price_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Checkout returns a structured configuration error when price IDs are missing."""
    monkeypatch.delenv("STRIPE_PRICE_TEAM", raising=False)
    org = Org(id="org_123", github_org_id=1, login="acme", name="Acme")

    response = await stripe_routes.create_checkout_session(
        stripe_routes.CheckoutSessionRequest(
            plan="team",
            seat_count=5,
            success_url="https://app.skillayer.com/success",
            cancel_url="https://app.skillayer.com/cancel",
        ),
        db=FakeDB(org),  # type: ignore[arg-type]
        current_org_id="org_123",
        current_user={"email": "dev@example.com"},
    )

    assert response.status_code == 503  # type: ignore[attr-defined]
    assert _json_response_body(response) == {
        "detail": "Stripe price for team is not configured",
        "code": "STRIPE_PRICE_NOT_CONFIGURED",
    }


@pytest.mark.anyio
async def test_create_checkout_session_rolls_back_on_stripe_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Checkout rolls back local DB state when Stripe session creation fails."""
    monkeypatch.setenv("STRIPE_PRICE_TEAM", "price_team_monthly")
    org = Org(id="org_123", github_org_id=1, login="acme", name="Acme", stripe_customer_id="cus_123")
    db = FakeDB(org)

    def fail_session_create(**kwargs: object) -> SimpleNamespace:
        raise RuntimeError("stripe unavailable")

    monkeypatch.setattr(stripe_routes.stripe.checkout.Session, "create", fail_session_create)

    response = await stripe_routes.create_checkout_session(
        stripe_routes.CheckoutSessionRequest(
            plan="team",
            seat_count=5,
            success_url="https://app.skillayer.com/success",
            cancel_url="https://app.skillayer.com/cancel",
        ),
        db=db,  # type: ignore[arg-type]
        current_org_id="org_123",
        current_user={"email": "dev@example.com"},
    )

    assert response.status_code == 502  # type: ignore[attr-defined]
    assert db.rollback_count == 1
    assert _json_response_body(response) == {
        "detail": "Could not create Stripe checkout session",
        "code": "STRIPE_CHECKOUT_FAILED",
    }


def test_checkout_endpoint_requires_auth() -> None:
    """Checkout is protected by auth dependencies."""
    response = _client(Org(id="org_123", github_org_id=1, login="acme", name="Acme"), with_auth=False).post(
        "/stripe/create-checkout-session",
        json={
            "plan": "team",
            "seat_count": 5,
            "success_url": "https://app.skillayer.com/success",
            "cancel_url": "https://app.skillayer.com/cancel",
        },
    )

    assert response.status_code in {401, 403}
    assert "detail" in response.json()
