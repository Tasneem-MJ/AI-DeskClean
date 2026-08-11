#!/bin/bash
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] Python 3 was not found."
  echo "Install Python 3.11 or 3.12 from https://www.python.org/downloads/macos/"
  exit 1
fi

if [ ! -f ".venv/bin/python3" ]; then
  echo "Preparing AI-DeskClean for development..."
  python3 -m venv .venv
  .venv/bin/python3 -m pip install --upgrade pip
  .venv/bin/python3 -m pip install -r requirements.txt
fi

exec .venv/bin/python3 app.py
