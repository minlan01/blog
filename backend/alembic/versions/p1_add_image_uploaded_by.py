"""Add uploaded_by field to images table

Revision ID: p1_add_image_uploaded_by
Revises: p1_add_message_status
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa

revision = "p1_add_image_uploaded_by"
down_revision = "p1_add_message_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("images", sa.Column("uploaded_by", sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column("images", "uploaded_by")
