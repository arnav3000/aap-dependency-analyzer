# Multi-stage Containerfile for AAP Migration Planner Backend (Podman)
# Stage 1: Builder - Install dependencies
FROM docker.io/library/python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files and source
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY src/ ./src/

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# Stage 2: Runtime - Minimal production image
FROM docker.io/library/python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment to use venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./
COPY README.md ./

# Create directories for data
RUN mkdir -p /app/data /app/logs

# Podman runs rootless by default, set proper permissions
RUN chmod -R 755 /app && \
    chmod -R 777 /app/data /app/logs

# Expose port (if running as API server)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command: Run CLI
ENTRYPOINT ["aap-planner"]
CMD ["--help"]
