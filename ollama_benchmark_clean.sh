add a set of prompts for the benchmark that will really probe which model is best for me. The code samples given to the agent must be at least 30 lines of code. I am a 40} years old NLP PhD researcher. I have almost 20 years of experience in python and programming in general. all my projects have test suites and type declarations so I need only minimal explanations and can review the code changes made by the agent both by hand and in an automated manner. Display the full content of the updated file.

ollama_bensmark.sh

#!/usr/bin/env bash

set -Eeuo pipefail

# =========================
# CONFIG
# =========================
TIMEOUT=180

REPORT="ollama_report.md"
CSV="ollama_stats.csv"
LOG="ollama_raw.log"

: > "$REPORT"
: > "$CSV"
: > "$LOG"

# =========================
# PROMPT
# =========================
PROMPT="Write a Python function that checks if a string is a palindrome. Keep it concise."

# =========================
# MODELS
# =========================
mapfile -t MODELS < <(ollama list | awk 'NR>1 {print $1}')

# =========================
# RUN FUNCTION
# =========================
run_model() {
  local model="$1"

  echo ""
  echo "======================================"
  echo "MODEL: $model"
  echo "======================================"

  local tmp
  tmp=$(mktemp)

  echo "[1] START"

  START=$(date +%s)

  echo "[2] RUNNING ollama (LIVE OUTPUT ENABLED)"
  echo "--------------------------------------"

  # =========================================================
  # LIVE STREAMING VERSION:
  # - output goes to screen
  # - AND to temp file for logging
  # - no pipe chains that can deadlock
  # =========================================================

  if timeout "$TIMEOUT" bash -c \
    "ollama run \"$model\" --verbose <<< \"$PROMPT\" | tee \"$tmp\"" \
    2>&1; then
    echo ""
    echo "[3] FINISHED OK"
  else
    echo ""
    echo "[3] TIMEOUT / ERROR"
  fi

  END=$(date +%s)
  DURATION=$((END - START))

  echo "[4] READING OUTPUT"
  OUTPUT=$(cat "$tmp")
  rm -f "$tmp"

  SIZE=${#OUTPUT}

  echo "[5] OUTPUT SIZE: $SIZE chars"

  # =========================
  # LOGGING
  # =========================

  {
    echo "===== MODEL: $model ====="
    echo "$OUTPUT"
    echo ""
  } >> "$LOG"

  echo "$model,$DURATION,$SIZE" >> "$CSV"

  {
    echo "## $model"
    echo ""
    echo "**Time:** ${DURATION}s"
    echo "**Output size:** ${SIZE}"
    echo ""
    echo '```'
    echo "$OUTPUT"
    echo '```'
    echo ""
    echo "---"
  } >> "$REPORT"

  echo "[6] DONE"
}

# =========================
# MAIN LOOP
# =========================

echo "=============================="
echo "OLLAMA CLEAN BENCHMARK v5 (LIVE)"
echo "Models: ${#MODELS[@]}"
echo "=============================="

for model in "${MODELS[@]}"; do
  run_model "$model"
done

echo ""
echo "=============================="
echo "DONE"
echo "Report: $REPORT"
echo "CSV:    $CSV"
echo "Log:    $LOG"
echo "=============================="cdcd
