#!/bin/bash

LOG_FILE="logs/session.log"

mkdir -p "$(dirname "$LOG_FILE")"

if [ ! -f "$LOG_FILE" ]; then
  touch "$LOG_FILE"
fi

echo "Session started at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
