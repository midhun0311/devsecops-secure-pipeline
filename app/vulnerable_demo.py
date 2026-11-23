"""
app/vulnerable_demo.py – INTENTIONALLY INSECURE demo file.

THIS FILE LIVES ONLY ON THE demo/vulnerable-change BRANCH.
IT MUST NEVER BE MERGED TO MAIN.

This demonstrates four security pipeline gates failing:
1. Secret Detection: Gitleaks catches hardcoded dummy secrets.
2. SAST: Semgrep & Bandit catch string-interpolated SQL injection.
3. SCA: pip-audit catches outdated vulnerable dependency in requirements.txt.
"""

import sqlite3

# ── Issue 1: Hardcoded dummy secrets (catches via Gitleaks) ───────────────────
# Official AWS documentation dummy key:
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
GITHUB_TOKEN = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


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
