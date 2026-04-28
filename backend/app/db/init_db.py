from sqlalchemy import inspect, text

from app.db.seed_data import seed_database
from app.db.session import Base, SessionLocal, engine
from app.models import Category, Comment, FriendLink, Post, SiteConfig, Tag, User, post_tags  # noqa: F401


def _migrate_email_nullable() -> None:
    """Make email column nullable if it exists and is NOT NULL."""
    insp = inspect(engine)
    if 'users' not in insp.get_table_names():
        return
    columns = {col['name']: col for col in insp.get_columns('users')}
    if 'email' in columns and not columns['email']['nullable']:
        if "sqlite" in str(engine.url):
            return  # SQLite doesn't support MODIFY COLUMN
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users MODIFY COLUMN email VARCHAR(200) NULL"))
            conn.commit()


def _migrate_view_count() -> None:
    """Add view_count column to posts if it doesn't exist."""
    insp = inspect(engine)
    if 'posts' not in insp.get_table_names():
        return
    columns = {col['name'] for col in insp.get_columns('posts')}
    if 'view_count' not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0"))
            conn.commit()


def _migrate_comment_fields() -> None:
    """Add parent_id and is_approved columns to comments if they don't exist."""
    insp = inspect(engine)
    if 'comments' not in insp.get_table_names():
        return
    columns = {col['name'] for col in insp.get_columns('comments')}
    with engine.connect() as conn:
        if 'parent_id' not in columns:
            conn.execute(text("ALTER TABLE comments ADD COLUMN parent_id INTEGER REFERENCES comments(id)"))
            conn.commit()
        if 'is_approved' not in columns:
            conn.execute(text("ALTER TABLE comments ADD COLUMN is_approved BOOLEAN DEFAULT 1"))
            conn.commit()


def _migrate_post_status() -> None:
    """Add status column to posts if it doesn't exist."""
    insp = inspect(engine)
    if 'posts' not in insp.get_table_names():
        return
    columns = {col['name'] for col in insp.get_columns('posts')}
    if 'status' not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE posts ADD COLUMN status VARCHAR(20) DEFAULT 'published'"))
            conn.commit()


def _migrate_comment_user_id_nullable() -> None:
    """Make comments.user_id nullable so users can be deleted without losing comments."""
    insp = inspect(engine)
    if 'comments' not in insp.get_table_names():
        return
    columns = {col['name']: col for col in insp.get_columns('comments')}
    if 'user_id' in columns and not columns['user_id']['nullable']:
        if "sqlite" in str(engine.url):
            return
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE comments MODIFY COLUMN user_id INTEGER NULL"))
            conn.commit()


def _migrate_image_data_mediumblob() -> None:
    """Change images.data from BLOB to MEDIUMBLOB for larger image uploads. MySQL only."""
    insp = inspect(engine)
    if 'images' not in insp.get_table_names():
        return
    # Skip for SQLite — it doesn't support MODIFY COLUMN
    if "sqlite" in str(engine.url):
        return
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE images MODIFY COLUMN data MEDIUMBLOB NOT NULL"))
        conn.commit()


def _migrate_message_reply_fields() -> None:
    """Add admin_reply, admin_reply_at, and parent_id columns to messages if they don't exist."""
    insp = inspect(engine)
    if 'messages' not in insp.get_table_names():
        return
    columns = {col['name'] for col in insp.get_columns('messages')}
    with engine.connect() as conn:
        if 'admin_reply' not in columns:
            conn.execute(text("ALTER TABLE messages ADD COLUMN admin_reply TEXT NULL"))
            conn.commit()
        if 'admin_reply_at' not in columns:
            conn.execute(text("ALTER TABLE messages ADD COLUMN admin_reply_at DATETIME NULL"))
            conn.commit()
        if 'parent_id' not in columns:
            conn.execute(text("ALTER TABLE messages ADD COLUMN parent_id INTEGER REFERENCES messages(id)"))
            conn.commit()


def _migrate_user_auth_fields() -> None:
    """Add refresh_token, failed_login_attempts, locked_until, email_verified to users."""
    insp = inspect(engine)
    if 'users' not in insp.get_table_names():
        return
    columns = {col['name'] for col in insp.get_columns('users')}
    with engine.connect() as conn:
        if 'refresh_token' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN refresh_token VARCHAR(500) NULL"))
            conn.commit()
        if 'failed_login_attempts' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
            conn.commit()
        if 'locked_until' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN locked_until DATETIME NULL"))
            conn.commit()
        if 'email_verified' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0"))
            conn.commit()


def _migrate_post_revision_table() -> None:
    """Create post_revisions table if it doesn't exist."""
    insp = inspect(engine)
    if 'post_revisions' in insp.get_table_names():
        return
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE post_revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL REFERENCES posts(id),
                title VARCHAR(200) NOT NULL,
                content_markdown TEXT NOT NULL,
                summary VARCHAR(500),
                version_number INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


def init_db() -> None:
    # First, migrate existing schema
    _migrate_email_nullable()
    _migrate_view_count()
    _migrate_comment_fields()
    _migrate_post_status()
    _migrate_comment_user_id_nullable()
    _migrate_image_data_mediumblob()
    _migrate_message_reply_fields()
    _migrate_user_auth_fields()
    _migrate_post_revision_table()

    # Then create any missing tables
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_database(db)
