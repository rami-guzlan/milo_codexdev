from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from milo_core.gui import app
from milo_core.gui.app import run_gui


class DummyGUI:
    def __init__(self, on_end):
        DummyGUI.instance = self
        self.on_end = on_end
        self.messages: list[tuple[str, str]] = []

    def set_send_callback(self, cb):
        self.cb = cb

    def add_message(self, author, msg):
        self.messages.append((author, msg))

    def mainloop(self):
        self.cb("hello")
        self.on_end()


class DummyGoodbyeGUI(DummyGUI):
    def mainloop(self):
        self.cb("goodbye")
        self.on_end()


def test_run_gui_basic_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app, "MiloGUI", DummyGUI)
    model = MagicMock()
    model.stream_response.return_value = iter(["hi"])
    memory = MagicMock()
    memory.retrieve_relevant_memories.return_value = []
    memory.consolidate_memories.return_value = None
    run_gui(model, None, None, memory)
    assert ("You", "hello") in DummyGUI.instance.messages
    assert ("M.I.L.O", "hi") in DummyGUI.instance.messages
    memory.consolidate_memories.assert_called_once()


def test_run_gui_summarizes_on_goodbye(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app, "MiloGUI", DummyGoodbyeGUI)
    model = MagicMock()
    model.stream_response.return_value = iter(["bye"])
    memory = MagicMock()
    memory.retrieve_relevant_memories.return_value = []
    memory.consolidate_memories.return_value = None
    run_gui(model, None, None, memory)
    memory.summarize_and_store_session.assert_called_once()
