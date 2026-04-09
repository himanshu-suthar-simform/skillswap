#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$REPO_ROOT/logs/tool_use.log"
MAX_SIZE_BYTES=$((5 * 1024 * 1024))  # 5 MB
MAX_INPUT_LENGTH=200

mkdir -p "$(dirname "$LOG_FILE")"

if [ ! -f "$LOG_FILE" ]; then
  touch "$LOG_FILE"
fi

# Rotate log if it exceeds the maximum size
if [ -f "$LOG_FILE" ] && [ "$(wc -c < "$LOG_FILE")" -ge "$MAX_SIZE_BYTES" ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
  touch "$LOG_FILE"
fi

TOOL_NAME="${TOOL_NAME:-unknown}"
# Sanitize: strip control characters and truncate to avoid leaking sensitive data
TOOL_INPUT_RAW="${TOOL_INPUT:-}"
TOOL_INPUT_CLEAN="$(echo "$TOOL_INPUT_RAW" | tr -d '[:cntrl:]')"
TOOL_INPUT="${TOOL_INPUT_CLEAN:0:$MAX_INPUT_LENGTH}"

echo "Tool executed at $(date '+%Y-%m-%d %H:%M:%S') | tool: $TOOL_NAME | input: $TOOL_INPUT" >> "$LOG_FILE"
