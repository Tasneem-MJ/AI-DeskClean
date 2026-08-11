from pathlib import Path

from backend.engine import collect_files


def test_collect_files_finds_normal_files(tmp_path):
    (tmp_path / "report.pdf").touch()
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "notes.txt").touch()

    files = collect_files(tmp_path, recursive=False)

    names = {file.name for file in files}

    assert names == {"report.pdf", "photo.jpg", "notes.txt"}


def test_collect_files_ignores_hidden_files(tmp_path):
    (tmp_path / "report.pdf").touch()
    (tmp_path / ".hidden.txt").touch()

    files = collect_files(tmp_path, recursive=False)

    names = {file.name for file in files}

    assert names == {"report.pdf"}


def test_collect_files_ignores_system_file_types(tmp_path):
    (tmp_path / "report.pdf").touch()
    (tmp_path / "program.exe").touch()
    (tmp_path / "library.dll").touch()

    files = collect_files(tmp_path, recursive=False)

    names = {file.name for file in files}

    assert names == {"report.pdf"}


def test_collect_files_finds_files_recursively(tmp_path):
    main_file = tmp_path / "report.pdf"
    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()
    nested_file = subfolder / "notes.txt"

    main_file.touch()
    nested_file.touch()

    files = collect_files(tmp_path, recursive=True)

    names = {file.name for file in files}

    assert names == {"report.pdf", "notes.txt"}