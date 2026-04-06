# Multi-stage build for RagyApp
# Stage 1: Builder - Install dependencies with uv
FROM python:3.12-slim as builder

# Install uv package manager
RUN pip install --no-cache-dir uv

WORKDIR /build

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies (no dev dependencies for production)
RUN uv sync --no-dev

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 ragy && \
    mkdir -p /app/ragy_db /app/.cache && \
    chown -R ragy:ragy /app

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /build/.venv /app/.venv

# Copy application code
COPY --chown=ragy:ragy ragy_api/ ./ragy_api/
COPY --chown=ragy:ragy ragy_cli/ ./ragy_cli/
COPY --chown=ragy:ragy ragy_mcp/ ./ragy_mcp/
COPY --chown=ragy:ragy conn_db/ ./conn_db/
COPY --chown=ragy:ragy conn_emb_hugging_face/ ./conn_emb_hugging_face/
COPY --chown=ragy:ragy conn_emb_ollama/ ./conn_emb_ollama/
COPY --chown=ragy:ragy conn_tavily/ ./conn_tavily/
COPY --chown=ragy:ragy conn_llm/ ./conn_llm/
COPY --chown=ragy:ragy sample_data/ ./sample_data/
COPY --chown=ragy:ragy README.md LICENSE CLAUDE.md ./

# Switch to non-root user
USER ragy

# Set environment for Python to find packages
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose API port
EXPOSE 8000

# Health check - 60s start period allows for model download on first run
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Start API server
CMD ["uvicorn", "ragy_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
