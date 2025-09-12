from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.core.io_paths import build_transcript_directory


def test_build_transcript_directory_formats_path(tmp_path: Path) -> None:
    base = tmp_path / "Documents" / "Call Transcripts"
    start = datetime(2024, 1, 2, 15, 30)
    path = build_transcript_directory(base, "ACME", "DoeJohn", start, "UTC", "NoAnswer")
    expected = base / "2024" / "01" / "ACME_DoeJohn_2024-01-02_1530_UTC_NoAnswer"
    assert path == expected
