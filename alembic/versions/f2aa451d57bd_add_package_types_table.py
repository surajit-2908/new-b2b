"""add package_types table

Revision ID: f2aa451d57bd
Revises: 468a895f9a56
Create Date: 2025-12-08 12:01:22.486938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2aa451d57bd'
down_revision: Union[str, None] = '468a895f9a56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "package_types",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now())
    )

def downgrade():
    op.drop_table("package_types")