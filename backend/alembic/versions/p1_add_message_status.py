"""Add status field to messages for moderation

Revision ID: p1_add_message_status
Revises: p1_add_chat_history
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa

revision = "p1_add_message_status"
down_revision = "p1_add_chat_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("status", sa.String(20), nullable=False, server_default="pending"))
    # Existing messages auto-approved
    op.execute("UPDATE messages SET status = 'approved'")


def downgrade() -> None:
    op.drop_column("messages", "status")
