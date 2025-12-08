"""update work packages table

Revision ID: 5fb6dc1ae1dc
Revises: 468a895f9a56
Create Date: 2025-12-08 12:05:08.038714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '5fb6dc1ae1dc'
down_revision: Union[str, None] = '468a895f9a56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Drop if exists
    if "work_packages" in inspector.get_table_names():
        op.drop_table("work_packages")

    # Recreate table
    op.create_table(
        "work_packages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("deal_id", sa.Integer(), sa.ForeignKey("deals.id"), nullable=False),
        sa.Column("package_type_id", sa.Integer(), sa.ForeignKey("package_types.id"), nullable=False),

        sa.Column("package_title", sa.Text(), nullable=False),
        sa.Column("package_summary", sa.Text(), nullable=False),

        sa.Column("key_deliverables", sa.Text(), nullable=False),
        sa.Column("acceptance_criteria", sa.Text(), nullable=False),
        sa.Column("required_skills_ids", sa.JSON(), nullable=False),
        sa.Column("primary_tools_ids", sa.JSON(), nullable=False),

        sa.Column("package_estimated_complexity", sa.Text(), nullable=False),

        sa.Column("package_price_allocation", sa.Numeric(), nullable=True),

        sa.Column("dependencies", sa.Text(), nullable=False),

        sa.Column("status", sa.String(100), nullable=True),
        sa.Column("draft_version", sa.Integer(), nullable=True),

        sa.Column("last_saved_at", sa.DateTime(),
                  server_default=sa.func.now(), nullable=True),
    )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "work_packages" in inspector.get_table_names():
        op.drop_table("work_packages")