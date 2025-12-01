"""add communications table

Revision ID: c4d76b622e37
Revises: bb81f8195a4a
Create Date: 2025-12-01 16:04:30.148546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'c4d76b622e37'
down_revision: Union[str, None] = 'bb81f8195a4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    
    if "communications" not in inspector.get_table_names():
        op.create_table(
            "communications",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("deals.id"), nullable=False),

            sa.Column("client_project_contact_name", sa.Text(), nullable=False),
            sa.Column("client_project_contact_email", sa.Text(), nullable=False),
            sa.Column("preferred_channel", sa.Text(), nullable=True),
            sa.Column("update_frequency", sa.Text(), nullable=True),

            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        )

def downgrade() -> None:
    op.drop_table("communications")
