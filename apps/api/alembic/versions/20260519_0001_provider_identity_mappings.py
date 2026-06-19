"""add provider identity mappings

Revision ID: 20260519_0001
Revises: 20260505_0006
Create Date: 2026-05-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260519_0001"
down_revision = "20260505_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "provider_identity_mappings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column("canonical_user_id", sa.String(length=255), nullable=False),
        sa.Column("canonical_email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("github_login", sa.String(length=128), nullable=True),
        sa.Column("sso_subject", sa.String(length=255), nullable=True),
        sa.Column("provider_user_id", sa.String(length=255), nullable=True),
        sa.Column("provider_actor_login", sa.String(length=255), nullable=True),
        sa.Column("local_identity", sa.String(length=255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1"),
        sa.Column("match_method", sa.String(length=64), nullable=False, server_default="admin"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="mapped"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("org_id", "provider", "provider_user_id", name="uq_provider_identity_user_id"),
    )
    op.create_index("ix_provider_identity_mappings_org_provider", "provider_identity_mappings", ["org_id", "provider"])
    op.create_index("ix_provider_identity_mappings_org_email", "provider_identity_mappings", ["org_id", "canonical_email"])


def downgrade() -> None:
    op.drop_index("ix_provider_identity_mappings_org_email", table_name="provider_identity_mappings")
    op.drop_index("ix_provider_identity_mappings_org_provider", table_name="provider_identity_mappings")
    op.drop_table("provider_identity_mappings")
