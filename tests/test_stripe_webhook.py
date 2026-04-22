from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from apps.api.api.routes import stripe as stripe_routes
from packages.db.models import Org


class FakeDB:
    """Tiny async DB double for route unit tests."""

    def __init__(self, org: Org | None = None) -> None:
        self.org = org
        self.flush_count = 0

    async def get(self, model: object, key: str) -> Org | None:
        """Return the configured org."""
        return self.org

    async def flush(self) -> None:
        """Record that a flush would happen."""
        self.flush_count += 1


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
    """Invalid Stripe webhook signatures return HTTP 400."""

    def fail_construct_event(body: bytes, signature: str | None, secret: str) -> dict[str, object]:
        raise ValueError("bad signature")

    monkeypatch.setattr(stripe_routes.stripe.Webhook, "construct_event", fail_construct_event)

    with pytest.raises(HTTPException) as exc:
        await stripe_routes.stripe_webhook(FakeRequest(headers={"stripe-signature": "bad"}), FakeDB())

    assert exc.value.status_code == 400


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
