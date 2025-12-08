"""add skills table

Revision ID: a368a1c8214d
Revises: f2aa451d57bd
Create Date: 2025-12-08 12:09:04.105878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a368a1c8214d'
down_revision: Union[str, None] = 'f2aa451d57bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())
    )

def downgrade():
    op.drop_table("skills")