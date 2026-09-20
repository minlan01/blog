"""P2: Create FTS5 virtual table for full-text search

Revision ID: p2_fts5
Revises: p1_user_auth_fields
Create Date: 2026-07-28

FTS5 is SQLite-only. On MySQL this migration is a no-op.
The virtual table includes a 'status' UNINDEXED column so queries can
filter by published/draft without a separate join.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "p2_fts5"
down_revision: Union[str, None] = "p1_user_auth_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # FTS5 is SQLite-only
    if bind.dialect.name != "sqlite":
        return

    # Create FTS5 virtual table with status as UNINDEXED column
    # UNINDEXED means: stored but not searchable, used for filtering only
    op.execute("""
        CREATE VIRTUAL TABLE posts_fts USING fts5(
            title,
            summary,
            content_text,
            status UNINDEXED,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    # Backfill: insert existing published posts into FTS index
    # jieba tokenization happens at the application layer (event listener),
    # but for the initial backfill we do a raw SQL copy with basic tokenization.
    # The event listener will handle re-tokenization on next update.
    op.execute("""
        INSERT INTO posts_fts (rowid, title, summary, content_text, status)
        SELECT id, title, summary, content_markdown, status
        FROM posts
        WHERE status = 'published'
    """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return
    op.execute("DROP TABLE IF EXISTS posts_fts")
