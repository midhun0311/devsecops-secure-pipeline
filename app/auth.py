"""
app/auth.py – password hashing and JWT token handling.

WHY security choices made here:
- Argon2 is the winner of the Password Hashing Competition; it is memory-hard
  so GPU-based brute force is very expensive.  Bcrypt is the common choice but
  Argon2 is the current recommendation (OWASP Password Storage Cheat Sheet).
- JWT tokens are signed with HMAC-SHA256 so the server can verify them without
  a database lookup on every request.  The secret key MUST stay secret.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# CryptContext picks Argon2 as the active algorithm; deprecated schemes are
# automatically re-hashed on the next login (forward migration).
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plaintext: str) -> str:
    """Return the Argon2 hash of *plaintext*. Store only this hash in the DB."""
    return pwd_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Return True when *plaintext* matches the stored *hashed* value."""
    return pwd_context.verify(plaintext, hashed)


def create_access_token(subject: str) -> str:
    """
    Build a JWT whose 'sub' claim identifies the user.

    The token expires after settings.access_token_expire_minutes so a stolen
    token has a limited window of usefulness.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str:
    """
    Validate a JWT and return the username stored in 'sub'.

    Raises JWTError (which callers should convert to HTTP 401) if the token
    is invalid, expired, or tampered with.
    """
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    username: str | None = payload.get("sub")
    if username is None:
        raise JWTError("Token payload missing 'sub' claim")
    return username
