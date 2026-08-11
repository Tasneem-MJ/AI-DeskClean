@echo off
setlocal

cd /d "%~dp0"

if not exist "ui\vendor\react.production.min.js" (
    echo Downloading offline UI libraries - one-time step...
    python scripts\fetch_vendor.py
    if errorlevel 1 goto :error
)

echo.
echo Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Building AI-DeskClean.exe with PyInstaller...
python -m PyInstaller --noconfirm --onefile --windowed --name AI-DeskClean --icon "ui\assets\app_icon.ico" --add-data "ui;ui" app.py
if errorlevel 1 goto :error

echo.
echo ============================================================
echo  Done. Your app is at: dist\AI-DeskClean.exe
echo  Copy that one file anywhere on this computer and run it.
echo ============================================================
pause
exit /b 0

:error
echo.
echo Build failed - see the message above.
pause
exit /b 1
