"""add package_number to work_packages

Revision ID: f0038d7aa82d
Revises: 5edd43134b96
Create Date: 2026-01-21 12:36:20.797375
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "f0038d7aa82d"
down_revision: Union[str, None] = "5edd43134b96"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("work_packages")]
    indexes = [idx["name"] for idx in inspector.get_indexes("work_packages")]

    if "package_number" not in columns:
        op.add_column(
            "work_packages",
            sa.Column("package_number", sa.String(length=50), nullable=True),
        )

    if "ix_work_packages_package_number" not in indexes:
        op.create_index(
            "ix_work_packages_package_number",
            "work_packages",
            ["package_number"],
            unique=True,
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    indexes = [idx["name"] for idx in inspector.get_indexes("work_packages")]
    columns = [col["name"] for col in inspector.get_columns("work_packages")]

    if "ix_work_packages_package_number" in indexes:
        op.drop_index("ix_work_packages_package_number", table_name="work_packages")

    if "package_number" in columns:
        op.drop_column("work_packages", "package_number")
