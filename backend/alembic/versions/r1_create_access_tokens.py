"""create access_tokens table

Revision ID: r1_create_access_tokens
Revises: q1_add_token_version
Create Date: 2026-07-31
"""
import sqlalchemy as sa
from alembic import op


revision = "r1_create_access_tokens"
down_revision = "q1_add_token_version"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "access_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("scopes", sa.String(200), server_default="*"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("revoked", sa.Boolean(), server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("access_tokens")
