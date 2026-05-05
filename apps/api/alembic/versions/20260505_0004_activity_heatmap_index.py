"""add activity heatmap query index

Revision ID: 20260505_0004
Revises: 20260505_0003
Create Date: 2026-05-05
"""

from __future__ import annotations

from alembic import op


revision = "20260505_0004"
down_revision = "20260505_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_skill_usage_events_activity_heatmap",
        "skill_usage_events",
        ["org_id", "repo_id", "loaded_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_skill_usage_events_activity_heatmap", table_name="skill_usage_events")
