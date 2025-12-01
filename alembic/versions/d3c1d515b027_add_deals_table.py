"""add deals table

Revision ID: d3c1d515b027
Revises: 8589dcc1a110
Create Date: 2025-12-01 11:48:59.666263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'd3c1d515b027'
down_revision: Union[str, None] = '8589dcc1a110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "deals" not in inspector.get_table_names():
        op.create_table(
            'deals',
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
            sa.Column("client_name", sa.Text(), nullable=False),
            sa.Column("primary_contact_name", sa.String(150), nullable=False), 
            sa.Column("primary_contact_email", sa.String(100), nullable=False),
            sa.Column("primary_contact_phone", sa.String(50), nullable=True),
            sa.Column("industry", sa.String(100), nullable=True),
            sa.Column('sector_package', sa.String(150), nullable=True),
            sa.Column('deal_name', sa.Text(), nullable=False),
            sa.Column('salesperson_name', sa.String(150), nullable=False),
            sa.Column('deal_close_date', sa.DateTime(), nullable=False),
            sa.Column('expected_start_date', sa.DateTime(), nullable=True),
            sa.Column('expected_end_date_or_deadline', sa.DateTime(), nullable=True),
            sa.Column('client_approved_scope_summary', sa.Text(), nullable=False),
            sa.Column('special_terms', sa.Text(), nullable=True),
            sa.Column('status', sa.String(100), nullable=True),  # draft / active
            sa.Column('draft_version', sa.Integer(), nullable=True),
            sa.Column('last_saved_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        )



def downgrade():
    op.drop_table("deals")