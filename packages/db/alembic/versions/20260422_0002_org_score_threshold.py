"""add_org_score_threshold

Revision ID: 20260422_0002
Revises: 20260420_0001
Create Date: 2026-04-22 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260422_0002"
down_revision: str | None = "20260420_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orgs", sa.Column("score_threshold", sa.Integer(), nullable=False, server_default="70"))
    op.alter_column("orgs", "score_threshold", server_default=None)


def downgrade() -> None:
    op.drop_column("orgs", "score_threshold")
