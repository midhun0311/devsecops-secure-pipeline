"""
app/main.py – FastAPI application entry point.

Route organisation:
  /health        – liveness probe (no auth required)
  /register      – create a new account
  /login         – exchange credentials for a JWT
  /notes/*       – CRUD for the authenticated user's notes
"""

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth import create_access_token, decode_token, verify_password
from app.database import Base, engine, get_db

# Create all tables on startup if they do not exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Notes API", version="1.0.0")

# HTTPBearer extracts the "Authorization: Bearer <token>" header automatically.
bearer_scheme = HTTPBearer()


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    Dependency used by protected routes.

    Returns the username encoded in the JWT, or raises HTTP 401 if the
    token is missing, expired, or tampered with.
    """
    try:
        return decode_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


# ── Public endpoints ─────────────────────────────────────────────────────────


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe – used by Docker/k8s and the CI pipeline."""
    return {"status": "ok"}


@app.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
    """Create a new user account with a hashed password."""
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.create_user(db, data)


@app.post("/login", response_model=schemas.Token, tags=["auth"])
def login(data: schemas.UserCreate, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Validate credentials and return a JWT.

    WHY: We return a generic error rather than "wrong password" vs "user not
    found" to avoid leaking which usernames exist (user enumeration).
    """
    user = crud.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}


# ── Protected note endpoints ──────────────────────────────────────────────────


@app.get("/notes", response_model=list[schemas.NoteOut], tags=["notes"])
def list_notes(
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[models.Note]:
    """Return all notes belonging to the authenticated user."""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_notes_for_user(db, user.id)


@app.post(
    "/notes",
    response_model=schemas.NoteOut,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
)
def create_note(
    data: schemas.NoteCreate,
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> models.Note:
    """Create a new note owned by the authenticated user."""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_note(db, data, user.id)


@app.put("/notes/{note_id}", response_model=schemas.NoteOut, tags=["notes"])
def update_note(
    note_id: int,
    data: schemas.NoteUpdate,
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> models.Note:
    """Update title or content of a note. Only the owner may edit it."""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    note = crud.get_note(db, note_id, user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud.update_note(db, note, data)


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"])
def delete_note(
    note_id: int,
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> None:
    """Delete a note. Only the owner may delete it."""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    note = crud.get_note(db, note_id, user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    crud.delete_note(db, note)
