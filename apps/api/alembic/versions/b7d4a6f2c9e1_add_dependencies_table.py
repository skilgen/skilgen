"""add_dependencies_table

Revision ID: b7d4a6f2c9e1
Revises: a4c2e3f91b65
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7d4a6f2c9e1"
down_revision: Union[str, Sequence[str], None] = "a4c2e3f91b65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create dependency risk findings table."""
    op.create_table(
        "dependencies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=255), nullable=True),
        sa.Column("ecosystem", sa.String(length=50), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("cves", sa.JSON(), nullable=False),
        sa.Column("latest_version", sa.String(length=255), nullable=True),
        sa.Column("license", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["analysis_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dependencies_repo_id", "dependencies", ["repo_id"], unique=False)
    op.create_index("ix_dependencies_run_id", "dependencies", ["run_id"], unique=False)
    op.create_index("ix_dependencies_risk_level", "dependencies", ["risk_level"], unique=False)


def downgrade() -> None:
    """Drop dependency risk findings table."""
    op.drop_index("ix_dependencies_risk_level", table_name="dependencies")
    op.drop_index("ix_dependencies_run_id", table_name="dependencies")
    op.drop_index("ix_dependencies_repo_id", table_name="dependencies")
    op.drop_table("dependencies")
