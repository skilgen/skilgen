"""add pr attribution risk columns

Revision ID: 20260428_0003
Revises: 20260428_0002
Create Date: 2026-04-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260428_0003"
down_revision = "20260428_0002"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in set(inspector.get_table_names()):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    json_type = postgresql.JSONB(astext_type=sa.Text()) if bind.dialect.name == "postgresql" else sa.JSON()
    object_default = sa.text("'{}'::jsonb") if bind.dialect.name == "postgresql" else sa.text("'{}'")

    if not _has_column("pr_attributions", "risk_score"):
        op.add_column(
            "pr_attributions",
            sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        )
    if not _has_column("pr_attributions", "risk_tier"):
        op.add_column(
            "pr_attributions",
            sa.Column("risk_tier", sa.String(length=16), nullable=False, server_default="green"),
        )
    if not _has_column("pr_attributions", "risk_breakdown"):
        op.add_column(
            "pr_attributions",
            sa.Column("risk_breakdown", json_type, nullable=False, server_default=object_default),
        )


def downgrade() -> None:
    if _has_column("pr_attributions", "risk_breakdown"):
        op.drop_column("pr_attributions", "risk_breakdown")
    if _has_column("pr_attributions", "risk_tier"):
        op.drop_column("pr_attributions", "risk_tier")
    if _has_column("pr_attributions", "risk_score"):
        op.drop_column("pr_attributions", "risk_score")
