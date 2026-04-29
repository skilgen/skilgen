"""source_connections_enterprise_skills

Revision ID: 20260426_0002
Revises: 20260420_0001
Create Date: 2026-04-26 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260426_0002"
down_revision: str | None = "20260420_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("is_enterprise", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_index("ix_skills_is_enterprise", "skills", ["is_enterprise"])

    op.create_table(
        "source_connections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("encrypted_params", sa.Text(), nullable=False),
        sa.Column("params_hint", sa.JSON(), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(), nullable=True),
        sa.Column("last_connected_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id", "source_type", name="uq_source_connections_org_source_type"),
    )
    op.create_index("ix_source_connections_org_id", "source_connections", ["org_id"])
    op.create_index("ix_source_connections_source_type", "source_connections", ["source_type"])


def downgrade() -> None:
    op.drop_index("ix_source_connections_source_type", table_name="source_connections")
    op.drop_index("ix_source_connections_org_id", table_name="source_connections")
    op.drop_table("source_connections")
    op.drop_index("ix_skills_is_enterprise", table_name="skills")
    op.drop_column("skills", "is_enterprise")
