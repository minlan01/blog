from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    """Build engine — use SQLite if MYSQL_HOST is unset or invalid for testing."""
    db_path = settings.SQLITE_DB_PATH
    if db_path == ":memory:" or db_path.endswith(".db"):
        # Use SQLite for testing or when explicitly configured
        return create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
    return create_engine(settings.database_url, pool_recycle=3600, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
