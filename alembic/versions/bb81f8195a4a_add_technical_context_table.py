"""add technical_context table

Revision ID: bb81f8195a4a
Revises: 1dfb9b2a77c3
Create Date: 2025-12-01 16:04:19.945259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'bb81f8195a4a'
down_revision: Union[str, None] = '1dfb9b2a77c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "technical_contexts" not in inspector.get_table_names():
        op.create_table(
            "technical_contexts",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("deals.id"), nullable=False),

            sa.Column("client_main_systems", sa.Text(), nullable=False),
            sa.Column("integration_targets", sa.Text(), nullable=True),
            sa.Column("tools_in_scope", sa.Text(), nullable=False),
            sa.Column("access_required_list", sa.Text(), nullable=False),
            sa.Column("credential_provision_method", sa.Text(), nullable=False),

            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        )


def downgrade() -> None:
    op.drop_table("technical_contexts")
