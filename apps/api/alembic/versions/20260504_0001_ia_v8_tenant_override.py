"""document IA_V8 tenant override carrier

Revision ID: 20260504_0001
Revises: 20260430_0007
Create Date: 2026-05-04
"""

from __future__ import annotations


revision = "20260504_0001"
down_revision = "20260430_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """orgs.settings already provides the JSON carrier.

    PR-1 standardizes orgs.settings.feature_flags.IA_V8 as the tenant
    override path. No schema change is required because orgs.settings
    already exists as a nullable JSON column.
    """


def downgrade() -> None:
    """No schema change was made in upgrade."""
