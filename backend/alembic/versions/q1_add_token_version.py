"""add token_version to users

Revision ID: q1_add_token_version
Revises: p1_add_image_uploaded_by
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "q1_add_token_version"
down_revision = "p1_add_image_uploaded_by"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("users", "token_version")
