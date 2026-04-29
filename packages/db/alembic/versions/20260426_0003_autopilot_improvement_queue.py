"""autopilot_improvement_queue

Revision ID: 20260426_0003
Revises: 20260426_0002
Create Date: 2026-04-26 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260426_0003"
down_revision: str | None = "20260426_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "autopilot_tasks" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("autopilot_tasks")}
    additions = [
        ("improvement_status", sa.Column("improvement_status", sa.String(length=32), nullable=True)),
        ("original_content", sa.Column("original_content", sa.Text(), nullable=True)),
        ("generated_content", sa.Column("generated_content", sa.Text(), nullable=True)),
        ("final_content", sa.Column("final_content", sa.Text(), nullable=True)),
        ("generation_error", sa.Column("generation_error", sa.Text(), nullable=True)),
        ("pr_url", sa.Column("pr_url", sa.String(length=2048), nullable=True)),
        ("pr_number", sa.Column("pr_number", sa.Integer(), nullable=True)),
        ("generated_at", sa.Column("generated_at", sa.DateTime(), nullable=True)),
        ("reviewed_at", sa.Column("reviewed_at", sa.DateTime(), nullable=True)),
    ]
    for name, column in additions:
        if name not in columns:
            op.add_column("autopilot_tasks", column)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "autopilot_tasks" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("autopilot_tasks")}
    for name in [
        "reviewed_at",
        "generated_at",
        "pr_number",
        "pr_url",
        "generation_error",
        "final_content",
        "generated_content",
        "original_content",
        "improvement_status",
    ]:
        if name in columns:
            op.drop_column("autopilot_tasks", name)
