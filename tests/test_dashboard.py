from backend.engine import compute_dashboard_stats


def test_dashboard_counts_organized_files():
    operations = [
        {
            "created_at": "2026-08-01T10:00:00",
            "undone": False,
            "moves": [
                {
                    "source": "/test/report.pdf",
                    "destination": "/test/Documents/report.pdf",
                },
                {
                    "source": "/test/photo.jpg",
                    "destination": "/test/Images/photo.jpg",
                },
            ],
        }
    ]

    stats = compute_dashboard_stats(operations)

    assert stats["operations"] == 1
    assert stats["files_organized"] == 2
    assert stats["categories"] == 2
    assert stats["undone"] == 0


def test_dashboard_does_not_count_undone_files():
    operations = [
        {
            "created_at": "2026-08-01T10:00:00",
            "undone": True,
            "moves": [
                {
                    "source": "/test/report.pdf",
                    "destination": "/test/Documents/report.pdf",
                },
            ],
        }
    ]

    stats = compute_dashboard_stats(operations)

    assert stats["operations"] == 1
    assert stats["files_organized"] == 0
    assert stats["undone"] == 1