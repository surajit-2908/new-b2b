"""add sector_package_id and custom_sector_package to deals

Revision ID: 468a895f9a56
Revises: 14c1e59540ec
Create Date: 2025-12-03 13:46:02.307865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '468a895f9a56'
down_revision: Union[str, None] = '14c1e59540ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'deals',
        sa.Column('sector_package_id', sa.Integer(), sa.ForeignKey('sector_packages.id'), nullable=False)
    )
    op.add_column(
        'deals',
        sa.Column('custom_sector_package', sa.String(200), nullable=True)
    )
    op.drop_column('deals', 'sector_package')


def downgrade() -> None:
    op.drop_column('deals', 'sector_package_id')
    op.drop_column('deals', 'custom_sector_package')
    op.add_column(
        'deals',
        sa.Column('sector_package', sa.String(200), nullable=True)
    )
