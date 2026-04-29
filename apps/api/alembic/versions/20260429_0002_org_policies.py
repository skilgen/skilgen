"""ensure org policies for PR policy engine

Revision ID: 20260429_0002
Revises: 20260429_0001
Create Date: 2026-04-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260429_0002"
down_revision = "20260429_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("org_policies"):
        op.create_table(
            "org_policies",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("description", sa.String(length=512), nullable=True),
            sa.Column("rule_type", sa.String(length=64), nullable=False),
            sa.Column("rule_config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
            sa.Column("severity", sa.String(length=16), server_default="error", nullable=False),
            sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("org_policies", "ix_org_policies_org_id"):
        op.create_index("ix_org_policies_org_id", "org_policies", ["org_id"])


def downgrade() -> None:
    if _has_index("org_policies", "ix_org_policies_org_id"):
        op.drop_index("ix_org_policies_org_id", table_name="org_policies")
