from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import Org

try:
    import stripe
except ModuleNotFoundError:  # pragma: no cover - production installs stripe via API requirements.
    stripe = None  # type: ignore[assignment]


router = APIRouter(prefix="/stripe", tags=["stripe"])


class PortalSessionRequest(BaseModel):
    return_url: str


@router.post("/create-portal-session")
async def create_portal_session(
    payload: PortalSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, str]:
    """Create a Stripe Customer Portal session for the current organization."""
    org = await db.get(Org, current_org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")

    stripe_customer_id = getattr(org, "stripe_customer_id", None)
    if not stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account")

    if stripe is None:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=payload.return_url,
    )
    portal_url = _session_url(session)
    if not portal_url:
        raise HTTPException(status_code=502, detail="Stripe portal session missing URL")
    return {"portal_url": portal_url}


def _session_url(session: Any) -> str | None:
    """Read a portal session URL from Stripe's object or a test double."""
    if isinstance(session, dict):
        value = session.get("url")
    else:
        value = getattr(session, "url", None)
    return str(value) if value else None
