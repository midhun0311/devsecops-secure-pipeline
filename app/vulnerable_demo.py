"""
app/vulnerable_demo.py – INTENTIONALLY INSECURE demo file.

THIS FILE EXISTS ONLY ON THE demo/vulnerable-change BRANCH.
It is NEVER merged to main. Its sole purpose is to show the CI pipeline
catching real security problems on a pull request.

Three issues planted here deliberately:

1. HARDCODED SECRET (Gitleaks)
   A fake/dummy AWS key is hardcoded. Obviously not real – but Gitleaks
   treats the pattern as a credential and fails the build.

2. VULNERABLE DEPENDENCY (pip-audit)
   urllib3==1.25.8 is listed in requirements.txt (on this branch only).
   It has known CVEs. pip-audit will flag and fail the build.

3. SQL INJECTION (Semgrep / Bandit)
   The search_notes function builds a raw SQL string using an f-string.
   A real attacker could inject SQL via the `query` parameter.
   Semgrep's OWASP rules and Bandit both catch this pattern.
"""

import sqlite3

# ── Issue 1: Hardcoded fake API key ──────────────────────────────────────────
# This is an obviously fake/dummy value – chosen to match Gitleaks' AWS key
# pattern so the pipeline demonstrates detection.
# NEVER use real credentials here or anywhere in source code.
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLEFAKEKEYDOESNOTEXIST"  # noqa: S105 – demo only


def search_notes(db_path: str, query: str) -> list:
    """
    Issue 3: SQL INJECTION – do NOT copy this pattern into real code.

    The user-supplied `query` is embedded directly into the SQL string.
    An attacker could pass: query = "' OR '1'='1" to dump all rows,
    or more dangerous payloads to modify/delete data.

    Safe fix: use parameterised queries -> cursor.execute("... WHERE title LIKE ?", (f"%{query}%",))
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # UNSAFE – never build SQL this way:
    sql = f"SELECT * FROM notes WHERE title LIKE '%{query}%'"  # noqa: S608 – demo only
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows
