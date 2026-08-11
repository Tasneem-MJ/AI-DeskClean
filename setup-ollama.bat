@echo off
chcp 65001 >nul
echo ==========================================
echo AI-DeskClean - Ollama Qwen2.5:1.5B Setup
echo ==========================================
where ollama >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Ollama is not installed.
  echo Download and install Ollama from the official Ollama website, then run this file again.
  pause
  exit /b 1
)
echo Starting Ollama service...
start "Ollama" /min ollama serve
ping 127.0.0.1 -n 4 >nul
echo Downloading qwen2.5:1.5b. This may take time depending on internet speed...
ollama pull qwen2.5:1.5b
if errorlevel 1 (
  echo [ERROR] Model download failed.
  pause
  exit /b 1
)
echo [SUCCESS] qwen2.5:1.5b is ready.
pause
