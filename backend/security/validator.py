import os
from pathlib import Path


DANGEROUS_ROOTS = {
    "c:\\",
    "c:/",
    "/",
    "/system",
    "/windows",
    "/applications",
}


def is_safe_target_folder(folder_path: str) -> bool:
    """Return True when the folder is safe to organize."""

    if not folder_path:
        return False

    resolved = str(Path(folder_path).resolve()).lower()

    normalized = resolved.replace("\\", "/")

    if normalized.rstrip("/") == "":
        return False

    for dangerous in DANGEROUS_ROOTS:
        if normalized.rstrip("/") == dangerous.rstrip("/"):
            return False

    if len(normalized) <= 3 and normalized.endswith(":/"):
        return False

    return True


def is_within_folder(file_path: str, folder_path: str) -> bool:

    try:
        Path(file_path).resolve().relative_to(
            Path(folder_path).resolve()
        )
        return True

    except ValueError:
        return False


def validate_folder_writable(folder_path: str) -> bool:

    return os.path.isdir(folder_path) and os.access(
        folder_path, os.W_OK
    )
