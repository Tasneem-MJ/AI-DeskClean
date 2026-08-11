"""AI-DeskClean desktop entry point."""

from __future__ import annotations

from pathlib import Path
import sys

import webview

from bridge.api import DesktopAPI


def resource_path(relative_path: str) -> Path:
    """Return a resource path for development or a packaged app."""

    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


def main() -> None:
    api = DesktopAPI()
    ui_path = resource_path("ui/index.html")
    icon_path = resource_path("ui/assets/app_icon.ico")

    if not ui_path.exists():
        raise FileNotFoundError(
            f"UI file was not found: {ui_path}"
        )

    webview.settings["DRAG_REGION_SELECTOR"] = ".pywebview-drag-region"

    webview.create_window(
        title="AI-DeskClean",
        url=ui_path.as_uri(),
        js_api=api,
        width=1280,
        height=800,
        min_size=(1000, 650),
        resizable=True,
        frameless=True,
        easy_drag=False,
        background_color="#F0EEE9",
    )

    webview.start(
        debug=False,
        icon=str(icon_path) if icon_path.exists() else None,
    )


if __name__ == "__main__":
    main()