#!/bin/bash

set -e
echo "=========================================="
echo "AI-DeskClean - Ollama Qwen2.5:1.5B Setup"
echo "=========================================="

if ! command -v ollama &> /dev/null; then
  echo "[ERROR] Ollama is not installed."
  echo "Install it with:"
  echo "  curl -fsSL https://ollama.com/install.sh | sh"
  echo "or see https://ollama.com/download/linux"
  read -p "Press Enter to exit..."
  exit 1
fi

echo "Starting Ollama service..."
(ollama serve &> /dev/null &) || true
sleep 2

echo "Downloading qwen2.5:1.5b. This may take time depending on internet speed..."
ollama pull qwen2.5:1.5b

echo "[SUCCESS] qwen2.5:1.5b is ready."
read -p "Press Enter to exit..."
