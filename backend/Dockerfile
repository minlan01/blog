# ── Stage 1: Build Python dependencies ──
FROM python:3.12-slim AS builder

WORKDIR /build

# Compile-time deps for bcrypt / cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ──
FROM python:3.12-slim

WORKDIR /app

# Runtime deps: curl for healthcheck, libffi3 for bcrypt/cffi
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        libffi8 \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos "" appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini alembic.ini
COPY uploads/ /app/uploads-seed/
COPY entrypoint.sh /entrypoint.sh

# Create runtime directories with correct ownership
RUN mkdir -p /app/data /app/uploads/images \
    && chown -R appuser:appuser /app /entrypoint.sh \
    && chmod +x /entrypoint.sh

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
