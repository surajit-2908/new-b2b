"""add work packages table

Revision ID: 1dfb9b2a77c3
Revises: d3c1d515b027
Create Date: 2025-12-01 13:28:54.171976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "1dfb9b2a77c3"
down_revision: Union[str, None] = "d3c1d515b027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "work_packages" not in inspector.get_table_names():
        op.create_table(
            "work_packages",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("deals.id"), nullable=False),
            sa.Column("package_title", sa.Text(), nullable=False),
            sa.Column("package_type", sa.String(150), nullable=False),
            sa.Column("package_summary", sa.Text(), nullable=False),
            sa.Column("key_deliverables", sa.Text(), nullable=False),
            sa.Column("acceptance_criteria", sa.Text(), nullable=False),
            sa.Column("required_skills", sa.Text(), nullable=False),
            sa.Column("primary_tools", sa.Text(), nullable=False),
            sa.Column("package_estimated_complexity", sa.Text(), nullable=False),
            sa.Column("package_price_allocation", sa.Numeric(), nullable=True),
            sa.Column("dependencies", sa.Text(), nullable=False),
            sa.Column("status", sa.String(100), nullable=True),  # draft / active
            sa.Column("draft_version", sa.Integer(), nullable=True),
            sa.Column("last_saved_at", sa.DateTime(), server_default=sa.func.now(),nullable=True),
        )


def downgrade():
    op.drop_table("deals")
