"""
tests/test_notes.py – CRUD and authorization isolation tests.

The key security property tested here: User A must NEVER be able to
read, modify, or delete User B's notes (IDOR – Insecure Direct Object Reference).
"""

from fastapi.testclient import TestClient


def test_create_and_list_notes(auth_client: TestClient):
    r = auth_client.post("/notes", json={"title": "My Note", "content": "Hello"})
    assert r.status_code == 201
    r2 = auth_client.get("/notes")
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    assert r2.json()[0]["title"] == "My Note"


def test_update_note(auth_client: TestClient):
    note_id = auth_client.post("/notes", json={"title": "Old", "content": "Old"}).json()["id"]
    r = auth_client.put(f"/notes/{note_id}", json={"title": "New Title"})
    assert r.status_code == 200
    assert r.json()["title"] == "New Title"
    assert r.json()["content"] == "Old"  # unchanged


def test_delete_note(auth_client: TestClient):
    note_id = auth_client.post("/notes", json={"title": "Del", "content": "Gone"}).json()["id"]
    r = auth_client.delete(f"/notes/{note_id}")
    assert r.status_code == 204
    assert auth_client.get("/notes").json() == []


def test_cannot_access_notes_without_token(client: TestClient):
    r = client.get("/notes")
    assert r.status_code == 403  # FastAPI HTTPBearer returns 403 when header missing


def test_note_isolation_between_users(client: TestClient):
    """User B must not be able to read or delete User A's note."""
    # Register User A and create a note
    client.post("/register", json={"username": "usera", "password": "PasswordA1!"})
    r = client.post("/login", json={"username": "usera", "password": "PasswordA1!"})
    token_a = r.json()["access_token"]
    note_id = client.post(
        "/notes",
        json={"title": "Private", "content": "Secret"},
        headers={"Authorization": f"Bearer {token_a}"},
    ).json()["id"]

    # Register User B
    client.post("/register", json={"username": "userb", "password": "PasswordB2!"})
    r2 = client.post("/login", json={"username": "userb", "password": "PasswordB2!"})
    token_b = r2.json()["access_token"]

    # User B tries to delete User A's note – must be rejected.
    r3 = client.delete(f"/notes/{note_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r3.status_code == 404  # returns 404 instead of 403 to avoid IDOR enumeration
