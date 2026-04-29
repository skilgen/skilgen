"""add pr review history

Revision ID: 20260426_0006_pr_review
Revises: 20260426_0005_autopilot
Create Date: 2026-04-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260426_0006_pr_review"
down_revision = "20260426_0005_autopilot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "pr_reviews" not in tables:
        op.create_table(
            "pr_reviews",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("repo_id", sa.String(), nullable=False),
            sa.Column("pr_url", sa.String(length=2048), nullable=True),
            sa.Column("pr_number", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="complete"),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("model_used", sa.String(length=128), nullable=True),
            sa.Column("findings_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("skills_checked", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("lines_scanned", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_pr_reviews_org_created_at", "pr_reviews", ["org_id", "created_at"])
        op.create_index("ix_pr_reviews_repo_created_at", "pr_reviews", ["repo_id", "created_at"])

    if "pr_review_findings" not in tables:
        op.create_table(
            "pr_review_findings",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("review_id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("repo_id", sa.String(), nullable=False),
            sa.Column("skill_id", sa.String(), nullable=True),
            sa.Column("file_path", sa.String(length=1024), nullable=False),
            sa.Column("line_number", sa.Integer(), nullable=True),
            sa.Column("severity", sa.String(length=32), nullable=False, server_default="warning"),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("rule_id", sa.String(length=128), nullable=True),
            sa.Column("suggestion", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["review_id"], ["pr_reviews.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="SET NULL"),
        )
        op.create_index("ix_pr_review_findings_review_id", "pr_review_findings", ["review_id"])
        op.create_index("ix_pr_review_findings_org_created_at", "pr_review_findings", ["org_id", "created_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "pr_review_findings" in tables:
        op.drop_index("ix_pr_review_findings_org_created_at", table_name="pr_review_findings")
        op.drop_index("ix_pr_review_findings_review_id", table_name="pr_review_findings")
        op.drop_table("pr_review_findings")
    if "pr_reviews" in tables:
        op.drop_index("ix_pr_reviews_repo_created_at", table_name="pr_reviews")
        op.drop_index("ix_pr_reviews_org_created_at", table_name="pr_reviews")
        op.drop_table("pr_reviews")
