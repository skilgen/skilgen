from __future__ import annotations

import logging
import os
from typing import Any, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field
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

    class _MissingStripePortalSession:
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
        billing_portal = type("billing_portal", (), {"Session": _MissingStripePortalSession})

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

    model_config = ConfigDict(str_strip_whitespace=True)

    plan: Literal["team", "business"]
    seat_count: int = Field(gt=0)
    success_url: AnyHttpUrl
    cancel_url: AnyHttpUrl


class PortalSessionRequest(BaseModel):
    """Request body for creating a Stripe Customer Portal session."""

    model_config = ConfigDict(str_strip_whitespace=True)

    return_url: AnyHttpUrl


def _error(status_code: int, detail: str, code: str) -> JSONResponse:
    """Build a structured JSON error response for Stripe routes."""
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})


async def _rollback(db: AsyncSession, context: str) -> None:
    """Rollback the current DB transaction and log rollback failures."""
    try:
        await db.rollback()
    except Exception:
        logger.exception("Stripe route rollback failed during %s", context)


async def _commit(db: AsyncSession, context: str) -> bool:
    """Commit a Stripe route transaction and log commit failures."""
    try:
        await db.commit()
        return True
    except Exception:
        logger.exception("Stripe route commit failed during %s", context)
        await _rollback(db, context)
        return False


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


def _session_url(session: Any) -> str | None:
    """Read a Stripe session URL from Stripe's object or a test double."""
    if isinstance(session, dict):
        value = session.get("url")
    else:
        value = getattr(session, "url", None)
    return str(value) if value else None


def _stripe_object_id(value: Any) -> str | None:
    """Read a Stripe object ID from Stripe's object, dict, or a test double."""
    if isinstance(value, dict):
        object_id = value.get("id")
    else:
        object_id = getattr(value, "id", None)
    return str(object_id) if object_id else None


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


@router.post("/webhook", response_model=None)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool] | JSONResponse:
    """Receive Stripe webhook events and update org billing state."""
    body = await request.body()
    signature = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET)
    if not webhook_secret:
        logger.error("Stripe webhook secret is not configured")
        return _error(503, "Stripe webhook secret is not configured", "STRIPE_WEBHOOK_SECRET_MISSING")
    try:
        event = stripe.Webhook.construct_event(body, signature, webhook_secret)
    except Exception as exc:
        logger.warning("Stripe webhook signature verification failed: %s", exc)
        return _error(400, "Invalid Stripe signature", "STRIPE_SIGNATURE_INVALID")

    event_type = event.get("type")
    obj = dict((event.get("data") or {}).get("object") or {})

    try:
        if event_type in {"customer.subscription.created", "customer.subscription.updated"}:
            await _apply_subscription_created_or_updated(db, obj)
            if not await _commit(db, "stripe webhook subscription update"):
                return _error(400, "Could not persist subscription update", "STRIPE_WEBHOOK_DB_COMMIT_FAILED")
        elif event_type == "customer.subscription.deleted":
            await _apply_subscription_deleted(db, obj)
            if not await _commit(db, "stripe webhook subscription delete"):
                return _error(400, "Could not persist subscription deletion", "STRIPE_WEBHOOK_DB_COMMIT_FAILED")
        elif event_type == "invoice.payment_failed":
            await _apply_payment_failed(db, obj)
            if not await _commit(db, "stripe webhook payment failure"):
                return _error(400, "Could not persist payment failure", "STRIPE_WEBHOOK_DB_COMMIT_FAILED")
    except Exception:
        logger.exception("Stripe webhook processing failed for event %s", event_type)
        await _rollback(db, "stripe webhook processing")
        return _error(400, "Could not process Stripe webhook", "STRIPE_WEBHOOK_PROCESSING_FAILED")

    return {"received": True}


@router.post("/create-checkout-session", response_model=None)
async def create_checkout_session(
    payload: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str] | JSONResponse:
    """Create a Stripe checkout session for a team or business subscription."""
    price_id = _price_ids().get(payload.plan)
    if not price_id:
        logger.error("Stripe price is not configured for plan %s", payload.plan)
        return _error(503, f"Stripe price for {payload.plan} is not configured", "STRIPE_PRICE_NOT_CONFIGURED")

    try:
        org = await db.get(Org, current_org_id)
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")

        customer_id = org.stripe_customer_id
        if not customer_id:
            customer = stripe.Customer.create(
                email=str(current_user.get("email") or ""),
                metadata={"org_id": org.id, "org_login": org.login},
            )
            customer_id = _stripe_object_id(customer)
            if not customer_id:
                await _rollback(db, "checkout customer creation")
                return _error(502, "Stripe customer missing ID", "STRIPE_CUSTOMER_ID_MISSING")
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
            success_url=str(payload.success_url),
            cancel_url=str(payload.cancel_url),
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
        checkout_url = _session_url(session)
        if not checkout_url:
            await _rollback(db, "checkout session creation")
            return _error(502, "Stripe checkout session missing URL", "STRIPE_CHECKOUT_URL_MISSING")
        if not await _commit(db, "checkout session creation"):
            return _error(400, "Could not persist Stripe checkout state", "STRIPE_CHECKOUT_DB_COMMIT_FAILED")
    except Exception:
        logger.exception("Stripe checkout session creation failed for org %s", current_org_id)
        await _rollback(db, "checkout session creation")
        return _error(502, "Could not create Stripe checkout session", "STRIPE_CHECKOUT_FAILED")
    return {"checkout_url": checkout_url}


@router.post("/create-portal-session", response_model=None)
async def create_portal_session(
    payload: PortalSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, str] | JSONResponse:
    """Create a Stripe Customer Portal session for the current organization."""
    try:
        org = await db.get(Org, current_org_id)
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")
        if not org.stripe_customer_id:
            return _error(400, "No billing account", "NO_BILLING_ACCOUNT")

        session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=str(payload.return_url),
        )
        portal_url = _session_url(session)
        if not portal_url:
            return _error(502, "Stripe portal session missing URL", "STRIPE_PORTAL_URL_MISSING")
    except Exception:
        logger.exception("Stripe portal session creation failed for org %s", current_org_id)
        await _rollback(db, "portal session creation")
        return _error(502, "Could not create Stripe portal session", "STRIPE_PORTAL_FAILED")
    return {"portal_url": portal_url}


@router.get("/subscription", response_model=None)
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object] | JSONResponse:
    """Return the current org billing subscription state."""
    try:
        org = await db.get(Org, current_org_id)
    except Exception:
        logger.exception("Stripe subscription lookup failed for org %s", current_org_id)
        await _rollback(db, "subscription lookup")
        return _error(400, "Could not load subscription", "SUBSCRIPTION_LOOKUP_FAILED")
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    return {
        "plan": org.plan,
        "status": org.stripe_subscription_status,
        "seat_count": int(org.seat_count or 0),
        "seat_limit": int(org.plan_seat_limit or PLAN_LIMITS["free"]),
        "stripe_customer_id": org.stripe_customer_id,
    }
