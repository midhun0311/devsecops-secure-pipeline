"""
app/vulnerable_demo.py – INTENTIONALLY INSECURE demo file.

THIS FILE LIVES ONLY ON THE demo/vulnerable-change BRANCH.
IT MUST NEVER BE MERGED TO MAIN.

This demonstrates three security pipeline gates failing:
1. Secret Detection: Gitleaks catches hardcoded fake API key pattern.
2. SAST: Semgrep & Bandit catch string-interpolated SQL injection.
3. SCA: pip-audit catches outdated vulnerable dependency in requirements.txt.
"""

import sqlite3

# ── Issue 1: Hardcoded fake API key (catches via Gitleaks) ───────────────────
# Dummy key matching AWS credential regex pattern.
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLEFAKEKEYDOESNOTEXIST"  # noqa: S105


def search_notes_vulnerable(db_path: str, search_term: str) -> list:
    """
    Issue 2: SQL Injection (catches via Semgrep & Bandit)

    Direct string interpolation with user input inside a SQL query.
    Allows SQL injection attacks.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Flaw: String formatting raw SQL query
    query = f"SELECT * FROM notes WHERE title LIKE '%{search_term}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
