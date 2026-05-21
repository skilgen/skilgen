"""device authorizations for skillayer-agent connect

Revision ID: 20260520_0006
Revises: 20260520_0005
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0006"
down_revision = "20260520_0005"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("device_authorizations"):
        op.create_table(
            "device_authorizations",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("device_code", sa.String(length=128), nullable=False),
            sa.Column("user_code", sa.String(length=32), nullable=False),
            sa.Column("org_id", sa.String(), nullable=True),
            sa.Column("user_id", sa.String(length=128), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("api_key", sa.String(length=255), nullable=True),
            sa.Column("project_root", sa.String(length=1024), nullable=True),
            sa.Column("repo_id", sa.String(length=128), nullable=True),
            sa.Column("repo_full_name", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("last_polled_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["org_id"], ["orgs.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("device_code", name="uq_device_authorizations_device_code"),
            sa.UniqueConstraint("user_code", name="uq_device_authorizations_user_code"),
        )
    if not _has_index("device_authorizations", "ix_device_authorizations_device_code"):
        op.create_index("ix_device_authorizations_device_code", "device_authorizations", ["device_code"])
    if not _has_index("device_authorizations", "ix_device_authorizations_user_code"):
        op.create_index("ix_device_authorizations_user_code", "device_authorizations", ["user_code"])
    if not _has_index("device_authorizations", "ix_device_authorizations_org_id"):
        op.create_index("ix_device_authorizations_org_id", "device_authorizations", ["org_id"])


def downgrade() -> None:
    if _has_index("device_authorizations", "ix_device_authorizations_org_id"):
        op.drop_index("ix_device_authorizations_org_id", table_name="device_authorizations")
    if _has_index("device_authorizations", "ix_device_authorizations_user_code"):
        op.drop_index("ix_device_authorizations_user_code", table_name="device_authorizations")
    if _has_index("device_authorizations", "ix_device_authorizations_device_code"):
        op.drop_index("ix_device_authorizations_device_code", table_name="device_authorizations")
    if _has_table("device_authorizations"):
        op.drop_table("device_authorizations")
