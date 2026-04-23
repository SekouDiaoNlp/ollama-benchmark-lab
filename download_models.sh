#!/usr/bin/env bash

# =========================
# SAFE MODEL DOWNLOADER
# =========================

set -euo pipefail

LOG_FILE="download_models.log"
MAX_RETRIES=3
SLEEP_BETWEEN_RETRIES=5

# -------------------------
# S / A TIER MODELS
# -------------------------

MODELS=(
  # S-tier (strongest)
  "phi3:medium"
  "qwen2.5:7b"
  "mistral:7b-instruct"
  "codellama:7b-instruct"
  "qwen2.5-coder:7b"
  "starcoder2:7b"
  "codegemma:7b"
  "granite-code:8b"

  # A-tier (fast / efficient)
  "qwen2.5:3b"
  "qwen2.5-coder:3b"
  "starcoder2:3b"
  "codegemma:2b"
  "granite-code:3b"
)

# -------------------------
# HELPERS
# -------------------------

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

is_installed() {
  ollama list | awk '{print $1}' | grep -qx "$1"
}

pull_model() {
  local model="$1"
  local attempt=1

  while (( attempt <= MAX_RETRIES )); do
    log "Pulling $model (attempt $attempt)..."

    if ollama pull "$model"; then
      log "SUCCESS: $model pulled"
      return 0
    else
      log "FAILED: $model (attempt $attempt)"
      ((attempt++))
      sleep "$SLEEP_BETWEEN_RETRIES"
    fi
  done

  log "ERROR: $model failed after $MAX_RETRIES attempts"
  return 1
}

verify_model() {
  local model="$1"

  if is_installed "$model"; then
    log "VERIFIED: $model installed"
    return 0
  else
    log "VERIFY FAILED: $model not found after pull"
    return 1
  fi
}

# -------------------------
# MAIN
# -------------------------

log "=== MODEL DOWNLOAD START ==="

for model in "${MODELS[@]}"; do
  if is_installed "$model"; then
    log "SKIP: $model already installed"
    continue
  fi

  if pull_model "$model"; then
    verify_model "$model" || true
  fi
done

log "=== DOWNLOAD COMPLETE ==="
