#!/bin/bash

LOG_FILE="logs/session.log"
MAX_SIZE_BYTES=$((5 * 1024 * 1024))  # 5 MB

mkdir -p "$(dirname "$LOG_FILE")"

if [ ! -f "$LOG_FILE" ]; then
  touch "$LOG_FILE"
fi

# Rotate log if it exceeds the maximum size
if [ -f "$LOG_FILE" ] && [ "$(wc -c < "$LOG_FILE")" -ge "$MAX_SIZE_BYTES" ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
  touch "$LOG_FILE"
fi

echo "Session started at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
