"""
app/crud.py – database operations (Create, Read, Update, Delete).

WHY: Keeping all DB calls here, away from the route handlers, means the
routes are small and easy to read.  SQLAlchemy's ORM always uses parameterised
queries under the hood, so SQL injection is structurally prevented.
"""

from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import hash_password

# ── User operations ──────────────────────────────────────────────────────────


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Return the User row matching *username*, or None if not found."""
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    """Hash the password, insert a new User row, and return it."""
    user = models.User(username=data.username, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Note operations ──────────────────────────────────────────────────────────


def get_notes_for_user(db: Session, owner_id: int) -> list[models.Note]:
    """Return all notes owned by *owner_id* – never another user's notes."""
    return db.query(models.Note).filter(models.Note.owner_id == owner_id).all()


def get_note(db: Session, note_id: int, owner_id: int) -> models.Note | None:
    """Return a single note only when it belongs to *owner_id*."""
    return (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == owner_id)
        .first()
    )


def create_note(db: Session, data: schemas.NoteCreate, owner_id: int) -> models.Note:
    """Insert a new note row and return it."""
    note = models.Note(title=data.title, content=data.content, owner_id=owner_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(db: Session, note: models.Note, data: schemas.NoteUpdate) -> models.Note:
    """Apply non-None fields from *data* to *note* and persist."""
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: models.Note) -> None:
    """Remove *note* from the database."""
    db.delete(note)
    db.commit()
