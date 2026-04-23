#!/usr/bin/env bash

set -Eeuo pipefail

# =========================
# CONFIG
# =========================
MODEL_DIR="./modelfiles"
SYSTEM_PROMPT="./system-prompts/no-yap.txt"
GLOBAL_PROMPT="./system-prompts/global-phd.txt"
LOG="build_noyap.log"

MAX_PARALLEL=2
LOCK_FILE="/tmp/noyap.lock"
TMP_SUFFIX="-tmp"

# Ensure log file exists
mkdir -p "$(dirname "$LOG")"
: > "$LOG"

# =========================
# LOCK
# =========================
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "⚠️ Another build is running. Exiting."
  exit 1
fi

# =========================
# LOGGING
# =========================
log() {
  echo "[$(date '+%F %T')] $*" | tee -a "$LOG"
}

# =========================
# MODEL CHECK
# =========================
is_installed() {
  local m="$1"
  ollama list | awk 'NR>1 {print $1}' | grep -qx "$m"
}

# =========================
# NAME NORMALIZATION
# =========================
make_model_names() {
  local raw="$1"

  local NAME_PART="${raw%%:*}"
  local TAG_PART="${raw#*:}"

  if [[ "$NAME_PART" == "$TAG_PART" ]]; then
    echo "${NAME_PART}:noyap ${NAME_PART}-tmp"
    return
  fi

  TAG_PART="${TAG_PART/.planning/-planning}"
  TAG_PART="${TAG_PART/.acting/-acting}"

  local TARGET="${NAME_PART}:${TAG_PART}-noyap"
  local TMP="${NAME_PART}:${TAG_PART}${TMP_SUFFIX}"

  echo "$TARGET $TMP"
}

# =========================
# BUILD ONE MODEL
# =========================
build_one() {
  local file="$1"

  log "Processing: $file"

  local BASE_MODEL
  BASE_MODEL=$(grep '^FROM ' "$file" | awk '{print $2}')

  [[ -z "$BASE_MODEL" ]] && {
    log "SKIP: no FROM in $file"
    return
  }

  if ! is_installed "$BASE_MODEL"; then
    log "SKIP: base model missing: $BASE_MODEL"
    return
  fi

  local NAME
  NAME=$(basename "$file" | sed 's/^Modelfile\.//')

  local TARGET_MODEL TMP_MODEL
  read -r TARGET_MODEL TMP_MODEL <<< "$(make_model_names "$NAME")"

  if is_installed "$TARGET_MODEL"; then
    log "SKIP: $TARGET_MODEL exists"
    return
  fi

  local MODE_FRAGMENT="$SYSTEM_PROMPT"

  # PLAN / ACT injection
  if [[ "$NAME" == *"planning"* ]]; then
    MODE_FRAGMENT="./system-prompts/no-yap-plan.txt"
  elif [[ "$NAME" == *"acting"* ]]; then
    MODE_FRAGMENT="./system-prompts/no-yap-act.txt"
  fi

  if [[ ! -f "$MODE_FRAGMENT" ]]; then
    log "ERROR: missing $MODE_FRAGMENT"
    return
  fi

  if [[ ! -f "$GLOBAL_PROMPT" ]]; then
    log "ERROR: missing $GLOBAL_PROMPT"
    return
  fi

  local TMPFILE
  TMPFILE=$(mktemp)

  {
    echo "FROM $BASE_MODEL"
    echo ""
    grep '^PARAMETER' "$file" || true
    echo ""
    echo "SYSTEM \"\"\""
    echo "MODEL_ID: $TARGET_MODEL"
    echo "BASE_MODEL: $BASE_MODEL"
    echo ""
    cat "$GLOBAL_PROMPT"
    echo ""
    cat "$MODE_FRAGMENT"
    echo "\"\"\""
  } > "$TMPFILE"

  log "Building: $TMP_MODEL"

  if ollama create "$TMP_MODEL" -f "$TMPFILE" >>"$LOG" 2>&1; then

    if ollama run "$TMP_MODEL" "ping" >/dev/null 2>&1; then
      ollama rm "$TARGET_MODEL" >/dev/null 2>&1 || true
      ollama cp "$TMP_MODEL" "$TARGET_MODEL"
      ollama rm "$TMP_MODEL"
      log "CREATED: $TARGET_MODEL"
    else
      log "FAILED integrity: $TMP_MODEL"
      ollama rm "$TMP_MODEL" >/dev/null 2>&1 || true
    fi
  else
    log "BUILD FAILED: $TMP_MODEL"
    ollama rm "$TMP_MODEL" >/dev/null 2>&1 || true
  fi

  rm -f "$TMPFILE"
}

export -f build_one log is_installed make_model_names
export SYSTEM_PROMPT GLOBAL_PROMPT TMP_SUFFIX LOG

# =========================
# MAIN
# =========================

FILES=()

for f in "$MODEL_DIR"/Modelfile.*; do
  [[ -f "$f" ]] && FILES+=("$f")
done

log "Models: ${#FILES[@]}"

printf "%s\n" "${FILES[@]}" | xargs -P "$MAX_PARALLEL" -I {} bash -c 'build_one "$@"' _ {}

log "DONE"

