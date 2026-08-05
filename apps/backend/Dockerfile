# FastAPI Backend Dockerfile
FROM python:3.14.6-slim

LABEL org.opencontainers.image.title="Wildeditor Backend" \
      org.opencontainers.image.description="FastAPI backend for Luminari Wilderness Editor"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PORT=8000

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY apps/backend/src/requirements.txt ./requirements.txt
COPY packages/auth packages/auth

# Install Python dependencies
RUN python -m pip install --no-cache-dir --upgrade \
      pip==26.2.1 setuptools==83.0.0 wheel==0.47.0 && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir --no-deps -e packages/auth && \
    python -m pip check

# Copy application code
COPY apps/backend/src/ ./src/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
