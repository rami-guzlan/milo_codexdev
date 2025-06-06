from __future__ import annotations

import threading
from typing import Iterable

from milo_core.llm import LocalModelInterface
from milo_core.memory import Message

from .interface import SpeechToText, TextToSpeech


def converse(model: LocalModelInterface, stt: SpeechToText, tts: TextToSpeech) -> None:
    """Run a simple interactive voice conversation loop."""

    history: list[Message] = []

    while True:
        user_input = stt.listen()
        if not user_input:
            continue

        print(f"User: {user_input}")
        history.append(Message(role="user", content=user_input))
        assistant_accum: list[str] = []

        def generate() -> Iterable[str]:
            for token in model.stream_response(history):
                if stop_event.is_set():
                    break
                assistant_accum.append(token)
                yield token

        stop_event = threading.Event()

        def listen_interrupt() -> None:
            stt.listen()
            stop_event.set()
            tts.stop()

        listener = threading.Thread(target=listen_interrupt, daemon=True)
        listener.start()

        tts.speak(generate())
        listener.join()
        if assistant_accum:
            history.append(Message(role="assistant", content="".join(assistant_accum)))
