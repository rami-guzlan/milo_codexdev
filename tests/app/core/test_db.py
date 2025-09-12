from __future__ import annotations

from pathlib import Path

from app.core.db import initialize_db


def test_initialize_db_creates_file(tmp_path: Path) -> None:
    db_file = tmp_path / "calls.db"
    conn = initialize_db(db_file)
    try:
        assert db_file.exists()
        assert conn.execute("SELECT 1").fetchone() == (1,)
    finally:
        conn.close()
