"""add bidding packages table

Revision ID: a80ad079da2f
Revises: 42ab98de1d63
Create Date: 2025-12-15 12:39:12.541185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a80ad079da2f'
down_revision: Union[str, None] = '42ab98de1d63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "bidding_packages" not in inspector.get_table_names():
        op.create_table(
            "bidding_packages",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("work_package_id", sa.Integer(), sa.ForeignKey("work_packages.id"), nullable=False),
            sa.Column("technician_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("bidding_amount", sa.Float(), nullable=False),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        )


def downgrade():
     op.drop_table("bidding_packages")