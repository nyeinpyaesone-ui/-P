# ERP03 Production Backend
# Python 3.12.13-slim on Debian Trixie
FROM python:3.12.13-slim@sha256:8f0e9b7c8d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/ ./apps/
COPY scripts/ ./scripts/

# Create logs directory and set permissions
RUN mkdir -p /app/logs \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Default command - run the FastAPI backend
CMD ["python", "-m", "uvicorn", "apps.erp.main:app", "--host", "0.0.0.0", "--port", "8000"]
