from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from milo_core.gui import app
from milo_core.gui.app import run_gui


class DummyThread:
    def __init__(self, target, daemon=False):
        self.target = target

    def start(self) -> None:
        self.target()


class DummyGUI:
    def __init__(self, on_end):
        DummyGUI.instance = self
        self.on_end = on_end
        self.messages: list[tuple[str, str]] = []
        self._stream_author = ""
        self._buffer = ""

    def set_send_callback(self, cb):
        self.cb = cb

    def add_message(self, author, msg):
        self.messages.append((author, msg))

    def start_stream_message(self, author):
        self._stream_author = author
        self._buffer = ""

    def append_stream_token(self, token):
        self._buffer += token

    def end_stream_message(self):
        self.messages.append((self._stream_author, self._buffer))

    def set_loading(self, loading):
        pass

    def schedule(self, cb, delay=0):
        cb()

    def mainloop(self):
        self.cb("hello")
        self.on_end()


class DummyGoodbyeGUI(DummyGUI):
    def mainloop(self):
        self.cb("goodbye")
        self.on_end()


def test_run_gui_basic_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app, "MiloGUI", DummyGUI)
    monkeypatch.setattr(app, "threading", MagicMock(Thread=DummyThread))
    model = MagicMock()
    model.stream_response.return_value = iter(["hi"])
    memory = MagicMock()
    memory.retrieve_relevant_memories.return_value = []
    memory.consolidate_memories.return_value = None
    run_gui(model, None, None, memory, MagicMock())
    assert ("You", "hello") in DummyGUI.instance.messages
    assert ("M.I.L.O", "hi") in DummyGUI.instance.messages
    memory.consolidate_memories.assert_called_once()


def test_run_gui_summarizes_on_goodbye(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app, "MiloGUI", DummyGoodbyeGUI)
    monkeypatch.setattr(app, "threading", MagicMock(Thread=DummyThread))
    model = MagicMock()
    model.stream_response.return_value = iter(["bye"])
    memory = MagicMock()
    memory.retrieve_relevant_memories.return_value = []
    memory.consolidate_memories.return_value = None
    run_gui(model, None, None, memory, MagicMock())
    memory.summarize_and_store_session.assert_called_once()
