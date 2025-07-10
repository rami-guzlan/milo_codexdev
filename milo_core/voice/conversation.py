from __future__ import annotations

import threading
from typing import Iterable

from milo_core.llm import LocalModelInterface
from milo_core.memory import ShortTermMemory
from milo_core.memory_manager import MemoryManager

from .interface import SpeechToText, TextToSpeech


def converse(
    model: LocalModelInterface,
    stt: SpeechToText,
    tts: TextToSpeech,
    memory_manager: MemoryManager,
) -> None:
    """Run a simple interactive voice conversation loop with memory."""

    session_memory = ShortTermMemory()

    while True:
        user_input = stt.listen()
        if not user_input:
            continue

        relevant_memories = memory_manager.retrieve_relevant_memories(user_input)
        if relevant_memories:
            context_str = " ".join(relevant_memories)
            session_memory.add_message(
                "system", f"Here is some relevant context: {context_str}"
            )

        print(f"User: {user_input}")
        session_memory.add_message("user", user_input)
        assistant_response_full: list[str] = []

        def generate() -> Iterable[str]:
            history = session_memory.get_messages()
            for token in model.stream_response(history):
                if stop_event.is_set():
                    break
                assistant_response_full.append(token)
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
        if stop_event.is_set() and assistant_response_full:
            interrupted = "".join(assistant_response_full)
            session_memory.add_message(
                "assistant", f"<interrupted_thought>{interrupted}</interrupted_thought>"
            )
        elif assistant_response_full:
            session_memory.add_message("assistant", "".join(assistant_response_full))

        if user_input.lower() == "goodbye":
            memory_manager.summarize_and_store_session(session_memory.get_messages())
            session_memory.clear()
