# ERP03 Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

# Copy application code
COPY apps/ ./apps/
COPY scripts/ ./scripts/

# Create logs directory
RUN mkdir -p /app/logs

# Expose API port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Default command - run the FastAPI/Flask backend
CMD ["python", "-m", "uvicorn", "apps.erp.main:app", "--host", "0.0.0.0", "--port", "8000"]
