"""initial_schema

Revision ID: 20260420_0001
Revises:
Create Date: 2026-04-20 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260420_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "orgs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("github_org_id", sa.BigInteger(), nullable=False),
        sa.Column("login", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=50), nullable=False),
        sa.Column("seat_count", sa.Integer(), nullable=False),
        sa.Column("workos_org_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_org_id"),
        sa.UniqueConstraint("login"),
    )
    op.create_table(
        "repos",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("github_repo_id", sa.BigInteger(), nullable=False),
        sa.Column("github_installation_id", sa.BigInteger(), nullable=True),
        sa.Column("full_name", sa.String(length=512), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("default_branch", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=255), nullable=True),
        sa.Column("is_monorepo", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_analysed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("full_name"),
        sa.UniqueConstraint("github_repo_id"),
    )
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("trigger", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("commit_sha", sa.String(length=255), nullable=True),
        sa.Column("branch", sa.String(length=255), nullable=True),
        sa.Column("score_total", sa.Integer(), nullable=True),
        sa.Column("score_groundedness", sa.Integer(), nullable=True),
        sa.Column("score_coverage", sa.Integer(), nullable=True),
        sa.Column("score_freshness", sa.Integer(), nullable=True),
        sa.Column("score_structure", sa.Integer(), nullable=True),
        sa.Column("domain_count", sa.Integer(), nullable=True),
        sa.Column("skill_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "score_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("score_total", sa.Integer(), nullable=False),
        sa.Column("score_groundedness", sa.Integer(), nullable=False),
        sa.Column("score_coverage", sa.Integer(), nullable=False),
        sa.Column("score_freshness", sa.Integer(), nullable=False),
        sa.Column("score_structure", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["analysis_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "skills",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("skill_path", sa.String(length=512), nullable=False),
        sa.Column("score_total", sa.Integer(), nullable=False),
        sa.Column("score_groundedness", sa.Integer(), nullable=False),
        sa.Column("score_coverage", sa.Integer(), nullable=False),
        sa.Column("score_freshness", sa.Integer(), nullable=False),
        sa.Column("score_structure", sa.Integer(), nullable=False),
        sa.Column("is_stale", sa.Boolean(), nullable=False),
        sa.Column("load_count_30d", sa.Integer(), nullable=False),
        sa.Column("last_loaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["analysis_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_runs_repo_created", "analysis_runs", ["repo_id", "created_at"])
    op.create_index("ix_score_history_repo_recorded", "score_history", ["repo_id", "recorded_at"])
    op.create_index("ix_skills_repo_score", "skills", ["repo_id", "score_total"])


def downgrade() -> None:
    op.drop_index("ix_skills_repo_score", table_name="skills")
    op.drop_index("ix_score_history_repo_recorded", table_name="score_history")
    op.drop_index("ix_analysis_runs_repo_created", table_name="analysis_runs")
    op.drop_table("skills")
    op.drop_table("score_history")
    op.drop_table("analysis_runs")
    op.drop_table("repos")
    op.drop_table("orgs")
