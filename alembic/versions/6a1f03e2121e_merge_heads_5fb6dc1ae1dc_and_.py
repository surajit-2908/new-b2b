"""merge heads 5fb6dc1ae1dc and a568bdbd8464

Revision ID: 6a1f03e2121e
Revises: 5fb6dc1ae1dc, a568bdbd8464
Create Date: 2025-12-09 16:21:24.288281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a1f03e2121e'
down_revision: Union[str, None] = ('5fb6dc1ae1dc', 'a568bdbd8464')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
