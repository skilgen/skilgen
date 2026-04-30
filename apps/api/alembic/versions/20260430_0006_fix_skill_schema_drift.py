"""fix skill schema drift

Revision ID: 20260430_0006
Revises: 20260430_0005
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260430_0006"
down_revision = "20260430_0005"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if _has_table("skills") and not _has_column("skills", "updated_at"):
        op.add_column(
            "skills",
            sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        )
    if _has_table("agent_load_events") and not _has_column("agent_load_events", "detected_runtime"):
        op.add_column("agent_load_events", sa.Column("detected_runtime", sa.String(length=100), nullable=True))


def downgrade() -> None:
    if _has_column("agent_load_events", "detected_runtime"):
        op.drop_column("agent_load_events", "detected_runtime")
    if _has_column("skills", "updated_at"):
        op.drop_column("skills", "updated_at")
