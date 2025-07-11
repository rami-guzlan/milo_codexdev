from __future__ import annotations

import threading
from unittest.mock import MagicMock

import pytest

from milo_core.voice import conversation


class DummyThread:
    def __init__(self, target, daemon=False):
        self.target = target

    def start(self) -> None:  # pragma: no cover - thread logic mocked
        pass

    def join(self) -> None:  # pragma: no cover - thread logic mocked
        pass


def test_converse_handles_interruption(monkeypatch: pytest.MonkeyPatch) -> None:
    stop_event = threading.Event()
    monkeypatch.setattr(conversation.threading, "Event", lambda: stop_event)
    monkeypatch.setattr(conversation.threading, "Thread", DummyThread)

    session_memory = MagicMock()
    monkeypatch.setattr(
        conversation, "ShortTermMemory", MagicMock(return_value=session_memory)
    )

    model = MagicMock()
    model.stream_response.return_value = iter(["He", "llo, ", "world"])

    calls = ["hello", "raise"]

    def listen_side_effect() -> str:
        value = calls.pop(0)
        if value == "raise":
            raise KeyboardInterrupt
        return value

    stt = MagicMock()
    stt.listen.side_effect = listen_side_effect

    consumed: list[str] = []
    tts = MagicMock()

    def speak(tokens: list[str]) -> None:
        for i, token in enumerate(tokens):
            consumed.append(token)
            if i == 0:
                stop_event.set()
                tts.stop()
                break

    tts.speak.side_effect = speak

    memory_manager = MagicMock()

    with pytest.raises(KeyboardInterrupt):
        conversation.converse(model, stt, tts, memory_manager, MagicMock())

    assert len(consumed) < 3
    tts.stop.assert_called_once()
    assistant_calls = [
        c for c in session_memory.add_message.call_args_list if c.args[0] == "assistant"
    ]
    assert any("<interrupted_thought>" in c.args[1] for c in assistant_calls)
