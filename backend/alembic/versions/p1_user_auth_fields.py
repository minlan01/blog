"""P1: Add must_change_password and refresh_token_hash to users

Revision ID: p1_user_auth_fields
Revises: 0001_root
Create Date: 2026-07-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "p1_user_auth_fields"
down_revision: Union[str, None] = "0001_root"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add must_change_password (default False)
    op.add_column(
        "users",
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # Add refresh_token_hash (nullable, for two-phase migration)
    op.add_column(
        "users",
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_users_refresh_token_hash", "users", ["refresh_token_hash"])


def downgrade() -> None:
    op.drop_index("ix_users_refresh_token_hash", table_name="users")
    op.drop_column("users", "refresh_token_hash")
    op.drop_column("users", "must_change_password")
