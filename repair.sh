#!/usr/bin/env bash

echo "Repairing Ollama registry..."

# Remove partials
find ~/.ollama/models/blobs -name "*partial*" -delete

# Re-pull missing models
while read -r model _; do
  if ! ollama run "$model" "ping" >/dev/null 2>&1; then
    echo "Re-pulling $model..."
    ollama pull "$model"
  fi
done < <(ollama list | tail -n +2)

echo "Repair complete."
