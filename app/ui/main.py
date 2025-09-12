"""Entry point for the cold-calling application's user interface."""

from __future__ import annotations

import tkinter as tk


def create_app() -> tk.Tk:
    """Create and return the root Tkinter application."""
    root = tk.Tk()
    root.title("Cold Calling App")
    return root


def main() -> None:
    """Launch the Tkinter main loop."""
    app = create_app()
    app.mainloop()


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
