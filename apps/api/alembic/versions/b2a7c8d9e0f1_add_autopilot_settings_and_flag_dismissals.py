"""add_autopilot_settings_and_flag_dismissals

Revision ID: b2a7c8d9e0f1
Revises: f1b2c3d4e5f6
Create Date: 2026-04-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b2a7c8d9e0f1"
down_revision: Union[str, Sequence[str], None] = "7e9b2c4d6a8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    org_columns = {column["name"] for column in inspector.get_columns("orgs")}
    if "settings" not in org_columns:
        op.add_column("orgs", sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    if "autopilot_tasks" not in inspector.get_table_names():
        op.create_table(
            "autopilot_tasks",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("repo_id", sa.String(), nullable=False),
            sa.Column("skill_id", sa.String(), nullable=True),
            sa.Column("task_type", sa.String(length=32), nullable=False),
            sa.Column("trigger_reason", sa.String(length=512), nullable=False),
            sa.Column("freshness_at_trigger", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
            sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("org_id", "repo_id", "skill_id", "task_type", "status", name="uq_autopilot_pending_task"),
        )
        op.create_index("ix_autopilot_tasks_org_status_created_at", "autopilot_tasks", ["org_id", "status", "created_at"])

    if "flag_dismissals" not in inspector.get_table_names():
        op.create_table(
            "flag_dismissals",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("flag_type", sa.String(length=100), nullable=False),
            sa.Column("repo_id", sa.String(), nullable=False),
            sa.Column("skill_id", sa.String(), nullable=True),
            sa.Column("dismissed_by", sa.String(length=255), nullable=False),
            sa.Column("reason", sa.String(length=255), nullable=False),
            sa.Column("dismissed_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
            sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("org_id", "flag_type", "repo_id", "skill_id", name="uq_flag_dismissals_scope"),
        )
        op.create_index("ix_flag_dismissals_org_dismissed_at", "flag_dismissals", ["org_id", "dismissed_at"])

    if "sla_policies" not in inspector.get_table_names():
        op.create_table(
            "sla_policies",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("repo_id", sa.String(), nullable=True),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("coverage_target_pct", sa.Integer(), nullable=False),
            sa.Column("alert_email", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("last_checked_at", sa.DateTime(), nullable=True),
            sa.Column("last_status", sa.String(length=32), nullable=False),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_sla_policies_org_active", "sla_policies", ["org_id", "is_active"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "sla_policies" in inspector.get_table_names():
        op.drop_index("ix_sla_policies_org_active", table_name="sla_policies")
        op.drop_table("sla_policies")
    if "flag_dismissals" in inspector.get_table_names():
        op.drop_index("ix_flag_dismissals_org_dismissed_at", table_name="flag_dismissals")
        op.drop_table("flag_dismissals")
    if "autopilot_tasks" in inspector.get_table_names():
        op.drop_index("ix_autopilot_tasks_org_status_created_at", table_name="autopilot_tasks")
        op.drop_table("autopilot_tasks")
    org_columns = {column["name"] for column in inspector.get_columns("orgs")}
    if "settings" in org_columns:
        op.drop_column("orgs", "settings")
