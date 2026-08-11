#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -f "ui/vendor/react.production.min.js" ]; then
    echo "Downloading offline UI libraries..."
    python3 scripts/fetch_vendor.py
fi

echo
echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo
echo "Building AI-DeskClean with PyInstaller..."
python3 -m PyInstaller --noconfirm --onefile --windowed --name AI-DeskClean --add-data "ui:ui" app.py

echo
echo "Done. The executable is in dist/."
