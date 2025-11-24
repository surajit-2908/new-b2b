"""add triple positive timestamp field

Revision ID: ac503b570d48
Revises: ab74428729b4
Create Date: 2025-11-24 15:53:47.862205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac503b570d48'
down_revision: Union[str, None] = 'ab74428729b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'leads',
        sa.Column('triple_positive_timestamp', sa.DateTime(), nullable=True)
    )
    
    # MySQL-specific: move the column after follow_up_status
    op.execute(
        """
        ALTER TABLE leads 
        MODIFY COLUMN triple_positive_timestamp DATETIME NULL 
        AFTER assigned_technician_id;
        """
    )

def downgrade():
    op.drop_column('leads', 'triple_positive_timestamp')
