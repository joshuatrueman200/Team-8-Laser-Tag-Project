#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
VENV_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/team-8-laser-tag/venv"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Error: $PYTHON was not found. Install Python 3.9 or newer." >&2
    exit 1
fi

if ! "$PYTHON" -m venv "$VENV_DIR"; then
    if ! command -v apt-get >/dev/null 2>&1; then
        echo "Error: could not create the virtual environment, and apt-get is unavailable. Install Python venv support." >&2
        exit 1
    fi
    if [ "$(id -u)" -eq 0 ]; then
        APT_GET=(apt-get)
    elif command -v sudo >/dev/null 2>&1; then
        APT_GET=(sudo apt-get)
    else
        echo "Error: install python3-venv with administrator access, then rerun this script." >&2
        exit 1
    fi
    "${APT_GET[@]}" update
    "${APT_GET[@]}" install -y python3-venv
    "$PYTHON" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade "pygame==2.6.1" "psycopg2-binary==2.9.13"
"$VENV_DIR/bin/python" -c "import pygame, psycopg2; print('Python dependencies are ready.')"

echo "Setup complete. Run the game with: cd \"$PROJECT_DIR\" && PGDATABASE=photon \"$VENV_DIR/bin/python\" main.py"