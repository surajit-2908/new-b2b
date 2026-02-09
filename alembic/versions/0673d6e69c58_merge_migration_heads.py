"""Merge migration heads

Revision ID: 0673d6e69c58
Revises: 2d6d7648a5e7, b2ec1434e9c9
Create Date: 2026-02-06 13:42:30.524921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0673d6e69c58'
down_revision: Union[str, None] = ('2d6d7648a5e7', 'b2ec1434e9c9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
