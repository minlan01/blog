import os
import tempfile
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test database before any app imports
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DB_PATH = _tmp_db.name
_tmp_db.close()
os.environ["SQLITE_DB_PATH"] = TEST_DB_PATH
os.environ["DATABASE_BACKEND"] = "sqlite"
os.environ["STORAGE_BACKEND"] = "local"
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PORT"] = "99999"  # Ensure MySQL isn't used

from app.db.session import Base, get_db, engine as prod_engine
from app.main import app
from app.core.security import hash_password
from app.models import Category, Comment, FriendLink, Post, SiteConfig, Tag, User

# Disable rate limiting for all tests
from app.api.v1.endpoints.auth import limiter as _auth_limiter
from app.api.v1.endpoints.comments import limiter as _comments_limiter
from app.api.v1.endpoints.messages import limiter as _messages_limiter
for _lim in [_auth_limiter, _comments_limiter, _messages_limiter]:
    _lim.enabled = False

_test_engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=_test_engine, autoflush=False, autocommit=False)


def _override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _setup_and_teardown_db():
    """Create tables and seed data for each test, then clean up."""
    Base.metadata.create_all(bind=_test_engine)
    db = TestSession()

    site = SiteConfig(
        site_name="Test Blog",
        hero_title="TEST",
        hero_subtitle="test",
        intro_text="A test blog",
        avatar="https://example.com/avatar.png",
        email="test@test.com",
        github_url="https://github.com/test",
        location="Test City",
    )
    db.add(site)

    admin = User(
        username="testadmin",
        password_hash=hash_password("testpass123"),
        role="super_admin",
        bio="Test Admin",
    )
    reader = User(
        username="testreader",
        password_hash=hash_password("testpass123"),
        role="user",
        bio="Test Reader",
    )
    db.add_all([admin, reader])
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def db_session(_setup_and_teardown_db):
    return _setup_and_teardown_db


@pytest.fixture
def admin_token(client):
    resp = client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "testpass123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
