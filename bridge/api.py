from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import webview

from backend.engine import (
    APP_DIR,
    BACKUP_DIR,
    OLLAMA_MODEL,
    OLLAMA_MODELS,
    academic_category_with_confidence,
    age_category,
    collect_files,
    compute_dashboard_stats,
    extension_category,
    list_operations,
    move_files,
    ollama_ready,
    read_settings,
    report_breakdown,
    rule_category,
    rules_from_structured,
    save_manifest,
    undo_manifest_path,
    write_settings,
)
from backend.security.validator import is_safe_target_folder


def _manifest_entry(op: dict[str, Any]) -> dict[str, Any]:
    """Convert an operation manifest to the format used by the UI."""

    created_at = op.get("created_at", "")
    try:
        ts = datetime.fromisoformat(created_at).timestamp()
    except Exception:
        ts = 0.0

    moves = op.get("moves", [])
    errors = op.get("errors", [])

    return {
        "id": int(ts * 1000) if ts else abs(hash(op.get("_path", ""))) % (10**12),
        "folder": op.get("root", ""),
        "timestamp": ts,
        "method": op.get("method"),
        "undone": bool(op.get("undone")),
        "moved_count": len(moves),
        "error_count": len(errors),
        "operations": [
            {
                "file_name": Path(m["destination"]).name,
                "original_path": m["source"],
                "new_path": m["destination"],
            }
            for m in moves
        ],
        "errors": [
            {"path": e.get("file", ""), "error": e.get("error", "")} for e in errors
        ],
    }


class DesktopAPI:

    def __init__(self) -> None:
        self.selected_folder: Path | None = None
        self.scanned_paths: list[Path] = []
        self.classified_files: list[dict[str, Any]] = []

        self._classify_offset: int = 0
        self._classify_method: str = "extension"
        self._classify_model_name: str = OLLAMA_MODEL
        self._classify_rules: list[tuple[str, list[str]]] = []
        self._classify_results: list[dict[str, Any]] = []


    def choose_folder(self) -> dict[str, Any]:
        """Open the native folder-selection dialog."""

        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)

        if not result:
            return {"success": False, "path": "", "message": "No folder was selected."}

        folder = Path(result[0]).resolve()

        if not is_safe_target_folder(str(folder)):
            return {
                "success": False,
                "path": str(folder),
                "message": (
                    "This folder cannot be used. Please choose a specific "
                    "folder rather than a whole drive or system directory."
                ),
            }

        self.selected_folder = folder

        return {
            "success": True,
            "path": str(self.selected_folder),
            "message": "Folder selected successfully.",
        }


    def scan_folder(self, include_subfolders: bool = True) -> dict[str, Any]:

        if self.selected_folder is None:
            return {"success": False, "count": 0, "message": "Select a folder first."}

        try:
            files = collect_files(self.selected_folder, bool(include_subfolders))
        except Exception as error:
            return {"success": False, "count": 0, "message": f"Scan failed: {error}"}

        if not files:
            return {
                "success": False,
                "count": 0,
                "message": "No scannable files were found in this scope.",
            }

        self.scanned_paths = files

        settings = read_settings()
        settings["recursive"] = bool(include_subfolders)
        write_settings(settings)

        return {
            "success": True,
            "count": len(files),
            "message": "Scan completed successfully.",
        }


    def get_ai_models(self) -> dict[str, Any]:
        """Return the available local AI models."""

        return {"success": True, "models": OLLAMA_MODELS, "default": OLLAMA_MODEL}

    def get_categories(self) -> dict[str, Any]:
        """Return categories available for manual reassignment."""

        from backend.engine import EXT_GROUPS

        names = list(EXT_GROUPS.keys()) + [
            "Other",
            "Last 30 Days",
            "1-6 Months",
            "6-12 Months",
            "1-2 Years",
            "Older than 2 Years",
        ]
        categories = {name: [""] for name in names}
        return {"success": True, "categories": categories}

    def classify_files_start(
        self,
        use_ai: bool = False,
        method: str = "extension",
        model_name: str | None = None,
        keyword_rules: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Prepare a new classification run. The UI then calls
        classify_files_batch() repeatedly to process the files a chunk
        at a time, so it can display a live completion percentage.
        """

        if not self.scanned_paths:
            return {"success": False, "total": 0, "message": "Scan a folder first."}

        resolved_method = method if method in {"extension", "ai", "keywords", "age"} else "extension"
        if use_ai:
            resolved_method = "ai"

        if resolved_method == "ai":
            chosen_model = model_name if model_name in OLLAMA_MODELS.values() else OLLAMA_MODEL

            if not ollama_ready(chosen_model):
                return {
                    "success": False,
                    "total": 0,
                    "message": (
                        f"Could not connect to Ollama or {chosen_model} is missing. "
                        "Run setup-ollama.bat and try again."
                    ),
                }

            self._classify_model_name = chosen_model
            settings = read_settings()
            settings["ollama_model"] = chosen_model
            write_settings(settings)
        else:
            self._classify_model_name = OLLAMA_MODEL

        self._classify_offset = 0
        self._classify_method = resolved_method
        self._classify_rules = rules_from_structured(keyword_rules)
        self._classify_results = []

        return {
            "success": True,
            "total": len(self.scanned_paths),
            "method": resolved_method,
        }

    def _classify_one_path(self, path: Path) -> dict[str, Any]:
        """Classify a single file according to the active method."""

        status = "ready"
        error = ""

        try:
            if self._classify_method == "extension":
                category = extension_category(path)
                confidence = 1.0
            elif self._classify_method == "age":
                category = age_category(path)
                confidence = 1.0
            elif self._classify_method == "keywords":
                category = rule_category(path, self._classify_rules, True)
                confidence = 1.0 if category != "Other" else 0.0
            elif self._classify_method == "ai":
                category, confidence = academic_category_with_confidence(
                    path, self._classify_model_name
                )
            else:
                category, confidence = "Other", 0.0
        except Exception as exc:
            category, confidence = "Other", 0.0
            status, error = "error", str(exc)

        try:
            stat = path.stat()
            size, modified = stat.st_size, stat.st_mtime
        except OSError:
            size, modified = 0, 0

        return {
            "path": str(path),
            "name": path.name,
            "extension": path.suffix,
            "size": size,
            "modified": modified,
            "category": category,
            "subcategory": "",
            "confidence": confidence,
            "method": self._classify_method,
            "is_duplicate": False,
            "requires_review": category == "Other",
            "status": status,
            "error": error,
        }

    def classify_files_batch(self, batch_size: int = 20) -> dict[str, Any]:
        """
        Classify the next chunk of files and report progress. Call
        classify_files_start() once first, then keep calling this until
        ``done`` is True.
        """

        total = len(self.scanned_paths)

        if total == 0:
            return {"success": False, "message": "Scan a folder first."}

        start = self._classify_offset
        end = min(start + max(1, batch_size), total)
        batch = self.scanned_paths[start:end]

        batch_results: list[dict[str, Any]] = []
        for path in batch:
            result = self._classify_one_path(path)
            batch_results.append(result)
            self._classify_results.append(result)

        self._classify_offset = end
        done = end >= total

        if done:
            self.classified_files = self._classify_results

        return {
            "success": True,
            "results": batch_results,
            "all_results": self._classify_results if done else None,
            "processed": end,
            "total": total,
            "done": done,
            "duplicate_count": 0,
        }

    def update_classification(
        self, path: str, category: str, subcategory: str
    ) -> dict[str, Any]:
        """Let the user manually override a suggested classification."""

        for file_data in self.classified_files:
            if file_data.get("path") == path:
                file_data["category"] = category
                file_data["subcategory"] = subcategory
                file_data["requires_review"] = False
                file_data["method"] = "manual"
                return {"success": True, "message": "Classification updated."}

        return {"success": False, "message": "File not found in results."}


    def organize_files(self, excluded_paths: list[str] | None = None) -> dict[str, Any]:

        if self.selected_folder is None:
            return {"success": False, "message": "Select a folder first."}

        if not self.classified_files:
            return {"success": False, "message": "Classify the scanned files first."}

        excluded = set(excluded_paths or [])
        chosen = [
            f
            for f in self.classified_files
            if f["path"] not in excluded and f.get("status", "ready") == "ready"
        ]

        if not chosen:
            return {"success": False, "message": "No files selected to organize."}

        manifest, time_taken = move_files(self.selected_folder, chosen)
        manifest["method"] = self._classify_method
        manifest["model"] = self._classify_model_name if self._classify_method == "ai" else None
        save_manifest(manifest)

        entry = _manifest_entry(manifest)
        entry.update(
            {
                "success": True,
                "message": "Organization completed.",
                "time_taken": time_taken,
            }
        )
        return entry


    def undo_last_operation(self) -> dict[str, Any]:
        """Restore every file moved by the most recent organize run."""

        latest = BACKUP_DIR / "latest.txt"
        if not latest.exists():
            return {
                "success": False,
                "restored_count": 0,
                "error_count": 0,
                "message": "There is no previous operation to undo.",
            }

        try:
            manifest_path = Path(latest.read_text(encoding="utf-8").strip())
        except Exception:
            return {
                "success": False,
                "restored_count": 0,
                "error_count": 0,
                "message": "There is no previous operation to undo.",
            }

        return undo_manifest_path(manifest_path)

    def get_history(self) -> dict[str, Any]:
        """Return every previously recorded organize operation."""

        return {"success": True, "history": [_manifest_entry(op) for op in list_operations()]}

    def get_dashboard_stats(self) -> dict[str, Any]:
        """Return dashboard totals and recent operations."""

        operations = list_operations()
        stats = compute_dashboard_stats(operations)
        recent = [_manifest_entry(op) for op in operations[:5]]

        latest = BACKUP_DIR / "latest.txt"
        can_undo = False
        if latest.exists():
            try:
                manifest_path = Path(latest.read_text(encoding="utf-8").strip())
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                can_undo = not manifest.get("undone")
            except Exception:
                can_undo = False

        return {
            "success": True,
            "stats": stats,
            "recent": recent,
            "can_undo": can_undo,
        }


    def get_reports(self) -> dict[str, Any]:
        """Return cumulative organization totals and breakdowns."""

        return {"success": True, "report": report_breakdown(list_operations())}

    def get_settings(self) -> dict[str, Any]:
        """Return the persisted app settings (language, recursive scan, model)."""

        return {"success": True, "settings": read_settings()}

    def save_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        """Persist app settings (e.g. the selected UI language)."""

        current = read_settings()
        current.update(settings or {})
        write_settings(current)
        return {"success": True, "settings": current}

    def restore_from_history(self, entry_id: int) -> dict[str, Any]:
        """Restore files from an arbitrary past history entry."""

        for op in list_operations():
            if _manifest_entry(op)["id"] == entry_id:
                return undo_manifest_path(Path(op["_path"]))

        return {
            "success": False,
            "restored_count": 0,
            "error_count": 0,
            "message": "History entry not found.",
        }


    def close_application(self) -> bool:
        """Close the desktop window."""

        webview.windows[0].destroy()
        return True

    def minimize_window(self) -> bool:
        """Minimize the desktop window to the taskbar."""

        webview.windows[0].minimize()
        return True

    def maximize_window(self) -> bool:
        """Maximize the desktop window."""

        webview.windows[0].maximize()
        return True

    def restore_window(self) -> bool:
        """Restore the desktop window from a maximized state."""

        webview.windows[0].restore()
        return True

    def open_folder(self, path: str) -> dict[str, Any]:
        """Open ``path`` in the operating system's file explorer."""

        folder = Path(path) if path else self.selected_folder

        if not folder or not folder.exists():
            return {"success": False, "message": "Folder not found."}

        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", str(folder)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])

            return {"success": True, "message": "Folder opened."}

        except Exception as error:
            return {"success": False, "message": f"Could not open folder: {error}"}
