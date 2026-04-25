"""add_org_api_key

Revision ID: 5a3c2f1d9e8b
Revises: 4b8a21f0c3d9
Create Date: 2026-04-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "5a3c2f1d9e8b"
down_revision = "4b8a21f0c3d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orgs", sa.Column("api_key", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_orgs_api_key", "orgs", ["api_key"])


def downgrade() -> None:
    op.drop_constraint("uq_orgs_api_key", "orgs", type_="unique")
    op.drop_column("orgs", "api_key")
