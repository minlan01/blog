from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    """Build engine for the configured database backend."""
    if settings.DATABASE_BACKEND.lower() == "sqlite":
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
        )
        # Enable WAL mode for better concurrent read/write performance
        # Required by FTS5 to avoid 'database is locked' under concurrent access
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=3000")
            cursor.close()
        return engine
    return create_engine(settings.database_url, pool_recycle=3600, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
