#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    APT_GET=(apt-get)
else
    APT_GET=(sudo apt-get)
fi

"${APT_GET[@]}" update
"${APT_GET[@]}" install -y python3 python3-pygame python3-psycopg2

python3 -c "import pygame, psycopg2; print('Python dependencies are ready.')"

echo "Setup complete. Run the game with: python3 main.py"
