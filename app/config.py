"""
app/config.py – centralised settings loaded from environment variables.

WHY: Hardcoding secrets in source is a critical vulnerability (CWE-798).
Pydantic Settings reads from a .env file locally and from real env vars in CI/CD,
so the same code works in every environment without touching the source file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Loaded from env or .env file; never from a default in production.
    # Must be at least 32 bytes for HMAC-SHA256 (RFC 7518 Section 3.2).
    secret_key: str = "insecure-dev-only-secret-key-must-be-32-bytes-long"  # noqa: S105
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./notes.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single global instance – import this everywhere, never create new Settings().
settings = Settings()
