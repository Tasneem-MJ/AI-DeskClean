from pathlib import Path

from backend.engine import extension_category


def test_pdf_is_document():
    assert extension_category(Path("report.pdf")) == "Documents"


def test_docx_is_document():
    assert extension_category(Path("assignment.docx")) == "Documents"


def test_jpg_is_image():
    assert extension_category(Path("photo.jpg")) == "Images"


def test_mp4_is_media():
    assert extension_category(Path("lecture.mp4")) == "Media"


def test_python_file_is_code():
    assert extension_category(Path("program.py")) == "Code"


def test_zip_is_archive():
    assert extension_category(Path("project.zip")) == "Archives"


def test_unknown_extension_is_other():
    assert extension_category(Path("something.xyz")) == "Other"