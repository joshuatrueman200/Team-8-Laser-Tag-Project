#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
VENV_DIR="$PROJECT_DIR/.venv"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Error: $PYTHON was not found. Install Python 3.9 or newer." >&2
    exit 1
fi

if ! "$PYTHON" -m ensurepip --version >/dev/null 2>&1; then
    if ! command -v apt-get >/dev/null 2>&1; then
        echo "Error: Python venv support is missing, and apt-get is unavailable." >&2
        exit 1
    fi
    if [ "$(id -u)" -eq 0 ]; then
        APT_GET=(apt-get)
    elif command -v sudo >/dev/null 2>&1; then
        APT_GET=(sudo apt-get)
    else
        echo "Error: install python3-venv with administrator access." >&2
        exit 1
    fi
    "${APT_GET[@]}" update
    "${APT_GET[@]}" install -y python3-venv
fi

"$PYTHON" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install -r "$PROJECT_DIR/requirements.txt"
"$VENV_DIR/bin/python" -c "import pygame, psycopg2; from pygame._sdl2.video import Renderer, Texture, Window; print('Python dependencies, including pygame._sdl2, are ready.')"

echo "Setup complete. Run the game with: $VENV_DIR/bin/python $PROJECT_DIR/main.py"