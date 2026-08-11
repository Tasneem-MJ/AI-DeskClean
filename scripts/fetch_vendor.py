"""
Run this ONCE, on a computer with internet access, before building the .exe.

It downloads the three JavaScript files the app's UI needs (React,
ReactDOM, and the Babel browser compiler) into ui/vendor/, so the app
can run completely offline afterwards - no internet connection needed
to use AI-DeskClean itself, only to fetch these three files the first
time.

Usage:
    python scripts/fetch_vendor.py
"""

from __future__ import annotations

import pathlib
import urllib.request

FILES = {
    "react.production.min.js": "https://unpkg.com/react@18/umd/react.production.min.js",
    "react-dom.production.min.js": "https://unpkg.com/react-dom@18/umd/react-dom.production.min.js",
    "babel.min.js": "https://unpkg.com/@babel/standalone/babel.min.js",
}


def main() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    vendor_dir = root / "ui" / "vendor"
    vendor_dir.mkdir(parents=True, exist_ok=True)

    for filename, url in FILES.items():
        dest = vendor_dir / filename
        print(f"Downloading {filename} ...")
        try:
            urllib.request.urlretrieve(url, dest)
            size_kb = dest.stat().st_size / 1024
            print(f"  saved to {dest} ({size_kb:.0f} KB)")
        except Exception as error:  # noqa: BLE001
            print(f"  FAILED: {error}")
            print(
                "  You can also download this file manually from the URL "
                "above and save it at the path shown."
            )

    print("\nDone. You only need to do this once - the files are reused")
    print("every time you build or run the app from now on.")


if __name__ == "__main__":
    main()
