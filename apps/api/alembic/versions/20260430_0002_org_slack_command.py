"""add org slack command settings

Revision ID: 20260430_0002
Revises: 20260430_0001
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260430_0002"
down_revision = "20260430_0001"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in set(inspector.get_table_names()):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("orgs", "slack_signing_secret"):
        op.add_column("orgs", sa.Column("slack_signing_secret", sa.Text(), nullable=True))
    if not _has_column("orgs", "slack_team_id"):
        op.add_column("orgs", sa.Column("slack_team_id", sa.Text(), nullable=True))


def downgrade() -> None:
    if _has_column("orgs", "slack_team_id"):
        op.drop_column("orgs", "slack_team_id")
    if _has_column("orgs", "slack_signing_secret"):
        op.drop_column("orgs", "slack_signing_secret")
