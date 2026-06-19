"""add_review_sessions_and_antipatterns

Revision ID: 7e9b2c4d6a8f
Revises: 6d0f1a2b3c4d
Create Date: 2026-04-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "7e9b2c4d6a8f"
down_revision = "6d0f1a2b3c4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("anti_patterns", sa.JSON(), nullable=True))
    op.add_column("agent_sessions", sa.Column("session_start", sa.DateTime(), server_default=sa.text("now()"), nullable=False))
    op.add_column("agent_sessions", sa.Column("session_end", sa.DateTime(), nullable=True))
    op.add_column("agent_sessions", sa.Column("skills_loaded", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False))
    op.add_column("agent_sessions", sa.Column("code_produced", sa.Text(), nullable=True))
    op.add_column("agent_sessions", sa.Column("outcome", sa.String(length=32), nullable=True))
    op.add_column("agent_sessions", sa.Column("notes", sa.Text(), nullable=True))
    op.create_table(
        "review_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("pr_url", sa.String(length=2048), nullable=True),
        sa.Column("comment_count", sa.Integer(), nullable=False),
        sa.Column("skills_checked", sa.Integer(), nullable=False),
        sa.Column("lines_scanned", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("review_runs")
    op.drop_column("agent_sessions", "notes")
    op.drop_column("agent_sessions", "outcome")
    op.drop_column("agent_sessions", "code_produced")
    op.drop_column("agent_sessions", "skills_loaded")
    op.drop_column("agent_sessions", "session_end")
    op.drop_column("agent_sessions", "session_start")
    op.drop_column("skills", "anti_patterns")
