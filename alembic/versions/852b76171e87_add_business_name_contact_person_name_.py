"""add business_name, contact_person_name, review to leads

Revision ID: 852b76171e87
Revises: 7494aa6e71b8
Create Date: 2026-02-25 12:00:28.091301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '852b76171e87'
down_revision: Union[str, None] = '7494aa6e71b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('leads', sa.Column('business_name', sa.String(length=255), nullable=True))
    op.add_column('leads', sa.Column('contact_person_name', sa.String(length=255), nullable=True))
    op.add_column('leads', sa.Column('review', sa.String(length=1024), nullable=True))


def downgrade():
    op.drop_column('leads', 'review')
    op.drop_column('leads', 'contact_person_name')
    op.drop_column('leads', 'business_name')