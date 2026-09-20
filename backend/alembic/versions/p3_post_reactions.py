"""P3: Create post_reactions table for likes and bookmarks

Revision ID: p3_post_reactions
Revises: p2_fts5
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "p3_post_reactions"
down_revision: Union[str, None] = "p2_fts5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post_reactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),  # 'like' | 'bookmark'
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id", "user_id", "type", name="uq_reaction_post_user_type"),
    )
    op.create_index("ix_post_reactions_id", "post_reactions", ["id"], unique=False)
    op.create_index("ix_post_reactions_user_type", "post_reactions", ["user_id", "type"], unique=False)
    op.create_index("ix_post_reactions_post_type", "post_reactions", ["post_id", "type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_post_reactions_post_type", table_name="post_reactions")
    op.drop_index("ix_post_reactions_user_type", table_name="post_reactions")
    op.drop_index("ix_post_reactions_id", table_name="post_reactions")
    op.drop_table("post_reactions")
