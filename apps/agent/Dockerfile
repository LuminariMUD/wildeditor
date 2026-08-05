# Dockerfile for Chat Agent Service
FROM python:3.14.6-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY apps/agent/requirements.txt .
COPY packages/auth packages/auth
RUN python -m pip install --no-cache-dir --upgrade \
      pip==26.2.1 setuptools==83.0.0 wheel==0.47.0 && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir --no-deps -e packages/auth && \
    python -m pip check

# Copy application code
COPY apps/agent/src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Environment variables (these will be overridden by docker-compose or GitHub Actions)
ENV HOST=0.0.0.0
ENV PORT=8002
ENV LOG_LEVEL=INFO
ENV STORAGE_BACKEND=memory
ENV SESSION_TTL=86400

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8002/health/ready', timeout=2)" || exit 1

# Expose port
EXPOSE 8002

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002", "--log-level", "info"]
