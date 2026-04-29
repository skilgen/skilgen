"""add digest config

Revision ID: 20260426_0004_digest
Revises: 20260426_0003
Create Date: 2026-04-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260426_0004_digest"
down_revision = "20260426_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "digest_configs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="Weekly AI Readiness Digest"),
        sa.Column("subject", sa.String(length=255), nullable=False, server_default="Your Weekly AI Readiness Report"),
        sa.Column("frequency", sa.String(length=32), nullable=False, server_default="weekly"),
        sa.Column("recipients", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("widgets", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("layout", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("org_id", name="uq_digest_configs_org_id"),
    )
    op.create_index("ix_digest_configs_org_id", "digest_configs", ["org_id"])


def downgrade() -> None:
    op.drop_index("ix_digest_configs_org_id", table_name="digest_configs")
    op.drop_table("digest_configs")
