"""FTS5 synchronization service.

Handles bidirectional sync between posts table and posts_fts virtual table
via SQLAlchemy ORM events. Uses jieba for Chinese tokenization.

Key design decisions (from Gate A review):
- Event listener is the SOLE FTS write path for ORM operations
- batch_delete_posts must explicitly DELETE from posts_fts (Query.delete bypass)
- Only 'published' posts are indexed (draft excluded for info leak prevention)
- escape_fts_query covers ALL FTS5 special characters including : and ~
- sanitize_snippet escapes HTML except <mark> tags (XSS prevention)
- after_update/after_delete must NOT commit separately (transaction atomicity)
"""
from __future__ import annotations

import hashlib
import html
import logging
import re
from typing import TYPE_CHECKING

import jieba
from sqlalchemy import event, text
from sqlalchemy.exc import OperationalError

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from app.models.post import Post

logger = logging.getLogger("blog")

# ── jieba initialization (once at module load) ──
# jieba.lcut loads its dictionary on first call; we force it now
jieba.initialize()


# ── Tokenization ──

def tokenize(text: str | None) -> str:
    """Tokenize text with jieba, return space-separated tokens."""
    if not text:
        return ""
    return " ".join(jieba.lcut(text))


# ── FTS sync helpers (called within ORM event, same transaction) ──

def _fts_upsert(connection: "Connection", post_id: int, title: str, summary: str,
                content: str, status: str) -> None:
    """Delete + insert into FTS. Must be called within the same transaction as the ORM op."""
    connection.execute(
        text("DELETE FROM posts_fts WHERE rowid = :id"),
        {"id": post_id},
    )
    # Only index published posts; drafts are excluded
    if status != "published":
        return
    connection.execute(
        text("""
            INSERT INTO posts_fts (rowid, title, summary, content_text, status)
            VALUES (:id, :title, :summary, :content, :status)
        """),
        {
            "id": post_id,
            "title": tokenize(title),
            "summary": tokenize(summary),
            "content": tokenize(content),
            "status": status,
        },
    )


def _fts_delete(connection: "Connection", post_id: int) -> None:
    """Delete from FTS by rowid."""
    connection.execute(
        text("DELETE FROM posts_fts WHERE rowid = :id"),
        {"id": post_id},
    )


# ── Event listener registration (must be called with Post class) ──

def register_fts_events(post_cls) -> None:
    """Register FTS event listeners on the Post model class.
    
    Must be called after Post class is defined to avoid string-based dispatch
    issues and circular imports. Called from app.models.__init__
    """
    @event.listens_for(post_cls, "after_insert")
    def _on_post_insert(mapper, connection, target) -> None:
        _fts_upsert(
            connection, target.id,
            target.title, target.summary or "",
            target.content_markdown, target.status,
        )

    @event.listens_for(post_cls, "after_update")
    def _on_post_update(mapper, connection, target) -> None:
        _fts_upsert(
            connection, target.id,
            target.title, target.summary or "",
            target.content_markdown, target.status,
        )

    @event.listens_for(post_cls, "after_delete")
    def _on_post_delete(mapper, connection, target) -> None:
        _fts_delete(connection, target.id)


# ── Explicit batch FTS ops (for Query.delete bypass) ──

def fts_batch_delete(connection: "Connection", post_ids: list[int]) -> None:
    """Explicitly delete FTS entries for batch-deleted posts.

    Call this after Query.delete() which bypasses ORM events.
    FTS bypass: explicit DELETE required because Query.delete() skips ORM events.
    """
    if not post_ids:
        return
    # SQLite doesn't support expanding IN with text(), use individual deletes
    for pid in post_ids:
        connection.execute(
            text("DELETE FROM posts_fts WHERE rowid = :id"),
            {"id": pid},
        )


# ── Query utilities ──

# ALL FTS5 special characters (P1: includes : and ~)
_FTS5_SPECIAL = re.compile(r'["()*\-+:^~]')

_MAX_TOKENS = 20  # DoS prevention


def escape_fts_query(q: str) -> str:
    """Escape user input for safe FTS5 MATCH query.

    Strategy:
    1. jieba tokenize the input
    2. Truncate to _MAX_TOKENS tokens (DoS prevention)
    3. For each token: escape internal double quotes (""), strip special chars, wrap in double quotes
    4. Join with OR

    Double-quote wrapping makes each token a phrase query,
    neutralizing all FTS5 operators inside.
    """
    if not q or not q.strip():
        return '""'

    tokens = jieba.lcut(q)[:_MAX_TOKENS]
    safe_parts = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        # Escape internal double quotes by doubling them (FTS5 escape)
        token = token.replace('"', '""')
        # Strip remaining special chars as defense in depth
        token = _FTS5_SPECIAL.sub(" ", token).strip()
        if token:
            safe_parts.append(f'"{token}"')

    return " OR ".join(safe_parts) if safe_parts else '""'


def sanitize_snippet(raw: str) -> str:
    """Sanitize FTS5 snippet() output for safe HTML rendering.

    Only <mark> and </mark> tags are preserved; all other content is HTML-escaped.
    This prevents stored XSS via malicious post content.
    """
    if not raw:
        return ""

    parts = raw.split("<mark>")
    result = [html.escape(parts[0])]

    for part in parts[1:]:
        if "</mark>" in part:
            marked_content, rest = part.split("</mark>", 1)
            result.append("<mark>")
            result.append(html.escape(marked_content))
            result.append("</mark>")
            result.append(html.escape(rest))
        else:
            # Malformed (no closing </mark>), escape everything
            result.append(html.escape("<mark>"))
            result.append(html.escape(part))

    return "".join(result)


# ── Search execution ──

def execute_fts_search(connection: "Connection", q: str, limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
    """Execute FTS5 search. Returns (results, total_count).

    - Filters: status='published' (info leak prevention)
    - Snippet: sanitized for XSS
    - Errors: classified (syntax error → empty; locked → 503-like)
    """
    fts_query = escape_fts_query(q)

    try:
        # Count total matches (for pagination)
        count_row = connection.execute(
            text("""
                SELECT count(*) AS cnt
                FROM posts_fts
                WHERE posts_fts MATCH :q AND status = 'published'
            """),
            {"q": fts_query},
        ).fetchone()
        total = count_row[0] if count_row else 0

        if total == 0:
            return [], 0

        # Get results with snippet (column index 2 = content_text)
        rows = connection.execute(
            text("""
                SELECT rowid,
                       snippet(posts_fts, 0, '<mark>', '</mark>', '...', 24) AS title_snippet,
                       snippet(posts_fts, 2, '<mark>', '</mark>', '...', 32) AS content_snippet,
                       rank
                FROM posts_fts
                WHERE posts_fts MATCH :q AND status = 'published'
                ORDER BY rank
                LIMIT :limit OFFSET :offset
            """),
            {"q": fts_query, "limit": limit, "offset": offset},
        ).fetchall()

        results = []
        for row in rows:
            results.append({
                "post_id": row[0],
                "title_snippet": sanitize_snippet(row[1]),
                "content_snippet": sanitize_snippet(row[2]),
                "rank": row[3],
            })

        return results, total

    except OperationalError as exc:
        error_msg = str(exc).lower()
        if "database is locked" in error_msg or "busy" in error_msg:
            # Lock timeout - should be retried or return 503
            logger.warning("FTS search lock timeout: %s", exc)
            raise  # Let caller decide to return 503
        elif "syntax error" in error_msg:
            # FTS query syntax error - log and return empty
            logger.error("FTS syntax error with query '%s': %s", fts_query, exc)
            return [], 0
        else:
            # Unexpected - log and return empty
            logger.error("FTS search unexpected error: %s", exc)
            return [], 0
