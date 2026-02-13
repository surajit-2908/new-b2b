"""add fields to cities table

Revision ID: c87c969caa54
Revises: 52acf5e5f61b
Create Date: 2026-02-13 16:11:23.857449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c87c969caa54'
down_revision: Union[str, None] = '52acf5e5f61b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('cities', sa.Column('state', sa.String(length=150), nullable=True))
    op.add_column('cities', sa.Column('geoid', sa.String(length=20), nullable=True))
    op.add_column('cities', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('cities', sa.Column('longitude', sa.Float(), nullable=True))

    # add unique constraint
    op.create_unique_constraint('uq_cities_geoid', 'cities', ['geoid'])
    
    op.execute("""
        ALTER TABLE cities
        MODIFY COLUMN created_at DATETIME AFTER longitude,
        MODIFY COLUMN updated_at DATETIME AFTER created_at;
    """)



def downgrade():
    op.drop_constraint('uq_cities_geoid', 'cities', type_='unique')
    op.drop_column('cities', 'longitude')
    op.drop_column('cities', 'latitude')
    op.drop_column('cities', 'geoid')
    op.drop_column('cities', 'state')