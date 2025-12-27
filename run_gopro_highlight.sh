#!/usr/bin/env bash
# Launcher script for gopro_highlight_gui.py
# - switches to the project directory
# - activates the virtualenv if present
# - opens a terminal and runs the script so output remains visible

set -e
cd "$(dirname "$0")" || exit 1

# Prefer to use the venv's python
VENV_ACTIVATE=".venv/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
  # Try common terminal emulators to open the process in a terminal window
  if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- bash -ic "source $VENV_ACTIVATE && python gopro_highlight_gui.py; echo; echo 'Finished (press Enter to close)'; read -r"
  elif command -v xterm >/dev/null 2>&1; then
    xterm -e bash -ic "source $VENV_ACTIVATE && python gopro_highlight_gui.py; echo; echo 'Finished (press Enter to close)'; read -r"
  elif command -v konsole >/dev/null 2>&1; then
    konsole -e bash -ic "source $VENV_ACTIVATE && python gopro_highlight_gui.py; echo; echo 'Finished (press Enter to close)'; read -r"
  else
    # No terminal emulator found — run in current shell
    echo "No terminal emulator found; running in the current shell..."
    source "$VENV_ACTIVATE"
    python gopro_highlight_gui.py
  fi
else
  echo ".venv not found — running system Python"
  python gopro_highlight_gui.py
fi
