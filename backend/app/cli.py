"""Blog CLI - Typer-based command line interface.

Usage:
    python -m app.cli <command> [options]

Commands:
    seed                    - Insert seed data (idempotent)
    diff_schema             - Compare ORM schema with actual DB schema
    migrate_refresh_tokens  - One-time: convert plaintext refresh_token to hash
    rebuild_fts             - Rebuild FTS5 index (P2)
    rerender_all            - Re-render all post content_html (P2)
    send_digest             - Send weekly digest to subscribers (P3)
    cleanup_revisions       - Clean up old post revisions (P3)
    cleanup_pending_subscribers - Clean up unconfirmed subscribers (P3)
    cleanup_read_events     - Clean up old read track events (P3)
    create_admin            - Interactively create a super admin
"""
import json
import sys
from typing import Optional

import typer

cli = typer.Typer(help="Blog CLI - database and maintenance commands.")


@cli.command()
def seed():
    """Insert seed data (admin user, site config, sample posts, etc.). Idempotent."""
    from app.db.session import SessionLocal
    from app.db.seed_data import seed_database

    typer.echo("Running seed...")
    with SessionLocal() as db:
        seed_database(db)
    typer.echo("Seed complete.")


@cli.command()
def diff_schema(full: bool = False):
    """Compare ORM schema with actual database schema.

    Exit code 0 = clean, 1 = differences found.
    Use --full to also check triggers and FTS tables (SQLite).
    """
    from sqlalchemy import inspect, text
    from app.db.session import engine
    from app.db.session import Base
    # Ensure all models are imported so Base.metadata is populated
    import app.models  # noqa: F401

    inspector = inspect(engine)

    report = {
        "missing_tables": [],
        "extra_tables": [],
        "table_diffs": {},
    }

    orm_tables = set(Base.metadata.tables.keys())
    db_tables = set(inspector.get_table_names())

    # Exclude alembic_version from comparison
    db_tables.discard("alembic_version")

    report["missing_tables"] = sorted(orm_tables - db_tables)
    report["extra_tables"] = sorted(db_tables - orm_tables)

    for table_name in sorted(orm_tables & db_tables):
        diff = {}
        orm_table = Base.metadata.tables[table_name]

        # --- Column comparison ---
        orm_cols = {c.name: c for c in orm_table.columns}
        db_cols = {c["name"]: c for c in inspector.get_columns(table_name)}
        col_diffs = []

        for name in sorted(orm_cols.keys()):
            if name not in db_cols:
                col_diffs.append({"column": name, "issue": "missing_in_db"})
            else:
                db_col = db_cols[name]
                orm_col = orm_cols[name]
                orm_type_str = str(orm_col.type)
                db_type_str = str(db_col["type"])
                if orm_type_str != db_type_str:
                    col_diffs.append({
                        "column": name,
                        "issue": "type_mismatch",
                        "orm": orm_type_str,
                        "db": db_type_str,
                    })
                if orm_col.nullable != db_col.get("nullable", True):
                    col_diffs.append({
                        "column": name,
                        "issue": "nullable_mismatch",
                        "orm": orm_col.nullable,
                        "db": db_col.get("nullable", True),
                    })

        for name in sorted(db_cols.keys() - orm_cols.keys()):
            col_diffs.append({"column": name, "issue": "extra_in_db"})

        # --- Index comparison ---
        orm_indexes = {idx.name: idx for idx in orm_table.indexes if idx.name}
        db_indexes = {idx["name"]: idx for idx in inspector.get_indexes(table_name) if idx.get("name")}
        idx_diffs = []

        for name in sorted(orm_indexes.keys()):
            if name not in db_indexes:
                idx_diffs.append({"index": name, "issue": "missing_in_db"})

        for name in sorted(db_indexes.keys() - orm_indexes.keys()):
            idx_diffs.append({"index": name, "issue": "extra_in_db"})

        # --- Unique constraint comparison ---
        orm_unique_names = set()
        for c in orm_table.constraints:
            if hasattr(c, "name") and c.name and "unique" in str(type(c).__name__).lower():
                orm_unique_names.add(c.name)

        db_unique_names = {u["name"] for u in inspector.get_unique_constraints(table_name) if u.get("name")}
        uq_diffs = []
        for name in sorted(orm_unique_names - db_unique_names):
            uq_diffs.append({"constraint": name, "issue": "missing_in_db"})
        for name in sorted(db_unique_names - orm_unique_names):
            uq_diffs.append({"constraint": name, "issue": "extra_in_db"})

        # --- Foreign key comparison ---
        orm_fk_names = {fk.name for fk in orm_table.foreign_keys if fk.name}
        db_fk_names = {fk["name"] for fk in inspector.get_foreign_keys(table_name) if fk.get("name")}
        fk_diffs = []
        for name in sorted(orm_fk_names - db_fk_names):
            fk_diffs.append({"fk": name, "issue": "missing_in_db"})
        for name in sorted(db_fk_names - orm_fk_names):
            fk_diffs.append({"fk": name, "issue": "extra_in_db"})

        if col_diffs or idx_diffs or uq_diffs or fk_diffs:
            if col_diffs:
                diff["columns"] = col_diffs
            if idx_diffs:
                diff["indexes"] = idx_diffs
            if uq_diffs:
                diff["unique_constraints"] = uq_diffs
            if fk_diffs:
                diff["foreign_keys"] = fk_diffs
            report["table_diffs"][table_name] = diff

    # --- Full mode: triggers and FTS ---
    if full:
        with engine.connect() as conn:
            # Triggers
            triggers_result = conn.execute(
                text("SELECT name, tbl_name FROM sqlite_master WHERE type='trigger'")
            )
            report["triggers"] = [
                {"name": row[0], "table": row[1]} for row in triggers_result
            ]

            # FTS virtual tables
            fts_result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND sql LIKE '%FTS%'")
            )
            report["fts_tables"] = [row[0] for row in fts_result]

    # --- Output ---
    has_diff = bool(
        report["missing_tables"]
        or report["extra_tables"]
        or report["table_diffs"]
    )

    print(json.dumps(report, indent=2, default=str, ensure_ascii=False))

    if has_diff:
        typer.echo("\nSchema differences found!", err=True)
        raise typer.Exit(1)
    else:
        typer.echo("\nSchema is clean - ORM matches DB.")


@cli.command()
def migrate_refresh_tokens():
    """One-time: convert plaintext refresh_token to sha256 hash."""
    import hashlib

    from app.db.session import SessionLocal
    from app.models.user import User

    typer.echo("Migrating refresh tokens to hash...")
    with SessionLocal() as db:
        users = db.query(User).filter(User.refresh_token.isnot(None)).all()
        count = 0
        for u in users:
            if u.refresh_token:
                u.refresh_token_hash = hashlib.sha256(
                    u.refresh_token.encode()
                ).hexdigest()
                u.refresh_token = None
                count += 1
        db.commit()
    typer.echo(f"Migrated {count} refresh tokens to hash.")


@cli.command()
def rebuild_fts():
    """Rebuild FTS5 index from scratch (full re-index)."""
    from sqlalchemy import text
    from app.db.session import engine
    import app.models  # noqa: F401 - ensure models loaded for event listeners
    from app.services.fts_sync import tokenize

    typer.echo("Rebuilding FTS5 index...")
    with engine.begin() as conn:
        # Check if FTS table exists (SQLite only)
        if engine.dialect.name != "sqlite":
            typer.echo("FTS5 is SQLite-only, skipping.")
            return

        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='posts_fts'"
        )).fetchone()
        if not result:
            typer.echo("posts_fts table does not exist. Run alembic upgrade head first.")
            raise typer.Exit(1)

        # Clear existing index
        conn.execute(text("DELETE FROM posts_fts"))
        typer.echo("Cleared existing FTS index.")

        # Re-index all published posts with jieba tokenization
        posts = conn.execute(text(
            "SELECT id, title, summary, content_markdown, status FROM posts WHERE status='published'"
        )).fetchall()

        for post in posts:
            pid, title, summary, content, status = post
            conn.execute(text("""
                INSERT INTO posts_fts (rowid, title, summary, content_text, status)
                VALUES (:id, :title, :summary, :content, :status)
            """), {
                "id": pid,
                "title": tokenize(title),
                "summary": tokenize(summary),
                "content": tokenize(content),
                "status": status,
            })

        typer.echo(f"Re-indexed {len(posts)} published posts.")


@cli.command()
def rerender_all():
    """Re-render all post content_html (P2 feature)."""
    typer.echo("Markdown rendering not yet implemented. Available after P2.")
    raise typer.Exit(1)


@cli.command()
def send_digest(days: int = 7, dry_run: bool = False, limit: int = 50):
    """Send weekly digest to confirmed subscribers (P3 feature)."""
    typer.echo("Email subscription not yet implemented. Available after P3.")
    raise typer.Exit(1)


@cli.command()
def cleanup_revisions(keep_last: int = 10, older_than_days: int = 180):
    """Clean up old post revisions, keeping last N per post."""
    from datetime import datetime, timedelta, timezone

    from app.db.session import SessionLocal
    from app.models.post_revision import PostRevision
    from sqlalchemy import func

    typer.echo(f"Cleaning up revisions (keep_last={keep_last}, older_than_days={older_than_days})...")
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    with SessionLocal() as db:
        # Get post_ids that have old revisions
        post_ids = (
            db.query(PostRevision.post_id)
            .filter(PostRevision.created_at < cutoff)
            .distinct()
            .all()
        )
        total_deleted = 0
        for (post_id,) in post_ids:
            # Get revisions for this post, ordered by version desc
            revs = (
                db.query(PostRevision)
                .filter(PostRevision.post_id == post_id)
                .order_by(PostRevision.version_number.desc())
                .all()
            )
            # Keep the latest N, delete the rest if they're old enough
            for rev in revs[keep_last:]:
                if rev.created_at < cutoff:
                    db.delete(rev)
                    total_deleted += 1
        db.commit()
    typer.echo(f"Deleted {total_deleted} old revisions.")


@cli.command()
def cleanup_pending_subscribers():
    """Clean up unconfirmed subscribers older than 30 days (P3 feature)."""
    typer.echo("Subscribers table not yet implemented. Available after P3.")
    raise typer.Exit(1)


@cli.command()
def cleanup_read_events(days: int = 7):
    """Clean up old read track events (P3 feature)."""
    typer.echo("Read track events not yet implemented. Available after P3.")
    raise typer.Exit(1)


@cli.command()
def create_admin(username: str, email: str):
    """Interactively create a super admin account."""
    import bcrypt

    from app.db.session import SessionLocal
    from app.models.user import User

    password = typer.prompt("Enter password", hide_input=True, confirmation_prompt=True)
    if len(password) < 8:
        typer.echo("Password must be at least 8 characters.", err=True)
        raise typer.Exit(1)

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    with SessionLocal() as db:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            typer.echo(f"User '{username}' already exists.", err=True)
            raise typer.Exit(1)

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role="super_admin",
            email_verified=True,
            must_change_password=True,
        )
        db.add(user)
        db.commit()
    typer.echo(f"Super admin '{username}' created. They will be prompted to change password on first login.")


if __name__ == "__main__":
    cli()
