# Multi-stage Dockerfile for the Secure Notes API
#
# Stage 1 (builder): install dependencies into an isolated venv
# Stage 2 (runtime): copy only the venv and app source – minimal attack surface

# ── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.15-slim AS builder

WORKDIR /build

# Apply security updates to base OS packages
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies into an isolated venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Install dependencies, then remove build tools from venv
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y setuptools pip || true && \
    rm -rf /opt/venv/lib/python3.12/site-packages/setuptools* \
           /opt/venv/lib/python3.12/site-packages/pip*


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.15-slim AS runtime

# Security hardening:
# 1. Update OS packages
# 2. Remove build tools (setuptools, pip) from base image to eliminate CVE-2025-47273
RUN apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/* \
           /usr/local/lib/python3.12/site-packages/setuptools* \
           /usr/local/lib/python3.12/site-packages/pip* \
           /usr/local/bin/pip*

# Non-root user with minimal privilege
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy the pre-built venv from the builder stage (cleaned of pip and setuptools)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
