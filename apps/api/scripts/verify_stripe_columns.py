"""Verify Stripe billing columns exist on the orgs table without printing secrets."""

from __future__ import annotations

import asyncio
import sys

from sqlalchemy import inspect

from packages.db.database import get_engine


REQUIRED_ORG_STRIPE_COLUMNS: frozenset[str] = frozenset(
    {
        "stripe_customer_id",
        "stripe_subscription_id",
        "stripe_subscription_status",
        "plan_seat_limit",
    }
)


def _read_org_columns(sync_connection: object) -> set[str]:
    """Read org table column names from a synchronous SQLAlchemy connection."""
    inspector = inspect(sync_connection)
    return {str(column["name"]) for column in inspector.get_columns("orgs")}


async def verify_stripe_columns() -> tuple[bool, set[str]]:
    """Return whether all Stripe org columns exist and the set of missing names."""
    engine = get_engine()
    async with engine.connect() as connection:
        columns = await connection.run_sync(_read_org_columns)
    missing = REQUIRED_ORG_STRIPE_COLUMNS.difference(columns)
    return not missing, missing


async def main() -> int:
    """Run the Stripe column verification helper."""
    try:
        ok, missing = await verify_stripe_columns()
    except Exception as exc:
        print(f"Stripe column verification failed: {exc}", file=sys.stderr)
        return 1
    if not ok:
        print("Missing Stripe org columns: " + ", ".join(sorted(missing)), file=sys.stderr)
        return 1
    print("Stripe org columns verified: " + ", ".join(sorted(REQUIRED_ORG_STRIPE_COLUMNS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
