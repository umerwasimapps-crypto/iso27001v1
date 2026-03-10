# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV UV_SYSTEM_PYTHON=1 \
    HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY src ./src
COPY knowledge_base ./knowledge_base
COPY memory ./memory
COPY policies ./policies

# Pre-build vector DB (optional)
RUN HUGGINGFACE_EMBEDDING_MODEL="BAAI/bge-m3" uv run python -m iso27001.knowledge.rag_loader || true

VOLUME ["/app/outputs", "/app/vector_db"]

ENV HUGGINGFACE_EMBEDDING_MODEL="BAAI/bge-m3"

CMD ["uv", "run", "crewai", "run"]
