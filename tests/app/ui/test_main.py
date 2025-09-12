from __future__ import annotations

import tkinter as tk
import pytest

from app.ui.main import create_app


def test_create_app_sets_title() -> None:
    try:
        app = create_app()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    try:
        assert app.title() == "Cold Calling App"
    finally:
        app.destroy()
