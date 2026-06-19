"""pull request branch columns for GitHub enrichment

Revision ID: 20260520_0002
Revises: 20260520_0001
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0002"
down_revision = "20260520_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_table("pull_requests"):
        return

    if not _has_column("pull_requests", "head_branch"):
        op.add_column("pull_requests", sa.Column("head_branch", sa.Text(), nullable=True))

    if not _has_column("pull_requests", "base_branch"):
        op.add_column("pull_requests", sa.Column("base_branch", sa.Text(), nullable=True))


def downgrade() -> None:
    if not _has_table("pull_requests"):
        return

    if _has_column("pull_requests", "base_branch"):
        op.drop_column("pull_requests", "base_branch")

    if _has_column("pull_requests", "head_branch"):
        op.drop_column("pull_requests", "head_branch")

