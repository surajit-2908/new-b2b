"""update work package table

Revision ID: 5edd43134b96
Revises: a80ad079da2f
Create Date: 2025-12-17 12:00:04.549458

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5edd43134b96"
down_revision: Union[str, None] = "a80ad079da2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------- helper functions ----------
def _get_columns(inspector):
    return {col["name"] for col in inspector.get_columns("work_packages")}


def _get_fks(inspector):
    return {fk["name"] for fk in inspector.get_foreign_keys("work_packages")}


# ---------- upgrade ----------
def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = _get_columns(inspector)
    fks = _get_fks(inspector)

    # 1. bidding_status
    if "bidding_status" not in columns:
        op.add_column(
            "work_packages",
            sa.Column("bidding_status", sa.String(20), nullable=True),
        )

    # 2. assigned_technician_id column
    if "assigned_technician_id" not in columns:
        op.add_column(
            "work_packages",
            sa.Column("assigned_technician_id", sa.Integer(), nullable=True),
        )

    # 3. foreign key (only if missing)
    fk_name = "fk_work_packages_assigned_technician_id"
    if fk_name not in fks and "assigned_technician_id" in _get_columns(sa.inspect(op.get_bind())):
        op.create_foreign_key(
            fk_name,
            "work_packages",
            "users",
            ["assigned_technician_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # 4. required_tools_ids
    if "required_tools_ids" not in columns:
        op.add_column(
            "work_packages",
            sa.Column("required_tools_ids", sa.JSON(), nullable=True),
        )

    # 5. bidding_duration_days
    if "bidding_duration_days" not in columns:
        op.add_column(
            "work_packages",
            sa.Column("bidding_duration_days", sa.Integer(), nullable=True),
        )


# ---------- downgrade ----------
def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = _get_columns(inspector)
    fks = _get_fks(inspector)

    fk_name = "fk_work_packages_assigned_technician_id"

    # 1. drop FK first (only if exists)
    if fk_name in fks:
        op.drop_constraint(
            fk_name,
            "work_packages",
            type_="foreignkey",
        )

    # 2. drop columns only if they exist
    if "assigned_technician_id" in columns:
        op.drop_column("work_packages", "assigned_technician_id")

    if "required_tools_ids" in columns:
        op.drop_column("work_packages", "required_tools_ids")

    if "bidding_duration_days" in columns:
        op.drop_column("work_packages", "bidding_duration_days")

    if "bidding_status" in columns:
        op.drop_column("work_packages", "bidding_status")