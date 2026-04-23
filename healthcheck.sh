#!/usr/bin/env bash

echo "Checking Ollama models..."

FAILED=0

while read -r model _; do
  if ! ollama run "$model" "ping" >/dev/null 2>&1; then
    echo "BROKEN: $model"
    FAILED=1
  else
    echo "OK: $model"
  fi
done < <(ollama list | tail -n +2)

exit $FAILED
