"""add agent jobs half life opportunities

Revision ID: 20260426_0003
Revises: c8d2e4f6a0b1
Create Date: 2026-04-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260426_0003"
down_revision = "c8d2e4f6a0b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_load_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("agent_runtime", sa.String(length=100), nullable=False),
        sa.Column("detected_runtime", sa.String(length=100), nullable=True),
        sa.Column("skill_path", sa.String(length=512), nullable=False),
        sa.Column("loaded_at", sa.DateTime(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=True),
    )
    op.create_table(
        "cross_repo_opportunities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("source_skill_id", sa.String(), nullable=False),
        sa.Column("target_repo_id", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
    )
    op.create_table(
        "half_life_cache",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("commit_velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("predicted_half_life_days", sa.Float(), nullable=False, server_default="90"),
        sa.Column("computed_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("half_life_cache")
    op.drop_table("cross_repo_opportunities")
    op.drop_table("agent_load_events")
