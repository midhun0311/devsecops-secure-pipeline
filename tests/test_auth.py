"""
tests/test_auth.py – registration and login endpoint tests.
"""

from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    r = client.post("/register", json={"username": "alice", "password": "Password123!"})
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "alice"
    # Security: hashed_password must NEVER appear in the response.
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_username(client: TestClient):
    client.post("/register", json={"username": "alice", "password": "Password123!"})
    r = client.post("/register", json={"username": "alice", "password": "AnotherPass9!"})
    assert r.status_code == 400


def test_register_short_password(client: TestClient):
    r = client.post("/register", json={"username": "bob", "password": "short"})
    assert r.status_code == 422  # Pydantic validation error


def test_register_invalid_username_chars(client: TestClient):
    r = client.post("/register", json={"username": "bad user!", "password": "Password123!"})
    assert r.status_code == 422


def test_login_success(client: TestClient):
    client.post("/register", json={"username": "alice", "password": "Password123!"})
    r = client.post("/login", json={"username": "alice", "password": "Password123!"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    client.post("/register", json={"username": "alice", "password": "Password123!"})
    r = client.post("/login", json={"username": "alice", "password": "WrongPass999!"})
    assert r.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    r = client.post("/login", json={"username": "ghost", "password": "Password123!"})
    # Must return the same 401 as wrong password to prevent user enumeration.
    assert r.status_code == 401
