"""add autopilot improvement queue fields

Revision ID: 20260426_0005_autopilot
Revises: 20260426_0004_digest
Create Date: 2026-04-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260426_0005_autopilot"
down_revision = "20260426_0004_digest"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("autopilot_tasks", sa.Column("improvement_status", sa.String(length=32), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("original_content", sa.Text(), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("generated_content", sa.Text(), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("final_content", sa.Text(), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("generation_error", sa.Text(), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("pr_url", sa.String(length=2048), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("pr_number", sa.Integer(), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("generated_at", sa.DateTime(), nullable=True))
    op.add_column("autopilot_tasks", sa.Column("reviewed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("autopilot_tasks", "reviewed_at")
    op.drop_column("autopilot_tasks", "generated_at")
    op.drop_column("autopilot_tasks", "pr_number")
    op.drop_column("autopilot_tasks", "pr_url")
    op.drop_column("autopilot_tasks", "generation_error")
    op.drop_column("autopilot_tasks", "final_content")
    op.drop_column("autopilot_tasks", "generated_content")
    op.drop_column("autopilot_tasks", "original_content")
    op.drop_column("autopilot_tasks", "improvement_status")
