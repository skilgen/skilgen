"""add_skill_source_taxonomy

Revision ID: f6a1d9c3b2e4
Revises: e2f4c6a8b9d0
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a1d9c3b2e4"
down_revision: Union[str, Sequence[str], None] = "e2f4c6a8b9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add source taxonomy fields to generated skills."""
    op.add_column("skills", sa.Column("source_type", sa.String(length=50), nullable=True, server_default="code"))
    op.add_column(
        "skills",
        sa.Column("skill_category", sa.String(length=50), nullable=True, server_default="codebase_architecture"),
    )
    op.create_index("ix_skills_source_type", "skills", ["source_type"])
    op.create_index("ix_skills_skill_category", "skills", ["skill_category"])
    op.alter_column("skills", "source_type", server_default=None)
    op.alter_column("skills", "skill_category", server_default=None)


def downgrade() -> None:
    """Remove source taxonomy fields from generated skills."""
    op.drop_index("ix_skills_skill_category", table_name="skills")
    op.drop_index("ix_skills_source_type", table_name="skills")
    op.drop_column("skills", "skill_category")
    op.drop_column("skills", "source_type")
