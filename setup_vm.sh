#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Error: $PYTHON was not found. Install Python 3.9 or newer." >&2
    exit 1
fi

if ! "$PYTHON" -c "import pygame, psycopg2" >/dev/null 2>&1; then
    if ! command -v apt-get >/dev/null 2>&1; then
        echo "Error: pygame or psycopg2 is missing, and apt-get is unavailable." >&2
        exit 1
    fi
    if [ "$(id -u)" -eq 0 ]; then
        APT_GET=(apt-get)
    elif command -v sudo >/dev/null 2>&1; then
        APT_GET=(sudo apt-get)
    else
        echo "Error: install python3-pygame and python3-psycopg2 with administrator access." >&2
        exit 1
    fi
    "${APT_GET[@]}" update
    "${APT_GET[@]}" install -y python3-pygame python3-psycopg2
fi

"$PYTHON" -c "import pygame, psycopg2; print('Python dependencies are ready.')"

echo "Setup complete. Run the game with: cd '$PROJECT_DIR' && PGDATABASE=photon $PYTHON main.py"