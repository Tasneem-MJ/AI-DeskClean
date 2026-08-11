#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "==============================================="
echo "  AI-DeskClean - macOS App Builder"
echo "==============================================="

if [ "$(uname -s)" != "Darwin" ]; then
  echo "[ERROR] This script must be run on macOS."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] Python 3 was not found."
  echo "Install Python 3.11 or 3.12 from https://www.python.org/downloads/macos/"
  exit 1
fi

if [ ! -f "ui/vendor/react.production.min.js" ]; then
  echo "[1/5] Downloading UI libraries..."
  python3 scripts/fetch_vendor.py
else
  echo "[1/5] UI libraries already present."
fi

echo "[2/5] Preparing virtual environment..."
if [ ! -f ".venv/bin/python3" ]; then
  python3 -m venv .venv
fi

echo "[3/5] Installing dependencies..."
.venv/bin/python3 -m pip install --upgrade pip
.venv/bin/python3 -m pip install -r requirements.txt

echo "[4/5] Preparing the macOS app icon..."
rm -rf build dist
ICON_SOURCE="ui/assets/app_icon.png"
ICONSET="build/AI-DeskClean.iconset"
ICON_FILE="build/AI-DeskClean.icns"

if [ ! -f "$ICON_SOURCE" ]; then
  echo "[ERROR] Missing app icon: $ICON_SOURCE"
  exit 1
fi

if ! command -v iconutil >/dev/null 2>&1; then
  echo "[ERROR] macOS iconutil was not found."
  exit 1
fi

mkdir -p "$ICONSET"
sips -z 16 16 "$ICON_SOURCE" --out "$ICONSET/icon_16x16.png" >/dev/null
sips -z 32 32 "$ICON_SOURCE" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "$ICON_SOURCE" --out "$ICONSET/icon_32x32.png" >/dev/null
sips -z 64 64 "$ICON_SOURCE" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$ICON_SOURCE" --out "$ICONSET/icon_128x128.png" >/dev/null
sips -z 256 256 "$ICON_SOURCE" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$ICON_SOURCE" --out "$ICONSET/icon_256x256.png" >/dev/null
sips -z 512 512 "$ICON_SOURCE" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "$ICON_SOURCE" --out "$ICONSET/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$ICON_SOURCE" --out "$ICONSET/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o "$ICON_FILE"

echo "[5/5] Building AI-DeskClean.app..."
.venv/bin/python3 -m PyInstaller   --noconfirm   --clean   --windowed   --name "AI-DeskClean"   --icon "$ICON_FILE"   --add-data "ui:ui"   --collect-all pypdf   --collect-all docx   --collect-all openpyxl   --collect-all pptx   app.py

echo "[5/5] Finished."
echo ""
echo "[SUCCESS] AI-DeskClean.app is ready:"
echo "  $(pwd)/dist/AI-DeskClean.app"
echo ""
echo "Copy AI-DeskClean.app to Applications and double-click it to launch."
echo "The first launch may require Control-click -> Open because the app is unsigned."

open dist
