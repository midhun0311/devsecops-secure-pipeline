"""
tests/conftest.py – shared test fixtures.

WHY: Using an in-memory SQLite DB for tests means each test run starts with a
clean slate and never touches the real notes.db file.
The `client` fixture provides a pre-authenticated HTTP client so individual
test functions stay short and focused.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# In-memory SQLite: fast, isolated, discarded when the process exits.
TEST_DATABASE_URL = "sqlite:///./test_notes.db"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Replace the production DB session with the test one."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables before every test for a clean state."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def client():
    """Unauthenticated test client."""
    return TestClient(app)


@pytest.fixture()
def auth_client(client: TestClient):
    """
    Test client with a valid JWT already in the Authorization header.
    Registers and logs in 'testuser' so individual tests do not repeat this.
    """
    client.post("/register", json={"username": "testuser", "password": "StrongPass1!"})
    response = client.post("/login", json={"username": "testuser", "password": "StrongPass1!"})
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
