"""create sector_packages table

Revision ID: 14c1e59540ec
Revises: 8ec610b99003
Create Date: 2025-12-03 13:36:18.931139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14c1e59540ec'
down_revision: Union[str, None] = '8ec610b99003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
            'sector_packages',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('name', sa.String(150), nullable=False, unique=True),
        )

def downgrade() -> None:
    op.drop_table('sector_packages')
