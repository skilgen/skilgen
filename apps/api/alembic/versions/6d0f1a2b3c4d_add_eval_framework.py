"""add_eval_framework

Revision ID: 6d0f1a2b3c4d
Revises: 5a3c2f1d9e8b
Create Date: 2026-04-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "6d0f1a2b3c4d"
down_revision = "5a3c2f1d9e8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_tasks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("agent_runtime", sa.String(length=64), nullable=False),
        sa.Column("task_description", sa.Text(), nullable=True),
        sa.Column("task_type", sa.String(length=64), nullable=True),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("skills_loaded", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("skill_domains_loaded", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("skill_score_at_task", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_tasks_org_repo_started", "agent_tasks", ["org_id", "repo_id", "started_at"])
    op.create_index("ix_agent_tasks_org_outcome_started", "agent_tasks", ["org_id", "outcome", "started_at"])

    op.create_table(
        "eval_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("eval_type", sa.String(length=32), nullable=False),
        sa.Column("skill_version_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("agent_runtime", sa.String(length=64), nullable=False),
        sa.Column("task_count", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("partial_count", sa.Integer(), nullable=False),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("avg_token_count", sa.Float(), nullable=True),
        sa.Column("avg_duration_seconds", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_sessions_org_repo_created", "eval_sessions", ["org_id", "repo_id", "created_at"])

    op.create_table(
        "ab_tests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("control_version_id", sa.String(), nullable=False),
        sa.Column("treatment_version_id", sa.String(), nullable=False),
        sa.Column("control_session_id", sa.String(), nullable=True),
        sa.Column("treatment_session_id", sa.String(), nullable=True),
        sa.Column("winner", sa.String(length=32), nullable=True),
        sa.Column("control_success_rate", sa.Float(), nullable=True),
        sa.Column("treatment_success_rate", sa.Float(), nullable=True),
        sa.Column("improvement_pct", sa.Float(), nullable=True),
        sa.Column("confidence", sa.String(length=32), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["control_version_id"], ["skill_versions.id"]),
        sa.ForeignKeyConstraint(["treatment_version_id"], ["skill_versions.id"]),
        sa.ForeignKeyConstraint(["control_session_id"], ["eval_sessions.id"]),
        sa.ForeignKeyConstraint(["treatment_session_id"], ["eval_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ab_tests_org_status_created", "ab_tests", ["org_id", "status", "created_at"])

    op.create_table(
        "skill_gaps",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("task_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("existing_skill_id", sa.String(), nullable=True),
        sa.Column("existing_skill_score", sa.Float(), nullable=True),
        sa.Column("gap_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["existing_skill_id"], ["skills.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skill_gaps_org_repo_status", "skill_gaps", ["org_id", "repo_id", "status"])
    op.create_index("ix_skill_gaps_org_domain_status", "skill_gaps", ["org_id", "domain", "status"])


def downgrade() -> None:
    op.drop_index("ix_skill_gaps_org_domain_status", table_name="skill_gaps")
    op.drop_index("ix_skill_gaps_org_repo_status", table_name="skill_gaps")
    op.drop_table("skill_gaps")
    op.drop_index("ix_ab_tests_org_status_created", table_name="ab_tests")
    op.drop_table("ab_tests")
    op.drop_index("ix_eval_sessions_org_repo_created", table_name="eval_sessions")
    op.drop_table("eval_sessions")
    op.drop_index("ix_agent_tasks_org_outcome_started", table_name="agent_tasks")
    op.drop_index("ix_agent_tasks_org_repo_started", table_name="agent_tasks")
    op.drop_table("agent_tasks")
