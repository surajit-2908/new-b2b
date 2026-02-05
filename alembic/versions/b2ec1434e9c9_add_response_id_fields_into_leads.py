"""add response_id fields into leads

Revision ID: b2ec1434e9c9
Revises: 1e541c1d2064
Create Date: 2026-02-05 17:21:20.913742
"""

from typing import Sequence, Union
from alembic import op


revision: str = "b2ec1434e9c9"
down_revision: Union[str, None] = "1e541c1d2064"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✅ MySQL-safe, column placed AFTER place_id
    op.execute(
        """
        ALTER TABLE leads
        ADD COLUMN response_id VARCHAR(255) NULL
        AFTER place_id
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE leads
        DROP COLUMN response_id
        """
    )
