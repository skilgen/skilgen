"""add org slack standup settings

Revision ID: 20260429_0001
Revises: 20260428_0004
Create Date: 2026-04-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260429_0001"
down_revision = "20260428_0004"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("orgs", "slack_webhook_url"):
        op.add_column("orgs", sa.Column("slack_webhook_url", sa.Text(), nullable=True))
    if not _has_column("orgs", "slack_standup_enabled"):
        op.add_column(
            "orgs",
            sa.Column("slack_standup_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
    if not _has_column("orgs", "slack_standup_hour"):
        op.add_column(
            "orgs",
            sa.Column("slack_standup_hour", sa.Integer(), nullable=False, server_default="9"),
        )


def downgrade() -> None:
    if _has_column("orgs", "slack_standup_hour"):
        op.drop_column("orgs", "slack_standup_hour")
    if _has_column("orgs", "slack_standup_enabled"):
        op.drop_column("orgs", "slack_standup_enabled")
    if _has_column("orgs", "slack_webhook_url"):
        op.drop_column("orgs", "slack_webhook_url")
