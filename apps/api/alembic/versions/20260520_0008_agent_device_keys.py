"""agent device keys and revocation metadata

Revision ID: 20260520_0008
Revises: 20260520_0007
Create Date: 2026-05-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0008"
down_revision = "20260520_0007"
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
    if not _has_table("device_authorizations"):
        return
    for column in (
        sa.Column("machine_id", sa.String(length=128), nullable=True),
        sa.Column("machine_label", sa.String(length=255), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
    ):
        if not _has_column("device_authorizations", column.name):
            op.add_column("device_authorizations", column)
    if not _has_index("device_authorizations", "ix_device_authorizations_machine_id"):
        op.create_index("ix_device_authorizations_machine_id", "device_authorizations", ["machine_id"])


def downgrade() -> None:
    if _has_index("device_authorizations", "ix_device_authorizations_machine_id"):
        op.drop_index("ix_device_authorizations_machine_id", table_name="device_authorizations")
    for column_name in ("revoked_at", "machine_label", "machine_id"):
        if _has_column("device_authorizations", column_name):
            op.drop_column("device_authorizations", column_name)
