"""add assigned technician field

Revision ID: ab74428729b4
Revises: 
Create Date: 2025-11-24 13:52:41.842082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab74428729b4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'leads',
        sa.Column('assigned_technician_id', sa.Integer(), nullable=True)
    )
    
    # MySQL-specific: move the column after follow_up_status
    op.execute(
        """
        ALTER TABLE leads 
        MODIFY COLUMN assigned_technician_id INT NULL 
        AFTER follow_up_status;
        """
    )

def downgrade():
    op.drop_column('leads', 'assigned_technician_id')
