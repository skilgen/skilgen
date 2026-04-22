from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import stripe
except ModuleNotFoundError:  # pragma: no cover - production installs stripe from requirements.txt.
    class _MissingStripeCustomer:
        @staticmethod
        def create(**kwargs: object) -> object:
            """Raise when the Stripe SDK is unavailable."""
            raise RuntimeError("Stripe SDK is not installed")

    class _MissingStripeCheckoutSession:
        @staticmethod
        def create(**kwargs: object) -> object:
            """Raise when the Stripe SDK is unavailable."""
            raise RuntimeError("Stripe SDK is not installed")

    class _MissingStripeWebhook:
        @staticmethod
        def construct_event(body: bytes, signature: str | None, secret: str) -> dict[str, object]:
            """Raise when the Stripe SDK is unavailable."""
            raise RuntimeError("Stripe SDK is not installed")

    class _MissingStripe:
        api_key = ""
        Webhook = _MissingStripeWebhook
        Customer = _MissingStripeCustomer
        checkout = type("checkout", (), {"Session": _MissingStripeCheckoutSession})

    stripe = _MissingStripe()  # type: ignore[assignment]

from apps.api.api.auth import get_current_org_id, get_current_user
from packages.db.database import get_db
from packages.db.models import Org


router = APIRouter(prefix="/stripe", tags=["stripe"])
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PRICE_IDS = {
    "team": os.getenv("STRIPE_PRICE_TEAM", ""),
    "business": os.getenv("STRIPE_PRICE_BUSINESS", ""),
}
PLAN_LIMITS = {
    "free": 3,
    "team": 999999,
    "business": 999999,
}


class CheckoutSessionRequest(BaseModel):
    """Request body for creating a Stripe checkout session."""

    plan: str
    seat_count: int = Field(gt=0)
    success_url: str
    cancel_url: str


def _price_ids() -> dict[str, str]:
    """Return Stripe price IDs from the current environment."""
    return {
        "team": os.getenv("STRIPE_PRICE_TEAM", PRICE_IDS["team"]),
        "business": os.getenv("STRIPE_PRICE_BUSINESS", PRICE_IDS["business"]),
    }


def _plan_for_price_id(price_id: str | None) -> str | None:
    """Map a Stripe price ID to a Skillayer plan name."""
    if not price_id:
        return None
    for plan, configured_price_id in _price_ids().items():
        if configured_price_id and configured_price_id == price_id:
            return plan
    return None


def _subscription_price_id(subscription: dict[str, Any]) -> str | None:
    """Extract the first subscription item price ID from a Stripe subscription."""
    items = subscription.get("items") or {}
    data = items.get("data") or []
    if not data:
        return None
    price = data[0].get("price") or {}
    return str(price.get("id") or "") or None


def _subscription_quantity(subscription: dict[str, Any]) -> int:
    """Extract the subscription seat quantity, defaulting to one seat."""
    items = subscription.get("items") or {}
    data = items.get("data") or []
    if not data:
        return 1
    return int(data[0].get("quantity") or 1)


async def _find_org_by_customer_id(db: AsyncSession, customer_id: str | None) -> Org | None:
    """Find an org by Stripe customer ID."""
    if not customer_id:
        return None
    result = await db.execute(select(Org).where(Org.stripe_customer_id == customer_id))
    return result.scalar_one_or_none()


async def _apply_subscription_created_or_updated(db: AsyncSession, subscription: dict[str, Any]) -> Org | None:
    """Apply a Stripe subscription create/update event to an org."""
    org = await _find_org_by_customer_id(db, str(subscription.get("customer") or ""))
    if org is None:
        return None
    plan = _plan_for_price_id(_subscription_price_id(subscription))
    if plan:
        org.plan = plan
        org.plan_seat_limit = PLAN_LIMITS[plan]
    org.seat_count = _subscription_quantity(subscription)
    org.stripe_subscription_id = str(subscription.get("id") or "") or None
    org.stripe_subscription_status = str(subscription.get("status") or "") or None
    await db.flush()
    return org


async def _apply_subscription_deleted(db: AsyncSession, subscription: dict[str, Any]) -> Org | None:
    """Apply a Stripe subscription deletion by downgrading an org to free."""
    org = await _find_org_by_customer_id(db, str(subscription.get("customer") or ""))
    if org is None:
        return None
    org.plan = "free"
    org.plan_seat_limit = PLAN_LIMITS["free"]
    org.stripe_subscription_id = str(subscription.get("id") or "") or org.stripe_subscription_id
    org.stripe_subscription_status = "canceled"
    await db.flush()
    return org


async def _apply_payment_failed(db: AsyncSession, invoice: dict[str, Any]) -> Org | None:
    """Mark an org subscription past due after an invoice payment failure."""
    org = await _find_org_by_customer_id(db, str(invoice.get("customer") or ""))
    if org is None:
        return None
    org.stripe_subscription_status = "past_due"
    logger.warning("Payment failed for org %s", org.id)
    await db.flush()
    return org


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Receive Stripe webhook events and update org billing state."""
    body = await request.body()
    signature = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET)
    try:
        event = stripe.Webhook.construct_event(body, signature, webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature") from exc

    event_type = event.get("type")
    obj = dict((event.get("data") or {}).get("object") or {})

    if event_type in {"customer.subscription.created", "customer.subscription.updated"}:
        await _apply_subscription_created_or_updated(db, obj)
    elif event_type == "customer.subscription.deleted":
        await _apply_subscription_deleted(db, obj)
    elif event_type == "invoice.payment_failed":
        await _apply_payment_failed(db, obj)

    return {"received": True}


@router.post("/create-checkout-session")
async def create_checkout_session(
    payload: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """Create a Stripe checkout session for a team or business subscription."""
    if payload.plan not in {"team", "business"}:
        raise HTTPException(status_code=400, detail="Unsupported plan")
    price_id = _price_ids().get(payload.plan)
    if not price_id:
        raise HTTPException(status_code=500, detail=f"Stripe price for {payload.plan} is not configured")

    org = await db.get(Org, current_org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")

    customer_id = org.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=str(current_user.get("email") or ""),
            metadata={"org_id": org.id, "org_login": org.login},
        )
        customer_id = str(customer.id)
        org.stripe_customer_id = customer_id
        await db.flush()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": payload.seat_count,
            }
        ],
        mode="subscription",
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
        metadata={
            "org_id": org.id,
            "plan": payload.plan,
        },
        subscription_data={
            "metadata": {
                "org_id": org.id,
                "plan": payload.plan,
            }
        },
    )
    return {"checkout_url": str(session.url)}


@router.get("/subscription")
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Return the current org billing subscription state."""
    org = await db.get(Org, current_org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {
        "plan": org.plan,
        "status": org.stripe_subscription_status,
        "seat_count": int(org.seat_count or 0),
        "seat_limit": int(org.plan_seat_limit or PLAN_LIMITS["free"]),
        "stripe_customer_id": org.stripe_customer_id,
    }
