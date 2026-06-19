"""add debt and dependency self service tables

Revision ID: 20260426_0007_debt_dependency
Revises: 20260426_0006_pr_review
Create Date: 2026-04-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260426_0007_debt_dependency"
down_revision = "20260426_0006_pr_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("repos", sa.Column("last_debt_analysis_at", sa.DateTime(), nullable=True))
    op.create_table(
        "coverage_gaps",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("domain", sa.String(length=80), nullable=False),
        sa.Column("gap_type", sa.String(length=32), nullable=False, server_default="missing"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("skill_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("org_id", "repo_id", "domain", "gap_type", name="uq_coverage_gaps_scope"),
    )
    op.create_index("ix_coverage_gaps_org_id", "coverage_gaps", ["org_id"])
    op.create_index("ix_coverage_gaps_repo_id", "coverage_gaps", ["repo_id"])
    op.create_index("ix_coverage_gaps_domain", "coverage_gaps", ["domain"])
    op.create_index("ix_coverage_gaps_status", "coverage_gaps", ["status"])
    op.create_table(
        "dependency_graph_cache",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=True),
        sa.Column("nodes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("edges_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("opportunities_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("computed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("org_id", "scope", "repo_id", name="uq_dependency_graph_cache_scope"),
    )
    op.create_index("ix_dependency_graph_cache_org_id", "dependency_graph_cache", ["org_id"])
    op.create_index("ix_dependency_graph_cache_scope", "dependency_graph_cache", ["scope"])
    op.create_index("ix_dependency_graph_cache_repo_id", "dependency_graph_cache", ["repo_id"])


def downgrade() -> None:
    op.drop_index("ix_dependency_graph_cache_repo_id", table_name="dependency_graph_cache")
    op.drop_index("ix_dependency_graph_cache_scope", table_name="dependency_graph_cache")
    op.drop_index("ix_dependency_graph_cache_org_id", table_name="dependency_graph_cache")
    op.drop_table("dependency_graph_cache")
    op.drop_index("ix_coverage_gaps_status", table_name="coverage_gaps")
    op.drop_index("ix_coverage_gaps_domain", table_name="coverage_gaps")
    op.drop_index("ix_coverage_gaps_repo_id", table_name="coverage_gaps")
    op.drop_index("ix_coverage_gaps_org_id", table_name="coverage_gaps")
    op.drop_table("coverage_gaps")
    op.drop_column("repos", "last_debt_analysis_at")
