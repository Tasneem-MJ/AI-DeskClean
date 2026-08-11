from pathlib import Path
import sys

from backend.security.validator import is_safe_target_folder




def test_empty_path_is_not_safe():
    assert is_safe_target_folder("") is False


def test_normal_folder_is_safe(tmp_path):
    assert is_safe_target_folder(str(tmp_path)) is True


def test_filesystem_root_is_not_safe():
    root = Path("/")

    assert is_safe_target_folder(str(root)) is False


def test_dangerous_roots_are_not_safe():
    dangerous_roots = [
        "/",
        "/system",
        "/Applications",
    ]

    for folder in dangerous_roots:
        assert is_safe_target_folder(folder) is False


def test_windows_roots_are_not_safe():
    if sys.platform != "win32":
        return

    windows_roots = [
        "c:\\",
        "c:/",
        "/windows",
    ]

    for folder in windows_roots:
        assert is_safe_target_folder(folder) is False



def test_windows_drive_root_is_not_safe():
    if sys.platform != "win32":
        return

    assert is_safe_target_folder("C:/") is False


def test_nested_normal_folder_is_safe(tmp_path):
    normal_folder = tmp_path / "MyFiles"
    normal_folder.mkdir()

    assert is_safe_target_folder(str(normal_folder)) is True
