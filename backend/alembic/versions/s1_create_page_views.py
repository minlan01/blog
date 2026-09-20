"""create page_views table

Revision ID: s1_create_page_views
Revises: r1_create_access_tokens
Create Date: 2026-07-31
"""
import sqlalchemy as sa
from alembic import op


revision = "s1_create_page_views"
down_revision = "r1_create_access_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "page_views",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("device", sa.String(20), server_default="desktop"),
        sa.Column("browser", sa.String(20), server_default="other"),
        sa.Column("referrer_source", sa.String(100), server_default="direct"),
        sa.Column("ip_hash", sa.String(8), server_default=""),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_page_views_path_created", "page_views", ["path", "created_at"])
    op.create_index("ix_page_views_created_at", "page_views", ["created_at"])


def downgrade() -> None:
    op.drop_table("page_views")
