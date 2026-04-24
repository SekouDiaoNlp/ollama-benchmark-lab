FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git curl bash && rm -rf /var/lib/apt/lists/*

RUN pip install pytest

WORKDIR /workspace

CMD ["sleep", "infinity"]