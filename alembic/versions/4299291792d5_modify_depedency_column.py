"""modify depedency column

Revision ID: 4299291792d5
Revises: 6a1f03e2121e
Create Date: 2025-12-09 16:21:42.040289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4299291792d5'
down_revision: Union[str, None] = '6a1f03e2121e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.add_column(
        "work_packages",
        sa.Column("dependencies_ids", sa.JSON(), nullable=True)
    )

    op.drop_column("work_packages", "dependencies")


def downgrade():
    op.add_column(
        "work_packages",
        sa.Column("dependencies", sa.Text(), nullable=False)
    )

    op.drop_column("work_packages", "dependencies_ids")