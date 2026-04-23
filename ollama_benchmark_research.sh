#!/usr/bin/env bash

set -Eeuo pipefail

# =========================
# CONFIG
# =========================

TIMEOUT=240
RETRIES=2

REPORT="ollama_report.md"
CSV="ollama_stats.csv"
LOG="ollama_raw.log"

: > "$REPORT"
: > "$CSV"
: > "$LOG"

# =========================
# SAFETY CHECKS
# =========================

echo "=============================="
echo "OLLAMA BENCHMARK v9 (CAPABILITY AWARE)"
echo "=============================="

if ! pgrep -f "ollama serve" > /dev/null; then
  echo "? ERROR: ollama serve is not running"
  exit 1
fi

MODEL_DIR="$HOME/.ollama/models"

if [[ ! -d "$MODEL_DIR" ]]; then
  echo "? ERROR: model directory missing"
  exit 1
fi

PARTIAL_COUNT=$(find "$MODEL_DIR" -type f -name "*partial*" 2>/dev/null | wc -l)

if [[ "$PARTIAL_COUNT" -gt 0 ]]; then
  echo "? WARNING: partial blobs detected ($PARTIAL_COUNT)"
  echo "Continuing anyway (benchmark-safe mode)"
fi

# =========================
# MODEL LOAD
# =========================

mapfile -t MODELS < <(
  ollama list | awk 'NR>1 {print $1}'
)

if [[ ${#MODELS[@]} -eq 0 ]]; then
  echo "? No models found"
  exit 1
fi

echo "? Models detected: ${#MODELS[@]}"

# =========================
# PROMPTS
# =========================

PLAN_PROMPTS=(
"Design a production ETL system in Python for streaming JSONL logs with validation, retries, and Parquet output."
"Design a testing architecture for a FastAPI ML inference system with unit, integration, and load layers."
"Design a distributed Python task system with retries, idempotency, workers, and observability."
"Design an NLP evaluation framework with pluggable metrics, dataset versioning, and experiment tracking."
"Design a typed Python SDK for REST APIs with auth, retry logic, and rate limiting."
)

ACT_PROMPTS=(
"Implement a 60–80 line Python module for streaming JSONL ingestion with validation, logging, and lazy iteration."
"Implement a thread-safe LRU cache with TTL using only Python stdlib."
"Implement a job queue system with worker threads, retry logic, and exponential backoff."
)

# =========================
# MODEL TAG DETECTION (NEW)
# =========================

get_model_tags() {
  local model="$1"

  if [[ "$model" == *"planning"* ]]; then
    echo "planning"
  elif [[ "$model" == *"acting"* ]]; then
    echo "acting"
  else
    echo "general"
  fi
}

# =========================
# SAFE RUNNER
# =========================

run_model() {
  local model="$1"
  local mode="$2"
  local prompt="$3"

  local attempt=1
  local output=""
  local duration=0

  while (( attempt <= RETRIES )); do

    echo "[RUN] $model | $mode | attempt $attempt"

    START=$(date +%s)

    if output=$(timeout -k 5 "$TIMEOUT" bash -c \
      "printf '%s\n\n%s\n' \"$mode\" \"$prompt\" | ollama run \"$model\"" 2>&1); then
      END=$(date +%s)
      duration=$((END - START))
      break
    fi

    echo "[WARN] retrying $model ($attempt)"
    ((attempt++))
  done

  SIZE_BYTES=$(printf "%s" "$output" | wc -c)

  # NEW: capability detection
  MODEL_TAG=$(get_model_tags "$model")

  echo "$model,$MODEL_TAG,$mode,$duration,$SIZE_BYTES" >> "$CSV"

  {
    echo "===== $model | $mode ====="
    echo "Tag: $MODEL_TAG"
    echo "Time: ${duration}s"
    echo "Bytes: ${SIZE_BYTES}"
    echo ""
    echo "$output"
    echo ""
  } >> "$LOG"

  {
    echo "## $model ? $mode ($MODEL_TAG)"
    echo ""
    echo "- Time: ${duration}s"
    echo "- Size: ${SIZE_BYTES} bytes"
    echo ""
    echo '```'
    echo "$output"
    echo '```'
    echo "---"
  } >> "$REPORT"
}

# =========================
# WARMUP
# =========================

echo "[WARMUP] Running first model lightly..."
if [[ ${#MODELS[@]} -gt 0 ]]; then
  timeout 30 ollama run "${MODELS[0]}" "warmup" >/dev/null 2>&1 || true
fi

# =========================
# BENCHMARK LOOP
# =========================

for model in "${MODELS[@]}"; do

  echo ""
  echo "######################################"
  echo "MODEL: $model"
  echo "######################################"

  for p in "${PLAN_PROMPTS[@]}"; do
    run_model "$model" "PLAN" "$p"
  done

  for p in "${ACT_PROMPTS[@]}"; do
    run_model "$model" "ACT" "$p"
  done

done

echo ""
echo "=============================="
echo "DONE"
echo "Report: $REPORT"
echo "CSV:    $CSV"
echo "Log:    $LOG"
echo "=============================="