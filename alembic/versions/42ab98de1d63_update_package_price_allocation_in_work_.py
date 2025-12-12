"""update package_price_allocation in work_packages

Revision ID: 42ab98de1d63
Revises: 4299291792d5
Create Date: 2025-12-12 13:32:58.349510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42ab98de1d63'
down_revision: Union[str, None] = '4299291792d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "work_packages",
        "package_price_allocation",
        existing_type=sa.Numeric(),
        type_=sa.Float(),
        existing_nullable=True
    )


def downgrade():
    op.alter_column(
        "work_packages",
        "package_price_allocation",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=True
    )
