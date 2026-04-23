"""add_skill_usage_events

Revision ID: c6e5c580a6a1
Revises: b7d4a6f2c9e1
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c6e5c580a6a1"
down_revision: Union[str, Sequence[str], None] = "b7d4a6f2c9e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create immutable skill usage events for analytics."""
    op.create_table(
        "skill_usage_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("agent_runtime", sa.String(length=100), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("loaded_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skill_usage_events_org_loaded_at", "skill_usage_events", ["org_id", "loaded_at"])
    op.create_index("ix_skill_usage_events_repo_loaded_at", "skill_usage_events", ["repo_id", "loaded_at"])
    op.create_index("ix_skill_usage_events_skill_loaded_at", "skill_usage_events", ["skill_id", "loaded_at"])


def downgrade() -> None:
    """Drop skill usage events and indexes."""
    op.drop_index("ix_skill_usage_events_skill_loaded_at", table_name="skill_usage_events")
    op.drop_index("ix_skill_usage_events_repo_loaded_at", table_name="skill_usage_events")
    op.drop_index("ix_skill_usage_events_org_loaded_at", table_name="skill_usage_events")
    op.drop_table("skill_usage_events")
