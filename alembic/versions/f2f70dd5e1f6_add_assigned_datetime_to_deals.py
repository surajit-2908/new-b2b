"""add assigned_datetime to deals

Revision ID: f2f70dd5e1f6
Revises: 852b76171e87
Create Date: 2026-02-27 12:00:17.500109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2f70dd5e1f6'
down_revision: Union[str, None] = '852b76171e87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
            "leads",
            sa.Column("assigned_datetime", sa.DateTime(timezone=True), nullable=True)
        )

def downgrade() -> None:
    op.drop_column("leads", "assigned_datetime")