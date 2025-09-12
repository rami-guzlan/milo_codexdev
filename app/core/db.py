"""Database helpers for managing the application's SQLite store.

This module currently contains placeholder functions that will be
implemented in future iterations.
"""

from __future__ import annotations

from pathlib import Path

import sqlite3


def initialize_db(db_path: Path) -> sqlite3.Connection:
    """Return a connection to the SQLite database located at ``db_path``.

    Parameters
    ----------
    db_path:
        Location of the SQLite database file.

    Returns
    -------
    sqlite3.Connection
        An open connection to the database.
    """
    return sqlite3.connect(db_path)
