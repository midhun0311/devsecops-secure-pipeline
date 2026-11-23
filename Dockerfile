# Multi-stage Dockerfile for the Secure Notes API
#
# Stage 1 (builder): install dependencies into an isolated venv
# Stage 2 (runtime): copy only the venv and app source – minimal attack surface

# ── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Apply security updates to base OS packages
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies into an isolated venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Upgrade pip and setuptools, install requirements, then remove build tools
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y setuptools pip


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Apply security updates to base OS packages and upgrade/remove global setuptools to eliminate CVE-2025-47273
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade "setuptools>=78.1.1" || true

# Non-root user with minimal privilege
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy the pre-built venv from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
