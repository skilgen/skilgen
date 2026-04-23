"""add_registry_skills

Revision ID: d4f9a71c2e8b
Revises: a4c2e3f91b65
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4f9a71c2e8b"
down_revision: Union[str, Sequence[str], None] = "a4c2e3f91b65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the public skill registry table and indexes."""
    op.create_table(
        "registry_skills",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("is_official", sa.Boolean(), nullable=False),
        sa.Column("import_count", sa.Integer(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_registry_skills_import_count", "registry_skills", ["import_count"], unique=False)
    op.create_index("ix_registry_skills_is_public", "registry_skills", ["is_public"], unique=False)
    op.create_index("ix_registry_skills_org_id", "registry_skills", ["org_id"], unique=False)
    op.create_index("ix_registry_skills_repo_id", "registry_skills", ["repo_id"], unique=False)
    op.create_index("ix_registry_skills_skill_id", "registry_skills", ["skill_id"], unique=False)


def downgrade() -> None:
    """Remove the public skill registry table and indexes."""
    op.drop_index("ix_registry_skills_skill_id", table_name="registry_skills")
    op.drop_index("ix_registry_skills_repo_id", table_name="registry_skills")
    op.drop_index("ix_registry_skills_org_id", table_name="registry_skills")
    op.drop_index("ix_registry_skills_is_public", table_name="registry_skills")
    op.drop_index("ix_registry_skills_import_count", table_name="registry_skills")
    op.drop_table("registry_skills")
