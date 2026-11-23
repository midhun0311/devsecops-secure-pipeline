"""
app/models.py – SQLAlchemy ORM table definitions.

WHY: Defining tables as Python classes (ORM) lets SQLAlchemy auto-generate
parameterised SQL, which prevents SQL injection. We never build raw SQL strings.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    # Store only the HASH, never the plaintext password.
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # One user owns many notes; deleting a user removes their notes too.
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="owner", cascade="all, delete"
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Foreign key enforces that every note belongs to a real user.
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="notes")
