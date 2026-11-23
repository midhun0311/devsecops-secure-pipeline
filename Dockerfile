# Multi-stage Dockerfile for the Secure Notes API
#
# Stage 1 (builder): install dependencies into a venv
# Stage 2 (runtime): copy only the venv and app source – no build tools in production
#
# WHY multi-stage?
# - Keeps the final image small (no pip, compilers, or test packages).
# - Reduces attack surface: fewer packages = fewer potential CVEs.

# ── Stage 1: builder ────────────────────────────────────────────────────────
# Pin the exact digest so the build is reproducible and immune to tag rewriting.
FROM python:3.12.7-slim AS builder

WORKDIR /build

# Install dependencies into an isolated venv so they are easy to copy.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12.7-slim AS runtime

# WHY non-root user?
# If the app process is ever compromised, the attacker gets UID 10001 with
# no home directory, sudo rights, or ability to write outside /app.
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy the pre-built venv from the builder stage (no pip in this layer).
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the application source – no tests, Dockerfiles, or .env files.
COPY app/ ./app/

# Switch to the non-root user BEFORE the final CMD.
USER appuser

EXPOSE 8000

# WHY not CMD ["python", "-m", "uvicorn", ...]?
# Using exec form (JSON array) means signals like SIGTERM reach uvicorn
# directly instead of being swallowed by a shell wrapper.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
