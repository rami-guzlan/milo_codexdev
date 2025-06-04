from __future__ import annotations

import threading
from typing import Iterable

from milo_core.llm import LocalModelInterface

from .interface import SpeechToText, TextToSpeech


def converse(model: LocalModelInterface, stt: SpeechToText, tts: TextToSpeech) -> None:
    """Run a simple interactive voice conversation loop."""

    while True:
        user_input = stt.listen()
        if not user_input:
            continue

        print(f"User: {user_input}")

        def generate() -> Iterable[str]:
            for token in model.stream_response(user_input):
                if stop_event.is_set():
                    break
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
