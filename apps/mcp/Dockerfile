FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install auth package first
COPY packages/auth packages/auth
RUN pip install -e packages/auth

# Copy requirements and install dependencies
COPY apps/mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server source
COPY apps/mcp/src ./src

# Create log directory
RUN mkdir -p /var/log/wildeditor-mcp

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8001

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Run the application
CMD ["python", "src/run_dev.py"]
