"""add admin login events

Revision ID: 20260430_0005
Revises: 20260430_0004
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260430_0005"
down_revision = "20260430_0004"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS login_events (
            id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
            org_id TEXT REFERENCES orgs(id) ON DELETE SET NULL,
            user_login TEXT,
            user_email TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_login_events_org_id ON login_events (org_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_login_events_user_login ON login_events (user_login, created_at DESC)")

    if not _has_column("orgs", "is_suspended"):
        op.add_column("orgs", sa.Column("is_suspended", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    if not _has_column("orgs", "suspended_at"):
        op.add_column("orgs", sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True))
    if not _has_column("orgs", "suspended_reason"):
        op.add_column("orgs", sa.Column("suspended_reason", sa.Text(), nullable=True))
    if not _has_column("orgs", "plan"):
        op.add_column("orgs", sa.Column("plan", sa.String(length=32), nullable=True, server_default="free"))


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_login_events_user_login")
    op.execute("DROP INDEX IF EXISTS ix_login_events_org_id")
    op.execute("DROP TABLE IF EXISTS login_events")

    if _has_column("orgs", "suspended_reason"):
        op.drop_column("orgs", "suspended_reason")
    if _has_column("orgs", "suspended_at"):
        op.drop_column("orgs", "suspended_at")
    if _has_column("orgs", "is_suspended"):
        op.drop_column("orgs", "is_suspended")
    # plan predates this migration in current Skillayer deployments; leave it intact on downgrade.
