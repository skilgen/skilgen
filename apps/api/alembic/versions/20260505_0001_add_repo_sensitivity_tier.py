"""add repo sensitivity tier

Revision ID: 20260505_0001
Revises: 20260504_0001
Create Date: 2026-05-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260505_0001"
down_revision = "20260504_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if _has_table("repos") and not _has_column("repos", "sensitivity_tier"):
        op.add_column(
            "repos",
            sa.Column("sensitivity_tier", sa.String(length=32), nullable=True, server_default="internal"),
        )


def downgrade() -> None:
    if _has_column("repos", "sensitivity_tier"):
        op.drop_column("repos", "sensitivity_tier")
