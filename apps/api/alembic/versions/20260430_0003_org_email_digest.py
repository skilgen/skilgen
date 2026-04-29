"""add org email digest settings

Revision ID: 20260430_0003
Revises: 20260430_0002
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260430_0003"
down_revision = "20260430_0002"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("orgs", "digest_email"):
        op.add_column("orgs", sa.Column("digest_email", sa.Text(), nullable=True))
    if not _has_column("orgs", "digest_enabled"):
        op.add_column("orgs", sa.Column("digest_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    if not _has_column("orgs", "digest_day"):
        op.add_column("orgs", sa.Column("digest_day", sa.Integer(), nullable=False, server_default="1"))
    if not _has_column("orgs", "digest_hour"):
        op.add_column("orgs", sa.Column("digest_hour", sa.Integer(), nullable=False, server_default="8"))


def downgrade() -> None:
    if _has_column("orgs", "digest_hour"):
        op.drop_column("orgs", "digest_hour")
    if _has_column("orgs", "digest_day"):
        op.drop_column("orgs", "digest_day")
    if _has_column("orgs", "digest_enabled"):
        op.drop_column("orgs", "digest_enabled")
    if _has_column("orgs", "digest_email"):
        op.drop_column("orgs", "digest_email")
