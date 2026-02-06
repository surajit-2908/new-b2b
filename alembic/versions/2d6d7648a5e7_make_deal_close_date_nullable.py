"""make deal_close_date nullable

Revision ID: 2d6d7648a5e7
Revises: 1e541c1d2064
Create Date: 2026-02-06 13:14:39.439412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d6d7648a5e7'
down_revision: Union[str, None] = '1e541c1d2064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'deals',
        'deal_close_date',
        existing_type=sa.DateTime(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        'deals',
        'deal_close_date',
        existing_type=sa.DateTime(),
        nullable=False,
    )
