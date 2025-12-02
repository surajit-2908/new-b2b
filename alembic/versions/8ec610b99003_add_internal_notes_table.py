"""add internal notes table

Revision ID: 8ec610b99003
Revises: c4d76b622e37
Create Date: 2025-12-02 12:26:59.298108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '8ec610b99003'
down_revision: Union[str, None] = 'c4d76b622e37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "internal_notes" not in inspector.get_table_names():
        op.create_table(
            "internal_notes",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("deals.id"), nullable=False),

            sa.Column("internal_risks_and_warnings", sa.Text(), nullable=True),
            sa.Column("internal_margin_sensitivity", sa.Text(), nullable=False), #Low/Medium/High
            sa.Column("internal_notes", sa.Text(), nullable=True),
        
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )


def downgrade():
     op.drop_table("internal_notes")