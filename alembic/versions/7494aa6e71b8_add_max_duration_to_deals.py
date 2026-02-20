"""add max_duration to deals

Revision ID: 7494aa6e71b8
Revises: c87c969caa54
Create Date: 2026-02-20 12:16:17.076436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7494aa6e71b8'
down_revision: Union[str, None] = 'c87c969caa54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE deals
        ADD COLUMN max_duration INT NULL AFTER expected_end_date_or_deadline;
    """)


def downgrade():
    op.drop_column("deals", "max_duration")