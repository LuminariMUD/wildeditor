FROM python:3.14.6-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONPATH=/app \
    PORT=8001

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY apps/mcp/requirements.txt .
COPY packages/auth packages/auth
RUN python -m pip install --no-cache-dir --upgrade \
      pip==26.2.1 setuptools==83.0.0 wheel==0.47.0 && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir --no-deps -e packages/auth && \
    python -m pip check

# Copy MCP server source
COPY apps/mcp/src ./src

# Create log directory
RUN mkdir -p /var/log/wildeditor-mcp && \
    useradd --create-home --uid 1000 mcp && \
    chown -R mcp:mcp /app /var/log/wildeditor-mcp
USER mcp

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
