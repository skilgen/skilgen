"""add_stripe_fields_to_orgs

Revision ID: a4c2e3f91b65
Revises: 7b68f2d4c9a1
Create Date: 2026-04-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4c2e3f91b65"
down_revision: Union[str, Sequence[str], None] = "7b68f2d4c9a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("orgs", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True))
    op.add_column("orgs", sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True))
    op.add_column("orgs", sa.Column("stripe_subscription_status", sa.String(length=50), nullable=True))
    op.add_column("orgs", sa.Column("plan_seat_limit", sa.Integer(), nullable=False, server_default="3"))
    op.alter_column("orgs", "plan_seat_limit", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orgs", "plan_seat_limit")
    op.drop_column("orgs", "stripe_subscription_status")
    op.drop_column("orgs", "stripe_subscription_id")
    op.drop_column("orgs", "stripe_customer_id")
