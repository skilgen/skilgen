"""add pr comments

Revision ID: 20260428_0004
Revises: 20260428_0003
Create Date: 2026-04-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260428_0004"
down_revision = "20260428_0003"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_table("pr_comments"):
        op.create_table(
            "pr_comments",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("pr_id", sa.String(), nullable=False),
            sa.Column("github_comment_id", sa.Integer(), nullable=True),
            sa.Column("violation_hash", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["pr_id"], ["pull_requests.id"], ondelete="CASCADE"),
        )
    else:
        if not _has_column("pr_comments", "github_comment_id"):
            op.add_column("pr_comments", sa.Column("github_comment_id", sa.Integer(), nullable=True))
        if not _has_column("pr_comments", "violation_hash"):
            op.add_column("pr_comments", sa.Column("violation_hash", sa.String(length=64), nullable=False, server_default=""))
        if not _has_column("pr_comments", "created_at"):
            op.add_column("pr_comments", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
        if not _has_column("pr_comments", "updated_at"):
            op.add_column("pr_comments", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))

    bind = op.get_bind()
    existing_indexes = {index["name"] for index in sa.inspect(bind).get_indexes("pr_comments")}
    if "ix_pr_comments_pr_violation_hash" not in existing_indexes:
        op.create_index("ix_pr_comments_pr_violation_hash", "pr_comments", ["pr_id", "violation_hash"], unique=True)
    if "ix_pr_comments_github_comment_id" not in existing_indexes:
        op.create_index("ix_pr_comments_github_comment_id", "pr_comments", ["github_comment_id"])


def downgrade() -> None:
    if _has_table("pr_comments"):
        existing_indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("pr_comments")}
        if "ix_pr_comments_github_comment_id" in existing_indexes:
            op.drop_index("ix_pr_comments_github_comment_id", table_name="pr_comments")
        if "ix_pr_comments_pr_violation_hash" in existing_indexes:
            op.drop_index("ix_pr_comments_pr_violation_hash", table_name="pr_comments")
        op.drop_table("pr_comments")
