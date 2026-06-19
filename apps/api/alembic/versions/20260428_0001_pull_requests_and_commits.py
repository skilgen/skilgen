"""add pull requests and commits

Revision ID: 20260428_0001
Revises: 20260427_0001
Create Date: 2026-04-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260428_0001"
down_revision = "20260427_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    json_type = postgresql.JSONB(astext_type=sa.Text()) if bind.dialect.name == "postgresql" else sa.JSON()
    empty_object_default = sa.text("'{}'::jsonb") if bind.dialect.name == "postgresql" else sa.text("'{}'")

    if "pull_requests" not in tables:
        op.create_table(
            "pull_requests",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("repo_id", sa.String(), nullable=False),
            sa.Column("github_pr_number", sa.Integer(), nullable=False),
            sa.Column("author_login", sa.Text(), nullable=True),
            sa.Column("author_type", sa.String(length=16), nullable=True),
            sa.Column("head_sha", sa.Text(), nullable=True),
            sa.Column("base_sha", sa.Text(), nullable=True),
            sa.Column("title", sa.Text(), nullable=True),
            sa.Column("body", sa.Text(), nullable=True),
            sa.Column("state", sa.String(length=16), nullable=True),
            sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("additions", sa.Integer(), nullable=True),
            sa.Column("deletions", sa.Integer(), nullable=True),
            sa.Column("changed_files", sa.Integer(), nullable=True),
            sa.Column("raw", json_type, nullable=False, server_default=empty_object_default),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
            sa.CheckConstraint("author_type IN ('User', 'Bot', 'App')", name="ck_pull_requests_author_type"),
            sa.CheckConstraint("state IN ('open', 'closed', 'merged')", name="ck_pull_requests_state"),
        )
        op.create_index(
            "ix_pull_requests_repo_pr_number",
            "pull_requests",
            ["repo_id", "github_pr_number"],
            unique=True,
        )
        if bind.dialect.name == "postgresql":
            op.execute("CREATE INDEX ix_pull_requests_repo_state_opened ON pull_requests (repo_id, state, opened_at DESC)")
        else:
            op.create_index("ix_pull_requests_repo_state_opened", "pull_requests", ["repo_id", "state", "opened_at"])

    if "commits" not in tables:
        op.create_table(
            "commits",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("repo_id", sa.String(), nullable=False),
            sa.Column("sha", sa.Text(), nullable=False),
            sa.Column("author_login", sa.Text(), nullable=True),
            sa.Column("author_email", sa.Text(), nullable=True),
            sa.Column("committer_login", sa.Text(), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("authored_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("additions", sa.Integer(), nullable=True),
            sa.Column("deletions", sa.Integer(), nullable=True),
            sa.Column("pr_id", sa.String(), nullable=True),
            sa.Column("raw", json_type, nullable=False, server_default=empty_object_default),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["repo_id"], ["repos.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["pr_id"], ["pull_requests.id"], ondelete="SET NULL"),
        )
        op.create_index("ix_commits_repo_sha", "commits", ["repo_id", "sha"], unique=True)
        if bind.dialect.name == "postgresql":
            op.execute("CREATE INDEX ix_commits_repo_authored_at ON commits (repo_id, authored_at DESC)")
        else:
            op.create_index("ix_commits_repo_authored_at", "commits", ["repo_id", "authored_at"])
        op.create_index("ix_commits_pr_id", "commits", ["pr_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "commits" in tables:
        op.drop_index("ix_commits_pr_id", table_name="commits")
        op.drop_index("ix_commits_repo_authored_at", table_name="commits")
        op.drop_index("ix_commits_repo_sha", table_name="commits")
        op.drop_table("commits")

    if "pull_requests" in tables:
        op.drop_index("ix_pull_requests_repo_state_opened", table_name="pull_requests")
        op.drop_index("ix_pull_requests_repo_pr_number", table_name="pull_requests")
        op.drop_table("pull_requests")
