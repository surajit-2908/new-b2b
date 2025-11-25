"""add lead free notes table

Revision ID: 8589dcc1a110
Revises: ac503b570d48
Create Date: 2025-11-25 09:57:13.224807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8589dcc1a110'
down_revision: Union[str, None] = 'ac503b570d48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() :
   op.create_table('lead_free_notes', 
                   sa.Column("id", sa.Integer(), primary_key=True, index=True),
                   sa.Column("lead_id",sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
                   sa.Column("notes", sa.Text(), nullable=False),
                   sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
                   sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
                   sa.Column("created_by", sa.Integer(),sa.ForeignKey("users.id"), nullable=False),
                   sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True)
                    
                   )


def downgrade():
    op.drop_table("lead_free_notes")
