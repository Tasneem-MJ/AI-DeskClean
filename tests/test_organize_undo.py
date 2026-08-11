from pathlib import Path

from backend.engine import move_files, undo_manifest_path


def test_files_can_be_organized_and_undone(tmp_path):
    report = tmp_path / "report.pdf"
    photo = tmp_path / "photo.jpg"

    report.write_text("test report")
    photo.write_text("test image")

    chosen = [
        {
            "path": str(report),
            "category": "Documents",
            "status": "ready",
        },
        {
            "path": str(photo),
            "category": "Images",
            "status": "ready",
        },
    ]

    manifest, _ = move_files(tmp_path, chosen)

    documents_file = tmp_path / "Documents" / "report.pdf"
    images_file = tmp_path / "Images" / "photo.jpg"

    assert documents_file.exists()
    assert images_file.exists()
    assert not report.exists()
    assert not photo.exists()

    manifest_path = tmp_path / "operation-test.json"
    import json

    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    result = undo_manifest_path(manifest_path)

    assert result["success"] is True
    assert report.exists()
    assert photo.exists()
    assert not documents_file.exists()
    assert not images_file.exists()