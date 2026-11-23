"""
app/database.py – SQLAlchemy engine and session factory.

WHY: Centralising DB setup here means every other module just imports
`get_db` and never worries about connection lifecycle.
Using check_same_thread=False is required for SQLite with FastAPI because
requests can span multiple threads.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# connect_args is SQLite-specific; remove it if switching to PostgreSQL.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# Each request gets its own Session; it is closed after the request completes.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All ORM models inherit from this class."""
    pass


def get_db():
    """FastAPI dependency that yields a DB session and closes it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
