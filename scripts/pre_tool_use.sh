#!/bin/bash

LOG_FILE="logs/tool_use.log"

mkdir -p "$(dirname "$LOG_FILE")"

if [ ! -f "$LOG_FILE" ]; then
  touch "$LOG_FILE"
fi

TOOL_NAME="${TOOL_NAME:-unknown}"
TOOL_INPUT="${TOOL_INPUT:-}"

echo "Tool executed at $(date '+%Y-%m-%d %H:%M:%S') | tool: $TOOL_NAME | input: $TOOL_INPUT" >> "$LOG_FILE"
