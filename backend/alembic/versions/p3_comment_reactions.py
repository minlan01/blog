"""P3: Create comment_reactions table for emoji reactions

Revision ID: p3_comment_reactions
Revises: p3_post_reactions
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "p3_comment_reactions"
down_revision: Union[str, None] = "p3_post_reactions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comment_reactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("emoji", sa.String(length=8), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("comment_id", "user_id", "emoji", name="uq_comment_reaction"),
    )
    op.create_index("ix_comment_reactions_comment_id", "comment_reactions", ["comment_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_comment_reactions_comment_id", table_name="comment_reactions")
    op.drop_table("comment_reactions")
