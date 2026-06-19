"""add_agent_sessions_and_memory_stubs

Revision ID: 8e14c9a5d2b1
Revises: f1b2c3d4e5f6
Create Date: 2026-04-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8e14c9a5d2b1"
down_revision: Union[str, Sequence[str], None] = "f1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(length=128), nullable=False),
        sa.Column("agent_runtime", sa.String(length=64), nullable=False),
        sa.Column("task_description", sa.Text(), nullable=True),
        sa.Column("engineer_login", sa.String(length=128), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("files_touched", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("skill_paths_loaded", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("transcript_summary", sa.Text(), nullable=True),
        sa.Column("raw_message_count", sa.Integer(), nullable=True),
        sa.Column("extraction_status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("discoveries_found", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repo_id", "session_id", name="uq_agent_sessions_repo_session"),
    )
    op.create_index("ix_agent_sessions_org_created_at", "agent_sessions", ["org_id", "created_at"])
    op.create_index("ix_agent_sessions_repo_created_at", "agent_sessions", ["repo_id", "created_at"])

    op.create_table(
        "skill_memory_stubs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("domain", sa.String(length=256), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=True),
        sa.Column("discovery_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("proposed_content", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), server_default="0.8", nullable=False),
        sa.Column("agent_runtime", sa.String(length=64), nullable=False),
        sa.Column("engineer_login", sa.String(length=128), nullable=True),
        sa.Column("task_description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("merged_version_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["agent_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skill_memory_stubs_org_status_created_at", "skill_memory_stubs", ["org_id", "status", "created_at"])
    op.create_index("ix_skill_memory_stubs_repo_created_at", "skill_memory_stubs", ["repo_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_skill_memory_stubs_repo_created_at", table_name="skill_memory_stubs")
    op.drop_index("ix_skill_memory_stubs_org_status_created_at", table_name="skill_memory_stubs")
    op.drop_table("skill_memory_stubs")
    op.drop_index("ix_agent_sessions_repo_created_at", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_org_created_at", table_name="agent_sessions")
    op.drop_table("agent_sessions")
