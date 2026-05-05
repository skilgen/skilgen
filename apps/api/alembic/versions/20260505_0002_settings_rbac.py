"""add settings rbac roles and bindings

Revision ID: 20260505_0002
Revises: 20260505_0001
Create Date: 2026-05-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260505_0002"
down_revision = "20260505_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("roles"):
        op.create_table(
            "roles",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("description", sa.String(length=512), nullable=True),
            sa.Column("permissions", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("org_id", "name", name="uq_roles_org_name"),
        )
    if not _has_index("roles", "ix_roles_org_id"):
        op.create_index("ix_roles_org_id", "roles", ["org_id"])

    if not _has_table("role_bindings"):
        op.create_table(
            "role_bindings",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("role_id", sa.String(), nullable=False),
            sa.Column("principal_type", sa.String(length=32), nullable=False),
            sa.Column("principal_id", sa.String(length=255), nullable=False),
            sa.Column("scope_expression", sa.JSON(), nullable=True, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("role_bindings", "ix_role_bindings_org_principal"):
        op.create_index("ix_role_bindings_org_principal", "role_bindings", ["org_id", "principal_type", "principal_id"])
    if not _has_index("role_bindings", "ix_role_bindings_role_id"):
        op.create_index("ix_role_bindings_role_id", "role_bindings", ["role_id"])


def downgrade() -> None:
    if _has_index("role_bindings", "ix_role_bindings_role_id"):
        op.drop_index("ix_role_bindings_role_id", table_name="role_bindings")
    if _has_index("role_bindings", "ix_role_bindings_org_principal"):
        op.drop_index("ix_role_bindings_org_principal", table_name="role_bindings")
    if _has_table("role_bindings"):
        op.drop_table("role_bindings")
    if _has_index("roles", "ix_roles_org_id"):
        op.drop_index("ix_roles_org_id", table_name="roles")
    if _has_table("roles"):
        op.drop_table("roles")
