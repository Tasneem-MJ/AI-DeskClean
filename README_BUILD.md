# AI-DeskClean — build & run

## Desktop app

AI-DeskClean is a desktop application. The Windows build produces an `.exe`;
the macOS build produces a normal `.app` bundle that users can open from
Finder like any other Mac application.

The app does not need a terminal after it has been built.

## Build the app

### Windows

Double-click `build_windows.bat`.

The finished application is:

`dist/AI-DeskClean.exe`

Copy that file to another Windows computer and double-click it to launch.

### macOS

Run `build-app-mac.sh` on a Mac. This is a developer/build step, not the
normal way users launch the application.

The finished application is:

`dist/AI-DeskClean.app`

Copy `AI-DeskClean.app` to the Applications folder and double-click it from
Finder. No Python installation or terminal command is needed on the Mac that
runs the packaged app.

The first launch may show a macOS security warning because the app is not
signed or notarized. Control-click the app, choose **Open**, then choose
**Open** again. Later launches work normally.

`build-app-mac.sh` must be run on macOS because PyInstaller builds for the
operating system it is running on.

## Development

For development, the Mac helper `run-app-mac.sh` starts the Python version
directly. It is not intended as the end-user launch method.

On Windows, use the Python entry point directly when developing:

```text
python app.py
```

The application UI and backend are kept separate:

- `ui/index.html` contains the desktop UI.
- `bridge/api.py` exposes the backend to the UI through pywebview.
- `backend/engine.py` contains file scanning, classification, organization,
  undo, history, and reporting.
- `backend/security/validator.py` checks folders before organization.

## Optional local AI classification

The "By AI Content" method uses a local Ollama model. The default model is
`qwen2.5:1.5b`.

Ollama is not bundled with the application. File-type, keyword, and age-based
classification work without it.

Use the setup helper for the operating system:

- Windows: `setup-ollama.bat`
- macOS: `setup-ollama-mac.sh`
- Linux: `setup-ollama-linux.sh`

## Offline UI files

The React, ReactDOM, and Babel files used by the UI are stored in
`ui/vendor/`. `scripts/fetch_vendor.py` can refresh them if needed.

## User data

AI-DeskClean stores its settings, logs, and operation manifests in:

`~/.ai_deskclean/`

This keeps user data separate from the packaged application.
