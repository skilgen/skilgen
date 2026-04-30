"""ensure sla policies table exists

Revision ID: 20260430_0007
Revises: 20260430_0006
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260430_0007"
down_revision = "20260430_0006"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("sla_policies"):
        op.create_table(
            "sla_policies",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("repo_id", sa.String(), nullable=True),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("coverage_target_pct", sa.Integer(), nullable=False, server_default="80"),
            sa.Column("alert_email", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.Column("last_checked_at", sa.DateTime(), nullable=True),
            sa.Column("last_status", sa.String(length=32), nullable=False, server_default="unknown"),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("sla_policies", "ix_sla_policies_org_active"):
        op.create_index("ix_sla_policies_org_active", "sla_policies", ["org_id", "is_active"])


def downgrade() -> None:
    if _has_index("sla_policies", "ix_sla_policies_org_active"):
        op.drop_index("ix_sla_policies_org_active", table_name="sla_policies")
