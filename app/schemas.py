"""
app/schemas.py – Pydantic models for request validation and response shaping.

WHY: Pydantic automatically rejects malformed input before it ever touches the
database, closing off a whole class of injection and logic bugs.  Separate
schemas for input vs output means we never accidentally leak internal fields
(like hashed_password) in an API response.
"""

from pydantic import BaseModel, Field


# ── Auth schemas ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Body expected when registering a new account."""
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    """Shape of the user object returned by the API (no password field)."""
    id: int
    username: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token returned after a successful login."""
    access_token: str
    token_type: str


# ── Note schemas ─────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    """Body expected when creating a new note."""
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)


class NoteUpdate(BaseModel):
    """Body for updating an existing note; both fields are optional."""
    title: str | None = Field(default=None, max_length=100)
    content: str | None = Field(default=None, max_length=5000)


class NoteOut(BaseModel):
    """Shape of a note object in API responses."""
    id: int
    title: str
    content: str
    owner_id: int

    model_config = {"from_attributes": True}
