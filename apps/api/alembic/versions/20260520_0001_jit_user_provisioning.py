"""jit org/user provisioning primitives

Revision ID: 20260520_0001
Revises: 20260519_0001
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0001"
down_revision = "20260519_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if not _has_column("orgs", "auto_join_domain"):
        op.add_column("orgs", sa.Column("auto_join_domain", sa.Boolean(), nullable=False, server_default=sa.text("true")))

    if not _has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=True),
            sa.Column("role", sa.String(length=32), nullable=False, server_default="developer"),
            sa.Column("source", sa.String(length=32), nullable=False, server_default="workos"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("org_id", "email", name="uq_users_org_email"),
        )

    if not _has_index("users", "ix_users_org_id"):
        op.create_index("ix_users_org_id", "users", ["org_id"])
    if not _has_index("users", "ix_users_email"):
        op.create_index("ix_users_email", "users", ["email"])


def downgrade() -> None:
    if _has_index("users", "ix_users_email"):
        op.drop_index("ix_users_email", table_name="users")
    if _has_index("users", "ix_users_org_id"):
        op.drop_index("ix_users_org_id", table_name="users")
    if _has_table("users"):
        op.drop_table("users")
    if _has_column("orgs", "auto_join_domain"):
        op.drop_column("orgs", "auto_join_domain")

