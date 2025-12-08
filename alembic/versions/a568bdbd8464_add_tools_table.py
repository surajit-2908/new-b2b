"""add tools table

Revision ID: a568bdbd8464
Revises: a368a1c8214d
Create Date: 2025-12-08 12:09:18.606534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a568bdbd8464'
down_revision: Union[str, None] = 'a368a1c8214d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())
    )

def downgrade():
    op.drop_table("tools")