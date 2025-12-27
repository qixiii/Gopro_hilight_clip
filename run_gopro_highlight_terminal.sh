#!/usr/bin/env bash
# Terminal wrapper for gopro_highlight_gui.py
# - switches to project dir
# - activates .venv if present
# - appends stdout/stderr to /home/qixi/code/gopro_run.log
# - waits for Enter so terminal remains open after the script finishes

set -e
cd "$(dirname "$0")" || exit 1
LOG="/home/qixi/code/gopro_run.log"

echo "=== Run started at $(date --iso-8601=seconds) ===" >> "$LOG"
if [ -f ".venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  source ".venv/bin/activate"
fi

python gopro_highlight_gui.py >> "$LOG" 2>&1 || echo "Script exited with status $? (see $LOG)" >> "$LOG"

echo "=== Run finished at $(date --iso-8601=seconds) ===" >> "$LOG"
echo "Output appended to $LOG"
read -rp "Press Enter to close..." 
