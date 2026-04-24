FROM python:3.11-slim

# Core system deps
RUN apt-get update && apt-get install -y \
    git \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Preinstall test tooling (CRITICAL)
RUN pip install --no-cache-dir \
    pytest \
    pytest-json-report \
    numpy \
    pydantic

# Create workspace
WORKDIR /workspace

# Keep container warm-ready
CMD ["sleep", "infinity"]