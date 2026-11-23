"""
app/config.py – centralised settings loaded from environment variables.

WHY: Hardcoding secrets in source is a critical vulnerability (CWE-798).
Pydantic Settings reads from a .env file locally and from real env vars in CI/CD,
so the same code works in every environment without touching the source file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Loaded from env or .env file; never from a default in production.
    secret_key: str = "INSECURE-dev-only-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./notes.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single global instance – import this everywhere, never create new Settings().
settings = Settings()
