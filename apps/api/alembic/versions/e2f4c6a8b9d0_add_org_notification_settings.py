"""add_org_notification_settings

Revision ID: e2f4c6a8b9d0
Revises: d4f9a71c2e8b
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e2f4c6a8b9d0"
down_revision: Union[str, Sequence[str], None] = "d4f9a71c2e8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add org-level score and notification settings."""
    op.add_column("orgs", sa.Column("score_threshold", sa.Integer(), nullable=False, server_default="60"))
    op.add_column("orgs", sa.Column("slack_webhook_url", sa.String(length=2048), nullable=True))
    op.add_column("orgs", sa.Column("notify_on_pr", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("orgs", sa.Column("notify_on_stale", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column("orgs", "score_threshold", server_default=None)
    op.alter_column("orgs", "notify_on_pr", server_default=None)
    op.alter_column("orgs", "notify_on_stale", server_default=None)


def downgrade() -> None:
    """Remove org-level score and notification settings."""
    org_columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("orgs")}
    for column_name in ("notify_on_stale", "notify_on_pr", "slack_webhook_url", "score_threshold"):
        if column_name in org_columns:
            op.drop_column("orgs", column_name)
