"""make salesperson_name nullable

Revision ID: 52acf5e5f61b
Revises: 0673d6e69c58
Create Date: 2026-02-06 13:42:45.106536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52acf5e5f61b'
down_revision: Union[str, None] = '0673d6e69c58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
