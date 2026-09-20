"""Add chat sessions and messages tables

Revision ID: p1_add_chat_history
Revises: p1_add_about_fields
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa

revision = "p1_add_chat_history"
down_revision = "p1_add_about"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False, server_default="新对话"),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # AI 记忆字段
    op.add_column("users", sa.Column("ai_memory", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "ai_memory")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
