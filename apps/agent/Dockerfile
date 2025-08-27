# Dockerfile for Chat Agent Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY apps/agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
  CMD python -c "import requests; requests.get('http://localhost:8002/health/')" || exit 1

# Expose port
EXPOSE 8002

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002", "--log-level", "info"]