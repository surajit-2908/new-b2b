"""add organic fields into leads

Revision ID: 1e541c1d2064
Revises: f0038d7aa82d
Create Date: 2026-01-28 12:04:51.302558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e541c1d2064'
down_revision: Union[str, None] = 'f0038d7aa82d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add user_id (nullable)
    op.add_column(
        'leads',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )

    # 2. Add lead_type with default value
    op.add_column(
        'leads',
        sa.Column(
            'lead_type',
            sa.String(length=50),
            nullable=False,
            server_default='Scrapping Lead'
        )
    )

    # 3. (Optional but recommended) Remove server default after setting existing rows
    op.alter_column(
        'leads',
        'lead_type',
        server_default=None
    )


def downgrade() -> None:
    op.drop_column('leads', 'lead_type')
    op.drop_column('leads', 'user_id')
