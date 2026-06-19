"""add_org_notification_settings_json

Revision ID: 9a7c3e4d1b20
Revises: f6a1d9c3b2e4
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a7c3e4d1b20"
down_revision: Union[str, Sequence[str], None] = "f6a1d9c3b2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add JSON notification settings storage for org-level policies."""
    op.add_column("orgs", sa.Column("notification_settings", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove JSON notification settings storage."""
    op.drop_column("orgs", "notification_settings")
