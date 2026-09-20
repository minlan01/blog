"""Drop plaintext refresh_token column (hash-only migration)

Revision ID: p1_drop_refresh_token
Revises: p3_comment_reactions
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa

revision = "p1_drop_refresh_token"
down_revision = "p3_comment_reactions"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "refresh_token")


def downgrade():
    op.add_column("users", sa.Column("refresh_token", sa.String(500), nullable=True))
